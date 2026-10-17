# Project Instructions for Claude Code

## Goal
Help implement analysis and writing in a reproducible way.

## Repo Map
- **studies/** - All data collections
  - **01_prepost/** - twins1 (P3263): Pre-post observational study (N=500)
    - **report.qmd** - Main analysis + narrative
  - **02_experimental/** - 3-condition experiment (Twin vs GPT Persona vs Control); raw/ also holds Noah's 2026-04-07 re-export
  - **03_noah_age/** - Noah's age-outgroup study (raw only)
  - **04_noah_race_FAILED/** - Noah's race-outgroup study (failed; raw only)
- **pilots/** - Pilot studies
  - **01_behavioral/** - twins2 (P3306): 3-condition behavioral pilot (failed)
  - **02_green_market_game/** - Green market game pilot
- **src/** - Reusable code
  - **r/** - R scripts for data processing
  - **python/** - Python scripts for data download and processing
- **data/**
  - **raw/** - Immutable raw data (never modify)
  - **processed/** - Cleaned and processed datasets
- **output/**
  - **figures/** - Generated plots and images
  - **tables/** - Generated tables
  - **models/** - Saved model outputs
- **lit/** - Papers and references
- **paper/** - Manuscript drafts

## Rules
- Never modify data/raw.
- Processed data goes in data/processed/.
- Figures and tables go in output/figures/ and output/tables/.
- Prefer adding new scripts in src/ over one-off notebook code.
- Document assumptions in studies/01_prepost/report.qmd.
- Claude can talk to me by editing docs/notes_for_ben.md include upgrades in reverse chronological order (new at top), and tag with date and time.
- Make a makefile to automate the pipeline.
- Dont add lines to legends in figures in ggplot
- Use consistent color schemes across figures.

## Writing Style
- Make sure every paragraph starts with a strong topic sentence
- Use simple concise and straightforward language
- Use active voice
- Never summarize one paper at a time, integrate them to tell a narrative
- When you make a list, make sure you are sorting it in some intelligent way (e.g., chronological, thematic, by importance, etc.)
- Use parallel structure whenever possible

## Project data
- title: Learning from AI Personas: Can marketers learn about consumers across the political divide by interacting with AI
- authors: Lira, Castelo, Toubia, Puntoni
- key findings (within-person N=500, environmental attitudes, May 2026 draft):
  1. **Belief accuracy improves** after a 10-min outgroup chatbot conversation (+0.39 pts on 5-pt GREEN scale, d=0.49); 57% of participants became more accurate.
  2. **Asymmetric updating across parties**: Dems learning about Reps gained much more accuracy (b=0.628, d=0.75) than Reps learning about Dems (b=0.163, d=0.29); interaction p<.001. Tracks the larger Dem→Rep baseline misperception.
  3. **Warmth gains are symmetric**: both parties gained ~3.5–5 pts on the 0–100 thermometer; interaction n.s.
  4. **Dunning–Kruger pattern in Republicans**: Reps gained *confidence* in their outgroup judgments (d=0.30, p<.001) despite learning less than Dems; Dems' confidence unchanged.
  5. **Accuracy→warmth coupling is asymmetric**: in Dems, accuracy gains correlate with warmth gains (r=0.22, p<.001); in Reps, no relationship (r=-0.009, p=.89).
  6. **Even baseline overestimators improved** (31% of 149), ruling out simple regression-to-mean.
  7. **Bot informativeness predicts both outcomes** (accuracy b=0.086, p=.004; warmth b=1.93, p<.001); perceived empathy does not (both p≈.06–.09).
  8. **Engagement/dose mostly doesn't matter**: turn count uncorrelated with outcomes; only Dem word count weakly predicts accuracy gains.
  9. **Political extremism does not moderate** intervention effectiveness despite extreme partisans showing larger baseline bias.
- stage: Pilot data complete; sibling general-science paper (gensci) is more developed (3 studies + behavioral DV + 1-week followup) and currently fielding a preregistered N=1,200 longitudinal replication.
- journal target: Journal of Marketing, JCR

## Paper summarization procedure
Given my goals with this research, can you read each of the pdfs in lit, and generate a detailed summary for each in the lit folder? If there are multiple studies, make sure to explain each. Give this to me as an md file i can download.