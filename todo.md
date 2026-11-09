# Todo

## Build the adaptive (GP/Thompson) pilot system + dashboard (2026-11-03)
- [x] Engine: GP (Matérn 5/2, one length-scale per knob, noise floor) + Thompson sampling, 20 warm-up random, 25% random, refit every 10, time cap (≤13 rounds) and N cap (120) → studies/06_bo_pilot/bo_pilot.py
- [x] Simulated players with a known true surface + simulated Prolific launch (overlapping arrivals) → simulate.py
- [x] Benchmark adaptive vs all-random over 30 launches → benchmark.py (both reach 74% of the best setting at N=120)
- [x] Dashboard (slices + Thompson draws, pick histograms, heatmaps vs truth, search path, length-scales, participant inspector) → https://claude.ai/artifact/FBbFBVaNong6azPYbpt4Q7
- [x] MongoDB queue + live CLI (init/step/refit), tested against a local mongod (`make bo-test`, 6/6 pass)
- [x] Branch `bo-pilot`, issue #21
- [ ] BenBen: decide on the outcome measure (straight-line slope penalizes fast learners in long games; see comms.md 2026-11-03)
- [ ] BenBen: decide whether adaptive sampling is worth it given the benchmark tie (see comms.md)
- [ ] Wire the game app to the queue (claim at start, write shares/revenues at finish) once the payoff option (a/b/c) is chosen

## Feedback on email to Stefano re: senior-twin ad null (2026-11-02)
- [x] Check each claim in the draft against the data (corrs, accuracy decomposition, party split)
- [x] Run mediation condition → green belief → ad persuasiveness (lavaan, 5,000 bootstraps), both studies
- [x] Coedit write-up with appendix: https://coedit-46g3.onrender.com/d/0N_QaNAVerBd4R7SjsRhGiHH (numbers locked to internal_checks/2026-11-02_senior_ad_null/results.json)
- [ ] BenBen: review the Coedit note before sharing with Stefano/Noah/Olivier
- [x] Answered @claude comments on the senior-ad note (2 replies, 4 suggestions)
- [x] Brief doc (cNf-f1CYTGRK0tvgu1u_tM4X): 3 hand-typed cites → Zotero cites (suggestions); Haws 2013/2014 year + hand-typed References list left for BenBen
- [x] prose-check rule `teaser-signpost` + CLAUDE.md (global + project) + research-writing skill
- [ ] Preregistration of age study (AsPredicted #280426, https://aspredicted.org/iz99m4.pdf): site blocks automated download; BenBen to check whether ad persuasiveness is listed as a DV

## Senior-twin null on ad rating: does politics come up unprompted? (2026-11-02)
- [x] Explain check #4 (replay 20 openers to Rep vs Dem senior twins, count unprompted politics)
- [x] Confirmed the real S2 twin chats were never saved (turn_count = 0 for all 130); only Noah's Apps Script proxy might hold them
- [ ] BenBen: ask Noah whether the twin app's Apps Script proxy logs requests (and which model it calls)
- [x] Paco reminder email scheduled for Tue 2026-11-03 09:00 ET (~/.benos/oneshot/noah_twin_logs_reminder.py; launchd com.benos.oneshot.noahlogs, deletes itself after sending)
- [ ] If logs arrive: code the real chats for unprompted politics (send coding prompt to BenBen first); else decide on the simulation fallback

## Why twin cut misperception but not ad rating in Study 2 (2026-11-01, Slack)
- [x] Bias/spread macros added to brief.qmd (SoneEst*, StwoEst*, *Sd*, *REstAd, StwoRepTwin*/StwoNonRepTwin*); brief.pdf re-rendered
- [x] Coedit: new paragraph s:4efcd26c20e6, party-paragraph topic sentence s:2652a0c113e6, added sentences s:f2d172e9f020; 23 locked numbers; comment added
- [ ] BenBen: port accepted text back into brief.qmd (coedit-port) once accepted

## Coedit brief: one figure style, bar charts only, no distributions (2026-11-01)
- [x] Restyled all figures as house-style bar charts in brief.qmd; dropped pre-post, histogram, scatter figs; brief.pdf rendered
- [x] Coedit: 5 main + 9 supplementary locked images, ref fixes, Supplementary figures heading (comment c:9a167d5d4103)
- [x] BenBen deleted old images (also removed main Figs 1-5 + Tables 1-6); re-added Figs 1-5 as s:54e17766bb12, s:a9187ddbdc71, s:cd06105a4bd3, s:001b6416623a, s:ab34e45fe911
- [ ] BenBen: decide whether Tables 1-6 come back
- [x] Persona/control-bot disclosure -> Supplementary materials (s:281fd6de4d44, s:e0b477ee01c1) + Lira et al. 2026 reference (s:ba2c1ec72af7)

## Enrich intro/discussion from arXiv 2607.02181 + overlap audit (2026-11-01)
- [x] Draft 7 additions + overlap audit -> comms.md (2026-11-01)
- [ ] BenBen: approve which additions go into coedit

## Summary effects table: 2 studies x 2 outcomes x 2 comparisons vs control (2026-11-01, Slack)
- [x] tbl-summary chunk in paper/marketing_brief/brief.qmd (Discussion); CSV in output/tables/brief_effects_summary.csv; brief.pdf re-rendered
- [x] Coedit: caption s:67612b356175 + locked table s:814c9803d70a after Discussion paragraph 1

## Accuracy about the specific twin, not the group mean (2026-10-31, Slack)
- [x] Score each estimate against the assigned twin's GREEN (studies/03_noah_age/individual_accuracy.qmd; age study only)
- [ ] Political study: blocked, only 3/138 twin participants have a twin ID in Qualtrics
- [x] Posted to coedit brief as suggestions after "Typical twins teach the most" (2 paragraphs s:d382c7767237, s:61f3ab23eb2f; 15 locked numbers; Figures 10b/10c; note comment c:ae7da835acd2)
- [x] Add ground-truth (senior mean) error to Figure 10c (new image s:8ed6a4b244c5)
- [ ] BenBen: reject the old Figure 10c image (s:617e6882f0f5)
- [ ] BenBen: reject the "130 twin" lock (s:545d13aa5bb8) and retype "twin", or ask me to redo it
- [x] 2026-11-01 re-run: all locked numbers reproduce; JSON signs fixed so d_z, vs_control_*, vs_persona_* match the positive values locked in the doc
- [x] 2026-11-01 Coedit: outline Study 2f (s:d831e957dcbe), Discussion 2 rewording (s:102fe4b28dca), Discussion paragraph sentence with locked slope (s:2b3ef300eeff), answer comment c:962f1125d6b7

## Ad persuasiveness reversal: twin vs persona (2026-10-31, Slack, Stefano's point 1)
- [x] Figure out why twin > persona on the ad in the political study but persona > twin in the age study (internal_checks/2026-10-31_ad_reversal/, not main content)
- [x] Pull and analyze conversations (control + persona from Postgres; twin transcripts were not saved)
- [x] Hypotheses tested in parallel: (A) noise/robustness, (B) persona transcript content, (C) twin profiles + bots-rate-the-ad simulation
- [x] Synthesis + recommendation sent in Slack (README.md in the folder; added D_twin_party test after the 10-min timeout)
- [ ] BenBen: approve the draft LLM coding prompts (B_transcripts/llm_coding_prompts_DRAFT.md) before any run
- [x] Follow-up: level effect vs party swamping, stat + plot (E_level_vs_party/)
- [x] STE explanation of the reversal added to the coedit brief as a suggestion (s:0bcf20a33898, after the Study 2 ad paragraph; 13 locked numbers)
- [x] Study 2 figure with twin bar split by twin party (src/r/jobtalk_bar_figures.R → output/figures/jobtalk/s2_twin_party.png; in brief.qmd as fig-s2-party; coedit suggestion s:f1edbc339910)
- [ ] BenBen: move E_level_vs_party code into the brief pipeline before the paragraph stays (source is gitignored)
- [ ] BenBen: fix twin app logging (post transcript every turn) before the multi-trial study

## Game design: GP / Bayesian optimization question (2026-10-31, Slack)
- [x] Answer whether GP Bayesian optimization fits the design choice (Slack reply)
- [x] Explain the power and recovery numbers in plain language (Slack reply)
- [x] Answer: why not update the GP after every pair of participants? (Slack reply: yes, sequential with Thompson sampling, refit every ~10 completions, 25% random draws)
- [x] Draw the GP kernels (uploaded to Slack: gp_kernels_explained.png)
- [x] Define the pilot knobs without belief questions (Slack reply)
- [x] Explain the 45% vs 85% power numbers (belief reports = extra measurement, not a separate outcome)
- [x] Answer: two sequential pilots (signal-to-noise first, then magnitude)? (yes; magnitude may come from the real-data payoff)
- [x] Scope a realistic payoff function from EV data (Pew interest, Gallup ownership, Davis-Li-Springel county concentration) (Slack reply)
- [ ] BenBen: pick payoff option (a) calibrate to data, with R under-estimated / (b) product where R wins / (c) competition-driven
- [ ] BenBen: approve or reject the adaptive-pilot plan (knobs drawn per participant, 2 batches, GP on the learning slope, time/cost caps)

## Coedit port (2026-10-29)
- [x] Port the marketing brief (3 studies) to coedit (first push, numbers unlocked → superseded)
- [x] Numbers from macros: brief.qmd writes numbers_brief.tex (56 \newcommand macros); re-pushed with 58 locked numbers
- [x] Deleted both earlier coedit docs (xzC_…, McMg…)
- [x] Clean read: figure/table numbers, no [label]/[ref] tags, reference list + appendix table rendered → https://coedit-46g3.onrender.com/d/cNf-f1CYTGRK0tvgu1u_tM4X (screenshots checked)
- [ ] BenBen: two hand-typed twin-vs-persona ad tests (S1: 0.10 pts, d = 0.09, p = .441; S2: 0.34 pts, d = 0.32, p = .012) have no code; compute them in R or drop them
- [ ] BenBen: commit paper/marketing_brief/ (brief.qmd, numbers_brief.tex, .coedit.json)? .coedit.json is what lets `check` keep coedit numbers in sync

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

## Individual-twin accuracy (2026-10-31)
- [x] Age study: accuracy relative to the specific twin (studies/03_noah_age/individual_accuracy.qmd → .html; figures individual_tracking.png, individual_accuracy_by_condition.png)
- [ ] Political study: blocked, only 3 of 138 twin participants have persona IDs (needs Noah's chatbot server logs)

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

## 2026-11-08 (Slack) — Lab deck for Stefano's lab: pilots + Bayesian model
- [x] HTML deck (html-slides skill) with screenshots of both pilots, results showing the null/backfire, and a step-by-step Bayesian learning model ending in condition effects on prior, openness, and the weight on Riverton good news → rebuilt 2026-11-08 with talk-slides standards (no eyebrow tags): `presentations/2026-11-09_lab_pilots/out/lab_pilots_live.html`
- [x] Add rule to html-slides skill: no small uppercase eyebrow tags, no "·"; research decks use talk-slides
- [x] (2026-11-08) Deck v2: highlight each equation term as it is explained; learning-rate form (m + α·surprise) and the weighted-average form; worked example (one treated player's first 6 clicks); model fitted to pilot 2 per player (`studies/10_bandit_game_pilot/fit_learner.py`)
