# Todo

## Staircase Indifference Pilot
- [x] v1 (4 tasks) — `SV_6u0w8nWPlYAr8fI` (superseded)
- [x] v2 (mortality + TMT + real framing) — `SV_9LW8WXUvJGECK0e` (superseded)
- [x] v3 (bot iframe) — `SV_eu1lOyOD9ve5IlU` (superseded)
- [x] v4 (bot + human-human via Render app) — `SV_2fbpWPjneZXf3wO`
- [x] Build Render pair-chat backend (`chat-pair-app/`) + smoke-test locally
- [ ] **Deploy chat-pair-app to Render**, paste URL into `HUMAN_CHAT_URL`, re-run `create_survey.py`
- [ ] Smoke-test preview URL
- [ ] Delete old pilots `SV_6u0w8nWPlYAr8fI`, `SV_9LW8WXUvJGECK0e`, `SV_eu1lOyOD9ve5IlU`

## S2 Game Experiment (MongoDB: synthetic-contact/participants)
- [x] Pull data from MongoDB and inspect structure
- [x] Write analysis QMD (`studies/02_experimental/game_analysis.qmd`)
- [x] Render with test data (N=2) — renders clean
- [x] Re-render with real data (N=32 → 37 completed)
- [x] Analyze round-by-round learning (result: no learning, slope = 0.71 pp/round, p = .40)
- [x] Compare to pilot (N=150): pilot had 3.09 pp/round learning, current has none
- [x] Pull and review chatbot transcripts from PostgreSQL
- [x] Diagnose root cause: competition cues dominate, making chatbot belief update irrelevant
- [ ] **Pause data collection on Connect** ← DO THIS
- [ ] Redesign game (equalize competition, or single-shot allocation)
- [ ] Pilot revised version
- [ ] Write up results for paper

## Pre-Post Immigration Study (Connect)
- [x] Data collection running
- [x] Preliminary results: replicates green attitudes findings
- [ ] Share full results with team
- [ ] Write up for paper

## Race-Based Twins Study (new — J&V extension)
- [x] Read Jacob & Vieites (2026) paper and extract DVs
- [x] Draft study design proposal (see comms.md 2026-03-23)
- [ ] BenBen: review proposal and answer 5 questions in comms.md
- [ ] Finalize design with Noah
- [ ] Check twin data for Black twins + tightwad scores availability
- [ ] Write pre-registration
- [ ] Build survey (Qualtrics or Render app)
- [ ] Launch pilot

## S2 Three-Condition Experiment (SV_9z4Iunuz8h46IuO)
- [x] Get survey definition and understand question structure
- [x] Write analysis QMD (`studies/02-experiment/analysis.qmd`)
- [x] **Download CSV from Qualtrics** (manual — 403 responses, 400 Democrats)
- [x] Render analysis.qmd — results match Word doc
- [ ] Write results section prose for paper
- [ ] Add to main report / paper
- [ ] Get correct pre-registration and add to folder

## Green Market Game Pilot
- [x] Save game HTML to pilots/green-market-game/
- [x] Analyze payoff math and difficulty calibration
- [x] Design 4-market layout with broken R-competition correlation
- [x] Choose payoff function (S-curve, half=30k, K=2.0, noise=0.30)
- [x] Build Qualtrics survey with embedded JS game
- [x] Run synthetic experiment (60 agents, 20/condition) — see pilots/green-market-game/simulation/
- [x] Fix optimizer bug (greedy → grid search)
- [x] Add 6 experience Likert items to survey (difficulty, engagement, frustration, feedback clarity, learning, length)
- [x] Update game to 8 rounds (was 10)
- [x] Improve open-ended questions (strategy + learning)
- [x] Write analysis pipeline (00_clean.r + analysis.qmd)
- [ ] Preview and test the survey end-to-end
- [ ] Verify embedded data export captures all round-level data
- [ ] Run self-pilot (play through a few times)
- [ ] Submit WBL form (90 ppl, 30/cell, $2.00, ~$240 total)
- [ ] Launch calibration pilot on Prolific
- [ ] Drop raw data into pilots/green-market-game/raw_data.csv
- [ ] Run 00_clean.r → render analysis.qmd → pick difficulty condition
