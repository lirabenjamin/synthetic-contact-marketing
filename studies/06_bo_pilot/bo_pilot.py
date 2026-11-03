"""Adaptive pilot engine for the multi-round allocation game (pilot 1).

Plan agreed on Slack 2026-10-31 (#synthetic-contact-marketing):
  * Three knobs, drawn per participant: signal-to-noise (snr), payoff curvature (alpha), rounds.
  * Outcome: each person's learning, measured from allocations only (no belief questions).
  * GP (Matern 5/2, one length-scale per knob, + white noise) on outcome ~ knobs.
  * Thompson sampling: every new participant gets the argmax of a fresh posterior draw.
  * 25% of assignments stay uniformly random; the first N_INIT are all random.
  * Refit after every REFIT_EVERY completions; caps on minutes per person and total N.

The game (2 markets, R and D):
  revenue_k = SCALE * w_k * share_k^alpha * exp(eps_k),  eps_k ~ N(0, sigma)
  log(w_R / w_D) = DELTA (fixed magnitude), sigma = DELTA / snr.
  Best share to R: s* = 1 / (1 + exp(-DELTA / (1 - alpha))).

Storage is abstracted so the same code runs against an in-memory store (simulation)
and MongoDB (live: the app claims assignments from `bo_queue` and writes allocations
to `bo_participants`; `python bo_pilot.py step` refits and refills the queue).
"""
from __future__ import annotations

import argparse
import json
import os
import time
import uuid
import warnings
from dataclasses import dataclass, field, asdict

import numpy as np
from scipy.stats import qmc
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel

# A length-scale at its upper bound is a result (the knob does not matter), not an error.
warnings.filterwarnings("ignore", category=ConvergenceWarning)


# ── Configuration ────────────────────────────────────────────────────────────
@dataclass
class Config:
    # Knob ranges
    snr_range: tuple = (0.25, 4.0)      # searched on a log scale
    alpha_range: tuple = (0.2, 0.8)     # payoff curvature; 1 = linear (corner optimum)
    rounds_range: tuple = (6, 15)       # integer
    # Game constants (pilot 1 fixes the magnitude; pilot 2 varies it)
    delta: float = 0.4                  # log(w_R / w_D): R pays about 1.5x per dollar
    scale: float = 50_000               # revenue at 100% share in the D market, before noise
    budget: float = 100_000
    s_min: float = 0.05
    s_max: float = 0.95
    # Caps
    minutes_base: float = 4.0           # instructions + chat-free overhead (assumption)
    minutes_per_round: float = 0.6      # about 35 s per round (assumption)
    minutes_cap: float = 12.0
    n_max: int = 120
    # Search policy
    n_init: int = 20                    # all-random warm-up
    refit_every: int = 10
    p_random: float = 0.25
    n_candidates: int = 1024
    queue_size: int = 25                # assignments kept ready for arrivals
    outcome: str = "pp"                 # "pp": gap closed in points; "fraction": share of gap closed
    seed: int = 20261103

    KNOBS = ("snr", "alpha", "rounds")

    def minutes(self, rounds):
        return self.minutes_base + self.minutes_per_round * np.asarray(rounds)

    def max_rounds(self):
        r = int(np.floor((self.minutes_cap - self.minutes_base) / self.minutes_per_round + 1e-9))
        return min(r, self.rounds_range[1])


# ── Game ─────────────────────────────────────────────────────────────────────
def best_share(cfg: Config, alpha):
    s = 1.0 / (1.0 + np.exp(-cfg.delta / (1.0 - np.asarray(alpha))))
    return np.clip(s, cfg.s_min, cfg.s_max)


def revenue(cfg: Config, share_r, alpha, snr, rng):
    """Revenue in (R, D) for one round. Vectorised over people."""
    sigma = cfg.delta / np.asarray(snr)
    share_r = np.asarray(share_r)
    w_r, w_d = np.exp(cfg.delta), 1.0
    eps_r = rng.normal(0, 1, share_r.shape) * sigma
    eps_d = rng.normal(0, 1, share_r.shape) * sigma
    rev_r = cfg.scale * w_r * share_r ** alpha * np.exp(eps_r)
    rev_d = cfg.scale * w_d * (1 - share_r) ** alpha * np.exp(eps_d)
    return rev_r, rev_d


# ── Outcome: learning from allocations ───────────────────────────────────────
def learning_scores(cfg: Config, shares, alpha, outcome=None):
    """Fit a line to |share_t - s*| over rounds, one row per person (vectorised).

    pp:       drop in the fitted gap from round 1 to the last round, in percentage points.
    fraction: that drop divided by the fitted round-1 gap (share of the gap closed).
    Positive = moved toward the best split.
    """
    outcome = outcome or cfg.outcome
    shares = np.atleast_2d(np.asarray(shares, float))
    n_rounds = shares.shape[1]
    t = np.arange(1, n_rounds + 1) - (n_rounds + 1) / 2
    gap = np.abs(shares - best_share(cfg, alpha))
    b = gap @ t / (t @ t)
    drop = -b * (n_rounds - 1)
    if outcome == "fraction":
        g1 = gap.mean(axis=1) - b * (n_rounds - 1) / 2       # fitted gap at round 1
        return drop / np.maximum(g1, 0.02)
    return 100 * drop


def learning_score(cfg: Config, shares, alpha, outcome=None):
    return float(learning_scores(cfg, shares, alpha, outcome)[0])


# ── Knob space <-> unit cube ─────────────────────────────────────────────────
def to_unit(cfg: Config, snr, alpha, rounds):
    lo, hi = np.log(cfg.snr_range)
    return np.column_stack([
        (np.log(snr) - lo) / (hi - lo),
        (np.asarray(alpha) - cfg.alpha_range[0]) / (cfg.alpha_range[1] - cfg.alpha_range[0]),
        (np.asarray(rounds) - cfg.rounds_range[0]) / (cfg.rounds_range[1] - cfg.rounds_range[0]),
    ])


def from_unit(cfg: Config, u):
    u = np.atleast_2d(u)
    lo, hi = np.log(cfg.snr_range)
    snr = np.exp(lo + u[:, 0] * (hi - lo))
    alpha = cfg.alpha_range[0] + u[:, 1] * (cfg.alpha_range[1] - cfg.alpha_range[0])
    rounds = np.rint(cfg.rounds_range[0] + u[:, 2] * (cfg.rounds_range[1] - cfg.rounds_range[0])).astype(int)
    return snr, alpha, rounds


def feasible(cfg: Config, rounds):
    return cfg.minutes(rounds) <= cfg.minutes_cap + 1e-9


def random_knobs(cfg: Config, rng, n=1):
    """Uniform over the feasible space (log-uniform snr, uniform alpha, uniform integer rounds)."""
    u = rng.uniform(size=(n, 3))
    r_lo, r_hi = cfg.rounds_range[0], cfg.max_rounds()
    u[:, 2] = (rng.integers(r_lo, r_hi + 1, n) - cfg.rounds_range[0]) / (cfg.rounds_range[1] - cfg.rounds_range[0])
    return from_unit(cfg, u)


def candidate_set(cfg: Config):
    """Fixed Sobol set of feasible settings; Thompson draws pick from these."""
    u = qmc.Sobol(d=3, scramble=True, seed=cfg.seed).random(cfg.n_candidates)
    snr, alpha, rounds = from_unit(cfg, u)
    keep = feasible(cfg, rounds)
    return snr[keep], alpha[keep], rounds[keep]


def eval_grid(cfg: Config, n_snr=21, n_alpha=21):
    """Regular grid used for the dashboard (heatmaps and slices)."""
    snr = np.exp(np.linspace(*np.log(cfg.snr_range), n_snr))
    alpha = np.linspace(*cfg.alpha_range, n_alpha)
    rounds = np.arange(cfg.rounds_range[0], cfg.rounds_range[1] + 1)
    S, A, R = np.meshgrid(snr, alpha, rounds, indexing="ij")
    return {"snr": snr, "alpha": alpha, "rounds": rounds,
            "flat": (S.ravel(), A.ravel(), R.ravel()), "shape": S.shape}


# ── GP model ─────────────────────────────────────────────────────────────────
def make_gp(seed):
    """Bounds are in unit-cube and standardised-y units.
    Length-scale >= 0.15: the outcome cannot swing up and down within 15% of a knob's range.
    Noise >= 0.3 of the outcome variance: one person's learning score is mostly noise, so the GP
    must not thread its mean through every point (without this floor, early fits with 20 people
    collapse to tiny length-scales and zero noise). A length-scale at the upper bound means
    that knob does not matter."""
    kernel = (ConstantKernel(0.5, (1e-2, 1e1))
              * Matern(length_scale=[0.5, 0.5, 0.5], length_scale_bounds=(0.15, 20.0), nu=2.5)
              + WhiteKernel(0.7, (0.3, 2.0)))
    return GaussianProcessRegressor(kernel, normalize_y=True, n_restarts_optimizer=4, random_state=seed)


def gp_hyper(gp):
    k = gp.kernel_
    return {"amplitude": float(np.sqrt(k.k1.k1.constant_value)),
            "length_scales": [float(x) for x in np.atleast_1d(k.k1.k2.length_scale)],
            "noise_sd": float(np.sqrt(k.k2.noise_level))}


class Posterior:
    """GP fitted to completed participants, with a cached joint posterior over the candidates
    so a Thompson draw costs one matrix-vector product."""

    def __init__(self, cfg: Config, X_unit, y, seed):
        self.cfg = cfg
        self.gp = make_gp(seed).fit(X_unit, y)
        cs, ca, cr = candidate_set(cfg)
        self.cand = (cs, ca, cr)
        self.Xc = to_unit(cfg, cs, ca, cr)
        mu, cov = self.gp.predict(self.Xc, return_cov=True)
        self.mu = mu
        self.L = np.linalg.cholesky(cov + 1e-8 * np.mean(np.diag(cov)) * np.eye(len(mu)))

    def thompson_index(self, rng, n=1):
        z = rng.standard_normal((len(self.mu), n))
        draws = self.mu[:, None] + self.L @ z
        return draws.argmax(axis=0)

    def recommend(self):
        i = int(np.argmax(self.mu))
        return {k: v[i].item() for k, v in zip(Config.KNOBS, self.cand)}


# ── Stores ───────────────────────────────────────────────────────────────────
class MemoryStore:
    """In-process store with the same interface as MongoStore. Used by the simulation."""

    def __init__(self):
        self.queue, self.participants, self.snapshots, self.meta = [], {}, [], {"last_fit_n": 0, "gp_version": 0}

    def push_queue(self, items):
        self.queue.extend(items)

    def clear_queue(self):
        self.queue = [q for q in self.queue if q["status"] != "queued"]

    def queued_count(self):
        return sum(q["status"] == "queued" for q in self.queue)

    def claim(self, pid, t):
        for q in self.queue:
            if q["status"] == "queued":
                q.update(status="claimed", pid=pid, claimed_at=t)
                self.participants[pid] = {"pid": pid, "started_at": t, **{k: q[k] for k in q if k not in ("status",)}}
                return q
        return None

    def complete(self, pid, shares, rev_r, rev_d, t):
        self.participants[pid].update(shares=list(map(float, shares)), rev_r=list(map(float, rev_r)),
                                      rev_d=list(map(float, rev_d)), finished_at=t, status="complete")

    def completed(self):
        return [p for p in self.participants.values() if p.get("status") == "complete"]

    def all_participants(self):
        return list(self.participants.values())

    def set_score(self, pid, score):
        self.participants[pid]["score"] = score

    def add_snapshot(self, snap):
        self.snapshots.append(snap)

    def get_snapshots(self):
        return self.snapshots

    def get_meta(self):
        return dict(self.meta)

    def set_meta(self, **kw):
        self.meta.update(kw)


class MongoStore:
    """Live store. Collections: bo_queue, bo_participants, bo_snapshots, bo_meta.

    App contract (see README.md):
      start:  claim(pid)  -> findOneAndUpdate on bo_queue {status:'queued'} sorted by created_at
      finish: write {shares, rev_r, rev_d, finished_at, status:'complete'} to bo_participants[pid]
    """

    def __init__(self, uri, db):
        from pymongo import MongoClient, ReturnDocument
        self._rd = ReturnDocument
        self.db = MongoClient(uri, serverSelectionTimeoutMS=5000)[db]

    def push_queue(self, items):
        if items:
            self.db.bo_queue.insert_many([dict(i) for i in items])

    def clear_queue(self):
        self.db.bo_queue.delete_many({"status": "queued"})

    def queued_count(self):
        return self.db.bo_queue.count_documents({"status": "queued"})

    def claim(self, pid, t):
        q = self.db.bo_queue.find_one_and_update(
            {"status": "queued"}, {"$set": {"status": "claimed", "pid": pid, "claimed_at": t}},
            sort=[("created_at", 1)], return_document=self._rd.AFTER)
        if q is None:
            return None
        doc = {k: v for k, v in q.items() if k not in ("_id", "status")}
        self.db.bo_participants.update_one({"pid": pid}, {"$set": {**doc, "started_at": t}}, upsert=True)
        return q

    def complete(self, pid, shares, rev_r, rev_d, t):
        self.db.bo_participants.update_one({"pid": pid}, {"$set": {
            "shares": list(map(float, shares)), "rev_r": list(map(float, rev_r)),
            "rev_d": list(map(float, rev_d)), "finished_at": t, "status": "complete"}})

    def completed(self):
        return list(self.db.bo_participants.find({"status": "complete"}, {"_id": 0}))

    def all_participants(self):
        return list(self.db.bo_participants.find({}, {"_id": 0}))

    def set_score(self, pid, score):
        self.db.bo_participants.update_one({"pid": pid}, {"$set": {"score": score}})

    def add_snapshot(self, snap):
        self.db.bo_snapshots.insert_one(json.loads(json.dumps(snap)))

    def get_snapshots(self):
        return list(self.db.bo_snapshots.find({}, {"_id": 0}).sort("version", 1))

    def get_meta(self):
        m = self.db.bo_meta.find_one({"_id": "state"}) or {}
        return {"last_fit_n": m.get("last_fit_n", 0), "gp_version": m.get("gp_version", 0)}

    def set_meta(self, **kw):
        self.db.bo_meta.update_one({"_id": "state"}, {"$set": kw}, upsert=True)


# ── Engine ───────────────────────────────────────────────────────────────────
@dataclass
class Engine:
    cfg: Config
    store: object
    truth: object = None                # optional callable(snr, alpha, rounds) -> expected score (simulation)
    rng: np.random.Generator = field(default=None)
    post: Posterior = None

    def __post_init__(self):
        self.rng = self.rng or np.random.default_rng(self.cfg.seed)

    # assignments
    def _item(self, snr, alpha, rounds, kind, now):
        return {"aid": uuid.uuid4().hex[:10], "snr": float(snr), "alpha": float(alpha), "rounds": int(rounds),
                "sigma": float(self.cfg.delta / snr), "best_share": float(best_share(self.cfg, alpha)),
                "kind": kind, "gp_version": self.store.get_meta()["gp_version"],
                "created_at": now, "status": "queued"}

    def make_assignments(self, n, now):
        items = []
        for _ in range(n):
            if self.post is None:
                s, a, r = random_knobs(self.cfg, self.rng)
                items.append(self._item(s[0], a[0], r[0], "warm-up random", now))
            elif self.rng.uniform() < self.cfg.p_random:
                s, a, r = random_knobs(self.cfg, self.rng)
                items.append(self._item(s[0], a[0], r[0], "random", now))
            else:
                i = self.post.thompson_index(self.rng)[0]
                cs, ca, cr = self.post.cand
                items.append(self._item(cs[i], ca[i], cr[i], "thompson", now))
        return items

    def n_issued(self):
        return len(self.store.all_participants())

    def refill(self, now):
        """Top the queue up to queue_size, never issuing more than n_max in total."""
        room = self.cfg.n_max - self.n_issued() - self.store.queued_count()
        need = min(self.cfg.queue_size - self.store.queued_count(), room)
        if need > 0:
            self.store.push_queue(self.make_assignments(need, now))

    # learning
    def score_completed(self):
        done = self.store.completed()
        for p in done:
            if "score" not in p:
                p["score"] = learning_score(self.cfg, p["shares"], p["alpha"])
                self.store.set_score(p["pid"], p["score"])
        return done

    def maybe_refit(self, now, force=False):
        done = self.score_completed()
        meta = self.store.get_meta()
        n = len(done)
        due = n >= self.cfg.n_init and n - meta["last_fit_n"] >= self.cfg.refit_every
        if not (due or (force and n >= 5)):
            return False
        X = to_unit(self.cfg, [p["snr"] for p in done], [p["alpha"] for p in done], [p["rounds"] for p in done])
        y = np.array([p["score"] for p in done])
        version = meta["gp_version"] + 1
        self.post = Posterior(self.cfg, X, y, self.cfg.seed + version)
        self.store.set_meta(last_fit_n=n, gp_version=version)
        self.store.add_snapshot(self.snapshot(version, n, now))
        # Unclaimed assignments were drawn from the old GP: replace them.
        self.store.clear_queue()
        self.refill(now)
        return True

    def load_posterior(self):
        """Rebuild the most recent GP (same data it was fitted on) without logging a new snapshot."""
        meta = self.store.get_meta()
        if meta["gp_version"] == 0:
            return
        done = sorted(self.score_completed(), key=lambda p: p["finished_at"])[:meta["last_fit_n"]]
        X = to_unit(self.cfg, [p["snr"] for p in done], [p["alpha"] for p in done], [p["rounds"] for p in done])
        self.post = Posterior(self.cfg, X, np.array([p["score"] for p in done]), self.cfg.seed + meta["gp_version"])

    # dashboard snapshot
    def snapshot(self, version, n, now, n_draws=500, n_example_draws=3):
        cfg, post = self.cfg, self.post
        rec = post.recommend()
        g = eval_grid(cfg)
        Xg = to_unit(cfg, *g["flat"])
        mu, sd = post.gp.predict(Xg, return_std=True)
        # Where Thompson would send the next person: argmax of many draws
        idx = post.thompson_index(self.rng, n_draws)
        cs, ca, cr = post.cand
        picks = {"snr": cs[idx].tolist(), "alpha": ca[idx].tolist(), "rounds": cr[idx].tolist()}
        # Example draws along 1D slices through the recommendation
        slices = {}
        for k, values in (("snr", g["snr"]), ("alpha", g["alpha"]),
                          ("rounds", np.arange(cfg.rounds_range[0], cfg.rounds_range[1] + 1))):
            pts = {kk: np.full(len(values), rec[kk], float) for kk in Config.KNOBS}
            pts[k] = np.asarray(values, float)
            Xs = to_unit(cfg, pts["snr"], pts["alpha"], pts["rounds"])
            m, c = post.gp.predict(Xs, return_cov=True)
            Ls = np.linalg.cholesky(c + 1e-8 * np.mean(np.diag(c)) * np.eye(len(m)))
            draws = (m[:, None] + Ls @ self.rng.standard_normal((len(m), n_example_draws))).T
            slices[k] = {"x": list(map(float, values)), "mean": m.tolist(),
                         "sd": np.sqrt(np.clip(np.diag(c), 0, None)).tolist(), "draws": draws.tolist()}
            if self.truth is not None:
                slices[k]["truth"] = self.truth(pts["snr"], pts["alpha"], pts["rounds"]).tolist()
        snap = {"version": version, "n": n, "time": now, "hyper": gp_hyper(post.gp),
                "recommend": rec, "rec_pred": float(post.mu.max()),
                "grid_mean": np.round(mu, 3).tolist(), "grid_sd": np.round(sd, 3).tolist(),
                "picks": picks, "slices": slices}
        if self.truth is not None:
            snap["rec_true"] = float(self.truth([rec["snr"]], [rec["alpha"]], [rec["rounds"]])[0])
        return snap


# ── CLI (live mode) ──────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Live adaptive-pilot job (MongoDB).")
    ap.add_argument("command", choices=["init", "step", "refit"])
    ap.add_argument("--db", default=os.environ.get("BO_DB", "bo_pilot"))
    ap.add_argument("--uri", default=os.environ.get("MDB_MCP_CONNECTION_STRING"))
    args = ap.parse_args()
    if not args.uri:
        raise SystemExit("Set --uri or MDB_MCP_CONNECTION_STRING.")
    cfg = Config()
    store = MongoStore(args.uri, args.db)
    eng = Engine(cfg, store)
    now = time.time()
    if args.command == "init":
        store.set_meta(last_fit_n=0, gp_version=0, config=asdict(cfg))
        eng.refill(now)
        print(f"Queue holds {store.queued_count()} warm-up assignments.")
        return
    if not eng.maybe_refit(now, force=args.command == "refit"):
        eng.load_posterior()   # the job is stateless: rebuild the last GP so top-ups use Thompson draws
    eng.refill(now)
    print(f"Completed {len(store.completed())}, queued {store.queued_count()}, GP version {store.get_meta()['gp_version']}.")


if __name__ == "__main__":
    main()
