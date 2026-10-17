# Learning from Twins: Can Marketers Learn About Consumers Across the Political Divide by Interacting with AI?

## Overview

This study tests whether interacting with AI chatbots prompted to represent political outgroups can improve marketers' understanding of those outgroups and reduce affective polarization. Participants (N=211) engaged with chatbots representing their political outgroup, then reported their beliefs about outgroup attitudes and created marketing messages targeted at the outgroup.

## Project Structure

```
.
├── studies/
│   ├── 01_prepost/             # twins1 (P3263): Pre-post study (N=500)
│   │   ├── report.qmd          # Main analysis + narrative
│   │   └── slides.qmd          # Presentation slides
│   └── 02_experimental/        # Marketing experiment
├── pilots/
│   ├── 01_behavioral/          # twins2 (P3306): 3-condition behavioral pilot (failed)
│   └── 02_green_market_game/   # Green market game pilot
├── data/
│   ├── raw/                    # Immutable raw data
│   └── processed/              # Cleaned and processed datasets
├── src/
│   ├── r/                      # R scripts for data processing
│   └── python/                 # Python scripts for data download
├── output/
│   ├── figures/                # Generated plots
│   └── tables/                 # Generated tables
├── paper/                      # Manuscript drafts
├── lit/                        # Papers and references
└── Makefile                    # Reproducible pipeline
```

## Quick Start

### Run the entire pipeline

```bash
make all
```

This will:
1. Clean the raw data
2. Download conversation data
3. Create analysis datasets
4. Analyze extreme cases
5. Generate HTML and PDF reports

### View available commands

```bash
make help
```

### Individual steps

```bash
make data              # Process data only
make analysis          # Create analysis datasets
make report-html       # Generate HTML report only (faster)
make report-pdf        # Generate PDF report only
make clean             # Remove all processed data and outputs
```

### Development workflow

For rapid iteration during analysis:

```bash
make dev               # Quick HTML-only render
```

## Requirements

### R packages
- tidyverse
- arrow
- lme4
- lmerTest
- modelsummary
- gt
- ggplot2
- ggpubr
- patchwork
- jsonlite

### Python packages
- pandas
- pyarrow
- psycopg2-binary
- python-dotenv

### Other
- Quarto (for rendering reports)
- Make (for running the pipeline)

## Reproducibility

All analyses are fully reproducible:

1. **Raw data**: `data/raw/qualtrics.parquet` (immutable)
2. **Data processing**: `src/r/clean_data.R`
3. **Conversation download**: `src/python/download_conversations.py`
4. **Analysis**: `studies/01_prepost/report.qmd`
5. **Publication dataset**: `data/processed/analysis_data.{parquet,csv}`

Run `make all` to reproduce the entire analysis from raw data to final report.

## Pre-registration

This study was pre-registered prior to data collection. See `docs/pre-registration.md` for complete details.

## Citation

(Citation information to be added upon publication)

## License

(License information to be added)
