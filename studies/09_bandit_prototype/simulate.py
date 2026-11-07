"""Design simulation for the click-bandit game (version a: constant payouts).

Each simulated Democrat makes T sales visits. Every visit goes to Riverton (R) or
Lakewood (D) and sells Poisson(lambda_k) panels. Riverton is better:
lambda_R = ratio * lambda_D.

Learner (one per person):
  prior   each county's rate ~ Gamma with mean s*exp(+/- mu0/2) and strength n0
          (n0 = pseudo-visits per county; s = geometric mean of the true rates).
          mu0 = believed log(lambda_R / lambda_D); the chat shifts mu0.
  update  conjugate Gamma-Poisson: posterior mean = (n0*m + sales) / (n0 + visits).
  choice  softmax on the posterior-mean difference (sales per visit), slope beta,
          plus a 5% lapse. Purely exploitative, so a pessimistic prior about
          Riverton means few Riverton visits and slow correction.

Population (control): mu0 ~ N(-0.35, 0.4), the pilot's control prior mean
(log Riverton/Lakewood pay ratio); log n0 ~ N(log n0_med, 0.8); log beta ~ N(log 2, 0.5).
Treatment: mu0 shifted by +delta. The belief slider reads mu0 + N(0, 0.3).

Outputs (output/): power.csv, curves.csv, fig_curves.png, fig_power.png.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)
RNG = np.random.default_rng(20261106)

LAMBDA_D = 2.0
T = 100
RATIOS = [1.2, 1.35, 1.5]
N0_MEDS = [5, 20]
DELTAS = [0.1, 0.2]           # chat shift in mu0 (log units); between-person SD 0.4 -> d = 0.25, 0.5
N_PER_ARM = [100, 150, 200, 300]
POOL = 6000                   # simulated people per arm per cell
REPS = 1000                   # resamples per power estimate
MU0_CONTROL, MU0_SD = -0.35, 0.4
SLIDER_SD = 0.3
LAPSE = 0.05


def play(mu0, n0, beta, ratio, rng):
    """Simulate T visits for a vector of people. Returns choices (1 = Riverton) and sales."""
    lam = np.array([LAMBDA_D * ratio, LAMBDA_D])
    s = np.sqrt(lam.prod())
    m = np.stack([s * np.exp(mu0 / 2), s * np.exp(-mu0 / 2)], 1)   # prior means, cols R, D
    a, b = m * n0[:, None], np.repeat(n0[:, None], 2, 1)
    n = len(mu0)
    choice, sales = np.zeros((n, T), np.int8), np.zeros((n, T), np.int16)
    for t in range(T):
        diff = a[:, 0] / b[:, 0] - a[:, 1] / b[:, 1]
        p_r = LAPSE / 2 + (1 - LAPSE) / (1 + np.exp(-beta * diff))
        go_r = rng.random(n) < p_r
        y = rng.poisson(np.where(go_r, lam[0], lam[1]))
        k = np.where(go_r, 0, 1)
        a[np.arange(n), k] += y
        b[np.arange(n), k] += 1
        choice[:, t], sales[:, t] = go_r, y
    return choice, sales


def ideal_curve(ratio, rng, n=20000):
    """Thompson sampling from a near-flat prior: how fast the game can be learned."""
    lam = np.array([LAMBDA_D * ratio, LAMBDA_D])
    a, b = np.full((n, 2), 0.5), np.full((n, 2), 0.25)
    out = np.zeros(T)
    for t in range(T):
        draw = rng.gamma(a, 1 / b)
        go_r = draw[:, 0] > draw[:, 1]
        y = rng.poisson(np.where(go_r, lam[0], lam[1]))
        k = np.where(go_r, 0, 1)
        a[np.arange(n), k] += y
        b[np.arange(n), k] += 1
        out[t] = go_r.mean()
    return out


def population(n, delta, n0_med, rng):
    mu0 = rng.normal(MU0_CONTROL + delta, MU0_SD, n)
    n0 = np.exp(rng.normal(np.log(n0_med), 0.8, n))
    beta = np.exp(rng.normal(np.log(2), 0.5, n))
    return mu0, n0, beta


def outcomes(mu0, choice, sales, rng):
    return {
        "Belief slider (before play)": mu0 + rng.normal(0, SLIDER_SD, len(mu0)),
        "Riverton share, visits 1-10": choice[:, :10].mean(1),
        "Riverton share, visits 1-50": choice[:, :50].mean(1),
        "Riverton share, visits 1-100": choice.mean(1),
        "Panels sold, 100 visits": sales.sum(1).astype(float),
    }


def power(x_c, x_t, n, rng):
    hits = 0
    for _ in range(REPS):
        c = rng.choice(x_c, n, replace=False)
        t = rng.choice(x_t, n, replace=False)
        hits += stats.ttest_ind(t, c, equal_var=False).pvalue < 0.05
    return hits / REPS


power_rows, curve_rows = [], []
for ratio in RATIOS:
    ideal = ideal_curve(ratio, RNG)
    curve_rows += [dict(ratio=ratio, n0_med=m, delta=np.nan, group="Ideal learner", visit=t + 1, p_r=ideal[t])
                   for m in N0_MEDS for t in range(T)]
    for n0_med in N0_MEDS:
        mu0, n0, beta = population(POOL, 0, n0_med, RNG)
        ch_c, sa_c = play(mu0, n0, beta, ratio, RNG)
        out_c = outcomes(mu0, ch_c, sa_c, RNG)
        curve_rows += [dict(ratio=ratio, n0_med=n0_med, delta=0, group="Control", visit=t + 1, p_r=v)
                       for t, v in enumerate(ch_c.mean(0))]
        for delta in DELTAS:
            mu0t, n0t, betat = population(POOL, delta, n0_med, RNG)
            ch_t, sa_t = play(mu0t, n0t, betat, ratio, RNG)
            out_t = outcomes(mu0t, ch_t, sa_t, RNG)
            curve_rows += [dict(ratio=ratio, n0_med=n0_med, delta=delta, group="Treatment", visit=t + 1, p_r=v)
                           for t, v in enumerate(ch_t.mean(0))]
            for name in out_c:
                xc, xt = out_c[name], out_t[name]
                d = (xt.mean() - xc.mean()) / np.sqrt((xt.var() + xc.var()) / 2)
                for n in N_PER_ARM:
                    power_rows.append(dict(ratio=ratio, n0_med=n0_med, delta=delta, outcome=name, d=d,
                                           n_per_arm=n, power=power(xc, xt, n, RNG)))
        print(f"done ratio={ratio} n0_med={n0_med}", flush=True)

pw = pd.DataFrame(power_rows)
cv = pd.DataFrame(curve_rows)
pw.to_csv(OUT / "power.csv", index=False)
cv.to_csv(OUT / "curves.csv", index=False)

# ---------------------------------- figures ----------------------------------
COL = {"Control": "#9ca3af", "Treatment": "#2563eb", "Ideal learner": "#111827"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})

fig, axes = plt.subplots(len(N0_MEDS), len(RATIOS), figsize=(11, 6.2), sharex=True, sharey=True)
for i, n0_med in enumerate(N0_MEDS):
    for j, ratio in enumerate(RATIOS):
        ax = axes[i, j]
        sub = cv[(cv.ratio == ratio) & (cv.n0_med == n0_med)]
        for g, dsel in [("Ideal learner", np.nan), ("Control", 0), ("Treatment", 0.2)]:
            s = sub[(sub.group == g) & ((sub.delta == dsel) | (np.isnan(dsel) & sub.delta.isna()))]
            sm = s.p_r.rolling(5, min_periods=1, center=True).mean()
            ax.plot(s.visit, sm, color=COL[g], lw=2, ls="--" if g == "Ideal learner" else "-",
                    label=g if g != "Treatment" else "Treatment (prior shifted +0.2)")
        ax.axhline(0.5, color="#d1d5db", lw=1, zorder=0)
        ax.set_ylim(0, 1)
        ax.set_title(f"Riverton sells {ratio:.2f}x per visit; prior worth ~{n0_med} visits", fontsize=9.5)
        if j == 0:
            ax.set_ylabel("Share of people visiting Riverton")
        if i == len(N0_MEDS) - 1:
            ax.set_xlabel("Visit number")
axes[0, 0].legend(frameon=False, fontsize=8.5, loc="lower right")
fig.suptitle("Learning curves: simulated Democrats (N = 6,000 per group) vs an ideal learner", fontweight="bold")
fig.tight_layout()
fig.savefig(OUT / "fig_curves.png", dpi=150)

focus = ["Belief slider (before play)", "Riverton share, visits 1-10", "Riverton share, visits 1-100"]
OCOL = dict(zip(focus, ["#111827", "#f59e0b", "#2563eb"]))
fig, axes = plt.subplots(len(N0_MEDS), len(RATIOS), figsize=(11, 6.2), sharex=True, sharey=True)
for i, n0_med in enumerate(N0_MEDS):
    for j, ratio in enumerate(RATIOS):
        ax = axes[i, j]
        for o in focus:
            for delta, ls in zip(DELTAS, [":", "-"]):
                s = pw[(pw.ratio == ratio) & (pw.n0_med == n0_med) & (pw.delta == delta) & (pw.outcome == o)]
                ax.plot(s.n_per_arm, s.power, color=OCOL[o], ls=ls, lw=2, marker="o", ms=4,
                        label=f"{o}, shift {delta}" if (i, j) == (0, 0) else None)
        ax.axhline(0.8, color="#d1d5db", lw=1, zorder=0)
        ax.set_ylim(0, 1)
        ax.set_title(f"Ratio {ratio:.2f}x; prior worth ~{n0_med} visits", fontsize=9.5)
        if j == 0:
            ax.set_ylabel("Power (alpha = .05)")
        if i == 1:
            ax.set_xlabel("People per condition")
fig.legend(loc="lower center", ncol=3, frameon=False, fontsize=8.5)
fig.suptitle("Power to detect the chat's shift in prior belief (solid: +0.2, d = 0.5; dotted: +0.1, d = 0.25)",
             fontweight="bold")
fig.tight_layout(rect=(0, 0.09, 1, 1))
fig.savefig(OUT / "fig_power.png", dpi=150)
print(pw[pw.n_per_arm == 200].pivot_table(index=["ratio", "n0_med", "delta"], columns="outcome", values="power").round(2).to_string())
