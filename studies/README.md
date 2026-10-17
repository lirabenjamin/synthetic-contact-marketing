# Data Collection Registry — Marketing Framing

All data collections for the marketing-framing version of the synthetic contact project.

---

## P3263 — twins1: Marketing Pre-Post (N=500)

| | |
|---|---|
| **P number** | P3263 |
| **Internal name** | Learning from Twins. Pilot 1: Establishing a wedge |
| **Qualtrics** | SV_7V5e1i5581koSwu |
| **Launch** | Dec 17, 2025 |
| **N** | 500 (250D + 250R) |
| **Design** | Within-person pre-post, single condition |
| **Framing** | Marketing (energy-saving home appliances) |
| **DVs** | Accuracy (6-item environmental attitudes), warmth, confidence, marketing slogans |
| **Pay** | $4.00 |
| **IRB** | 853653 |
| **Clean data** | `data/processed/cleaned_data.parquet` (500 obs) |
| **Download** | `src/r/download_qualtrics.R` |
| **Analysis** | `studies/01_prepost/report.qmd` |
| **Status** | Complete. Needs re-download for full N=500. |

---

## P3306 — twins2: 3-Condition Pre-Post with Dictator Game (N≈400) ❌

| | |
|---|---|
| **P number** | P3306 |
| **Internal name** | twins2 - pilot dvs |
| **Qualtrics** | SV_1Bn8JHpeFDRuu5E |
| **Launch** | Feb 17, 2026 |
| **N** | 401 (started at 100, batched up) |
| **Design** | Pre-post, 3 conditions (contact / chat / game), marketing framing |
| **Framing** | Marketing (energy-saving home appliances) |
| **DVs** | Accuracy, warmth, dictator game (0-50 donation to outgroup), marketing slogans |
| **Pay** | $4.00 |
| **IRB** | 860019 |
| **Excludes** | P3263 |
| **Clean data** | `pilots/01_behavioral/analysis_data.parquet` |
| **Download/clean** | `pilots/01_behavioral/00 clean.r` |
| **Analysis** | `pilots/01_behavioral/code.qmd` (main), `pilots/01_behavioral/t3 experiment pilot/code.qmd` (condition comparison) |
| **Status** | **Failed — demand effects.** Pre-measures contaminated between-subjects comparison. |

**Notes:** Counterbalanced design (Block 1 vs Block 2 for pre-interaction beliefs). Dictator game DV added. 7 participants reported to Prolific. The `t3 experiment pilot/` subfolder re-analyzes the same data focusing on condition comparisons (Contact vs. Chat vs. Game).

---

## S2 — Three-Condition Experiment: Twin vs. GPT Persona vs. Control

| | |
|---|---|
| **Qualtrics** | SV_9z4Iunuz8h46IuO |
| **Fielded** | Mar 12, 2026 |
| **N** | 403 finished (443 incl. partials); analysis restricted to Democrats |
| **Design** | Between-subjects, 3 conditions: Digital Twin / GPT Persona / Control (dogs bot); Republican outgroup |
| **DVs** | GREEN beliefs about outgroup (6 items), ad persuasiveness |
| **Raw data** | `studies/02_experimental/data/raw/qualtrics.csv` (403 finished); `qualtrics_reexport_2026-04-07.csv` (Noah's re-export, all 443 + recaptcha columns) |
| **Analysis** | `studies/02_experimental/analysis.qmd` |
| **Status** | Analyzed. Results section not yet written. |

---

## Noah's outgroup extensions (raw only, not analyzed)

| Folder | Outgroup | Status |
|---|---|---|
| `03_noah_age/` | Age | Raw Qualtrics export (Apr 7, 2026). Not analyzed. |
| `04_noah_race_FAILED/` | Race | Failed. Raw export kept for the record. |

---

## Folder Structure Mapping

```
marketing/
├── studies/
│   ├── 01_prepost/                  ← P3263 (twins1) analysis + report
│   │   ├── report.qmd
│   │   └── slides.qmd
│   ├── 02_experimental/             ← S2 three-condition experiment
│   │   ├── analysis.qmd
│   │   └── data/raw/                ← qualtrics.csv + Noah's 04-07 re-export
│   ├── 03_noah_age/                 ← raw only
│   └── 04_noah_race_FAILED/         ← raw only
│
├── pilots/
│   ├── 01_behavioral/               ← P3306 (twins2) — failed pilot
│   └── 02_green_market_game/        ← Green market game pilot
│
├── pilots/01_behavioral/                 ← P3306 (twins2) — failed pilot
│   ├── raw_data.parquet
│   ├── analysis_data.parquet
│   ├── 00 clean.r
│   ├── code.qmd
│   └── t3 experiment pilot/         ← P3306 re-analyzed by condition
│       ├── analysis_data.parquet
│       └── code.qmd
│
├── data/                            ← P3263 (twins1) data
│   ├── raw/qualtrics.parquet
│   └── processed/cleaned_data.parquet
│
└── src/r/                           ← Processing scripts for P3263
```
