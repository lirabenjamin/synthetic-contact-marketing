"""Fit a Bayesian learner to each person's allocations: prior mean, prior strength, choice noise.

Model (same learner as studies/05_bayesian_game_design/simulate.R, adapted to the share^alpha game)
  theta = log(market A pays / market B pays). Truth: +delta if A is the better market, else -delta.
  Belief before round 1:            m_1 = mu0                         (prior mean)
  Signal from round t:              y_t = log(revA_t / revB_t) - alpha * log(s_t / (1 - s_t))
                                    (the revenue ratio with the effect of the split removed)
  Update after round t:             m_{t+1} = m_t + (y_t - m_t) / (n0 + t)
                                    n0 = prior strength, in rounds of feedback. The weight on the
                                    newest round, 1 / (n0 + t), is the learning rate.
  Allocation in round t:            s_t ~ Normal(s*(m_t), sig_s), censored at the 5% / 95% limits,
                                    with s*(m) = 1 / (1 + exp(-m / (1 - alpha)))
  A large n0 means a sticky prior.

Evidence weight (omega) compares n0 with an ideal Bayesian for this game. The better market is drawn
at random, so the correct prior is centred on 0 with SD about delta, and each round's signal has
SD sigma * sqrt(2). The ideal prior strength is n0* = 2 sigma^2 / delta^2 = 2 / SNR^2, and
omega = n0* / n0: 1 = ideal, below 1 = underweights evidence (conservative), above 1 = overreacts.
Equivalently, the person acts like a Bayesian who thinks each round is omega times as informative.

Assumption: the learner knows alpha (the curve shape) when reading the signal and choosing a split.

Estimation: exact grid posterior per person over (mu0, log n0, log sig_s) with flat priors on the
grid. Reports posterior medians and 80% intervals, so weakly identified people get wide intervals.

  python fit_learner.py --games games.json      # JSON copied from the Market Split page
  python fit_learner.py --mongo [--db bo_pilot] # live participants (MDB_MCP_CONNECTION_STRING)
  python fit_learner.py --recovery              # parameter recovery across game settings
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
from scipy.stats import norm, spearmanr

S_MIN, S_MAX = 0.05, 0.95
MU0 = np.round(np.linspace(-2.5, 2.5, 51), 3)
LOG_N0 = np.linspace(np.log(0.05), np.log(100), 39)
LOG_SIG = np.linspace(np.log(0.02), np.log(0.4), 10)
HERE = Path(__file__).parent


def s_star(m, alpha):
    return np.clip(1 / (1 + np.exp(-m / (1 - alpha))), S_MIN, S_MAX)


def signals(shares, rev_a, rev_b, alpha):
    s = np.asarray(shares, float)
    return np.log(np.asarray(rev_a, float) / np.asarray(rev_b, float)) - alpha * np.log(s / (1 - s))


def belief_paths(mu0, n0, y):
    """Beliefs before each round, for every (mu0, n0) pair: shape (len(mu0), len(y))."""
    m = np.empty((len(mu0), len(y)))
    m[:, 0] = mu0
    for t in range(len(y) - 1):
        m[:, t + 1] = m[:, t] + (y[t] - m[:, t]) / (n0 + t + 1)
    return m


def fit_person(shares, rev_a, rev_b, alpha):
    s = np.asarray(shares, float)
    y = signals(s, rev_a, rev_b, alpha)
    M, LN = (a.ravel() for a in np.meshgrid(MU0, LOG_N0, indexing="ij"))
    pred = s_star(belief_paths(M, np.exp(LN), y), alpha)                   # (P, T)
    sig = np.exp(LOG_SIG)[None, None, :]
    z = (s[None, :, None] - pred[:, :, None]) / sig
    lo, hi = s[None, :, None] <= S_MIN + 1e-6, s[None, :, None] >= S_MAX - 1e-6
    ll = np.where(lo, norm.logcdf((S_MIN - pred[:, :, None]) / sig),
                  np.where(hi, norm.logsf((S_MAX - pred[:, :, None]) / sig), norm.logpdf(z) - np.log(sig)))
    ll = ll.sum(axis=1)                                                   # (P, S)
    post = np.exp(ll - ll.max())
    post /= post.sum()
    p3 = post.reshape(len(MU0), len(LOG_N0), len(LOG_SIG))

    def summ(values, marg):
        c = np.cumsum(marg)
        q = lambda p: float(values[min(np.searchsorted(c, p), len(values) - 1)])
        return q(0.5), q(0.1), q(0.9)

    mu = summ(MU0, p3.sum(axis=(1, 2)))
    ln0 = summ(LOG_N0, p3.sum(axis=(0, 2)))
    lsig = summ(LOG_SIG, p3.sum(axis=(0, 1)))
    i_map = np.unravel_index(post.argmax(), post.shape)[0]
    path = belief_paths(M[[i_map]], np.exp(LN[[i_map]]), y)[0]
    n0 = np.exp(ln0)
    return {"mu0": mu[0], "mu0_lo": mu[1], "mu0_hi": mu[2],
            "n0": float(n0[0]), "n0_lo": float(n0[1]), "n0_hi": float(n0[2]),
            "lr1": 1 / (1 + float(n0[0])), "sig_s": float(np.exp(lsig[0])),
            "fitted_shares": s_star(path, alpha).round(3).tolist(), "beliefs": path.round(3).tolist()}


# ── Parameter recovery ───────────────────────────────────────────────────────
POP = {"mu0_offset": -0.4, "mu0_sd": 0.35, "n0_median": 4.0, "log_n0_sd": 0.6, "sig_s": 0.10}


def simulate_person(rng, delta, alpha, snr, rounds, mu0, n0, sig_s):
    """Market A is the better market here (theta = +delta)."""
    sigma = delta / snr
    m, s_all, ra, rb = mu0, [], [], []
    for t in range(rounds):
        s = float(np.clip(s_star(m, alpha) + rng.normal(0, sig_s), S_MIN, S_MAX))
        r_a = np.exp(delta) * s ** alpha * np.exp(rng.normal(0, sigma))
        r_b = (1 - s) ** alpha * np.exp(rng.normal(0, sigma))
        y = np.log(r_a / r_b) - alpha * np.log(s / (1 - s))
        m = m + (y - m) / (n0 + t + 1)
        s_all.append(s); ra.append(r_a); rb.append(r_b)
    return s_all, ra, rb


def recovery(n_people=200, seed=11):
    rows = []
    for delta in (0.4, 0.8):
        for alpha in (0.35, 0.65):
            for snr in (1.0, 2.0, 4.0):
                for rounds in (8, 13):
                    rng = np.random.default_rng(seed)
                    mu0 = delta + POP["mu0_offset"] + rng.normal(0, POP["mu0_sd"], n_people)
                    n0 = POP["n0_median"] * np.exp(rng.normal(0, POP["log_n0_sd"], n_people))
                    fits = [fit_person(*simulate_person(rng, delta, alpha, snr, rounds, a, b, POP["sig_s"]), alpha)
                            for a, b in zip(mu0, n0)]
                    mu_hat = np.array([f["mu0"] for f in fits])
                    n0_hat = np.array([f["n0"] for f in fits])
                    covered = np.mean([f["n0_lo"] <= b <= f["n0_hi"] for f, b in zip(fits, n0)])
                    width = np.median([np.log(f["n0_hi"] / f["n0_lo"]) for f in fits])
                    rows.append({"delta": delta, "alpha": alpha, "snr": snr, "rounds": rounds,
                                 "r_mu0": float(np.corrcoef(mu0, mu_hat)[0, 1]),
                                 "rho_n0": float(spearmanr(n0, n0_hat)[0]),
                                 "n0_80ci_coverage": float(covered),
                                 "n0_80ci_fold_width": float(np.exp(width))})
                    print({k: round(v, 2) if isinstance(v, float) else v for k, v in rows[-1].items()}, flush=True)
    return rows


def fit_records(records):
    """records: dicts with shares_A, rev_A, rev_B, alpha (the Market Split JSON format)."""
    out = []
    for r in records:
        f = fit_person(r["shares_A"], r["rev_A"], r["rev_B"], r["alpha"])
        truth = r["delta"] if r.get("better", "A") == "A" else -r["delta"]
        n0_ideal = 2 / r["snr"] ** 2
        out.append({**{k: r.get(k) for k in ("when", "pid", "delta", "alpha", "snr", "rounds")}, "theta_true": truth,
                    **{k: v for k, v in f.items() if k not in ("fitted_shares", "beliefs")},
                    "n0_ideal": n0_ideal, "omega": n0_ideal / f["n0"], "omega_lo": n0_ideal / f["n0_hi"],
                    "omega_hi": n0_ideal / f["n0_lo"], "final_belief": f["beliefs"][-1]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", help="JSON copied from the Market Split page")
    ap.add_argument("--mongo", action="store_true")
    ap.add_argument("--db", default=os.environ.get("BO_DB", "bo_pilot"))
    ap.add_argument("--recovery", action="store_true")
    ap.add_argument("--out", default=str(HERE / "output"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(exist_ok=True)
    if args.recovery:
        rows = recovery()
        (out / "learner_recovery.json").write_text(json.dumps({"population": POP, "rows": rows}, indent=1))
        print(f"Wrote {out / 'learner_recovery.json'}")
        return
    if args.games:
        records = json.loads(Path(args.games).read_text())
    elif args.mongo:
        from bo_pilot import Config, MongoStore
        cfg = Config()
        records = [{"pid": p["pid"], "shares_A": p["shares"], "rev_A": p["rev_r"], "rev_B": p["rev_d"],
                    "alpha": p["alpha"], "delta": cfg.delta, "snr": p["snr"], "rounds": p["rounds"], "better": "A"}
                   for p in MongoStore(os.environ["MDB_MCP_CONNECTION_STRING"], args.db).completed()]
    else:
        raise SystemExit("Pass --games, --mongo or --recovery.")
    fits = fit_records(records)
    for f in fits:
        print(f"theta {f['theta_true']:+.2f} | prior mean {f['mu0']:+.2f} [{f['mu0_lo']:+.2f}, {f['mu0_hi']:+.2f}]"
              f" | prior strength n0 {f['n0']:.1f} [{f['n0_lo']:.1f}, {f['n0_hi']:.1f}] rounds"
              f" | evidence weight {f['omega']:.2f} [{f['omega_lo']:.2f}, {f['omega_hi']:.2f}]"
              f" | round-1 learning rate {f['lr1']:.2f} | choice noise {f['sig_s']:.2f} | final belief {f['final_belief']:+.2f}")
    (out / "learner_fits.json").write_text(json.dumps(fits, indent=1))
    print(f"Wrote {out / 'learner_fits.json'}")


if __name__ == "__main__":
    main()
