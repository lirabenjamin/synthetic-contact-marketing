"""Bayesian learner fit for the allocation-game pilot (Prolific, Nov 2026).

Reuses the learner in studies/06_bo_pilot/fit_learner.py (imported, not copied): the signal
y_t = log(rev_R / rev_D) - alpha * log(s_t / (1 - s_t)), the belief update
m_{t+1} = m_t + (y_t - m_t) / (n0 + t), and the split rule s*(m) = 1 / (1 + exp(-m / (1 - alpha))).
theta = log(w_R / w_D) is the Riverton pay advantage; mu0 is the belief about it before round 1.

Changes from fit_learner.py, all to match the live game (survey-app gameEngine.js, tag
v2.1.0-allocation-game-pilot):
  1. Split limits 0.10-0.90 (was 0.05-0.95).
  2. Splits are chosen on a 5% grid, so the choice likelihood is the probability that the latent
     split s*(m_t) + N(0, sig_s) rounds to the chosen grid point (was a normal density on a
     continuous split). The end points 0.10 and 0.90 take the censored tails.
  3. Game settings: alpha = 0.5, delta = 1.0, sigma = 0.7 (signal-to-noise delta / sigma = 1.43);
     Riverton is always the better market (R-world), 10 rounds.
  4. Choice-noise grid widened to 0.02-0.60 share points (was 0.02-0.40), because several pilot
     players jump between far-apart splits.
  5. Reports posterior means and SDs (log n0 and log sig_s on the log scale) as well as medians.
  6. Parameter recovery varies choice noise across simulated people (was fixed at 0.10), so its
     recovery can be checked, and draws the population from the pilot's own fitted values.

Writes to data/processed/: learner_fits.csv (one row per person), learner_recovery.csv (one row per
simulated person), learner_ideal.csv (ideal-learner benchmark per person) and learner_ideal_mc.csv.
Run from this folder:  python3 fit_learner_pilot.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "06_bo_pilot"))
import fit_learner as fl  # noqa: E402

PROC = HERE / "data" / "processed"

# Live game (gameEngine.js)
ALPHA, DELTA, SIGMA, ROUNDS = 0.5, 1.0, 0.7, 10
S_MIN, S_MAX, STEP = 0.10, 0.90, 0.05
GRID = np.round(np.arange(S_MIN, S_MAX + 1e-9, STEP), 2)
fl.S_MIN, fl.S_MAX = S_MIN, S_MAX                 # change 1, used by fl.s_star
MU0, LOG_N0 = fl.MU0, fl.LOG_N0
LOG_SIG = np.linspace(np.log(0.02), np.log(0.6), 12)   # change 4
N0_IDEAL = 2 * SIGMA ** 2 / DELTA ** 2            # 0.98 rounds: correct prior strength if R or D is equally likely


def exp_rev(s, theta=DELTA):
    return np.exp(theta / 2) * s ** ALPHA + np.exp(-theta / 2) * (1 - s) ** ALPHA


def grid_choice(m):
    """Grid split with the highest expected revenue for belief m (the posterior variance cancels)."""
    m = np.atleast_1d(m)
    r = np.exp(m[:, None] / 2) * GRID[None, :] ** ALPHA + np.exp(-m[:, None] / 2) * (1 - GRID[None, :]) ** ALPHA
    return GRID[r.argmax(axis=1)]


def fit_person(shares, rev_r, rev_d):
    """Port of fl.fit_person with the grid likelihood (change 2) and posterior means (change 5)."""
    s = np.asarray(shares, float)
    y = fl.signals(s, rev_r, rev_d, ALPHA)
    M, LN = (a.ravel() for a in np.meshgrid(MU0, LOG_N0, indexing="ij"))
    pred = fl.s_star(fl.belief_paths(M, np.exp(LN), y), ALPHA)[:, :, None]   # (P, T, 1)
    sig = np.exp(LOG_SIG)[None, None, :]
    hi_edge = np.where(s >= S_MAX - 1e-6, np.inf, s + STEP / 2)[None, :, None]
    lo_edge = np.where(s <= S_MIN + 1e-6, -np.inf, s - STEP / 2)[None, :, None]
    p = norm.cdf((hi_edge - pred) / sig) - norm.cdf((lo_edge - pred) / sig)
    ll = np.log(np.clip(p, 1e-300, None)).sum(axis=1)                         # (P, S)
    post = np.exp(ll - ll.max())
    post /= post.sum()
    p3 = post.reshape(len(MU0), len(LOG_N0), len(LOG_SIG))
    out = {}
    for name, values, axes in (("mu0", MU0, (1, 2)), ("log_n0", LOG_N0, (0, 2)), ("log_sig", LOG_SIG, (0, 1))):
        marg = p3.sum(axis=axes)
        mean = float(marg @ values)
        c = np.cumsum(marg)
        q = lambda pr: float(values[min(np.searchsorted(c, pr), len(values) - 1)])
        out.update({name: mean, f"{name}_sd": float(np.sqrt(marg @ (values - mean) ** 2)),
                    f"{name}_med": q(0.5), f"{name}_lo80": q(0.1), f"{name}_hi80": q(0.9)})
    i_map = post.argmax(axis=None)
    path = fl.belief_paths(M[[i_map // len(LOG_SIG)]], np.exp(LN[[i_map // len(LOG_SIG)]]), y)[0]
    out["fitted_r10_share"] = float(fl.s_star(path, ALPHA)[-1])
    return out, y


# ── Parameter recovery at the live settings ─────────────────────────────────
def simulate_person(rng, mu0, n0, sig_s):
    """Port of fl.simulate_person for the live game: R-world, grid splits, sigma = 0.7."""
    m, s_all, rr, rd = mu0, [], [], []
    for t in range(ROUNDS):
        latent = fl.s_star(m, ALPHA) + rng.normal(0, sig_s)
        s = float(np.clip(np.round(latent / STEP) * STEP, S_MIN, S_MAX))
        r_r = np.exp(DELTA / 2) * s ** ALPHA * np.exp(rng.normal(0, SIGMA))
        r_d = np.exp(-DELTA / 2) * (1 - s) ** ALPHA * np.exp(rng.normal(0, SIGMA))
        y = np.log(r_r / r_d) - ALPHA * np.log(s / (1 - s))
        m = m + (y - m) / (n0 + t + 1)
        s_all.append(s); rr.append(r_r); rd.append(r_d)
    return s_all, rr, rd


def recovery(fits, n_people=400, seed=11):
    """Simulated people drawn from the spread of the pilot's own posterior means."""
    rng = np.random.default_rng(seed)
    mu0 = rng.normal(fits.mu0.mean(), fits.mu0.std(), n_people)
    ln0 = np.clip(rng.normal(fits.log_n0.mean(), max(fits.log_n0.std(), 0.8), n_people), LOG_N0[0], LOG_N0[-1])
    lsig = np.clip(rng.normal(fits.log_sig.mean(), fits.log_sig.std(), n_people), LOG_SIG[0], LOG_SIG[-1])
    rows = []
    for a, b, c in zip(mu0, ln0, lsig):
        f, _ = fit_person(*simulate_person(rng, a, np.exp(b), np.exp(c)))
        rows.append({"mu0_true": a, "log_n0_true": b, "log_sig_true": c,
                     "mu0_hat": f["mu0"], "log_n0_hat": f["log_n0"], "log_sig_hat": f["log_sig"],
                     "log_n0_in80": f["log_n0_lo80"] <= b <= f["log_n0_hi80"],
                     "mu0_in80": f["mu0_lo80"] <= a <= f["mu0_hi80"]})
    return pd.DataFrame(rows)


# ── Ideal Bayesian benchmark ────────────────────────────────────────────────
def ideal_shares(y, mu0=0.0, n0=0.0):
    """Grid splits of a noise-free learner; n0 = 0 is a flat prior (belief = mean of signals so far).
    With a flat prior there is no belief before round 1, so round 1 is the even split."""
    m = fl.belief_paths(np.array([mu0]), np.array([n0]), y)[0]
    s = grid_choice(m)
    if n0 == 0:
        s[0] = 0.5
    return s


def ideal_mc(n_games=20000, seed=7):
    """Round-by-round mean split of ideal learners over fresh luck draws (signal SD = sigma * sqrt(2))."""
    rng = np.random.default_rng(seed)
    y = DELTA + rng.normal(0, SIGMA * np.sqrt(2), (n_games, ROUNDS))
    rows = []
    for label, n0 in (("flat", 0.0), ("calibrated", N0_IDEAL)):
        s = np.array([ideal_shares(yy, 0.0, n0) for yy in y])
        for t in range(ROUNDS):
            rows.append({"learner": label, "round": t + 1, "mean_share": s[:, t].mean(),
                         "q10": np.quantile(s[:, t], 0.1), "q90": np.quantile(s[:, t], 0.9)})
    return pd.DataFrame(rows)


def main():
    rounds = pd.read_csv(PROC / "rounds.csv").sort_values(["participant_id", "round"])
    full = rounds.groupby("participant_id").filter(lambda d: len(d) == ROUNDS and set(d["round"]) == set(range(1, 11)))
    fits, ideal = [], []
    for pid, d in full.groupby("participant_id"):
        f, y = fit_person(d.share_R, d.rev_R, d.rev_D)
        cond = d.condition.iloc[0]
        fits.append({"participant_id": pid, "condition": cond, "share_r1": d.share_R.iloc[0],
                     "share_r10": d.share_R.iloc[-1], "mean_signal": float(np.mean(y)), **f})
        flat = ideal_shares(y)
        calib = ideal_shares(y, 0.0, N0_IDEAL)
        own_prior = ideal_shares(y, f["mu0"], N0_IDEAL)          # person's prior, ideal learning
        own_learning = ideal_shares(y, 0.0, np.exp(f["log_n0"]))  # neutral prior, person's learning
        for t in range(ROUNDS):
            ideal.append({"participant_id": pid, "condition": cond, "round": t + 1, "actual": d.share_R.iloc[t],
                          "flat": flat[t], "calibrated": calib[t], "own_prior_ideal_learning": own_prior[t],
                          "neutral_prior_own_learning": own_learning[t]})
    fits = pd.DataFrame(fits)
    fits.to_csv(PROC / "learner_fits.csv", index=False)
    pd.DataFrame(ideal).to_csv(PROC / "learner_ideal.csv", index=False)
    ideal_mc().to_csv(PROC / "learner_ideal_mc.csv", index=False)
    rec = recovery(fits)
    rec.to_csv(PROC / "learner_recovery.csv", index=False)
    print(f"Fitted {len(fits)} people. Recovery r: mu0 {np.corrcoef(rec.mu0_true, rec.mu0_hat)[0, 1]:.2f}, "
          f"log n0 {np.corrcoef(rec.log_n0_true, rec.log_n0_hat)[0, 1]:.2f}, "
          f"log noise {np.corrcoef(rec.log_sig_true, rec.log_sig_hat)[0, 1]:.2f}")


if __name__ == "__main__":
    main()
