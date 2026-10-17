#!/usr/bin/env Rscript
# ── Green Market Game Pilot: Exploratory Data Analysis ───────────────────────
#
# Input:  clean_data.parquet, round_data.parquet
# Output: eda/ subfolder with diagnostic plots
#
# Run:    Rscript pilots/green-market-game/01_eda.r
# ─────────────────────────────────────────────────────────────────────────────

library(tidyverse)
library(arrow)
library(patchwork)
library(corrplot)

here <- tryCatch(
  dirname(rstudioapi::getSourceEditorContext()$path),
  error = function(e) {
    args <- commandArgs(trailingOnly = FALSE)
    file_arg <- args[grep("--file=", args)]
    if (length(file_arg) > 0) dirname(sub("--file=", "", file_arg)) else "."
  }
)

d <- read_parquet(file.path(here, "clean_data.parquet"))
rounds <- read_parquet(file.path(here, "round_data.parquet"))

eda_dir <- file.path(here, "eda")
dir.create(eda_dir, showWarnings = FALSE)

theme_set(
  theme_minimal(base_size = 12) +
    theme(panel.grid.minor = element_blank())
)

DIFF_COLORS <- c(easy = "#22c55e", medium = "#f59e0b", hard = "#ef4444")

# ── 1. Numeric variable distributions ───────────────────────────────────────

num_vars <- d |>
  select(where(is.numeric), -id) |>
  select(-starts_with("game_"))

png(file.path(eda_dir, "histograms.png"), width = 1400, height = 1000, res = 150)
num_vars |>
  pivot_longer(everything(), names_to = "variable", values_to = "value") |>
  ggplot(aes(x = value)) +
  geom_histogram(bins = 25, fill = "steelblue", alpha = 0.7) +
  facet_wrap(~variable, scales = "free", ncol = 4) +
  labs(title = "Distributions of all numeric variables")
dev.off()

# ── 2. Correlation matrix (key DVs) ─────────────────────────────────────────

cor_vars <- d |>
  select(
    pre_belief_dem, pre_belief_rep, pre_pct_R,
    post_belief_dem, post_belief_rep, post_pct_R,
    belief_shift_dem, belief_shift_rep, alloc_shift,
    pre_belief_gap, gap_change,
    exp_difficult, exp_engaging, exp_frustrated,
    exp_feedback_clear, exp_learning, exp_too_long,
    age, duration_min,
    game_cumulative_revenue, game_pct_optimal
  ) |>
  drop_na()

cor_mat <- cor(cor_vars)

png(file.path(eda_dir, "correlation_matrix_full.png"), width = 1200, height = 1200, res = 150)
corrplot(cor_mat, method = "color", type = "lower", tl.cex = 0.6,
         addCoef.col = "black", number.cex = 0.45,
         title = "Full correlation matrix", mar = c(0, 0, 2, 0))
dev.off()

# Sub-matrix: beliefs only
belief_vars <- d |>
  select(pre_belief_dem, pre_belief_rep, pre_pct_R,
         post_belief_dem, post_belief_rep, post_pct_R,
         belief_shift_dem, belief_shift_rep, alloc_shift,
         pre_belief_gap, gap_change) |>
  drop_na()

png(file.path(eda_dir, "correlation_matrix_beliefs.png"), width = 900, height = 900, res = 150)
corrplot(cor(belief_vars), method = "color", type = "lower", tl.cex = 0.7,
         addCoef.col = "black", number.cex = 0.5,
         title = "Belief measures correlation", mar = c(0, 0, 2, 0))
dev.off()

# Sub-matrix: experience only
exp_vars <- d |>
  select(starts_with("exp_")) |>
  drop_na()

png(file.path(eda_dir, "correlation_matrix_experience.png"), width = 700, height = 700, res = 150)
corrplot(cor(exp_vars), method = "color", type = "lower", tl.cex = 0.8,
         addCoef.col = "black", number.cex = 0.6,
         title = "Experience measures correlation", mar = c(0, 0, 2, 0))
dev.off()

# ── 3. Outlier checks ───────────────────────────────────────────────────────

outlier_vars <- d |>
  select(alloc_shift, belief_shift_rep, belief_shift_dem, gap_change,
         duration_min, age, game_cumulative_revenue)

png(file.path(eda_dir, "outlier_boxplots.png"), width = 1200, height = 600, res = 150)
outlier_vars |>
  pivot_longer(everything(), names_to = "variable", values_to = "value") |>
  ggplot(aes(x = variable, y = value)) +
  geom_boxplot(fill = "steelblue", alpha = 0.5) +
  geom_jitter(width = 0.15, alpha = 0.3, size = 1) +
  facet_wrap(~variable, scales = "free", ncol = 4) +
  labs(title = "Outlier diagnostics") +
  theme(axis.text.x = element_blank())
dev.off()

# Duration by difficulty
png(file.path(eda_dir, "duration_by_difficulty.png"), width = 700, height = 400, res = 150)
d |>
  ggplot(aes(x = difficulty, y = duration_min, fill = difficulty)) +
  geom_boxplot(alpha = 0.7) +
  geom_jitter(width = 0.15, alpha = 0.3) +
  scale_fill_manual(values = DIFF_COLORS, guide = "none") +
  labs(title = "Survey duration by difficulty", y = "Duration (min)")
dev.off()

# ── 4. Key DVs by condition ─────────────────────────────────────────────────

png(file.path(eda_dir, "alloc_shift_by_condition.png"), width = 800, height = 400, res = 150)
d |>
  ggplot(aes(x = difficulty, y = alloc_shift, fill = difficulty)) +
  geom_boxplot(alpha = 0.7, width = 0.6) +
  geom_jitter(width = 0.15, alpha = 0.4, size = 1.5) +
  geom_hline(yintercept = 0, linetype = "dashed") +
  scale_fill_manual(values = DIFF_COLORS, guide = "none") +
  labs(title = "Allocation shift (pre→post % to R-markets) by difficulty",
       y = "Shift (pp)")
dev.off()

png(file.path(eda_dir, "belief_shift_by_condition.png"), width = 900, height = 400, res = 150)
d |>
  select(id, difficulty, belief_shift_dem, belief_shift_rep) |>
  pivot_longer(starts_with("belief"), names_to = "target", values_to = "shift") |>
  mutate(target = ifelse(str_detect(target, "dem"), "Dem belief", "Rep belief")) |>
  ggplot(aes(x = difficulty, y = shift, fill = difficulty)) +
  geom_boxplot(alpha = 0.7) +
  geom_jitter(width = 0.15, alpha = 0.3, size = 1) +
  geom_hline(yintercept = 0, linetype = "dashed") +
  facet_wrap(~target) +
  scale_fill_manual(values = DIFF_COLORS, guide = "none") +
  labs(title = "Belief shift by difficulty", y = "Shift (pp)")
dev.off()

# ── 5. Party distribution ───────────────────────────────────────────────────

png(file.path(eda_dir, "party_distribution.png"), width = 800, height = 400, res = 150)
d |>
  count(difficulty, party) |>
  ggplot(aes(x = party, y = n, fill = difficulty)) +
  geom_col(position = "dodge", alpha = 0.8) +
  scale_fill_manual(values = DIFF_COLORS) +
  labs(title = "Party distribution by condition", y = "Count") +
  theme(axis.text.x = element_text(angle = 20, hjust = 1))
dev.off()

# ── 6. Round-level revenue curves ───────────────────────────────────────────

png(file.path(eda_dir, "revenue_curves.png"), width = 800, height = 400, res = 150)
rounds |>
  group_by(difficulty, round) |>
  summarize(mean_rev = mean(total_rev, na.rm = TRUE),
            se = sd(total_rev, na.rm = TRUE) / sqrt(n()),
            .groups = "drop") |>
  ggplot(aes(x = round, y = mean_rev / 1000, color = difficulty)) +
  geom_line(linewidth = 1.2) +
  geom_point(size = 2) +
  geom_ribbon(aes(ymin = (mean_rev - 1.96 * se) / 1000,
                  ymax = (mean_rev + 1.96 * se) / 1000, fill = difficulty),
              alpha = 0.1, color = NA) +
  scale_color_manual(values = DIFF_COLORS) +
  scale_fill_manual(values = DIFF_COLORS) +
  scale_x_continuous(breaks = 1:8) +
  labs(title = "Revenue learning curves", x = "Round", y = "Mean revenue ($k)")
dev.off()

# ── 7. pct_R curves by round ────────────────────────────────────────────────

png(file.path(eda_dir, "pct_R_curves.png"), width = 800, height = 400, res = 150)
rounds |>
  group_by(difficulty, round) |>
  summarize(mean_pct_R = mean(pct_R, na.rm = TRUE),
            se = sd(pct_R, na.rm = TRUE) / sqrt(n()),
            .groups = "drop") |>
  ggplot(aes(x = round, y = mean_pct_R, color = difficulty)) +
  geom_line(linewidth = 1.2) +
  geom_point(size = 2) +
  geom_hline(yintercept = 50, linetype = "dashed", color = "grey50") +
  scale_color_manual(values = DIFF_COLORS) +
  scale_x_continuous(breaks = 1:8) +
  scale_y_continuous(limits = c(0, 100)) +
  labs(title = "% allocated to R-leaning markets by round",
       x = "Round", y = "% to R-markets")
dev.off()

cat(sprintf("EDA complete. %d plots saved to %s/\n",
            length(list.files(eda_dir, pattern = "\\.png$")), eda_dir))
