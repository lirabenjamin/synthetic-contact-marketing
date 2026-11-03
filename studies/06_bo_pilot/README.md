# Adaptive pilot for the multi-round game (pilot 1)

This folder holds a GP with Thompson sampling that chooses the game's knobs for each new participant, plus a dashboard that shows how it chooses them. The plan comes from Slack, 2026-10-31 (#synthetic-contact-marketing). Issue #21.

| Knob | Range | Meaning |
|---|---|---|
| Signal-to-noise | 0.25–4 (log scale) | True pay gap log(R/D) = 0.4, divided by the SD of each round's revenue noise |
| Payoff curvature α | 0.2–0.8 | Revenue ∝ share^α; the best share to R is 1/(1+exp(−0.4/(1−α))) |
| Rounds | 6–15, capped by time | Each game takes 4 + 0.6 × rounds minutes, with a 12-minute cap, so at most 13 rounds |

**Outcome.** For each person, fit a straight line to their distance from the best split across rounds. The score is how far that fitted line drops from round 1 to the last round, in percentage points.

**Policy.** The first 20 people get random knobs. After that, 25% of people still get random knobs and the rest get Thompson draws over 1,024 candidate settings. The GP refits after every 10 completions, and the run stops at 120 people.

## Files
- `bo_pilot.py`: the game, the outcome, the GP, the engine, the in-memory and MongoDB stores, and the live CLI.
- `simulate.py`: simulated players with known rules, and a simulated Prolific launch with overlapping arrivals.
- `benchmark.py`: compares the adaptive policy with plain random assignment over 30 simulated launches.
- `dashboard.py` + `dashboard_template.html`: build the dashboard as one self-contained HTML file.
- `test_bo_pilot.py`: tests of the formulas, the GP, the launch policy and the MongoDB queue.

## Commands (from the repo root)
- `make bo-sim`: runs the simulated launch and the benchmark, then writes `dashboard.html`.
- `make bo-test`: runs the tests, including the MongoDB test against a temporary local `mongod`.
- `make bo-live-dashboard`: builds `dashboard_live.html` from the live database (needs `MDB_MCP_CONNECTION_STRING`).

## Live run: app contract (not wired into the game app yet)
1. Before launch, run `python bo_pilot.py init --db bo_pilot` once. It queues 25 warm-up assignments.
2. When a person starts, the app atomically claims the oldest queued doc in `bo_queue`: `findOneAndUpdate({status:'queued'}, {$set:{status:'claimed', pid, claimed_at}}, {sort:{created_at:1}})`. It then writes the doc's fields plus `started_at` to `bo_participants`. The app uses the `snr`, `sigma`, `alpha` and `rounds` fields from that doc.
3. When the person finishes, the app sets `shares`, `rev_r`, `rev_d` (one value per round), `finished_at` and `status:'complete'` on `bo_participants`.
4. A cron job runs `python bo_pilot.py step --db bo_pilot` every minute. It scores new completions, refits the GP once 10 more people have finished, swaps the unclaimed queue for fresh draws, and keeps 25 assignments queued without exceeding 120 people in total.
