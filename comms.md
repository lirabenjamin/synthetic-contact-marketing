# Comms

## 2026-04-20 — Staircase Pilot v4: Human-human chat via Render app

New survey: **`SV_2fbpWPjneZXf3wO`**
- Preview: https://upenn.qualtrics.com/jfe/form/SV_2fbpWPjneZXf3wO
- Edit: https://upenn.qualtrics.com/survey-builder/SV_2fbpWPjneZXf3wO/edit

**What's new:**
- Built a tiny pairing backend at `pilots/03_staircase_indifference/chat-pair-app/` — Express + Socket.IO, waiting-room queues keyed by party, Dem↔Rep cross-matches only, 3-min chat window, `postMessage` to Qualtrics on completion.
- Smoke-tested locally: two clients (Dem + Rep) paired and echoed messages; two Dems correctly stayed unmatched.
- Qualtrics human branch now iframes the deployed URL (`${HUMAN_CHAT_URL}/?party=…&outgroup=…&id=ResponseID`) and listens for `chat_ended`/`chat_continue` postMessages to gate the Next button.
- Captures: `chat_start_ts`, `chat_end_ts`, `chat_end_reason` (one of `timeout`, `partnerLeft`, `noMatch`, `ended`).

**Deploy steps (you):**
1. Commit + push the repo (this one, no new repo needed).
2. Render → New → **Web Service** → connect the repo → **Root Directory = `pilots/03_staircase_indifference/chat-pair-app`**. Runtime = Node (auto-detected). Free plan.
3. Deploy. Note the URL.
4. Set `HUMAN_CHAT_URL=https://your-url.onrender.com` in `.env` and re-run `pilots/03_staircase_indifference/create_survey.py`.
5. Free tier spins down after 15 min idle; for a live pilot upgrade or ping `/healthz` every 10 min.

**Open decisions:**
- Matching timeout is 2 min; chat duration is 3 min (hardcoded in `server.js`). Change if you want.
- In-memory state — restarts drop rooms. Fine for short pilots.

## 2026-04-20 — Staircase Pilot v3: Bot iframe in; human still stubbed

New survey: **`SV_eu1lOyOD9ve5IlU`** (v2 `SV_9LW8WXUvJGECK0e` superseded)

- Preview: https://upenn.qualtrics.com/jfe/form/SV_eu1lOyOD9ve5IlU
- Edit: https://upenn.qualtrics.com/survey-builder/SV_eu1lOyOD9ve5IlU/edit

**What's new:**
- Bot condition now embeds `https://reframe001-7a186c892e5e.herokuapp.com/?condition=twin_{democrat|republican}&id={ResponseID}` as an iframe with a sticky 3-min countdown. Continue button hidden until timer ends. Captures `chat_start_ts`, `chat_end_ts`.
- Human condition = placeholder page (clearly labeled "matching not available, TBD") + a Continue button. Captures `chat_human_placeholder_shown=1` so you can filter those out of analysis.

**Decision you owe me for human-human matching:** Qualtrics alone can't do this (each session is stateless, no participant-to-participant channel). Cleanest paths:
- **Tiny Render app w/ WebSockets** — Waiting queue + pair + 3-min chat + return to Qualtrics. ~1-2 hr. Uses `render-survey` skill. Same infra as your other apps.
- **Firebase Realtime DB from Qualtrics JS** — No backend to deploy. Client-side matching logic. Lighter but introduces a dep.
- **Extend the reframe Heroku app** — Add a `condition=human_pair` mode to the existing app. Keeps infra consolidated; I'd need the app's source.

Reply with which path and I'll ship it.

## 2026-04-17 17:25 — Staircase Pilot v2: Mortality-Only + Real Task

Rebuilt per your revised scope. New survey ID: **`SV_9LW8WXUvJGECK0e`**.

- Preview: https://upenn.qualtrics.com/jfe/form/SV_9LW8WXUvJGECK0e
- Edit:    https://upenn.qualtrics.com/survey-builder/SV_9LW8WXUvJGECK0e/edit

**What changed:**
- Only 1 task left: mortality (removed math, slider, counting)
- Consent + instructions rewritten: choices are REAL, participant actually does what they pick
- Added real mortality reflection block with classic Rosenblatt TMT prompts + sticky countdown timer (duration = `mortality_threshold` from staircase). Writing auto-saves to `mortality_response` every 5 s + on input; continue button is hidden until timer hits 0.
- Branch logic routes by `final_pick`:
  - `final_pick == "mortality"` → Mortality Reflection block → End
  - `final_pick == "chat"` → End block saying "we'll send you to the conversation now"

**Your to-do to ship this:**
1. **Configure end-of-survey redirect URL** (Qualtrics → Survey Options → End of Survey). That's the hook where participants who picked chat get sent to your conversation system. You can pipe `${e://Field/outgroup_label}`, `${e://Field/chat_partner}`, `${e://Field/ResponseID}` into the redirect URL.
2. **Delete the old pilot** (`SV_6u0w8nWPlYAr8fI`) — I left it so you can diff, but it's superseded.
3. **Click through the preview once.** I couldn't smoke-test (Chrome extension wasn't connected). Sanity checks: (a) taste trial shows age input, (b) staircase shows 3-min chat card vs variable-minute mortality card, (c) final pick shows 2 cards, (d) if you pick mortality, you see TMT prompts + 3-min timer, (e) text you type in the textarea saves to `mortality_response`.

**Key embedded data captured:**
- `chat_partner` (human | bot)
- `outgroup_label` (Republican | Democrat)
- `mortality_threshold` (minutes, staircase indifference)
- `mortality_trials` (JSON array of per-trial choices)
- `final_pick` (chat | mortality), `final_pick_duration`
- `mortality_response`, `mortality_response_chars`, `mortality_start_ts`, `mortality_end_ts`

## 2026-04-17 17:00 — Staircase Indifference Pilot: Built & Activated

BenBen — the survey is live. Files in `pilots/03_staircase_indifference/create_survey.py`.

**Survey ID:** `SV_6u0w8nWPlYAr8fI`
- Preview: https://upenn.qualtrics.com/jfe/form/SV_6u0w8nWPlYAr8fI
- Edit:    https://upenn.qualtrics.com/survey-builder/SV_6u0w8nWPlYAr8fI/edit

**Design decisions I made (revise as needed):**
1. **Party ID is 2-option** (Democrat/Republican). Independents have no clean outgroup; happy to add an "Independent, leans ___" branch if you want it.
2. **Outgroup label is computed in JS** from the party question's piped text, not via survey-flow branches. Cleaner, no manual step.
3. **chat_partner randomizer is even/50-50** between "human" and "bot". Bot condition shows "Talk to a [Rep/Dem] AI"; human shows "Talk to a [Rep/Dem]".
4. **Final task routing is stubbed**: after the final pick, I show a thank-you page that displays the pick + duration. I did **not** wire real chat or TMT-writing because (a) your instructions page explicitly says "your choices here are hypothetical" and (b) real chat routing needs infra we don't have yet. Tell me if you want me to add: (i) a bot chat iframe (Heroku app, like in pilots/02), (ii) a real TMT writing prompt w/ timer, (iii) a redirect URL for human-chat pairing.
5. **Staircase params** (from your JS): start at 10 min, step 5 halving on reversals, min 0.5 min, max 30, stops at 8 trials or 3 small reversals. Indifference = mean of last two reversals.

**Known gaps you should verify:**
- Consent is passive (just a descriptive page + Next). If IRB wants an explicit "I consent: Yes/No" with a No-→end branch, flag it and I'll add it.
- I couldn't smoke-test in a live browser (Chrome extension wasn't connected on my side). **Please click through the preview URL once** and flag anything weird.
- Embedded data written by JS at runtime: `task_order`, `{math,mortality,slider,counting}_{threshold,trials}`, `final_pick`, `final_pick_duration`.

## 2026-03-27 — Game Experiment: No Learning, Redesign Needed

BenBen, here's the summary of our analysis session:

**Current state:** N=37 completed (still collecting ~5/hr). Data shows **zero treatment effect** and **zero learning**.

**Treatment effect:** d = -0.04 on trial 1 (the cleanest measure). Overall d = -0.22 across all rounds, driven entirely by a random spike at round 5.

**Learning:** Slope = +0.71 pp/round, p = .40. Compare to the pilot (N=150) which had slope = 3.09 pp/round, p < .0001 and a +27pp total shift. Current study: +4.6pp total. People are not learning which markets are better.

**Root cause:** Competition labels dominate the task. The exp(-2×competition) term creates a 3.7× revenue difference between best/worst markets. Receptivity gap is only 10pp and goes the wrong direction (Dems more receptive). Both conditions can solve the game from competition cues alone — the chatbot belief update is irrelevant to the optimal strategy.

**Bot transcripts:** Many treatment participants never discussed energy products. Those who did often had their stereotypes *confirmed* by the sycophantic bot. Several participants chatted about marsupials, cats, or Trump for 5 minutes.

**Recommendation:** Pause collection and redesign. Key options:
1. Equalize competition across markets (so receptivity beliefs drive decisions)
2. Single allocation decision (no feedback, pure belief measure)
3. Remove competition labels entirely

**Email sent to team (2026-03-26):** Updated Noah/Olivier/Stefano on game pilot results, pre-post immigration replication, bot sycophancy issue, bot validity findings, and twin typicality study idea.

---

## 2026-03-24 — Game Experiment Analysis Pipeline Ready

BenBen, the analysis QMD for the game experiment is at `studies/02_experimental/game_analysis.qmd`. It renders to a self-contained HTML.

**What it does:**
- Pulls directly from MongoDB (`synthetic-contact/participants`) — no manual export needed
- Filters incomplete + test PIDs, flags quality issues (chatbot duration, honeypot, bot timing, tab leaves)
- **Primary DV**: `game_total_pct_R` (% of total budget to R-leaning markets) — t-test + OLS with covariates
- **Learning curve**: Round-by-round `pct_R` by condition — mixed-effects model with random intercept + slope per participant
- **Market-level allocation**: Per-market allocation trends over rounds
- **Revenue + % optimal**: Boxplots + t-tests
- **Mediation**: `condition → pct_R → cumulative_revenue` via lavaan (bootstrapped indirect effects, as you prefer)
- **Moderation**: `condition × extremity` interaction on `pct_R`
- **Bonus**: Real-money comparison across conditions
- **Decision time**: Round-by-round allocation time

**Current state**: Only 2 test participants in MongoDB. All inferential stats are guarded (show descriptives only until N is sufficient). Once you launch on Prolific, just re-render:
```
cd studies/02_experimental && quarto render game_analysis.qmd
```

**Note**: The MongoDB URI with credentials is hardcoded in the QMD. If this goes to GitHub, we should move it to `.env`. Let me know.

## 2026-03-23 — Race-Based Twins Study: Jacob & Vieites DVs + Proposed Design

BenBen, here's my analysis of the Jacob & Vieites paper and how we should design the twins study.

### What Jacob & Vieites Actually Measured (Their DVs)

Their paper has 9 studies, escalating from perceptions → stereotypes → strategic decisions → interventions. The DVs that matter:

**Perception DVs (Studies 1A, 1C):**
- **Income-rank perception** (1-10 scale): "Where does this consumer fall from Bottom 1% to Top 1%?" Given *identical* income info, White professionals place Black consumers ~0.45 points lower. This is a *racialized interpretation of income* — the same salary "means less" when the person is Black.

**Stereotype DVs (Study 1B):**
- **Which group prioritizes what?** Forced-choice: Black vs. White consumers on innovation, quality, customization, price. Result: 39% said Black consumers prioritize price (vs 8% for White). Only 5% said Black consumers prioritize innovation (vs 46% for White). This is the consumption stereotype.

**Strategic Marketing Decision DVs (the ones that sell to JM):**
- **Study 1C**: Classify consumer into market segment — low-price/low-quality vs. high-quality/high-price (7-point agreement scale). Black consumers were classified more into the cheap segment (d = -.30), *mediated by income-rank perception*.
- **Study 2A**: Binary product-price strategy choice — "Should we pursue high-quality/high-price or mid/low-quality/mid-low-price for this consumer group?" 48% chose low-quality for Black consumers vs 35% for White.
- **Study 2B**: Confidence in market-entry profitability (7-point scale). Professionals rated Black-majority markets as less profitable (M = 4.43 vs 5.17, d = .54) despite *identical average income*.
- **Study 3**: Choose between two market regions. 57% of senior marketers chose the less affluent White region over the more affluent Black region.
- **Studies 4, 5A, 5B**: Same market-entry choice, but with diversity training or deliberation prompts as interventions.

### Your Concern is Right: Tightwad Scale Alone Isn't Enough

Noah's design has participants (1) predict tightwad scores and (2) say whether Black or White consumers are more price-sensitive. That's fine as a *mechanism measure*, but JM reviewers will ask "so what?" You need a DV that shows the bias matters for marketing.

Jacob & Vieites' genius is that they show the *causal chain*: lay theory → income misperception → consumption stereotypes → **bad strategic decisions** (wrong product portfolio, avoided markets, missed revenue). The strategic decision is what makes it a marketing paper rather than a social psych paper.

### Proposed Design: Twins Study on Racial Consumer Misconceptions

**Participants:** White business professionals/MBA students (Prolific or WBL)

**Design:** 2 conditions (between-subjects)
- **Treatment:** Chat with a Black digital twin for ~5 min
- **Control:** No chat (or neutral chat about non-consumption topic, e.g., dogs — like S2)

**Procedure:**
1. Brief intro: "You are a marketing manager evaluating consumer segments"
2. [Treatment only] Chat with a randomly selected Black twin. Participant is told they're chatting with a real person who participated in a prior study. Do NOT tell them it's about spending habits — that way they can't extract the answer directly (addresses Noah's concern about triviality).
3. Post-chat measures (all participants):

**DV 1 — Consumption stereotype correction (mechanism, parallels J&V Study 1B):**
- "Thinking about Black Americans, which group is more [price-sensitive / quality-demanding / innovation-seeking / interested in customization]?" (Black vs White vs equal) — same forced-choice as J&V 1B

**DV 2 — Income perception (mechanism, parallels J&V Study 1A):**
- "Imagine a Black American earning $75,000/year. Where would you place this person's economic standing?" (1-10 income rank) — same as J&V 1A
- Same for a White American earning $75,000/year (within-subjects, counterbalanced)

**DV 3 — Strategic marketing decision (the money DV, parallels J&V Studies 2-5):**
- Market-entry scenario: "Your company is expanding into a new region. Region A is 80% Black, average household income $85K. Region B is 80% White, average household income $78K. Which region do you recommend?" — direct parallel to J&V Study 3
- Could also add: product-price strategy choice (high-quality/high-price vs mid/low for a Black consumer segment) — parallel to J&V Study 2A

**DV 4 — Tightwad/spendthrift prediction (specific to twins ground truth):**
- Predict how the person they chatted with (or "the average Black American") falls on the tightwad-spendthrift scale
- We have ground truth from the twin data to measure accuracy

**Moderators (recorded from twin data):**
- Twin's actual income
- Twin's actual tightwad score
- Conversation length / engagement

### Why This Works for JM

1. **Direct parallel to J&V**: Same DVs (income perception, consumption stereotypes, market-entry decisions) but with a *new intervention* (AI twin interaction vs. their diversity training / deliberation prompts)
2. **Completes their story**: J&V show the problem exists and test two interventions. We show a *third, scalable intervention* — conversational AI. This is a natural extension, not a replication.
3. **Ground truth**: Unlike J&V, we have actual twin data on spending behavior, so we can measure whether misconceptions get *corrected toward reality* (not just reduced). This is stronger than J&V who only show bias exists.
4. **The "so what" is clear**: If chatting with a Black twin changes strategic marketing decisions (DV3), that's directly actionable — firms could use AI personas in market research training.

### Questions for You

1. **Control condition**: No chat, dogs chat, or chat with a *White* twin? The latter would let us isolate the race-specificity of the learning effect (J&V don't have this — they only compare Black vs White target, never an interaction).

2. **Specific person vs. average Black person**: You and Noah agreed on a specific person (the twin). I think we can do *both* — predict for the twin (DV4) AND predict for average Black consumers (DVs 1-3). The first tests individuated learning, the second tests generalization. If chatting with one Black person changes beliefs about Black consumers *in general*, that's a much bigger finding.

3. **Do we need the market-entry DV (DV3)?** I think yes — it's what makes this a marketing paper. Without it, we're just measuring perception change (which is closer to JPSP). The market-entry decision is the bridge.

4. **Sample**: WBL for business students, or Prolific for business professionals? J&V used both across studies. For a first study, Prolific professionals screened for business experience is probably faster and more credible.

5. **Twin selection**: Should we pre-select twins who are moderate on tightwadness (to maximize surprise/learning) or random (for generalizability)?

---

## 2026-03-17 — S2 Three-Condition Experiment Analysis (SV_9z4Iunuz8h46IuO)

BenBen, I built the full analysis QMD at `studies/02-experiment/analysis.qmd`. Here's what I need from you:

**ACTION REQUIRED: Download the CSV from Qualtrics manually.**
The API can see the survey metadata but can't export data (cross-datacenter error — your API token is on `upenn.qualtrics.com` but the survey data lives in a different DC). Steps:
1. Go to Qualtrics → SV_9z4Iunuz8h46IuO ("Digital Twins - Marketing Pilot") → Data & Analysis → Export & Import → Export Data → CSV
2. Save as `studies/02-experiment/data/raw/qualtrics.csv`
3. Then render: `quarto render studies/02-experiment/analysis.qmd`
> Data was downloaded

**Survey structure notes:**
- Three conditions: `twin`, `persona`, `control` (dogs chat) — randomized via BlockRandomizer
- The pre-treatment environmental attitude items (g1-g6 matrix with own/rep/dem) and warmth sliders are **in the Trash block** — they are NOT presented to participants
- This means we have a **purely between-subjects design**: post-treatment outgroup estimates only (green1-6), plus persuasiveness rating
- Ground truth for accuracy uses S1 data (`data/processed/analysis_data.parquet`)
- Embedded data from chatbot: session_id, persona_id, turn_count, transcript, green_score, green_distance
> no pretest by design. it biases through gricean norms. there are two ground truths the other comes from olivier's twin data which you can find in the word file, what the number is.

**Questions for you:**
1. Is it intentional that there are no pre-treatment measures? The prereg specifies pre-post-followup, but this survey only has post.
> Intentional. This is a different pre-registration to do that I will eventually need to do to go get it and put it in the folder for you. 

2. Should I add the warmth and confidence analyses once you have those measures, or is this a different version?
> If they're in the data, add them. If not, then no. 

3. The prereg mentions a Space Invaders game condition — but the survey has dogs chat as control and "persona" instead of game. Confirm the three conditions are: Twin, Persona (outgroup prompt), Control (dogs chat)?
> Yeah, you're looking at a different pre-registration. I'll remind me to give you the correct one at some point. 

## 2026-03-15 — Analysis Pipeline Ready

BenBen, the analysis is ready to go when data comes in. Here's the workflow:

1. Export from Qualtrics → save as `pilots/green-market-game/raw_data.csv`
2. Run `Rscript pilots/green-market-game/00_clean.r` → produces `clean_data.csv` + `round_data.csv`
3. Render `pilots/green-market-game/analysis.qmd` → full report

**What the report covers:**
- Q1: Do people learn? (allocation shifts, belief shifts, learning curves)
- Q2: Which difficulty is best? (experience scorecard: engaging vs frustrated vs felt learning)
- Q3: Benchmarking for chatbot study (effect sizes to compare against)
- Q4: Moderators (party affiliation, pre-game bias)
- Open-ended response samples

The cleaning script auto-detects Qualtrics column names so it should work regardless of export format quirks. If it breaks, most likely cause is column naming — just ping me.

## 2026-03-15 — Synthetic Experiment v2 + Experience Measures

BenBen, updated the simulation and added experience questions to the survey script.

**What changed:**
1. **Fixed optimizer bug.** The greedy $5k-step optimizer was suboptimal in hard mode (agents could beat "optimal" by 6%). Replaced with grid search. Now % optimal properly differentiates: easy 83% > medium 79% > hard 72%.
2. **Added payoff surface analysis.** The key insight: easy mode has a FLAT surface (50/50 split = 95% of optimal), hard mode is STEEP (50/50 = 78%). This explains why easy agents plateau early and hard agents keep climbing.
3. **Added convergence analysis.** Round-by-round % of optimal with spaghetti plots + early-vs-late comparison stats.
4. **Added 6 experience Likert items to `create_survey.py`:** difficulty, engagement, frustration, feedback clarity, learning, game length. These will tell us which difficulty condition hits the learning-to-frustration sweet spot.

**Important:** The experience items are in the script but the existing Qualtrics survey (SV_037Z7P2Ns52zaHs) doesn't have them yet. You need to either re-run `create_survey.py` to make a new survey, or I can add them to the existing survey via the API. Let me know.

**Files:** All in `pilots/green-market-game/simulation/` — `simulate.py`, `round_data.csv`, `agent_data.csv`, `report.qmd`, `report.html`

## 2026-03-09 — Green Market Game Pilot Survey Created

BenBen, the survey is live at: https://upenn.qualtrics.com/jfe/form/SV_037Z7P2Ns52zaHs

**Survey ID:** SV_037Z7P2Ns52zaHs

**What's in it:**
- Consent + instructions
- Pre-game belief sliders (D/R receptivity, allocation preference)
- The full 10-round game with embedded JS (saves all round data to embedded data)
- Post-game belief sliders + open-ended strategy questions
- Demographics (age, gender, party, education)
- Debrief explaining the twist

**Randomization:** 3 difficulty conditions (easy/medium/hard) varying S-curve halfMax, competition steepness K, and noise.

**What to test before launching:**
1. Preview the survey — play through all 10 rounds to confirm the game works within Qualtrics
2. Check that the Next button is hidden during the game and reappears after round 10
3. Verify embedded data is being saved (check a test response's data export)
4. The game uses vanilla JS with no external deps, so it should work fine in the Qualtrics frame

**Questions for you:**
- The game currently starts with an intro/start button inside the question. Should that be a separate Qualtrics page instead?
- Do you want a Prolific completion redirect URL added?
- Should the difficulty conditions also vary number of rounds (e.g., 8 vs 10 vs 12)?
