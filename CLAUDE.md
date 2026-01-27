# Project Instructions for Claude Code

## Goal
Help implement analysis and writing in a reproducible way.

## Repo Map
- **analysis/report.qmd** - Main analysis + narrative
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

## Rules
- Never modify data/raw.
- Processed data goes in data/processed/.
- Figures and tables go in output/figures/ and output/tables/.
- Prefer adding new scripts in src/ over one-off notebook code.
- Document assumptions in analysis/report.qmd.
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
- title: Learning from Twins: Can marketers learn about consumers across the political divide by interacting with AI
- abstract
Political polarization poses a fundamental challenge for marketers who must communicate effectively with ideologically diverse consumers. 
  Misperceptions about political outgroups—where partisans hold exaggerated and inaccurate views of those across the political divide—can undermine marketing strategies targeting broad consumer bases. This study tests whether brief interactions with an AI chatbot representing a political outgroup can improve marketers' understanding of that outgroup and reduce affective polarization. 
  Participants interacted with a chatbot prompted to represent their political outgroup and responded to questions about environmental attitudes before and after the interaction. 
  Results demonstrate that chatbot interactions significantly improved both belief accuracy and warmth toward the outgroup. 
  However, these effects were asymmetric: Democrats learning about Republicans showed substantially greater accuracy improvements than Republicans learning about Democrats, though both groups increased warmth at similar rates. 
  Political extremism predicted greater baseline bias and lower warmth but did not moderate the intervention's effectiveness, indicating that both moderate and extreme partisans benefited equally. 
  Bot informativeness predicted better outcomes, while perceived empathy did not. 
  These findings suggest AI-mediated interactions offer a scalable tool for reducing political misperceptions in consumer research, though important questions remain about domain specificity, temporal durability, and how insights from AI interactions transfer to understanding actual outgroup members.
- stage: Pilot
- journal target: Journal of Marketing, JCR

## Paper summarization procedure
Given my goals with this research, can you read each of the pdfs in lit, and generate a detailed summary for each in the lit folder? If there are multiple studies, make sure to explain each. Give this to me as an md file i can download.