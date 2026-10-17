# Histogram of GREEN scores in Twin-2K-500 (Toubia et al. 2025), overall and by the paper's age split (under 65 vs. 65+).
# Y axis = percentage of twins within each panel.
# Writes output/figures/twin2k_green_hist.{png,pdf} and twin2k_green_density_65plus.{png,pdf}.
suppressMessages({library(tidyverse); library(patchwork)})

base <- "https://huggingface.co/datasets/LLM-Digital-Twin/Twin-2K-500/resolve/main/raw_data/"
tmp  <- tempfile(); dir.create(tmp)
download.file(paste0(base, "wave%201%20scores.csv"), file.path(tmp, "scores.csv"), quiet = TRUE)
download.file(paste0(base, "wave_1_labels_anonymized.csv"), file.path(tmp, "labels.csv"), quiet = TRUE)

scores <- read_csv(file.path(tmp, "scores.csv"), show_col_types = FALSE) |> select(TWIN_ID, green = score_GREEN)
labels <- read_csv(file.path(tmp, "labels.csv"), show_col_types = FALSE)[-(1:2), ] |>
  transmute(TWIN_ID = as.numeric(TWIN_ID), age = if_else(Q13 == "65+", "65+", "Under 65"))
gt <- left_join(scores, labels, by = "TWIN_ID") |> filter(!is.na(green))

age_colors <- c("Under 65" = "#93C5FD", "65+" = "#1E3A8A")

p_all <- ggplot(gt, aes(green, y = after_stat(density * width))) +
  geom_histogram(binwidth = 1/6, center = 1, fill = "grey40", color = "white") +
  geom_vline(xintercept = mean(gt$green), linetype = "dashed") +
  labs(title = sprintf("All twins (N = %d)", nrow(gt)),
       subtitle = sprintf("M = %.2f, SD = %.2f", mean(gt$green), sd(gt$green)),
       x = "GREEN score (1–5)", y = "% of twins")

by_age <- gt |> filter(!is.na(age)) |> mutate(age = factor(age, levels = names(age_colors)))
age_stats <- by_age |> group_by(age) |> summarise(M = mean(green), SD = sd(green), n = n())
p_age <- ggplot(by_age, aes(green, y = after_stat(density * width), fill = age)) +
  geom_histogram(binwidth = 1/6, center = 1, color = "white") +
  geom_vline(data = age_stats, aes(xintercept = M), linetype = "dashed") +
  facet_wrap(~ age, ncol = 1,
             labeller = as_labeller(setNames(sprintf("%s (n = %d, M = %.2f, SD = %.2f)",
                                                     age_stats$age, age_stats$n, age_stats$M, age_stats$SD),
                                             age_stats$age))) +
  scale_fill_manual(values = age_colors, guide = "none") +
  labs(title = "By age", x = "GREEN score (1–5)", y = "% of twins")

p <- (p_all | p_age) & theme_minimal(base_size = 12) & scale_x_continuous(breaks = 1:5) &
  scale_y_continuous(breaks = seq(0, 0.12, 0.02), labels = scales::label_percent(accuracy = 1))
for (ext in c("png", "pdf")) ggsave(here::here(paste0("output/figures/twin2k_green_hist.", ext)), p, width = 11, height = 5, dpi = 200, device = if (ext == "pdf") cairo_pdf else NULL)
print(age_stats)
cat("Distinct GREEN values:", n_distinct(gt$green), "\n")
# Density of GREEN for twins aged 65+ only (the Study 2 outgroup)
olds <- by_age |> filter(age == "65+")
p_olds <- ggplot(olds, aes(green)) +
  geom_density(fill = age_colors[["65+"]], color = NA, alpha = 0.8) +
  geom_vline(xintercept = mean(olds$green), linetype = "dashed") +
  scale_x_continuous(breaks = 1:5, limits = c(1, 5)) +
  labs(title = sprintf("Twins aged 65+ (n = %d)", nrow(olds)),
       subtitle = sprintf("M = %.2f, SD = %.2f", mean(olds$green), sd(olds$green)),
       x = "GREEN score (1–5)", y = "Density") +
  theme_minimal(base_size = 12)
for (ext in c("png", "pdf")) ggsave(here::here(paste0("output/figures/twin2k_green_density_65plus.", ext)), p_olds, width = 10, height = 3.5, dpi = 200, device = if (ext == "pdf") cairo_pdf else NULL)
