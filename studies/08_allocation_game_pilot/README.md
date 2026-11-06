# 08 Allocation-game pilot (Prolific, Nov 2026)

Pilot of the 10-round budget game. Democrats chat for 5 minutes with a Republican persona bot (treatment) or a cats-vs-dogs bot (control), then split $100,000 between Riverton (Republican-leaning) and Lakewood (Democratic-leaning) counties. App: `twins/survey-app`, branch `two-world-game`, tag `v2.1.0-allocation-game-pilot` (commit 1ac0f92). Prolific study id `6aee0fb81756ff0fd8a8a934`. Launched 2026-11-06, target N about 20.

## Rerun (one command)

```sh
make -C studies/08_allocation_game_pilot      # from the repo root
```

This pulls fresh data (`pull_data.py`) and renders `analysis.html` (`analysis.qmd`). `make pull` or `make report` runs one step.

Needs: `MDB_MCP_CONNECTION_STRING` in the environment (falls back to `MONGODB_URI` in the repo `.env`), and `DATABASE_URL` in the repo `.env` for the chat logs. Python 3 with pymongo, psycopg2, pandas, python-dotenv; R with tidyverse, jsonlite, knitr; Quarto.

## Files

| File | Content |
|---|---|
| `pull_data.py` | Read-only pull from MongoDB `twins-allocation-game` (participants, screenouts, client_errors) and the chatbot Postgres `conversation_logs`. Drops test records (Prolific ID starting `TEST_`/`test_`, or `test = true`). |
| `analysis.qmd` / `analysis.html` | Pilot report: flow and timing, data quality, game results, treatment vs control, integrity checks. |
| `data/raw/*.jsonl` | Full Mongo records (with Prolific IDs and keystrokes). |
| `data/processed/*.csv` | `participants.csv` (one row per assigned person), `rounds.csv` (one row per round), `screenouts.csv`, `chat_messages.csv` (one row per chat exchange; `is_system_prompt` marks the logged bot prompt), `client_errors.csv`. |

`data/` is gitignored: it holds Prolific IDs and chat text.
