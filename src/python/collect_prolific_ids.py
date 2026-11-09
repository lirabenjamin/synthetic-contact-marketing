"""Collect every Prolific participant ID that has taken part in a twins study (gensci + marketing),
for a Prolific custom blocklist.

Scans data files (csv, tsv, parquet, jsonl, json, xlsx) under the twins project folders for columns
whose name looks like a Prolific ID column and keeps values that look like Prolific IDs
(24 hexadecimal characters). Our apps' own database ids (column `participant_id`, `_id`) are also
24-hex, so those column names are ignored. Also reads the Prolific API (PROLIFIC_TOKEN in
~/Documents/benOS2.0/.env) for studies whose internal name starts with "Twins".

Output: one row per (prolific_id, source); `--out` also writes a deduplicated single-column CSV.

Usage:  python3 src/python/collect_prolific_ids.py --out <dir>
The IDs are personal data: write them to a gitignored folder (e.g. twins/marketing/data/processed/exclusions).
"""
import argparse
import json
import os
import re
import urllib.request
from pathlib import Path

import pandas as pd

TWINS = Path("/Users/blira/Documents/01_research_local/twins")
ROOTS = [TWINS / "gensci", TWINS / "marketing", TWINS / "marketing-bandit", TWINS / "twins3-replicationcontrol",
         TWINS / "twins1-wedge"]
SKIP_DIRS = {"node_modules", ".git", "_archive", "release", ".quarto", "renv"}
ID_COL = re.compile(r"prolific|^pid$|^p_id$|workerid|participantid|^prolificpid$", re.I)
NOT_ID_COL = re.compile(r"^(participant_id|_id|id|user_id|participant)$|study|session|submission", re.I)
PROLIFIC_ID = re.compile(r"^[0-9a-f]{24}$")
EXT = {".csv", ".tsv", ".parquet", ".jsonl", ".json", ".xlsx"}


def read(path):
    s = path.suffix.lower()
    if s == ".csv":
        return [pd.read_csv(path, dtype=str, low_memory=False, on_bad_lines="skip")]
    if s == ".tsv":
        return [pd.read_csv(path, sep="\t", dtype=str, on_bad_lines="skip")]
    if s == ".parquet":
        return [pd.read_parquet(path)]
    if s == ".jsonl":
        return [pd.read_json(path, lines=True, dtype=False)]
    if s == ".json":
        obj = json.loads(path.read_text())
        return [pd.json_normalize(obj)] if isinstance(obj, list) else []
    if s == ".xlsx":
        return list(pd.read_excel(path, sheet_name=None, dtype=str).values())
    return []


def scan_files():
    rows = []
    for root in ROOTS:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in EXT or SKIP_DIRS & set(path.parts):
                continue
            if path.stat().st_size > 300e6:
                continue
            try:
                frames = read(path)
            except Exception:
                continue
            for df in frames:
                for col in df.columns:  # NOT_ID_COL is searched, so study or session id columns are skipped
                    name = str(col)
                    if not ID_COL.search(name) or NOT_ID_COL.search(name):
                        continue
                    vals = df[col].dropna().astype(str).str.strip()
                    ids = vals[vals.str.fullmatch(PROLIFIC_ID.pattern)]
                    for pid in ids.unique():
                        rows.append({"prolific_id": pid, "source": str(path.relative_to(TWINS)), "column": name})
    return rows


def scan_prolific_api():
    env = Path.home() / "Documents/benOS2.0/.env"
    token = next((l.split("=", 1)[1].strip() for l in env.read_text().splitlines() if l.startswith("PROLIFIC_TOKEN=")), None) if env.exists() else None
    if not token:
        return []
    get = lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"Authorization": "Token " + token})))
    rows = []
    for s in get("https://api.prolific.com/api/v1/studies/?limit=500")["results"]:
        if not (s.get("internal_name") or "").lower().startswith("twins"):
            continue
        for sub in get(f"https://api.prolific.com/api/v1/studies/{s['id']}/submissions/?limit=500")["results"]:
            rows.append({"prolific_id": sub["participant_id"], "source": f"Prolific API: {s['internal_name']} ({s['id']})", "column": "participant_id"})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    out = Path(ap.parse_args().out)
    out.mkdir(parents=True, exist_ok=True)
    rows = pd.DataFrame(scan_files() + scan_prolific_api()).drop_duplicates(["prolific_id", "source"])
    rows["project"] = rows.source.map(lambda s: "gensci" if s.startswith("gensci") else "marketing")
    rows.sort_values(["project", "source", "prolific_id"]).to_csv(out / "twins_prolific_ids_by_source.csv", index=False)
    uniq = rows.drop_duplicates("prolific_id")[["prolific_id"]].sort_values("prolific_id")
    uniq.to_csv(out / "twins_prolific_exclusions.csv", index=False)
    print(rows.groupby(["project", "source"]).prolific_id.nunique().to_string())
    print(f"\n{len(uniq)} unique Prolific IDs → {out / 'twins_prolific_exclusions.csv'}")


if __name__ == "__main__":
    main()
