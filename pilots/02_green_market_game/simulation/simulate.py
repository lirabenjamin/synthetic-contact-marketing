#!/usr/bin/env python3
"""
Synthetic experiment: simulate 60 agents (20 per difficulty condition)
playing the Green Market Game.

Agents do NOT know the payoff structure. They start with priors about
which markets are good for eco-products, observe revenue feedback each
round, and update their allocations via a simple reinforcement rule.

Agent characteristics:
  - political_lean:  -1 (strong D) to +1 (strong R)
  - eco_bias:        prior belief that D-markets are better for eco products
                     (higher = stronger bias toward D-markets)
  - learning_rate:   how fast they shift allocations based on ROI feedback
  - exploration:     noise in allocation decisions (0 = pure exploitation)

Output: simulation_results.csv (round-level data for all agents)
"""

import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

# ── Game parameters (mirroring the JS game exactly) ─────────────────────────

TOWNS = [
    {"id": "harlan",     "name": "Harlan County, KY",    "rS": 0.78, "dS": 0.22, "mkt": 50_000, "comp": 0.20},
    {"id": "williamson", "name": "Williamson County, TN", "rS": 0.72, "dS": 0.28, "mkt": 75_000, "comp": 0.35},
    {"id": "burlington", "name": "Burlington, VT",        "rS": 0.32, "dS": 0.68, "mkt": 45_000, "comp": 0.45},
    {"id": "middlesex",  "name": "Middlesex County, MA",  "rS": 0.28, "dS": 0.72, "mkt": 65_000, "comp": 0.85},
]

DIFFICULTY = {
    "easy":   {"halfMax": 25_000, "K": 1.5, "noise": 0.20},
    "medium": {"halfMax": 30_000, "K": 2.0, "noise": 0.30},
    "hard":   {"halfMax": 35_000, "K": 2.5, "noise": 0.35},
}

RECEP = {"dem": 0.75, "rep": 0.65}
PRICE = 7
BUDGET = 100_000
ROUNDS = 10
TOWN_IDS = [t["id"] for t in TOWNS]


# ── Payoff functions (same as JS) ───────────────────────────────────────────

def s_curve(alloc, half_max):
    return (alloc ** 2) / (alloc ** 2 + half_max ** 2)


def expected_revenue(town, alloc, params):
    if alloc <= 0:
        return 0.0
    r = town["mkt"] * (town["rS"] * RECEP["rep"] + town["dS"] * RECEP["dem"])
    return r * s_curve(alloc, params["halfMax"]) * np.exp(-params["K"] * town["comp"]) * PRICE


def payoff(town, alloc, params, rng):
    if alloc <= 0:
        return 0.0
    m = expected_revenue(town, alloc, params)
    s = m * params["noise"] + np.sqrt(alloc) * 2
    return max(0.0, rng.normal(m, s))


def compute_optimal(params):
    """Find optimal allocation via grid search over $1k increments.

    The JS game uses a greedy $5k-step approach which can be suboptimal
    when the payoff surface is steep (hard mode). This brute-force search
    over all 4-market splits at $1k resolution finds the true optimum.
    """
    from itertools import product

    step = 1000
    steps = BUDGET // step
    best_total, best_alloc = -np.inf, None

    # Greedy seed first (fast), then refine around it
    alloc = {t["id"]: 0 for t in TOWNS}
    for _ in range(BUDGET // 5000):
        best_id, best_gain = None, -np.inf
        for t in TOWNS:
            gain = expected_revenue(t, alloc[t["id"]] + 5000, params) - expected_revenue(t, alloc[t["id"]], params)
            if gain > best_gain:
                best_gain = gain
                best_id = t["id"]
        alloc[best_id] += 5000
    greedy_total = sum(expected_revenue(t, alloc[t["id"]], params) for t in TOWNS)
    best_total = greedy_total
    best_alloc = dict(alloc)

    # Refine: search ±20k around greedy in $1k steps
    ids = [t["id"] for t in TOWNS]
    base = [alloc[tid] for tid in ids]
    for d0 in range(-20, 21, 1):
        for d1 in range(-20, 21, 1):
            for d2 in range(-20, 21, 1):
                vals = [
                    base[0] + d0 * step,
                    base[1] + d1 * step,
                    base[2] + d2 * step,
                    0,
                ]
                vals[3] = BUDGET - sum(vals[:3])
                if any(v < 0 for v in vals):
                    continue
                total = sum(
                    expected_revenue(TOWNS[i], vals[i], params)
                    for i in range(4)
                )
                if total > best_total:
                    best_total = total
                    best_alloc = {ids[i]: vals[i] for i in range(4)}

    return best_alloc, best_total


# ── Agent definition ────────────────────────────────────────────────────────

def generate_agent(agent_id, rng):
    """Create an agent with random characteristics."""
    political_lean = rng.uniform(-1, 1)  # -1 = strong D, +1 = strong R
    # Eco-bias: D-leaning people think D-markets are better (and vice versa, but weaker)
    eco_bias = 0.6 - 0.3 * political_lean + rng.normal(0, 0.15)
    eco_bias = np.clip(eco_bias, 0.1, 0.95)
    learning_rate = rng.uniform(0.1, 0.6)
    exploration = rng.uniform(0.05, 0.25)
    return {
        "agent_id": agent_id,
        "political_lean": round(political_lean, 3),
        "eco_bias": round(eco_bias, 3),
        "learning_rate": round(learning_rate, 3),
        "exploration": round(exploration, 3),
    }


def initial_allocation(agent):
    """Set starting allocation based on eco_bias (bias toward D-leaning markets)."""
    bias = agent["eco_bias"]
    # Weight: D-markets get more if eco_bias is high
    raw = {}
    for t in TOWNS:
        d_share = t["dS"]
        raw[t["id"]] = 0.5 + (d_share - 0.5) * bias  # higher D-share → more $ if biased
    total = sum(raw.values())
    return {tid: (v / total) * BUDGET for tid, v in raw.items()}


def update_allocation(prev_alloc, prev_roi, agent, rng):
    """
    Simple reinforcement: shift budget toward markets with higher observed ROI.
    Agent doesn't know the payoff function — just responds to what worked.
    """
    lr = agent["learning_rate"]
    expl = agent["exploration"]

    # Compute ROI-weighted target
    roi_vals = np.array([max(prev_roi.get(tid, 0), 0.01) for tid in TOWN_IDS])
    roi_weights = roi_vals / roi_vals.sum()

    # Current proportions
    prev_total = sum(prev_alloc.values())
    if prev_total == 0:
        prev_total = BUDGET
    curr_props = np.array([prev_alloc[tid] / prev_total for tid in TOWN_IDS])

    # Blend toward ROI signal
    new_props = (1 - lr) * curr_props + lr * roi_weights

    # Add exploration noise
    noise = rng.normal(0, expl, size=len(TOWN_IDS))
    new_props = new_props + noise
    new_props = np.clip(new_props, 0.02, None)  # minimum 2% per market
    new_props = new_props / new_props.sum()

    # Convert to dollar amounts (round to $5k increments)
    alloc = {}
    for i, tid in enumerate(TOWN_IDS):
        alloc[tid] = round(new_props[i] * BUDGET / 5000) * 5000
    # Fix rounding to hit budget exactly
    diff = BUDGET - sum(alloc.values())
    if diff != 0:
        # Add/subtract from the largest allocation
        largest = max(alloc, key=alloc.get)
        alloc[largest] += diff
    # Ensure no negatives
    for tid in TOWN_IDS:
        alloc[tid] = max(0, alloc[tid])

    return alloc


# ── Run simulation ──────────────────────────────────────────────────────────

def run_simulation(n_per_condition=20):
    rng = np.random.default_rng(2024)
    records = []
    agent_records = []
    agent_counter = 0

    for diff_name, params in DIFFICULTY.items():
        opt_alloc, opt_rev = compute_optimal(params)

        for i in range(n_per_condition):
            agent_counter += 1
            agent = generate_agent(agent_counter, rng)
            agent["difficulty"] = diff_name

            # Pre-game beliefs: initial allocation preference
            init_alloc = initial_allocation(agent)
            pre_pct_R = sum(init_alloc[t["id"]] for t in TOWNS if t["rS"] > 0.5) / BUDGET * 100

            alloc = {tid: round(v / 5000) * 5000 for tid, v in init_alloc.items()}
            diff_budget = BUDGET - sum(alloc.values())
            if diff_budget != 0:
                largest = max(alloc, key=alloc.get)
                alloc[largest] += diff_budget

            cum_rev = 0.0

            for rd in range(1, ROUNDS + 1):
                # Play round
                revenues = {}
                roi = {}
                for t in TOWNS:
                    rev = payoff(t, alloc[t["id"]], params, rng)
                    revenues[t["id"]] = rev
                    roi[t["id"]] = rev / alloc[t["id"]] if alloc[t["id"]] > 0 else 0

                round_rev = sum(revenues.values())
                cum_rev += round_rev
                pct_R = sum(alloc[t["id"]] for t in TOWNS if t["rS"] > 0.5) / BUDGET * 100

                record = {
                    "agent_id": agent["agent_id"],
                    "difficulty": diff_name,
                    "political_lean": agent["political_lean"],
                    "eco_bias": agent["eco_bias"],
                    "learning_rate": agent["learning_rate"],
                    "exploration": agent["exploration"],
                    "round": rd,
                    "round_revenue": round(round_rev, 2),
                    "cumulative_revenue": round(cum_rev, 2),
                    "pct_to_R_markets": round(pct_R, 1),
                }
                for t in TOWNS:
                    record[f"alloc_{t['id']}"] = alloc[t["id"]]
                    record[f"rev_{t['id']}"] = round(revenues[t["id"]], 2)
                    record[f"roi_{t['id']}"] = round(roi[t["id"]], 4)
                records.append(record)

                # Update allocation for next round
                if rd < ROUNDS:
                    alloc = update_allocation(alloc, roi, agent, rng)

            # Post-game: final allocation preference
            post_pct_R = sum(alloc[t["id"]] for t in TOWNS if t["rS"] > 0.5) / BUDGET * 100

            agent_records.append({
                "agent_id": agent["agent_id"],
                "difficulty": diff_name,
                "political_lean": agent["political_lean"],
                "eco_bias": agent["eco_bias"],
                "learning_rate": agent["learning_rate"],
                "exploration": agent["exploration"],
                "pre_pct_R": round(pre_pct_R, 1),
                "post_pct_R": round(post_pct_R, 1),
                "belief_shift": round(post_pct_R - pre_pct_R, 1),
                "total_revenue": round(cum_rev, 2),
                "pct_optimal": round(cum_rev / (opt_rev * ROUNDS) * 100, 1),
            })

    rounds_df = pd.DataFrame(records)
    agents_df = pd.DataFrame(agent_records)
    return rounds_df, agents_df


if __name__ == "__main__":
    out_dir = Path(__file__).parent
    rounds_df, agents_df = run_simulation(n_per_condition=20)
    rounds_df.to_csv(out_dir / "round_data.csv", index=False)
    agents_df.to_csv(out_dir / "agent_data.csv", index=False)
    print(f"Saved {len(rounds_df)} round records and {len(agents_df)} agent records")
    print(f"\nAgent summary by difficulty:")
    print(agents_df.groupby("difficulty")[["belief_shift", "total_revenue", "pct_optimal"]].mean().round(1))
