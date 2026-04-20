# Todo

## S2 Game Experiment (MongoDB: synthetic-contact/participants)
- [x] Pull data from MongoDB and inspect structure
- [x] Write analysis QMD (`studies/02_experimental/game_analysis.qmd`)
- [x] Render with test data (N=2) — renders clean
- [ ] Re-render once real data is collected (remove test-data guards)
- [ ] Write up results for paper

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
