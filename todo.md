# Todo

## Multi-round game replication + Bayesian learning model (2026-10-13)
- [x] Diagnose 8-round pilot (Mar 24-26, N=50): no round-1 effect (46.4 vs 47.0%), no learning toward 100% optimum, allocation changes unrelated to last-round ROI
- [x] Propose model parameters, hypotheses, and redesign (Slack reply)
- [ ] BenBen: pick design (2-market vs 4-market; receptivity-driven payoff; per-round belief elicitation) and say whether to adapt the existing app minimally or rebuild the game
- [ ] Simulate an ideal Bayesian learner + parameter recovery + power before launch

## Slides (2026-10-07)
- [x] Re-create pre/post line plots in studies/01_prepost/slides.qmd as bar charts (main effects, by party, extremity, confidence); fixed warmth d sign bug; re-rendered slides.pdf
- [x] BU job talk Part 2 (S1–S3): remake point/line plots as bars (slides 75, 79, 80, 82) via src/r/jobtalk_bar_figures.R → ~/Documents/BU_JobTalk_bars_v2.pptx (original untouched; fixed crops on slides 82/87)
- [x] Age misperception gap bar chart for slide 85 (actual vs. perceived vs. twin bots) → output/figures/jobtalk/age_misperception_gap.png
- [x] Brief paper PDF of the 3 marketing studies (political, age, single-round allocation), 14 figures + 7 tables, STE-style prose → paper/marketing_brief/brief.pdf (`make brief`)
- [x] Correlation plot: estimated outgroup GREEN vs. ad persuasiveness, both studies → output/figures/jobtalk/belief_vs_ad_rating.png
- [x] Histogram of Twin-2K-500 GREEN scores (overall + under 65 vs. 65+, y = % within group) → output/figures/twin2k_green_hist.{png,pdf} (src/r/twin2k_green_hist.R)
- [x] Density plot of GREEN for 65+ twins only → output/figures/twin2k_green_density_65plus.{png,pdf}
- [ ] Qualtrics screens → PDF: recorder never captured screens; retry when BenBen can click through (preview link SV_9z4Iunuz8h46IuO)
- [ ] BenBen: fix talk order (outline says S2 age before S3 allocation; deck shows allocation slide 84 first); fix slide 84 subtitle N=99 → 98
- [ ] BenBen: decide on 65+ exclusion in age study (bars use it; old slides didn't), check slide text numbers

## Repo housekeeping (2026-10-07)
- [x] Consolidate Noah pilot into 02_experimental (same data; re-export moved to data/raw/), renumber Noah age/race to 03/04
- [x] Fix 02-experiment path bug in analysis.qmd; re-render
- [x] Update studies/README.md, README.md, CLAUDE.md repo map
- [x] Age study: misperception-gap figure + continuous prototypicality (studies/03_noah_age/analysis.qmd, Twin-2K-500 ground truth via src/r/twin2k_age_ground_truth.R)
- [ ] Ask Noah: (a) chatbot server logs to recover twin IDs in political study; (b) source of age-study persona IDs (don't match Twin-2K-500 TWIN_IDs); (c) why green_distance reference = 3.346 (18-29 mean, not 65+)
- [ ] Split game_analysis.qmd into single-round (Apr 3, N=98) vs multi-round (Mar 24-26, N=50)

## S2 Game Experiment (MongoDB: synthetic-contact/participants)
- [x] Pull data from MongoDB and inspect structure
- [x] Write analysis QMD (`studies/02_experimental/game_analysis.qmd`)
- [x] Render with test data (N=2) — renders clean
- [x] Re-render once real data is collected — rendered 2026-10-07 BUT pools two studies (51 multi-round Mar 24-26 + 99 single-round Apr 3) — needs split
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
- [x] Write analysis QMD (`studies/02_experimental/analysis.qmd`)
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
