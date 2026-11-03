"""Simulated participants and a simulated Prolific launch, to check the adaptive loop
before any real person plays.

Simulated person (ASSUMPTIONS for checking the machinery, not estimates from data):
  * Belief about DELTA = log(R pays / D pays). Prior mean ~ N(-0.4, 0.35): people think the
    D market pays better (March pilot: about 46% of budget to R). Prior SD tau0 ~ lognormal(log 0.3, 0.5).
  * Each round they see revenue in both markets and update like a Kalman / normal learner
    with the true noise of the round's signal (sigma * sqrt(2)). Low noise -> fast learning.
  * They allocate the best share for their current belief, plus noise (SD 10 points),
    clipped to [5%, 95%].
  * 20% are inattentive from the start (random allocations around 50%).
  * Fatigue: after round 10, each extra round carries a 10% chance of disengaging for the
    rest of the game (random allocations).
Because we know these rules, we can compute the TRUE expected learning score at every
setting and check whether the GP + Thompson loop finds the best one.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from dashboard import export_data
from bo_pilot import Config, Engine, MemoryStore, eval_grid, learning_scores, revenue

PRIOR_MEAN, PRIOR_SD = -0.4, 0.35
TAU0_LOG_MEAN, TAU0_LOG_SD = np.log(0.3), 0.5
ALLOC_SD = 0.10
P_INATTENTIVE = 0.20
FATIGUE_START, FATIGUE_HAZARD = 10, 0.10
ASSUMPTIONS = {"Prior belief about log(R/D) pay": f"N({PRIOR_MEAN}, {PRIOR_SD}): most people think the D market pays more",
               "Prior uncertainty (SD)": f"lognormal, median {np.exp(TAU0_LOG_MEAN):.2f}",
               "Updating": "normal learner that knows the round's noise, so clean feedback means fast learning",
               "Allocation noise": f"SD {int(ALLOC_SD * 100)} points of budget",
               "Inattentive from the start": f"{int(P_INATTENTIVE * 100)}%",
               "Fatigue": f"after round {FATIGUE_START}, {int(FATIGUE_HAZARD * 100)}% chance per round of clicking at random for the rest of the game"}


def play(cfg: Config, snr, alpha, rounds, rng, n=1):
    """Simulate n people at one setting. Returns shares (n x rounds), rev_r, rev_d."""
    sig_y = cfg.delta / snr * np.sqrt(2)
    m = rng.normal(PRIOR_MEAN, PRIOR_SD, n)
    v = np.exp(rng.normal(TAU0_LOG_MEAN, TAU0_LOG_SD, n)) ** 2
    engaged = rng.uniform(size=n) > P_INATTENTIVE
    shares, rr, rd = np.empty((n, rounds)), np.empty((n, rounds)), np.empty((n, rounds))
    for t in range(rounds):
        if t >= FATIGUE_START:
            engaged &= rng.uniform(size=n) > FATIGUE_HAZARD
        target = 1 / (1 + np.exp(-m / (1 - alpha)))
        s = np.where(engaged, target + rng.normal(0, ALLOC_SD, n), rng.uniform(0.3, 0.7, n))
        s = np.clip(s, cfg.s_min, cfg.s_max)
        r_r, r_d = revenue(cfg, s, alpha, snr, rng)
        # signal about delta, after removing the known effect of the split
        y = np.log(r_r / r_d) - alpha * (np.log(s) - np.log(1 - s))
        k = v / (v + sig_y ** 2)
        m, v = m + k * (y - m), (1 - k) * v
        shares[:, t], rr[:, t], rd[:, t] = s, r_r, r_d
    return shares, rr, rd


def true_surface(cfg: Config, n_people=600, seed=7):
    """Expected learning score on the dashboard grid (Monte Carlo, common random numbers)."""
    g = eval_grid(cfg)
    S, A, R = g["flat"]
    out = np.empty(len(S))
    for i, (s, a, r) in enumerate(zip(S, A, R)):
        sh, _, _ = play(cfg, s, a, int(r), np.random.default_rng(seed), n_people)
        out[i] = learning_scores(cfg, sh, a).mean()
    return out.reshape(g["shape"])


def truth_fn(cfg: Config, surface):
    """Interpolate the true surface (log snr, alpha, rounds) for arbitrary settings."""
    from scipy.interpolate import RegularGridInterpolator
    g = eval_grid(cfg)
    f = RegularGridInterpolator((np.log(g["snr"]), g["alpha"], g["rounds"].astype(float)), surface)
    return lambda snr, alpha, rounds: f(np.column_stack([np.log(snr), alpha, np.asarray(rounds, float)]))


def run_launch(cfg: Config, truth=None, arrivals_per_min=1.5, seed=11):
    """Simulated Prolific launch: Poisson arrivals, people overlap, assignments are claimed
    from the queue at arrival, the GP refits after every `refit_every` completions."""
    rng = np.random.default_rng(seed)
    store = MemoryStore()
    eng = Engine(cfg, store, truth=truth, rng=np.random.default_rng(seed + 1))
    t, events, pid = 0.0, [], 0
    eng.refill(t)
    # arrivals until n_max people have claimed an assignment
    while pid < cfg.n_max:
        t += rng.exponential(1 / arrivals_per_min)
        events.append(("arrive", t, f"p{pid:03d}"))
        pid += 1
    pending = sorted(events, key=lambda e: e[1])
    while pending:
        kind, t, p = pending.pop(0)
        if kind == "arrive":
            q = store.claim(p, t)
            if q is None:                       # queue empty: the live job would top it up
                eng.refill(t)
                q = store.claim(p, t)
            dur = cfg.minutes(q["rounds"]) * np.exp(rng.normal(0, 0.25))
            pending.append(("finish", t + dur, p))
            pending.sort(key=lambda e: e[1])
        else:
            q = store.participants[p]
            sh, rr, rd = play(cfg, q["snr"], q["alpha"], q["rounds"], rng)
            store.complete(p, sh[0], rr[0], rd[0], t)
            if truth is not None:
                q["true_mean"] = float(truth([q["snr"]], [q["alpha"]], [q["rounds"]])[0])
            eng.maybe_refit(t)
            eng.refill(t)
    eng.score_completed()
    return store, eng


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="output/sim_run.json")
    ap.add_argument("--outcome", default="pp", choices=["pp", "fraction"])
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()
    cfg = Config(outcome=args.outcome)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    surface = true_surface(cfg)
    store, eng = run_launch(cfg, truth=truth_fn(cfg, surface), seed=args.seed)
    Path(args.out).write_text(json.dumps(export_data(cfg, store, surface, ASSUMPTIONS), default=float))
    last = store.get_snapshots()[-1]
    print(f"{len(store.completed())} completed, {len(store.get_snapshots())} refits. "
          f"Recommendation {last['recommend']} -> true {last['rec_true']:.1f}; "
          f"best feasible true value {np.max(surface[:, :, :cfg.max_rounds() - cfg.rounds_range[0] + 1]):.1f}")


if __name__ == "__main__":
    main()
