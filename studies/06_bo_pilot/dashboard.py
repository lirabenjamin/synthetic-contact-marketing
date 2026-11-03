"""Build the adaptive-pilot dashboard: one self-contained HTML file with the run data embedded.

  Simulation:  python dashboard.py --run output/sim_run.json --bench output/benchmark.json
  Live:        python dashboard.py --mongo [--db bo_pilot]      (reads MDB_MCP_CONNECTION_STRING)
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np

from bo_pilot import Config, MongoStore, eval_grid

HERE = Path(__file__).parent


def export_data(cfg: Config, store, surface=None, assumptions=None):
    g = eval_grid(cfg)
    data = {
        "mode": "simulation" if surface is not None else "live",
        "config": {k: getattr(cfg, k) for k in cfg.__dataclass_fields__},
        "max_rounds": cfg.max_rounds(),
        "grid": {"snr": g["snr"].tolist(), "alpha": g["alpha"].tolist(), "rounds": g["rounds"].tolist()},
        "participants": sorted(store.all_participants(), key=lambda p: p["started_at"]),
        "snapshots": store.get_snapshots(),
    }
    if surface is not None:
        feasible = np.isin(g["rounds"], np.arange(cfg.rounds_range[0], cfg.max_rounds() + 1))
        i = np.unravel_index(np.argmax(np.where(feasible[None, None, :], surface, -np.inf)), surface.shape)
        data["truth"] = {"grid": np.round(surface.ravel(), 3).tolist(),
                         "best": {"snr": float(g["snr"][i[0]]), "alpha": float(g["alpha"][i[1]]),
                                  "rounds": int(g["rounds"][i[2]]), "value": float(surface[i])},
                         "assumptions": assumptions or {}}
    return data


def build(data, bench, out):
    html = (HERE / "dashboard_template.html").read_text()
    payload = json.dumps({"run": data, "bench": bench}, default=float).replace("</", "<\\/")
    Path(out).write_text(html.replace("/*__DATA__*/null", payload))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", help="run JSON written by simulate.py")
    ap.add_argument("--bench", help="benchmark JSON written by benchmark.py")
    ap.add_argument("--mongo", action="store_true", help="read the live run from MongoDB")
    ap.add_argument("--db", default=os.environ.get("BO_DB", "bo_pilot"))
    ap.add_argument("--out", default=str(HERE / "dashboard.html"))
    args = ap.parse_args()
    if args.mongo:
        uri = os.environ.get("MDB_MCP_CONNECTION_STRING")
        if not uri:
            raise SystemExit("Set MDB_MCP_CONNECTION_STRING.")
        data = export_data(Config(), MongoStore(uri, args.db))
    else:
        data = json.loads(Path(args.run).read_text())
    bench = json.loads(Path(args.bench).read_text()) if args.bench else None
    build(data, bench, args.out)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
