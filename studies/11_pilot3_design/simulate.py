"""Pilot 3 design simulation: does a safe known option ("hot stove" game) make the chat's
effect on beliefs show up more strongly in behavior than the two-county game of pilot 2?

Designs (100 clicks of $1,000; money back per $1 has Gamma noise with SD = mean / sqrt(k)):
  two_counties  pilot 2: Riverton (unknown, mean 1.35, k = 2.7) vs Lakewood (unknown, mean 1.00, k = 2.0)
  safe_1.10     Republican homeowners (unknown, mean 1.35, k = 2.7) vs a general list that always
                returns exactly $1.10 per $1, which the player knows
  safe_1.20     same, the known option returns $1.20

Simulated Democrats: belief about the Republican option's mean return, prior mean
m0 = ref * exp(mu0) with mu0 ~ N(-0.35 + shift, 0.4) (ref = 1.00 in two_counties, the safe
return otherwise), prior worth n0 clicks (log n0 ~ N(log 10, 0.8)). Gamma-Gamma conjugate
updating, softmax choice on the difference in expected return with slope beta
(log beta ~ N(log 8, 0.5), per $1), 5% lapse. In two_counties the Lakewood prior is centered on
its true mean. The chat shifts mu0 by +0.2 (d = 0.5) or +0.1 (d = 0.25).

Outputs: output/power.csv, output/fig_curves.png, output/fig_power.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)
RNG = np.random.default_rng(20261107)
T, POOL, REPS = 100, 6000, 800
LAPSE = 0.05
DESIGNS = {
    "two_counties": dict(safe=None, ref=1.00),
    "safe_1.10": dict(safe=1.10, ref=1.10),
    "safe_1.20": dict(safe=1.20, ref=1.20),
}
R_MEAN, R_K, D_MEAN, D_K = 1.35, 2.7, 1.00, 2.0


def population(n, shift, ref):
    mu0 = RNG.normal(-0.35 + shift, 0.4, n)
    return ref * np.exp(mu0), np.exp(RNG.normal(np.log(10), 0.8, n)), np.exp(RNG.normal(np.log(8), 0.5, n)), mu0


def play(m0, n0, beta, design):
    n = len(m0)
    # Gamma-Gamma updating on the rate of a Gamma(k) return with known shape k:
    # posterior mean of the mean return = (n0 * m0 + sum returns) / (n0 + visits)
    sR, cR = n0 * m0, n0.copy()
    sD, cD = n0 * D_MEAN, n0.copy()
    choice = np.zeros((n, T), np.int8)
    back = np.zeros((n, T))
    for t in range(T):
        eR = sR / cR
        eO = design["safe"] if design["safe"] is not None else sD / cD
        p = LAPSE / 2 + (1 - LAPSE) / (1 + np.exp(-beta * (eR - eO)))
        goR = RNG.random(n) < p
        yR = RNG.gamma(R_K, R_MEAN / R_K, n)
        yO = np.full(n, design["safe"]) if design["safe"] is not None else RNG.gamma(D_K, D_MEAN / D_K, n)
        y = np.where(goR, yR, yO)
        sR += np.where(goR, y, 0); cR += goR
        if design["safe"] is None:
            sD += np.where(~goR, y, 0); cD += ~goR
        choice[:, t], back[:, t] = goR, y
    return choice, back


def power(xc, xt, n):
    hits = 0
    for _ in range(REPS):
        hits += stats.ttest_ind(RNG.choice(xt, n, replace=False), RNG.choice(xc, n, replace=False), equal_var=False).pvalue < 0.05
    return hits / REPS


rows, curves = [], []
for name, des in DESIGNS.items():
    out = {}
    for shift in (0.0, 0.1, 0.2):
        m0, n0, beta, mu0 = population(POOL, shift, des["ref"])
        ch, bk = play(m0, n0, beta, des)
        out[shift] = {"Forecast before play": mu0 + RNG.normal(0, 0.3, POOL),
                      "Republican share, clicks 1-10": ch[:, :10].mean(1),
                      "Republican share, clicks 1-20": ch[:, :20].mean(1),
                      "Republican share, all 100": ch.mean(1),
                      "Money back": bk.sum(1)}
        curves += [dict(design=name, shift=shift, click=t + 1, p=v) for t, v in enumerate(ch.mean(0))]
    for shift in (0.1, 0.2):
        for k in out[0]:
            xc, xt = out[0][k], out[shift][k]
            d = (xt.mean() - xc.mean()) / np.sqrt((xt.var() + xc.var()) / 2)
            for n in (50, 100, 150):
                rows.append(dict(design=name, shift=shift, outcome=k, d=round(d, 3), n_per_arm=n, power=power(xc, xt, n)))
    print("done", name, flush=True)

pw = pd.DataFrame(rows)
pw.to_csv(OUT / "power.csv", index=False)
cv = pd.DataFrame(curves)

COL = {0.0: "#9ca3af", 0.2: "#2563eb"}
TITLES = {"two_counties": "Pilot 2: two unknown counties", "safe_1.10": "Pilot 3: Republican list vs a sure $1.10",
          "safe_1.20": "Variant: Republican list vs a sure $1.20"}
fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), sharey=True)
for ax, name in zip(axes, DESIGNS):
    for shift, lab in ((0.0, "Control"), (0.2, "Treatment (belief +0.2)")):
        s = cv[(cv.design == name) & (cv["shift"] == shift)]
        ax.plot(s.click, s.p.rolling(5, min_periods=1, center=True).mean(), color=COL[shift], lw=2, label=lab)
    ax.set_title(TITLES[name], fontsize=10)
    ax.set_xlabel("Click"); ax.set_ylim(0, 1); ax.axhline(0.5, color="#e5e7eb", lw=1, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
axes[0].set_ylabel("Share choosing the Republican option")
axes[0].legend(frameon=False, fontsize=8, loc="lower right")
fig.tight_layout(); fig.savefig(OUT / "fig_curves.png", dpi=150)

focus = ["Forecast before play", "Republican share, clicks 1-10", "Republican share, all 100"]
fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), sharey=True)
for ax, o in zip(axes, focus):
    for name, c in zip(DESIGNS, ["#9ca3af", "#2563eb", "#f59e0b"]):
        s = pw[(pw.design == name) & (pw.outcome == o) & (pw["shift"] == 0.2)]
        ax.plot(s.n_per_arm, s.power, marker="o", color=c, lw=2, label=TITLES[name])
    ax.axhline(0.8, color="#e5e7eb", lw=1, zorder=0); ax.set_ylim(0, 1); ax.set_title(o, fontsize=10)
    ax.set_xlabel("People per condition"); ax.spines[["top", "right"]].set_visible(False)
axes[0].set_ylabel("Power (belief shift +0.2, d = 0.5)")
axes[2].legend(frameon=False, fontsize=8, loc="lower right")
fig.tight_layout(); fig.savefig(OUT / "fig_power.png", dpi=150)
print(pw[pw.n_per_arm == 100].pivot_table(index=["outcome"], columns=["design", "shift"], values="power").round(2).to_string())
print(pw[pw.n_per_arm == 100].pivot_table(index=["outcome"], columns=["design", "shift"], values="d").round(2).to_string())
