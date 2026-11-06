"""Pull the allocation-game pilot (Prolific, Nov 2026) and write flat files to data/.

Read-only. Sources:
  - MongoDB database `twins-allocation-game`: participants, screenouts, client_errors
    (the `testing` collection holds test-mode sessions and is never read).
  - Chatbot Postgres (`conversation_logs`, user_id = the participant's Mongo _id).

Connection strings come from the environment, never from code:
  MDB_MCP_CONNECTION_STRING (falls back to MONGODB_URI in the repo .env)
  DATABASE_URL (repo .env) for the chat logs; chats are skipped if it is missing.

Excluded: prolific_pid starting with TEST_ / test_ (any case), test == true.

Run from anywhere:  python3 studies/08_allocation_game_pilot/pull_data.py
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
DB_NAME = "twins-allocation-game"
# Text inputs with an id in the app. The animal check, extremity slider and chat (an iframe) carry no id
# or are not captured, so their keys land in keys_unlabeled.
TEXT_FIELDS = {"math-answer": "math_check", "age": "age", "comments": "comments"}

dotenv.load_dotenv(REPO / ".env")


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
    keys = d.get("keystrokes") or []
    leaves = d.get("tab_leaves") or []
    row = {
        "participant_id": str(d["_id"]),
        "prolific_pid": d.get("prolific_pid"),
        "submission_id": d.get("submission_id") or d.get("orphan_submission_id"),
        "prolific_study_id": d.get("prolific_study_id"),
        "orphan": bool(d.get("orphan", False)),
        "condition": d.get("condition"),
        "chatbot_condition": d.get("chatbot_condition"),
        "party": d.get("party"),
        "extremity": d.get("extremity"),
        "game_world": ",".join(d.get("game_world_order") or []),
        "game_seed": d.get("game_seed"),
        "app_commit": (d.get("app_version") or {}).get("gitCommit"),
        "started_at": iso(d.get("started_at")),
        "chatbot_start": iso(d.get("chatbot_start")),
        "chatbot_end": iso(d.get("chatbot_end")),
        "chatbot_duration_ms": d.get("chatbot_duration_ms"),
        "chatbot_server_elapsed_ms": d.get("chatbot_server_elapsed_ms"),
        "chatbot_duration_valid": d.get("chatbot_duration_valid"),
        "n_rounds_saved": len(d.get("game_rounds") or []),
        "game_cumulative_revenue": d.get("game_cumulative_revenue"),
        "game_bonus": d.get("game_bonus"),
        "game_score_R_world": d.get("game_score_R_world"),
        "game_finished_at": iso(d.get("game_finished_at")),
        "completed_at": iso(d.get("completed_at")),
        "gender": d.get("gender"),
        "age": d.get("age"),
        "race": ";".join(d.get("race") or []),
        "education": d.get("education"),
        "comments": d.get("comments"),
        "honeypot_value": d.get("honeypot_value"),
        "bot_timing_ms": d.get("bot_timing_ms"),
        "n_keystrokes": len(keys),
        "n_paste": sum(1 for k in keys if str(k.get("key", "")).lower() == "v"
                       and any(p.get("key") in ("[Control]", "[Meta]") and 0 <= k["ts"] - p["ts"] < 1500
                               for p in keys)),
        "n_tab_leaves": len(leaves),
        "tab_leave_total_s": sum((l.get("durationMs") or 0) for l in leaves) / 1000,
        "user_agent": d.get("user_agent"),
    }
    for field, name in TEXT_FIELDS.items():
        row[f"keys_{name}"] = sum(1 for k in keys if k.get("field") == field)
    row["keys_unlabeled"] = sum(1 for k in keys if k.get("field") not in TEXT_FIELDS)
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

    rounds = [
        {"participant_id": str(d["_id"]), "condition": d.get("condition"),
         **{k: (iso(v) if k == "saved_at" else v) for k, v in r.items()}}
        for d in parts for r in (d.get("game_rounds") or [])
    ]
    pd.DataFrame(rounds).to_csv(PROC / "rounds.csv", index=False)

    pd.DataFrame([{
        "prolific_pid": d.get("prolific_pid"), "submission_id": d.get("submission_id"),
        "prolific_study_id": d.get("prolific_study_id"), "party": d.get("party"),
        "extremity": d.get("extremity"), "math_passed": d.get("math_passed"),
        "animal_passed": d.get("animal_passed"), "reasons": ";".join(d.get("reasons") or []),
        "screened_out_at": iso(d.get("screened_out_at")),
        "ts_attention_math": (d.get("screen_timestamps") or {}).get("attention_math"),
    } for d in screen], columns=["prolific_pid", "submission_id", "prolific_study_id", "party", "extremity",
                                 "math_passed", "animal_passed", "reasons", "screened_out_at",
                                 "ts_attention_math"]).to_csv(PROC / "screenouts.csv", index=False)

    pd.DataFrame([{"where": d.get("where"), "message": d.get("message"),
                   "participant_id": d.get("participant_id"), "at": iso(d.get("at"))} for d in errors],
                 columns=["where", "message", "participant_id", "at"]).to_csv(PROC / "client_errors.csv", index=False)

    # Chat logs: one row per exchange (participant message + bot response). The chat app logs
    # the bot's system prompt as the first "message" of each session, paired with the opening
    # greeting; is_system_prompt marks those rows and bot_prompt says which bot was served.
    n_chat = 0
    chat_cols = ["participant_id", "timestamp", "message", "response"]
    pg_url = os.environ.get("DATABASE_URL")
    if pg_url and parts:
        import psycopg2
        with psycopg2.connect(pg_url, sslmode="require") as con, con.cursor() as cur:
            cur.execute(
                "SELECT user_id, timestamp, message, response FROM conversation_logs "
                "WHERE user_id = ANY(%s) ORDER BY user_id, timestamp",
                ([str(d["_id"]) for d in parts],))
            chats = pd.DataFrame(cur.fetchall(), columns=chat_cols)
        n_chat = len(chats)
    else:
        chats = pd.DataFrame(columns=chat_cols)
        print("DATABASE_URL not set: chat logs skipped.")
    msg = chats["message"].fillna("").str.lower()
    chats["is_system_prompt"] = msg.str.startswith(("you are ", "your objective"))
    chats["bot_prompt"] = None
    chats.loc[chats.is_system_prompt & msg.str.contains("republican"), "bot_prompt"] = "republican_persona"
    chats.loc[chats.is_system_prompt & msg.str.contains("cats or dogs"), "bot_prompt"] = "cats_dogs"
    chats.loc[chats.is_system_prompt & chats.bot_prompt.isna(), "bot_prompt"] = "other"
    chats.to_csv(PROC / "chat_messages.csv", index=False)

    (HERE / "data" / "pull_log.json").write_text(json.dumps({
        "pulled_at": datetime.now(timezone.utc).isoformat(), "participants": len(parts),
        "screenouts": len(screen), "client_errors": len(errors), "test_records_excluded": n_test,
        "chat_exchanges": n_chat}, indent=2))
    print(f"Pulled {len(parts)} participants, {len(screen)} screen-outs, {len(rounds)} rounds, "
          f"{n_chat} chat exchanges; excluded {n_test} test records.")


if __name__ == "__main__":
    main()
