"""Does adaptive sampling beat a plain random design with the same N?

Repeats the simulated launch with different seeds under two policies:
  adaptive: the planned loop (20 warm-up, then Thompson with 25% random, refit every 10)
  random:   every participant gets uniformly random knobs; the GP is still refit every 10
Both use the same GP and the same rule for the final pick (argmax of the posterior mean),
so any gap comes from where the participants were placed.
Score = TRUE expected learning at the recommended setting, as a share of the best feasible value.
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from bo_pilot import Config
from simulate import run_launch, true_surface, truth_fn

_SURFACE = None


def _init(surface):
    global _SURFACE
    _SURFACE = surface


def one_run(args):
    policy, seed = args
    cfg = Config(p_random=1.0) if policy == "random" else Config()
    store, _ = run_launch(cfg, truth=truth_fn(cfg, _SURFACE), seed=seed)
    return {"policy": policy, "seed": seed,
            "path": [{"n": s["n"], "rec_true": s["rec_true"]} for s in store.get_snapshots()]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--out", default="output/benchmark.json")
    args = ap.parse_args()
    cfg = Config()
    surface = true_surface(cfg)
    best = float(np.max(surface[:, :, :cfg.max_rounds() - cfg.rounds_range[0] + 1]))
    jobs = [(p, 100 + s) for s in range(args.seeds) for p in ("adaptive", "random")]
    with ProcessPoolExecutor(initializer=_init, initargs=(surface,)) as ex:
        runs = list(ex.map(one_run, jobs))
    summary = {}
    for policy in ("adaptive", "random"):
        paths = [r["path"] for r in runs if r["policy"] == policy]
        ns = sorted({p["n"] for path in paths for p in path})
        rows = []
        for n in ns:
            vals = np.array([next((p["rec_true"] for p in path if p["n"] == n), np.nan) for path in paths]) / best
            vals = vals[~np.isnan(vals)]
            rows.append({"n": n, "mean": float(vals.mean()), "se": float(vals.std(ddof=1) / np.sqrt(len(vals))),
                         "k": int(len(vals))})
        final = np.array([path[-1]["rec_true"] for path in paths]) / best
        summary[policy] = {"by_n": rows, "final_mean": float(final.mean()),
                           "final_se": float(final.std(ddof=1) / np.sqrt(len(final))), "final": final.tolist()}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"best_true": best, "seeds": args.seeds, **summary}))
    for p in ("adaptive", "random"):
        print(f"{p}: final pick reaches {100 * summary[p]['final_mean']:.0f}% of the best "
              f"(SE {100 * summary[p]['final_se']:.0f})")


if __name__ == "__main__":
    main()
