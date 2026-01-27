# Main Study Proposal: AI-Mediated Contact for Reducing Political Misperceptions

**Date:** January 15, 2026
**Authors:** Benjamin Lira, Noah Castelo, Olivier Toubia, Stefano Puntoni

## Executive Summary

Building on strong pilot results showing that AI chatbot interactions improve belief accuracy and warmth toward political outgroups, we propose a main study that addresses key limitations and tests alternative explanations. The study will include control conditions to benchmark AI effectiveness, longitudinal follow-up to assess durability, and behavioral measures to test downstream consequences.

---

## Pilot Findings Recap

Our pilot demonstrated that 10-minute conversations with AI chatbots representing political outgroups significantly improved:
- **Belief accuracy**: Participants' estimates of outgroup environmental attitudes became more accurate
- **Outgroup warmth**: Feeling thermometer ratings increased

Key insights:
- Both Democrats and Republicans benefited (though Democrats showed larger accuracy gains)
- Political extremists benefited as much as moderates
- Bot informativeness predicted outcomes; empathy did not
- Effects were immediate but temporal durability is unknown

---

## Main Study Design

### Core Research Question
Can AI-mediated interactions reduce political misperceptions, and how does this approach compare to alternative interventions?

### Design Overview: 4-Condition Between-Subjects Design

**Intervention Condition** (4 levels, run for both D→R and R→D):
1. **AI Chatbot** (replication): 10-minute conversation with Claude (as in pilot)
2. **Google Search**: 10 minutes to search and read about outgroup environmental attitudes
3. **Perspective-Taking**: Standard psychology intervention (write essay from outgroup perspective; Wang et al., 2014)
4. **Neutral Control**: 10-minute conversation with AI about cats and dogs (engagement-matched) (as in Costello et al., 2025.)

**Learner Direction**: Run all conditions for both Democrats learning about Republicans (D→R) and Republicans learning about Democrats (R→D)

**Total:** 8 cells (4 conditions, each run for both directions)

---

## Why These Controls?

### 1. Google Search
- **Tests**: How does AI compare to self-directed information search?
- **Rationale**: Cheapest, most accessible alternative intervention
- **Important caveats**:
  - Information quality and content differs between Google and AI
  - Different effort requirements may lead to different engagement levels
  - Search terms may be biased (e.g., "why do Republicans hate the environment" yields different results than "Republican environmental views"; Leung & Urminsky, 2025)
- **What it tells us**: Not a pure "information-only" control, but a realistic comparison to what people might do on their own

### 2. Perspective-Taking (PT)
- **Tests**: How does AI compare to gold-standard psychology intervention?
- **Rationale**: Established method for reducing intergroup bias (Wang et al., 2014)
- **Implementation**: Participants write essay from outgroup perspective, describing their environmental views and reasoning
- **Mechanism**: Structured empathy exercise without new information provision

### 3. Cats/Dogs Control
- **Tests**: Time on task + engagement with AI interface
- **Rationale**: Controls for repeated measurement, demand characteristics, and AI interaction novelty
- **Mechanism**: Neither information nor empathy about outgroup
- **Precedent**: Costello et al. (conspiracy theory reduction)

### Theoretical Leverage
Comparing across conditions provides insight into effectiveness (though mechanism interpretations are limited by confounds):
- **AI vs. Cats/Dogs**: Does synthetic contact work?
- **AI vs. Google**: Does guided dialogue outperform self-directed search?
- **AI vs. PT**: Does AI compare favorably to established psychology intervention?
- **Google vs. PT**: Which alternative is more effective?

Note: Clean mechanism decomposition is challenging because Google differs from AI in multiple ways (search bias, information content, effort, engagement), not just dialogue vs. no-dialogue

---

## Longitudinal Component

### Follow-Up Timeline
**1-week post-intervention** (conservative; consider 2 weeks in discussion with co-authors)

### Rationale
- Pilot showed immediate effects but no durability data
- Contact theory literature shows decay over time
- Critical for practical recommendations about intervention frequency
- One week is feasible for retention while allowing time for decay

### Follow-Up Measures
- Belief accuracy (re-estimate outgroup attitudes)
- Outgroup warmth (feeling thermometer)
- Confidence in judgments

**Implementation:** Brief (2-3 minutes), no interaction required to minimize attrition

---

## Outcome Measures

### Primary DVs (same as pilot)
1. **Belief Accuracy**: |Perceived - Actual| outgroup environmental attitudes (6-item scale)
2. **Outgroup Warmth**: Feeling thermometer (0-100)

### Secondary DVs (new)

#### 1. Conversation Willingness (Self-Report)
Post-intervention, immediate (two items):
1. "How likely would you be to start a conversation with a [Republican/Democrat] about political issues?" (1-7)
2. "How comfortable would you feel discussing environmental policy with a [Republican/Democrat]?" (1-7)

**Purpose**: Bridge from attitudes to behavioral intentions (multiple items for reliability)

#### 2. Partner Preference (Revealed Preference)
Post-intervention, immediate:
- "If given the opportunity for a brief conversation about current events, who would you prefer to speak with?"
  - [ ] A Democrat
  - [ ] A Republican
  - [ ] No preference

**Purpose**: Behaviorally anchored measure of openness to outgroup contact

**Framing**: Hypothetical (to avoid false expectations and protect follow-up retention) but captures genuine preference

### Why These DVs?
- **Theoretical**: Tests whether learning translates to engagement willingness (contact theory prediction)
- **General science fit**: More universal than marketing slogans
- **Mechanism insight**: Do all interventions increase warmth, but only AI increases engagement readiness?

---

## Sample and Power

### Proposed Sample Size
- **250 per cell × 8 cells = 2,000 total**
- Pilot had N = 500 for simple design; scaling proportionally for 4× conditions
- Adequate power for:
  - Main effects of condition
  - Contrasts between specific conditions
  - Condition × Direction interactions
  - Mediation analyses (accuracy/warmth → behavioral DVs)

### Recruitment
- Qualtrics panels (as in pilot)
- Prescreened partisans (political orientation <25 or >75 on 0-100 scale)
- Balanced recruitment across all cells

### Ground Truth
Collect fresh ground truth from participants' own attitudes within the study (rather than relying on pilot data):
- Democrats' green_own = ground truth about Democrats
- Republicans' green_own = ground truth about Republicans

**Advantages**: Larger sample, no temporal mismatch, cleaner for reviewers

---

## Procedure

### Phase 1: Baseline (5 minutes)
1. Own environmental attitudes (6 items, 1-5 scale)
2. Estimate Democrat and Republican environmental attitudes (same 6 items)
3. Warmth toward Democrats and Republicans (feeling thermometer)
4. Confidence in outgroup judgments (1-5 scale)

### Phase 2: Intervention (10 minutes)
**Randomly assigned to one of four conditions:**

**A. AI Chatbot**
- Converse with Claude Sonnet prompted as outgroup member
- Discuss environmental attitudes
- Same prompting as pilot

**B. Google Search**
- "You have 10 minutes to use Google to learn about [Democrat/Republican] environmental attitudes"
- Open-ended search, self-directed
- Record search queries and clicked links (for process data)

**C. Perspective-Taking**
- "Take the perspective of a typical [Democrat/Republican]"
- Write essay describing their environmental views and reasoning
- Standard PT instructions following Wang et al. (2014)

**D. Cats/Dogs Control**
- Converse with Claude about cats and dogs
- Same interface, same duration
- No political content

### Phase 3: Post-Intervention (5 minutes)
1. Re-estimate outgroup environmental attitudes (same 6 items)
2. Re-rate outgroup warmth (feeling thermometer)
3. Confidence in post-intervention judgments (1-5)
4. Bot informativeness and empathy ratings (AI and Control conditions only)
5. Conversation willingness (2 items, 1-7 scale)
6. Partner preference (forced choice + no preference)

### Phase 4: Follow-Up (1 week later, 2-3 minutes)
1. Re-estimate outgroup environmental attitudes
2. Re-rate outgroup warmth
3. Confidence in judgments
4. (Optional) Conversation willingness again to test durability

---

## Analysis Plan

### Primary Analyses (Pre-Registered)

**H1: Main Effect of AI vs. Control**
- Mixed-effects: DV ~ Time × Condition + (1|ID)
- Focus: AI vs. Cats/Dogs control
- Expected: AI > Control for accuracy and warmth

**H2: AI vs. Alternative Interventions**
- Contrasts: AI vs. Google, AI vs. PT, Google vs. PT
- Expected: AI ≥ alternatives (exploratory on ordering)

**H3: Durability**
- Test Time 2 (pre) vs. Time 3 (1-week follow-up)
- Expected: Partial decay but sustained effects

**H4: Behavioral Intentions**
- Does intervention condition predict conversation willingness and partner preference?
- Mediation: Accuracy/Warmth → Willingness

### Secondary Analyses (Exploratory)

**Condition Comparisons**
- Pairwise comparisons: AI vs. Google, AI vs. PT, Google vs. PT
- Note: Mechanism interpretation is limited because conditions differ in multiple dimensions (not just single mechanism manipulation)
- Focus on effectiveness comparisons rather than clean mechanism decomposition

**Direction Asymmetry**
- Replicate pilot finding (D→R vs. R→D)
- Does asymmetry persist across conditions, or is it AI-specific?

**Process Measures**
- For Google condition: Do search queries predict outcomes?
- For AI/Control conditions: Do informativeness/empathy ratings replicate pilot?

---

## Why Environmental Attitudes?

### Retain from Pilot (Don't Change Domain)
- Working paradigm with clear effects
- Ground truth available within-sample
- Partisan divide exists but not maximal (room for learning)
- Relevant to marketing (green products, CSR messaging)

### Generalizability Concerns (for Discussion)
- Acknowledge domain-specificity as limitation
- Propose future studies on other domains (immigration, healthcare)
- Asymmetry likely domain-specific (not generalizable finding about Dems vs. Reps)

---

## Marketing Slogans: Keep or Drop?

### Pilot Included
Participants wrote slogans for energy-saving appliances targeting outgroup

### Decision: Make Secondary or Drop

**Option A: Keep as exploratory secondary analysis**
- Test whether intervention improves slogan quality (rated by outgroup members or LLM)
- Relevant for JM/JCR positioning
- Demonstrates applied downstream consequence

**Option B: Drop entirely**
- Focus on general science angle (contact theory, polarization reduction)
- Conversation willingness/partner preference are cleaner secondary DVs
- Avoids complications of defining/rating "good" marketing

**Recommendation:** Keep but treat as purely exploratory (not pre-registered, not in main text unless significant)

---

## Timeline and Next Steps

### Before Data Collection
1. **Power analysis**: Confirm 50/cell is adequate for planned contrasts
2. **Pre-registration**: Register on AsPredicted or OSF
3. **IRB approval**: Update protocol with new conditions and follow-up
4. **Materials development**:
   - Google search instructions
   - PT essay prompt
   - Cats/dogs chatbot prompt
   - Follow-up survey flow

### Data Collection
- **Wave 1**: Main study (N = 400)
- **Wave 2**: 1-week follow-up (expect ~80% retention = 320)

### Analysis and Writing
- Preregistered confirmatory analyses
- Exploratory analyses (mechanism, process data)
- Draft for submission to general science journal or top-tier marketing

---

## Discussion Points for Co-Authors

1. **Sample size**: Is 250/cell (2,000 total) the right target? This scales from pilot's N=500 for simpler design.

2. **Real human conversation condition**: Should we add a 5th condition where participants actually speak with a real cross-party human?
   - **Pros**:
     - Most direct test of AI vs. human contact
     - Addresses potential reviewer concern about ecological validity
     - Tests whether AI-mediated learning transfers to human interactions
   - **Cons**:
     - Expensive and logistically complex (recruiting, scheduling, moderation)
     - High attrition risk (people may not show up for scheduled conversations)
     - Ethical considerations (preventing hostile interactions)
     - Longer timeline (coordination required)
   - **Options**:
     - Include now as 5th condition (fewer per cell, or larger N)
     - Save for Study 3 (focused comparison of AI vs. human contact)
     - Don't include (argue AI scalability is the value proposition)

3. **Follow-up timing**: 1 week vs. 2 weeks vs. both (1 week + 1 month)?

4. **Venue strategy**:
   - General science (Science, PNAS) → emphasize contact theory, polarization reduction
   - Marketing (JM, JCR) → emphasize consumer insights, applied implications
   - Psychology (PSPB, JPSP) → emphasize mechanism, intervention comparison

5. **Marketing slogans**: Keep as secondary or drop entirely?

6. **Budget**: Estimate costs for 2,000-person main study + follow-up (+ potential human conversation condition)

7. **Timeline**: Realistic data collection window?

---

## Key Strengths of This Design

1. **Addresses major pilot limitations**: Adds controls, temporal data, behavioral measures
2. **Mechanism insight**: Disentangles information vs. empathy through condition comparison
3. **Benchmarking**: Tests AI against gold-standard (PT) and practical alternative (Google)
4. **Theoretical contribution**: Extends contact theory to AI-mediated interactions
5. **Practical value**: Informs when/whether organizations should use AI for bridging divides
6. **Replication**: Core AI condition replicates pilot in larger, more diverse sample

---

## Questions?

Contact: Benjamin Lira (blira@wharton.upenn.edu)

---

## References

Leung, E., & Urminsky, O. (2025). How search engine algorithms shape consumer beliefs. *Journal of Marketing Research* (forthcoming).

Wang, C. S., Kenneth, T., Ku, G., & Galinsky, A. D. (2014). Perspective-taking increases willingness to engage in intergroup contact. *PLoS ONE, 9*(1), e85681.
