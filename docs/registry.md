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
| **Analysis** | `analysis/report.qmd` |
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
| **Clean data** | `t2 new dv pilot/analysis_data.parquet` |
| **Download/clean** | `t2 new dv pilot/00 clean.r` |
| **Analysis** | `t2 new dv pilot/code.qmd` (main), `t2 new dv pilot/t3 experiment pilot/code.qmd` (condition comparison) |
| **Status** | **Failed — demand effects.** Pre-measures contaminated between-subjects comparison. |

**Notes:** Counterbalanced design (Block 1 vs Block 2 for pre-interaction beliefs). Dictator game DV added. 7 participants reported to Prolific. The `t3 experiment pilot/` subfolder re-analyzes the same data focusing on condition comparisons (Contact vs. Chat vs. Game).

---

## Folder Structure Mapping

```
marketing/
├── data/                           ← P3263 (twins1) data
│   ├── raw/qualtrics.parquet         (211 obs — NEEDS RE-DOWNLOAD for 500)
│   └── processed/cleaned_data.parquet
│
├── t2 new dv pilot/                ← P3306 (twins2) data
│   ├── raw_data.parquet
│   ├── analysis_data.parquet
│   ├── 00 clean.r
│   ├── code.qmd
│   └── t3 experiment pilot/        ← P3306 re-analyzed by condition
│       ├── analysis_data.parquet
│       └── code.qmd
│
├── analysis/report.qmd             ← Main P3263 analysis
├── src/r/                          ← Processing scripts for P3263
└── t4 full/                        ← Planned full marketing study (N=2000)
    └── pre-registration.md
```
