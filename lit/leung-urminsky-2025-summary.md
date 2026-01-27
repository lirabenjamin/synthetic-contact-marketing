# The Narrow Search Effect and How Broadening Search Promotes Belief Updating

**Authors:** Eugina Leung & Oleg Urminsky  
**Published:** PNAS 2025, Vol. 122, No. 13  
**DOI:** https://doi.org/10.1073/pnas.2408175122

---

## Core Thesis

Search engines optimized for relevance can perpetuate echo chambers by combining with users' biased search behaviors. When people search using directionally narrow terms that reflect their prior beliefs, and algorithms return highly relevant but narrow results, this creates a "narrow search effect" that limits belief updating. Algorithm-based interventions that broaden search results are more effective than user-based interventions at promoting belief updating.

---

## Theoretical Framework

### The Narrow Search Effect

The paper proposes that belief polarization persists through a two-stage process:

1. **Confirmation bias in hypothesis generation**: People formulate search terms reflecting their prior beliefs (e.g., "caffeine health benefits" vs. "caffeine health risks")
2. **Algorithm amplification**: Search engines optimized for relevance return narrow results matching these directional queries, reinforcing existing beliefs rather than exposing users to broader information

This differs from prior work on filter bubbles and echo chambers, which focused on how algorithms target users. Here, the issue originates with user behavior—even without differential targeting, echo chambers persist because users search narrowly.

### Two Types of Confirmation Bias

The authors distinguish between:
- **Confirmation bias in hypothesis generation**: Formulating questions that elicit affirming responses
- **Confirmation bias in selective attention**: Paying more attention to evidence aligning with beliefs

Their work targets the first type, testing whether broadening search results can promote belief updating despite potential selective attention.

---

## Empirical Evidence

### Initial Demonstration: 2020 Election

Google Trends data showed that during the November 2020 election uncertainty period, the Republican vote share in a state predicted whether users searched "Trump win/won" vs. "Biden win/won" (r = 0.53, p < 0.001). Different directionally narrow queries yielded different results, meaning voters in different states received different information aligned with their expectations.

---

## Study Set 1: Prior Beliefs → Search Terms → Belief Updating

### Study 1a (N = 768)
**Design**: Participants rated beliefs on six topics (caffeine health, gas prices, crime rates, nuclear energy, coronavirus impact, bitcoin impact), then generated Google search terms.

**Results**: 
- Search terms were frequently directionally narrow (9-34% across topics)
- Search term direction consistently correlated with prior beliefs:
  - Caffeine: r = 0.13
  - Gas prices: r = 0.23
  - Crime rates: r = 0.13
  - Nuclear energy: r = 0.19
  - Coronavirus: r = 0.24
  - Bitcoin: r = 0.21
  - All p < 0.001

### Study 1b (N = 713)
**Design**: Self-generated health topics. Participants named a food/beverage they were uncertain about, generated a search term, and rated motivations.

**Results**:
- Search term direction correlated with prior beliefs (r = 0.34, p < 0.001)
- Only 8% reported intentionally seeking confirmation
- Effect persisted after excluding confirmation seekers (r = 0.31, p < 0.001)

**Implication**: Narrow search occurs even for personally relevant topics where people genuinely seek information.

### Studies 2a-2f (Total N = 1,658)
**Design**: Random assignment to directionally narrow search terms on Google (e.g., "nuclear energy is good" vs. "nuclear energy is bad") across six topics from Study 1a.

**Results**: Post-search beliefs significantly differed by assigned search term:
- Caffeine: d = 1.08
- Gas prices: d = 0.54
- Crime rates: d = 0.29
- Nuclear energy: d = 1.39
- Coronavirus: d = 0.50
- Bitcoin: d = 0.69
- All p < 0.05

**Posttest control** (N = 251): Showing identical results across all conditions produced no belief differences (p = 0.52), confirming effects stem from actual search result differences, not priming.

### Study 2g (N = 674)
**Design**: Custom search engine interface using Google API. Participants named a food/beverage, generated a search term, but were randomly shown results for either "[food] health benefits" or "[food] health risks."

**Results**:
- Benefits condition → more positive beliefs (M = 4.30 vs. 3.62, d = 1.97, p < 0.001)
- No difference in perceived usefulness/relevance
- Only 11% reported confirmation-seeking; effect persisted after exclusion (d = 1.93)

### Study 3 (N = 774)
**Design**: ChatGPT 3.5 responses to directionally narrow queries across four topics (caffeine, gas prices, crime rates, nuclear energy).

**Results**: 
Despite ChatGPT explicitly acknowledging opposing viewpoints in responses, directionally narrow queries still produced different post-search beliefs:
- Caffeine: d = 0.10
- Gas prices: d = 0.53
- Crime rates: d = 0.53
- Nuclear energy: d = 0.50
- All p < 0.001

**Implication**: AI-assisted search is also subject to the narrow search effect.

### Study 4 (N = 751)
**Design**: Full mediation test. Participants rated caffeine beliefs, generated search terms, then were randomly assigned to either:
- **Spontaneous search**: Use their own search term
- **Broad search**: All use "caffeine health benefits and risks"

**Results**:
- Prior beliefs predicted search term direction (r = 0.22, p < 0.001)
- **Spontaneous condition**: Prior beliefs strongly predicted post-search beliefs (b = 0.64), mediated by search term direction (indirect b = 0.045, 95% CI [0.019, 0.078])
- **Broad condition**: Prior beliefs more weakly predicted post-search beliefs (b = 0.55), not mediated by unused search term
- Interaction: Broad search reduced impact of prior beliefs (b = -0.14, p = 0.029)

**Real-world validation**: Google Adwords data showed 26% of caffeine-related searches (with >1,000 monthly volume) were directionally narrow. Content analysis confirmed these terms generated more directional results than broad searches.

### Study 5 (N = 346)
**Design**: Dutch undergraduates randomly assigned to search "caffeine health benefits" or "caffeine health risks" on Google, then chose between caffeinated or decaffeinated energy drink to take home.

**Results**:
- Benefits condition → more positive beliefs (M = 4.17 vs. 2.92, p < 0.001)
- Benefits condition → more likely to choose caffeinated drink (52% vs. 36%, p < 0.01)
- Post-search beliefs mediated effect on choice (indirect b = -0.56, 95% CI [-0.87, -0.32])

**Implication**: Narrow search affects consequential consumption decisions, not just stated beliefs.

---

## Study Set 2: Testing Interventions

### Study 6 (N = 130)
**Design**: Testing if additional searches help. Half conducted one caffeine search, half conducted two.

**Results**:
- One search: Prior beliefs → final beliefs (r = 0.58, p < 0.001)
- Two searches: Prior beliefs → final beliefs (r = 0.73, p < 0.001)
- No improvement from additional search (z = 1.39, p = 0.08)

**Implication**: People don't spontaneously correct for narrow search by broadening subsequent searches.

### Study 7 (N = 431)
**Design**: 2×2 design testing counterfactual consideration timing:
- Search term: Benefits vs. risks
- Prompt timing: Before search vs. after search
- Prompt asked participants to consider how beliefs might differ with opposite search term

**Results**:
- **After-search prompt** (replication): Benefits > risks (M = 5.16 vs. 3.49, p < 0.001)
- **Before-search prompt**: Effect reduced but not eliminated (M = 4.76 vs. 3.89, p < 0.001)
- Interaction: F(1,427) = 8.13, p < 0.01

**Implication**: Prompting counterfactual thinking helps but doesn't fully eliminate the narrow search effect.

### Study 8a (N = 333)
**Design**: Custom search engine. Participants generated caffeine search terms but were randomly shown results from:
1. Their own term
2. "Caffeine health risks"
3. "Caffeine health benefits"  
4. "Caffeine health risks and benefits"

**Results**:
- Post-search beliefs differed by result type (F(3,329) = 10.19, p < 0.001)
- Broad results → middle beliefs (between benefits and risks conditions)
- **No difference in perceived usefulness or relevance** (ps > 0.38)

**Implication**: Algorithms can modify beliefs by broadening results without reducing perceived quality.

### Study 8b (N = 770)
**Design**: New domain (age and thinking abilities). Custom search engine showing either:
- **Spontaneous**: Results from participant-generated term
- **Broad**: Balanced results on age-thinking relationship

Context: Participants read prompt about debate over younger vs. older leaders and thinking abilities (based on Biden age criticism, but not mentioned to avoid partisanship).

**Results**:
- Broad condition → more positive beliefs about age-thinking relationship (M = 3.88 vs. 3.28, p < 0.001)
- Only 5% reported confirmation-seeking; effect persisted after exclusion
- No difference in usefulness (p = 0.38) or relevance (p = 0.29)

### Study 9a (N = 193)
**Design**: Custom search engine with mixed results strategy:
- **Control**: Top 10 Google results for participant's search term
- **Broadened**: Alternating results from participant's term and "caffeine health risks and benefits"

**Results**:
- Broadened condition → more positive beliefs (M = 4.72 vs. 4.22, p = 0.036)
- No difference in usefulness or relevance (ps < 0.57)

**Implication**: Mixing narrow and broad results is effective.

### Study 9b (N = 793)
**Design**: Custom AI chatbot interface using ChatGPT. Participants generated queries about age-thinking abilities, then received responses from:
- **Narrow**: ChatGPT prompted for "most relevant and accurate answer" (~250 words, bullet points)
- **Broad**: ChatGPT prompted for "balanced viewpoint, pros and cons, multiple perspectives" (~250 words)

**Results**:
- Broad condition → more positive beliefs (M = 3.98 vs. 3.40, p < 0.001)
- Only 7.1% reported confirmation-seeking; effect persisted after exclusion
- No difference in usefulness or relevance (ps > 0.20)

**Implication**: AI chatbots can be designed for broad responses via prompt engineering, promoting belief updating without sacrificing perceived quality.

---

## Additional Studies

### New Bing Study (SI Appendix)
Tested AI-powered Bing (GPT-4) on caffeine health. Found Bing sometimes reformulates narrow queries to broader versions (e.g., "nuclear energy is good" → "nuclear energy pros and cons"), but not consistently. Replicated narrow search effect for caffeine.

### Search Broadly Button Study (N = 101)
84% of participants indicated interest in a "Search Broadly" button feature that would provide broader results (opposite of Google's "I'm Feeling Lucky" button).

---

## Key Mechanisms

### Why Narrow Search Persists

1. **User tendency**: Prior beliefs → directionally narrow search terms
2. **Algorithm optimization**: Relevance-focused algorithms return narrow results matching directional queries
3. **Limited spontaneous correction**: Users don't naturally broaden searches or adjust for narrowness
4. **Belief reinforcement**: Narrow results confirm prior beliefs, preventing updating

### Why Broadening Works

1. **Information exposure**: Provides perspectives users wouldn't have searched for
2. **Receptivity**: People are receptive to broader information when provided (not just selective attention)
3. **No quality trade-off**: Broader results perceived as equally useful and relevant
4. **Genuine information-seeking**: Most people aren't intentionally seeking confirmation

---

## Theoretical Contributions

### Extension of Confirmation Bias Literature

- Distinguishes hypothesis-generation from selective-attention confirmation bias
- Shows hypothesis-generation bias can be addressed by broadening information provision
- Demonstrates that selective-attention bias doesn't override benefits of broader information (for these topic types)

### Beyond Filter Bubbles

- Filter bubble research: Algorithms target different users differently
- This research: Even without targeting, users' search behaviors create echo chambers
- Implication: Algorithmic solutions needed even when platforms don't personalize

### Human-Algorithm Interaction

- People's behavioral biases interact with algorithmic design choices
- Relevance optimization has unintended consequence of amplifying confirmation bias
- Need for "behaviorally informed" algorithm design

---

## Practical Implications

### For Search Engine Design

1. **Default to breadth**: Consider broader search as default rather than requiring users to request it
2. **Mixed results**: Alternate between narrow and broad results
3. **Prompt engineering**: For AI chatbots, design prompts that encourage balanced responses
4. **Search Broadly feature**: Implement explicit user option for broader results (84% interested)

### For Information Provision Tools

1. **AI advantage**: Prompt engineering may be more feasible than algorithm redesign
2. **Hybrid approach**: Combine narrow (relevant) and broad (balanced) information
3. **No relevance trade-off**: Broadening doesn't reduce perceived usefulness

### For Reducing Polarization

1. **Shared factual foundation**: Broader search can create more common ground across different belief holders
2. **Social cohesion**: Reducing belief polarization through better information access
3. **Scalable intervention**: Algorithm changes more scalable than individual-level interventions

---

## Boundary Conditions & Limitations

### When Narrow Search Effect Occurs

The effect requires:
1. Users hold biased beliefs that shape search terms
2. Technology yields different results based on query directionality
3. Users' beliefs are malleable enough to update from information

### When Broadening May Not Help

- **Specific factual queries**: (e.g., "Eiffel Tower opening hours") don't benefit from breadth
- **Misinformation-heavy topics**: (e.g., "Where was Obama born") may expose some users to more misinformation
- **Motivated reasoning contexts**: Politically charged topics may show stronger selective attention
- **Strongly held views**: When people resist updating beliefs

### Unanswered Questions

- **Domain specificity**: Do effects generalize beyond health, finance, and policy topics?
- **Temporal durability**: How long do belief changes persist?
- **Transfer to actual outgroups**: Does broader search transfer to understanding real people vs. just abstract topics?
- **Optimal breadth**: What's the right balance between relevance and breadth?

---

## Methodological Strengths

1. **Multi-platform**: Google, ChatGPT, AI-powered Bing, custom interfaces
2. **Multi-topic**: Health, financial, political, societal domains
3. **Converging evidence**: 21 studies (14 preregistered), N = 9,906
4. **Experimental control**: Custom search engines allow manipulating results while holding search terms constant
5. **Ecological validity**: Google Trends data, real search terms, consequential choices
6. **Mechanism testing**: Mediation analyses, posttest controls
7. **Alternative explanations ruled out**: Priming, demand effects, intentional confirmation-seeking

---

## Relevance to Your Research

### Direct Connections

1. **Political polarization context**: Your work examines how marketers can understand across political divides; this paper shows how search behaviors entrench divisions
2. **AI as intervention**: Both use AI tools to bridge understanding gaps (you: chatbots representing outgroups; them: AI-broadened search)
3. **Belief updating**: Both measure whether interventions improve accuracy and reduce bias
4. **Asymmetry patterns**: Both may find differential effects across groups (they: Democrats vs Republicans learn differently; you: might find similar asymmetries)

### Useful Concepts

1. **Confirmation bias types**: Distinguishing hypothesis-generation from selective-attention helps clarify your mechanisms
2. **Algorithm-based vs user-based interventions**: You're testing a user-based intervention (interacting with AI); this shows algorithm changes are often more effective
3. **Information receptivity**: Their finding that people are receptive to broader info suggests your participants might be receptive to AI insights despite political differences
4. **Perceived quality**: Their finding that broader results don't reduce perceived usefulness/relevance is encouraging for your AI chatbot intervention

### Theoretical Framework You Can Adapt

**Their Logic**:
- Biased search → Narrow results → Limited belief updating
- Broadening results → More balanced information → Better belief updating

**Your Logic Could Be**:
- Biased perceptions of outgroup → Avoidance of outgroup perspectives → Persistent misperceptions
- AI interaction with outgroup perspective → Exposure to actual outgroup views → Reduced misperceptions

### Methodological Insights

1. **Control for genuine information-seeking**: Ask about motivations for interaction; exclude confirmation-seekers in robustness checks
2. **Measure perceived quality**: Assess whether AI interactions are seen as informative/useful
3. **Test mechanisms**: Use mediation to show bot informativeness matters
4. **Domain variation**: Test multiple topics to show generalizability
5. **Asymmetry analysis**: Republicans vs Democrats may differ in how much they update, like their findings

### Potential Discussion Points

1. **Complementary approaches**: Their work shows algorithm changes help; yours shows user-initiated interactions help
2. **Scalability**: Your intervention requires user motivation to interact; theirs can be implemented as default
3. **Transfer question**: Both face questions about whether effects transfer (them: search topics to real understanding; you: AI interactions to real people)
4. **Political context**: Both operate in polarized environment where belief updating is challenging

### Citations to Consider

- Their findings on AI-assisted search (Study 3, 9b) relevant for your AI chatbot design
- Their asymmetry in Democrat vs Republican learning (Study 3, Study 8b) may parallel your findings
- Their discussion of motivated reasoning as boundary condition relevant for your political context
- Their work on confirmation bias in hypothesis generation vs selective attention helps frame your theoretical contribution

---

## Quotable Insights

> "Wide horizons lead the soul to broad ideas; circumscribed horizons engender narrow ideas" - Victor Hugo (quoted in discussion)

> "When information-provision technology not only focuses on relevance but also broadens horizons, individuals will access more thorough and broader information, fostering more broadly informed beliefs and decisions."

> "Search engines have the potential to facilitate social cohesion by providing shared access to broad and diverse perspectives, thereby promoting a common factual understanding among groups with different beliefs."

---

## Bottom Line

Search engines optimized purely for relevance inadvertently create echo chambers by amplifying users' natural tendency toward directionally narrow searches. Algorithm-based interventions that broaden search results effectively promote belief updating across diverse topics without sacrificing perceived relevance. This suggests information technology should be redesigned with behavioral science insights to counter confirmation bias and foster shared factual understanding in polarized societies.
