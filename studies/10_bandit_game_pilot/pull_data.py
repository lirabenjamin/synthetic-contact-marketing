"""Pull the investment-game (bandit) pilot (Prolific, Nov 2026) and write flat files to data/.

Read-only. Sources:
  - MongoDB database `twins-bandit-game`: participants, screenouts, client_errors
    (the `testing` collection holds test-mode sessions and is never read).
  - Chatbot Postgres (`conversation_logs`, user_id = the participant's Mongo _id).

Connection strings come from the environment, never from code:
  MDB_MCP_CONNECTION_STRING (falls back to MONGODB_URI in the repo .env)
  DATABASE_URL (repo .env) for the chat logs; chats are skipped if it is missing.

Excluded: prolific_pid starting with TEST_ / test_ (any case), test == true.

Run from anywhere:  python3 studies/10_bandit_game_pilot/pull_data.py
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import dotenv
import pandas as pd
from bson import ObjectId
from pymongo import MongoClient

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RAW, PROC = HERE / "data" / "raw", HERE / "data" / "processed"
DB_NAME = "twins-bandit-game"
PROLIFIC_STUDY_ID = "6aef9994ac7e235b0696943f"

# The repo .env is gitignored, so a git worktree may not have it; fall back to the main checkout.
for env in (REPO / ".env", REPO.parent / "marketing" / ".env"):
    if env.exists():
        dotenv.load_dotenv(env)
        break


def is_test(doc):
    pid = str(doc.get("prolific_pid") or "")
    return pid.lower().startswith("test_") or doc.get("test") is True


def jsonable(x):
    if isinstance(x, ObjectId):
        return str(x)
    if isinstance(x, datetime):
        return x.replace(tzinfo=timezone.utc).isoformat() if x.tzinfo is None else x.isoformat()
    if isinstance(x, dict):
        return {k: jsonable(v) for k, v in x.items()}
    if isinstance(x, list):
        return [jsonable(v) for v in x]
    return x


def write_jsonl(docs, path):
    with open(path, "w") as f:
        for d in docs:
            f.write(json.dumps(jsonable(d)) + "\n")


def iso(x):
    return jsonable(x) if x is not None else None


def participant_row(d):
    ts = d.get("screen_timestamps") or {}
    leaves = d.get("tab_leaves") or []
    inv = d.get("game_investments") or []
    row = {
        "participant_id": str(d["_id"]),
        "prolific_pid": d.get("prolific_pid"),
        "condition": d.get("condition"),
        "chatbot_condition": d.get("chatbot_condition"),
        "extremity": d.get("extremity"),
        "game_seed": d.get("game_seed"),
        "app_commit": (d.get("app_version") or {}).get("gitCommit"),
        "started_at": iso(d.get("started_at")),
        "chatbot_duration_valid": d.get("chatbot_duration_valid"),
        "n_investments_saved": len({v["n"] for v in inv}),
        "n_back_mismatch": sum(1 for v in inv if v.get("back_client") is not None and v["back_client"] != v["back"]),
        "game_n_riverton": d.get("game_n_riverton"),
        "game_money_back": d.get("game_money_back"),
        "game_bonus": d.get("game_bonus"),
        "game_bonus_client": d.get("game_bonus_client"),
        "tutorial_check_attempts": d.get("tutorial_check_attempts"),
        "pilot_better_county": d.get("pilot_better_county"),
        "pilot_decision_strategy": d.get("pilot_decision_strategy"),
        "game_finished_at": iso(d.get("game_finished_at")),
        "completed_at": iso(d.get("completed_at")),
        "gender": d.get("gender"),
        "age": d.get("age"),
        "education": d.get("education"),
        "comments": d.get("comments"),
        "n_tab_leaves": len(leaves),
        "tab_leave_total_s": sum((l.get("durationMs") or 0) for l in leaves) / 1000,
    }
    for screen, t in ts.items():
        row[f"ts_{screen}"] = t
    return row


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    PROC.mkdir(parents=True, exist_ok=True)

    uri = os.environ.get("MDB_MCP_CONNECTION_STRING") or os.environ.get("MONGODB_URI")
    if not uri:
        raise SystemExit("Set MDB_MCP_CONNECTION_STRING (or MONGODB_URI in the repo .env).")
    db = MongoClient(uri, serverSelectionTimeoutMS=15000)[DB_NAME]

    parts = list(db.participants.find({}))
    screen = list(db.screenouts.find({}))
    errors = list(db.client_errors.find({}))
    n_test = sum(is_test(d) for d in parts) + sum(is_test(d) for d in screen)
    parts = [d for d in parts if not is_test(d)]
    screen = [d for d in screen if not is_test(d)]
    errors = [d for d in errors if not is_test(d)]

    write_jsonl(parts, RAW / "participants.jsonl")
    write_jsonl(screen, RAW / "screenouts.jsonl")
    write_jsonl(errors, RAW / "client_errors.jsonl")

    pd.DataFrame([participant_row(d) for d in parts]).to_csv(PROC / "participants.csv", index=False)

    inv = [
        {"participant_id": str(d["_id"]), "condition": d.get("condition"),
         **{k: (iso(v) if k == "saved_at" else v) for k, v in r.items()}}
        for d in parts for r in {v["n"]: v for v in (d.get("game_investments") or [])}.values()
    ]
    pd.DataFrame(inv).sort_values(["participant_id", "n"]).to_csv(PROC / "investments.csv", index=False)

    pd.DataFrame([{"prolific_pid": d.get("prolific_pid"), "reasons": ";".join(d.get("reasons") or []),
                   "screened_out_at": iso(d.get("screened_out_at"))} for d in screen],
                 columns=["prolific_pid", "reasons", "screened_out_at"]).to_csv(PROC / "screenouts.csv", index=False)
    pd.DataFrame([{"where": d.get("where"), "message": d.get("message"), "at": iso(d.get("at"))} for d in errors],
                 columns=["where", "message", "at"]).to_csv(PROC / "client_errors.csv", index=False)

    # Chat logs: one row per exchange. The chat app logs the bot's system prompt as the first
    # "message" of a session; identify it by its text, not by how it starts, because a
    # participant can also type "You are ...".
    chat_cols = ["participant_id", "timestamp", "message", "response"]
    pg_url = os.environ.get("DATABASE_URL")
    if pg_url and parts:
        import psycopg2
        with psycopg2.connect(pg_url, sslmode="require") as con, con.cursor() as cur:
            cur.execute("SELECT user_id, timestamp, message, response FROM conversation_logs "
                        "WHERE user_id = ANY(%s) ORDER BY user_id, timestamp", ([str(d["_id"]) for d in parts],))
            chats = pd.DataFrame(cur.fetchall(), columns=chat_cols)
    else:
        chats = pd.DataFrame(columns=chat_cols)
        print("DATABASE_URL not set: chat logs skipped.")
    msg = chats["message"].fillna("").str.lower()
    rep = msg.str.contains("identifies as a republican")
    dogs = msg.str.contains("debate with users about whether cats or dogs")
    chats["is_system_prompt"] = rep | dogs
    chats["bot_prompt"] = None
    chats.loc[rep, "bot_prompt"] = "republican_persona"
    chats.loc[dogs, "bot_prompt"] = "cats_dogs"
    chats.to_csv(PROC / "chat_messages.csv", index=False)

    (HERE / "data" / "pull_log.json").write_text(json.dumps({
        "pulled_at": datetime.now(timezone.utc).isoformat(), "prolific_study_id": PROLIFIC_STUDY_ID,
        "participants": len(parts), "screenouts": len(screen), "client_errors": len(errors),
        "test_records_excluded": n_test, "investments": len(inv), "chat_exchanges": len(chats)}, indent=2))
    print(f"Pulled {len(parts)} participants, {len(screen)} screen-outs, {len(inv)} investments, "
          f"{len(chats)} chat exchanges; excluded {n_test} test records.")


if __name__ == "__main__":
    main()
