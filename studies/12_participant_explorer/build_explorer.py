"""Build a self-contained participant explorer (one HTML file, data embedded) for the two
Prolific pilots of the allocation game:

  pilot 1  studies/08_allocation_game_pilot  slider game, 10 rounds (Nov 6)
  pilot 2  studies/10_bandit_game_pilot      investment game, 100 clicks (Nov 7)

Reads each pilot's data/processed/*.csv (run that pilot's pull_data.py first). Prolific IDs are
left out; participants are labeled by the last 4 characters of their database id.
The output, explorer.html, holds chat text, so it is gitignored and should not be posted publicly.

Run:  python3 studies/12_participant_explorer/build_explorer.py
"""
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
STUDIES = HERE.parent
# data/ is gitignored, so a git worktree may lack it; fall back to the main checkout
FALLBACK = STUDIES.parents[1] / "marketing" / "studies"


def proc(study):
    for root in (STUDIES, FALLBACK):
        p = root / study / "data" / "processed"
        if (p / "participants.csv").exists():
            return p
    raise SystemExit(f"No processed data for {study}; run its pull_data.py first.")


def clean(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    return v.item() if hasattr(v, "item") else v


def chats_by_person(p):
    c = pd.read_csv(p / "chat_messages.csv")
    msg = c["message"].fillna("")
    low = msg.str.lower()
    prompt = low.str.contains("identifies as a republican") | low.str.contains("debate with users about whether cats or dogs")
    out = {}
    for pid, g in c.assign(prompt=prompt).sort_values("timestamp").groupby("participant_id"):
        turns = []
        for _, r in g.iterrows():
            if not r.prompt and isinstance(r.message, str) and r.message.strip():
                turns.append({"who": "user", "text": r.message, "t": str(r.timestamp)})
            if isinstance(r.response, str) and r.response.strip():
                turns.append({"who": "bot", "text": r.response, "t": str(r.timestamp)})
        out[pid] = turns
    return out


def minutes(a, b):
    try:
        return round((pd.to_datetime(b) - pd.to_datetime(a)).total_seconds() / 60, 1)
    except (TypeError, ValueError):
        return None


def pilot1():
    p = proc("08_allocation_game_pilot")
    parts = pd.read_csv(p / "participants.csv")
    rounds = pd.read_csv(p / "rounds.csv")
    chats = chats_by_person(p)
    people = []
    for _, r in parts[parts.completed_at.notna()].iterrows():
        rr = rounds[rounds.participant_id == r.participant_id].sort_values("round")
        people.append({
            "id": r.participant_id[-4:], "pid_full": r.participant_id, "condition": r.condition,
            "extremity": clean(r.extremity), "age": clean(r.age), "gender": clean(r.gender), "education": clean(r.education),
            "comments": clean(r.comments), "bonus": clean(r.game_bonus),
            "minutes_total": minutes(r.ts_attention_math, r.completed_at),
            "rounds": [{"round": int(x["round"]), "share_R": x.share_R, "rev_R": int(x.rev_R), "rev_D": int(x.rev_D),
                        "alloc_R": int(x.alloc_R), "alloc_D": int(x.alloc_D)} for _, x in rr.iterrows()],
            "chat": chats.get(r.participant_id, []),
        })
    return {"key": "p1", "label": "Pilot 1 · slider game (Nov 6, N = %d)" % len(people), "type": "slider",
            "note": "Each round splits $100,000 between Riverton (Republican-leaning) and Lakewood (Democratic-leaning) with a slider. "
                    "Best split: 88% to Riverton. Revenue has diminishing returns and luck.",
            "people": people}


def pilot2():
    p = proc("10_bandit_game_pilot")
    parts = pd.read_csv(p / "participants.csv")
    inv = pd.read_csv(p / "investments.csv")
    chats = chats_by_person(p)
    people = []
    for _, r in parts[parts.completed_at.notna()].iterrows():
        ii = inv[inv.participant_id == r.participant_id].sort_values("n")
        people.append({
            "id": r.participant_id[-4:], "pid_full": r.participant_id, "condition": r.condition,
            "extremity": clean(r.extremity), "age": clean(r.age), "gender": clean(r.gender), "education": clean(r.education),
            "comments": clean(r.comments), "bonus": clean(r.game_bonus), "money_back": clean(r.game_money_back),
            "check_attempts": clean(r.tutorial_check_attempts), "better": clean(r.pilot_better_county),
            "strategy": clean(r.pilot_decision_strategy),
            "minutes_total": minutes(r.ts_attention_math, r.completed_at),
            "clicks": [{"n": int(x.n), "c": x.county, "back": int(x.back), "ms": clean(x.ms_since_last)} for _, x in ii.iterrows()],
            "chat": chats.get(r.participant_id, []),
        })
    return {"key": "p2", "label": "Pilot 2 · investment game (Nov 7, N = %d)" % len(people), "type": "bandit",
            "note": "100 clicks of $1,000 to Riverton (Republican-leaning, on average $1,350 back) or Lakewood "
                    "(Democratic-leaning, on average $1,000 back). Every click to Riverton is best.",
            "people": people}


def main():
    data = [pilot2(), pilot1()]
    for d in data:
        for person in d["people"]:
            person.pop("pid_full")
    html = (HERE / "template.html").read_text().replace("/*__DATA__*/null", json.dumps(data))
    (HERE / "explorer.html").write_text(html)
    print("Wrote explorer.html:", ", ".join(f'{d["label"]}' for d in data))


if __name__ == "__main__":
    main()
