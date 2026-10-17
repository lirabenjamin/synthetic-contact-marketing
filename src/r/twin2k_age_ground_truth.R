# Ground truth GREEN by age bracket (and party) from Twin-2K-500 (Toubia et al. 2025).
# Downloads wave-1 scores + labels from Hugging Face, writes data/processed/ground_truth_twin2k.csv.
suppressMessages({library(tidyverse)})

base <- "https://huggingface.co/datasets/LLM-Digital-Twin/Twin-2K-500/resolve/main/raw_data/"
tmp  <- tempfile(); dir.create(tmp)
download.file(paste0(base, "wave%201%20scores.csv"), file.path(tmp, "scores.csv"), quiet = TRUE)
download.file(paste0(base, "wave_1_labels_anonymized.csv"), file.path(tmp, "labels.csv"), quiet = TRUE)

scores <- read_csv(file.path(tmp, "scores.csv"), show_col_types = FALSE) |> select(TWIN_ID, green = score_GREEN)
labels <- read_csv(file.path(tmp, "labels.csv"), show_col_types = FALSE)[-(1:2), ] |>
  transmute(TWIN_ID = as.numeric(TWIN_ID), age_bracket = Q13, party = Q20)

gt <- inner_join(scores, labels, by = "TWIN_ID") |> filter(!is.na(green))
summ <- function(df, grp, type) df |> group_by(group = .data[[grp]]) |>
  summarise(M = mean(green), SD = sd(green), n = n(), .groups = "drop") |> mutate(SE = SD / sqrt(n), type = type)

out <- bind_rows(summ(gt, "age_bracket", "age"), summ(gt, "party", "party"))
write_csv(out, here::here("data/processed/ground_truth_twin2k.csv"))
print(out)
