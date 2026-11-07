# 10 Investment-game (bandit) pilot (Prolific, Nov 2026)

Pilot of the money-in/money-out investment game (design: `studies/09_bandit_prototype`). Democrats chat for 5 minutes with a Republican persona bot (treatment) or a cats-vs-dogs bot (control), then invest a $100,000 budget $1,000 at a time in Riverton (Republican-leaning, $1.35 back per $1 on average) or Lakewood (Democratic-leaning, $1.00). Bonus maps money back linearly from $100,000 (floor) to $135,000 (optimum) onto $0-$1.00.

- App: `twins/survey-app` (repo lirabenjamin/scrsmg), branch `bandit-game`, tag `v3.0.0-bandit-pilot` (commit 8c58c1f), issue scrsmg#2. Live at https://twins-allocation-game.onrender.com (Render env `DB_NAME=twins-bandit-game`).
- Data: MongoDB database `twins-bandit-game` (`participants`, `screenouts`, `client_errors`; test runs in `testing`). Per participant: `game_seed` (yoked: k-th treated and k-th control share it), `game_investments` (one row per click, money back recomputed server-side), `game_money_back`, `game_bonus`, `game_n_riverton`, `tutorial_check_attempts`, `pilot_better_county`, `pilot_decision_strategy`.
- Prolific study `6aef9994ac7e235b0696943f`, published 2026-11-07, 20 places, $2.00 reward, US Democrats on desktop, excludes the 08 pilot (study `6aee0fb81756ff0fd8a8a934`).
- Bonuses: `node scripts/export-bonuses.mjs` in the app repo recomputes each bonus from the seed and saved clicks.
- Copy: Coedit doc https://coedit-46g3.onrender.com/d/83uSD2Opp25W7mhjNo5v7xxx
