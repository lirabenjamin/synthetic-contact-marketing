#!/usr/bin/env Rscript
# ── Green Market Game Pilot: Data Cleaning ───────────────────────────────────
#
# Input:  Qualtrics survey SV_037Z7P2Ns52zaHs
# Output: clean_data.csv / .parquet   (one row per participant)
#         round_data.csv / .parquet   (one row per participant × round)
#
# Run:    Rscript pilots/green-market-game/00_clean.r
# ─────────────────────────────────────────────────────────────────────────────

library(tidyverse)
library(qualtRics)
library(arrow)

# ── 1. Download ──────────────────────────────────────────────────────────────

survey_id <- "SV_037Z7P2Ns52zaHs"

raw <- fetch_survey(
  surveyID = survey_id,
  verbose = TRUE,
  convert = FALSE
)

cat(sprintf("Downloaded %d rows × %d cols\n", nrow(raw), ncol(raw)))

# ── 2. Filter ────────────────────────────────────────────────────────────────

# Drop previews
raw <- raw |> filter(DistributionChannel != "preview")

# Keep only Prolific participants
raw <- raw |>
 filter(
    !is.na(PROLIFIC_PID),
    PROLIFIC_PID != "",
    PROLIFIC_PID != "{{%PROLIFIC_PID%}}"
  )

cat(sprintf("After filtering: %d participants\n", nrow(raw)))

# ── 3. Recode helpers ───────────────────────────────────────────────────────

likert_to_num <- function(x) {
  recode(x,
    "Strongly disagree" = 1,
    "Disagree"          = 2,
    "Somewhat disagree" = 3,
    "Neither agree nor disagree" = 4,
    "Somewhat agree"    = 5,
    "Agree"             = 6,
    "Strongly agree"    = 7,
    .default = NA_real_
  )
}

# ── 4. Participant-level dataset ─────────────────────────────────────────────

d <- raw |>
  transmute(
    id = row_number(),
    prolific_pid = PROLIFIC_PID,
    duration_min = as.numeric(`Duration (in seconds)`) / 60,
    difficulty = factor(difficulty, levels = c("easy", "medium", "hard")),

    # Pre-game beliefs (slider: % who would buy eco products)
    pre_belief_dem = as.numeric(What__strong____strong__of_eac_1...18),
    pre_belief_rep = as.numeric(What__strong____strong__of_eac_2...19),
    pre_pct_R      = as.numeric(If_you_had__strong__100k__stro_1...20),

    # Post-game beliefs
    post_belief_dem = as.numeric(What__strong____strong__of_eac_1...21),
    post_belief_rep = as.numeric(What__strong____strong__of_eac_2...22),
    post_pct_R      = as.numeric(If_you_had__strong__100k__stro_1...23),

    # Open-ended
    strategy_text = What__strong_strategy__strong_,
    learning_text = What_did_you__strong_learn__st,

    # Experience measures (Likert 1–7)
    exp_difficult      = likert_to_num(exp_difficult),
    exp_engaging        = likert_to_num(exp_engaging),
    exp_frustrated      = likert_to_num(exp_frustrated),
    exp_feedback_clear  = likert_to_num(exp_feedback_clear),
    exp_learning        = likert_to_num(exp_learning),
    exp_too_long        = likert_to_num(exp_too_long),

    # Demographics
    age       = as.numeric(What_is_your_age_),
    gender    = Q10,
    party     = Q11,
    education = Q12,

    # Game aggregates (embedded data)
    game_cumulative_revenue = as.numeric(game_cumulative_revenue),
    game_pct_optimal        = as.numeric(game_pct_optimal),
    game_total_pct_R        = as.numeric(game_total_pct_R),
  ) |>
  mutate(
    # Derived measures
    belief_shift_dem = post_belief_dem - pre_belief_dem,
    belief_shift_rep = post_belief_rep - pre_belief_rep,
    alloc_shift      = post_pct_R - pre_pct_R,
    pre_belief_gap   = pre_belief_dem - pre_belief_rep,
    post_belief_gap  = post_belief_dem - post_belief_rep,
    gap_change       = post_belief_gap - pre_belief_gap,

    # Party lean (collapsed)
    party_lean = case_when(
      party %in% c("Strong Democrat", "Lean Democrat") ~ "Democrat",
      party %in% c("Strong Republican", "Lean Republican") ~ "Republican",
      party == "Independent" ~ "Independent",
      TRUE ~ NA_character_
    ),
    party_lean = factor(party_lean, levels = c("Democrat", "Independent", "Republican")),
  )

cat(sprintf("Participant-level: %d rows, %d cols\n", nrow(d), ncol(d)))

# ── 5. Round-level dataset ───────────────────────────────────────────────────

towns <- c("harlan", "williamson", "burlington", "middlesex")
n_rounds <- 8  # rounds 9-10 have data for only 1 person

round_data <- map_dfr(seq_len(nrow(raw)), function(i) {
  row <- raw[i, ]
  map_dfr(1:n_rounds, function(r) {
    allocs <- map_dbl(towns, \(t) {
      col <- paste0("game_round_", r, "_alloc_", t)
      if (col %in% names(row)) as.numeric(row[[col]]) else NA_real_
    })
    revs <- map_dbl(towns, \(t) {
      col <- paste0("game_round_", r, "_rev_", t)
      if (col %in% names(row)) as.numeric(row[[col]]) else NA_real_
    })
    tibble(
      id    = i,
      round = r,
      alloc_harlan     = allocs[1],
      alloc_williamson = allocs[2],
      alloc_burlington = allocs[3],
      alloc_middlesex  = allocs[4],
      rev_harlan       = revs[1],
      rev_williamson   = revs[2],
      rev_burlington   = revs[3],
      rev_middlesex    = revs[4],
      total_rev = as.numeric(row[[paste0("game_round_", r, "_total_rev")]]),
      pct_R     = as.numeric(row[[paste0("game_round_", r, "_pct_R")]]),
    )
  })
}) |>
  left_join(d |> select(id, difficulty, party, party_lean, age, gender), by = "id")

cat(sprintf("Round-level: %d rows (%d participants × %d rounds)\n",
            nrow(round_data), nrow(d), n_rounds))

# ── 6. Save ──────────────────────────────────────────────────────────────────

here <- tryCatch(
  dirname(rstudioapi::getSourceEditorContext()$path),
  error = function(e) {
    # When run from command line
    args <- commandArgs(trailingOnly = FALSE)
    file_arg <- args[grep("--file=", args)]
    if (length(file_arg) > 0) {
      dirname(sub("--file=", "", file_arg))
    } else {
      "."
    }
  }
)

write_csv(d, file.path(here, "clean_data.csv"))
write_parquet(d, file.path(here, "clean_data.parquet"))
write_csv(round_data, file.path(here, "round_data.csv"))
write_parquet(round_data, file.path(here, "round_data.parquet"))

cat(sprintf("Saved to %s\n", here))
cat(sprintf("  clean_data: %d participants\n", nrow(d)))
cat(sprintf("  round_data: %d rows\n", nrow(round_data)))
