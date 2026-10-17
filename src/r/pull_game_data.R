# Pull the single-round allocation game (Apr 3, 2026) from MongoDB and cache it.
# Output: data/processed/game_single_round.parquet (one row per participant)
# The multi-round pilot (Mar 24-26, 8 rounds) is excluded: same app, different game.
# Run from the repo root: Rscript src/r/pull_game_data.R

suppressMessages({
  library(tidyverse)
  library(mongolite)
  library(arrow)
})

dotenv::load_dot_env(".env")
con <- mongo(collection = "participants", db = "synthetic-contact", url = Sys.getenv("MONGODB_URI"))
raw <- con$find("{}")
con$disconnect()

game <- raw |>
  filter(!is.na(completed_at), !str_starts(prolific_pid, "test_")) |>
  mutate(n_rounds = map_int(game_rounds, ~ if (is.data.frame(.x)) nrow(.x) else 0L)) |>
  filter(n_rounds == 1) |>
  mutate(r1 = map(game_rounds, ~ .x[1, ])) |>
  unnest_wider(r1, names_sep = "_") |>
  transmute(
    submission_id, condition, party, extremity, age, gender, education, race,
    chat_minutes = chatbot_duration_ms / 60000,
    alloc_harlan = r1_alloc_harlan, alloc_williamson = r1_alloc_williamson,
    alloc_burlington = r1_alloc_burlington, alloc_middlesex = r1_alloc_middlesex,
    pct_R = game_total_pct_R, revenue = game_cumulative_revenue,
    pct_optimal = game_pct_optimal, bonus = game_bonus,
    completed_at = as.character(completed_at)
  )

write_parquet(game, "data/processed/game_single_round.parquet")
cat("Saved", nrow(game), "participants:\n")
print(count(game, condition, party))
