# 11 Pilot 3 design

## Revision after discussion (BenBen, 2026-11-08): what runs

- **Kept:** the 6 GREEN questions about the average Republican, before and after the chat.
- **Dropped:** the sure-thing option (back to a standard two-armed bandit) and the dollar forecast.
- **Length:** 50 clicks of $1,000 ($50,000 budget; BenBen, 2026-11-09); bonus $50,000 money back → $0, $67,500 → $1.00.
- **Options:** "Ads to Republican homeowners" (on average $1.35 back per $1) vs "Ads to all homeowners" (on average $1.00), both with luck. No Democratic option, no counties, no vote shares.
- **Pay:** $2.00 for 10 minutes as in the earlier pilots (BenBen, 2026-11-08), bonus up to $1.00.
- **Sample:** 30 via the Wharton Behavioral Lab (Prolific panel), more later if needed.
- **Live:** https://twins-allocation-game.onrender.com, app tag `v4.0.0-pilot3` (commit a231960), MongoDB `twins-pilot3`. Live end-to-end test passed 2026-11-08.

The rest of this memo is the original proposal, kept for the record.

## Original proposal: Republican homeowners vs a sure thing (2026-11-07)

Built, tested end to end, **not deployed**. App: `twins/survey-app` (repo lirabenjamin/scrsmg), branch `pilot3-hot-stove`, commit 672bc36. Data would go to MongoDB `twins-pilot3`. Screenshots of every new screen are in `screenshots/`; the design simulation is `simulate.py` (`output/`).

## Flow

| # | Screen | Both conditions? | New in pilot 3 |
|---|---|---|---|
| 1 | Consent, attention checks, party, party strength (Democrats only) | yes | consent bonus line now "up to $1.10" |
| 2 | Cover story: SunCell is deciding whether to advertise to a group it has never targeted, Republican homeowners | yes | rewritten |
| 3 | **Beliefs before the chat**: how the average Republican would rate the 6 GREEN items (1-5), and a forecast of how much $1,000 of ads to Republican homeowners brings back (5¢ if within $100 of the truth) | yes | new |
| 4 | Chat, 5 minutes: Republican persona bot (treatment) or cats-vs-dogs bot (control); same neutral instruction | yes | unchanged |
| 5 | **Beliefs after the chat**: the same 6 GREEN items and forecast | yes | new |
| 6 | Instructions (3 screens) and the 2-question check | yes | rewritten for the new options |
| 7 | Game: 100 clicks of $1,000, each to **Ads to Republican homeowners** (results vary; on average $1.35 back per $1) or **Regular campaign** (always exactly $1,100 back) | yes | new structure |
| 8 | Which option brought back more on average? How did you decide? | yes | rewritten |
| 9 | Demographics, redirect | yes | unchanged |

Bonus: money back maps linearly from $110,000 (every click to the regular campaign) to $135,000 (every click to the Republican option, expected) onto $0-$1.00, clipped, plus up to 2 x 5¢ for accurate forecasts.

## Choices and reasons

1. **One Republican option against a party-neutral sure thing; no Democratic county, no vote shares.** In pilot 2, treated participants punished the Republican county for bad luck (stayed after a bad return 59% vs 82% in control) and forgave the Democratic county (70% vs 55%), and wrote "I went with the democrats" and "I tried to be fair". With no Democratic option there is no ingroup to favor and nothing to split fairly. The label "Republican homeowners" stays: the chat teaches about Republicans, so the game must ask about them.
2. **A known sure option (the "hot stove" design; Denrell & March 2001).** The choice now turns on one belief, whether ads to Republicans beat a known $1,100, which is the belief the chat targets. A pessimist sticks with the sure thing and never finds out the Republican option pays more; this is how stereotypes persist through under-sampling (Denrell 2005), and in marketing terms it is how a segment stays under-served. The truth is stipulated: fewer competitors target Republican homeowners.
3. **GREEN beliefs about Republicans before and after the chat** (the 6 items from our earlier studies). The pre-chat questions put the environment on the table in both conditions, so treated participants have a reason to ask the Republican bot about it without being told to; the post-chat questions check whether the chat moved the belief; the pre-chat answers are a covariate (ANCOVA), which cuts the sample needed. In our earlier studies Democrats underestimated Republicans' environmental concern and the chat corrected part of it.
4. **An incentivized dollar forecast before and after the chat.** It is the most direct measure of the belief that drives the game, framed as part of the business decision and paid for accuracy, which limits cheap talk and demand. Analysis: post-chat forecast ~ condition + pre-chat forecast.
5. **Primary game outcome: share of clicks 1-20 to the Republican option, controlling for the pre-chat forecast.** Early clicks carry the belief; later clicks mostly reflect learning.

## What the simulation says (and does not)

Under the same simulated Democrats as before (belief shift d = 0.5, 100 per condition), the new structure raises power modestly: 0.80 vs 0.77 for clicks 1-10 and 0.78 vs 0.69 for all 100 clicks (`output/power.csv`). The model cannot capture the two larger gains: removing the ingroup and fairness motives that reversed the effect in pilot 2, and the pre-chat covariates (with a pre-post correlation of 0.6, ANCOVA needs about 36% fewer people).

## Risks

- **Demand.** GREEN questions about Republicans, then a Republican bot, then ads to Republicans make the hypothesis guessable. Paying for forecast accuracy and for game earnings limits it; a reviewer will still ask. Dropping the pre-chat GREEN questions removes most of the cue but costs power.
- **Chat content still depends on the participant.** If treated chats rarely reach the environment, the belief will not move.
- **Aversion to Republicans as customers** ("I want nothing to do with those guys") can still hold people back; that is part of what the chat should change.

## Decisions for the discussion

1. Keep the pre-chat GREEN questions (power, topic) or drop them (less demand)?
2. Sure option at $1,100 or $1,200 (more people stick with it, so beliefs matter longer, but fewer try the Republican option at all)?
3. Keep the 5¢ forecast incentive?
4. Run pilot 3 at about 50 per condition (about $400), with go criteria: post-chat forecast and GREEN beliefs higher in treatment, Republican share of clicks 1-20 at least equal, no party or fairness reasons in the open text.
