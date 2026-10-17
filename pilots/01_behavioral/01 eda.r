# =============================================================================
# 01 eda.r — Exploratory Data Analysis for T2 New DV Pilot
# =============================================================================

library(arrow)
library(dplyr)
library(tidyr)
library(ggplot2)
library(corrplot)
library(patchwork)

# --- Load data ---
dat <- read_parquet("t2 new dv pilot/analysis_data.parquet")

# --- Create output directory ---
eda_path <- "t2 new dv pilot/eda/"
dir.create(eda_path, recursive = TRUE, showWarnings = FALSE)

# --- Color scheme ---
party_colors <- c("D→R" = "#2166AC", "R→D" = "#B2182B")

# =============================================================================
# 1. Sample descriptives
# =============================================================================
cat("=== SAMPLE DESCRIPTIVES ===\n")
cat("N:", nrow(dat), "\n")
cat("\nParty:\n"); print(table(dat$learner_party))
cat("\nBlock:\n"); print(table(dat$block))
cat("\nGender:\n"); print(table(dat$gender))
cat("\nAge:\n"); print(summary(dat$age))
cat("\nDuration (seconds):\n"); print(summary(dat$duration_sec))

# =============================================================================
# 2. Histograms for all numeric variables
# =============================================================================
numeric_vars <- dat %>%
  select(where(is.numeric)) %>%
  select(-starts_with("race_"), -matches("ResponseId|PROLIFIC"))

# Key variables to plot
key_vars <- c(
  "green_own", "green_ingroup", "green_outgroup_pre", "green_outgroup_post",
  "accuracy_pre", "accuracy_post",
  "warmth_outgroup_pre", "warmth_outgroup_post",
  "warmth_ingroup_pre", "warmth_ingroup_post",
  "warmth_diff_pre", "warmth_diff_post",
  "confidence_ingroup", "confidence_outgroup_pre", "confidence_outgroup_post",
  "donation", "political_extremism",
  "age", "duration_sec"
)

plots <- list()
for (v in key_vars) {
  if (v %in% names(dat)) {
    plots[[v]] <- ggplot(dat, aes(x = .data[[v]])) +
      geom_histogram(bins = 15, fill = "steelblue", color = "white", alpha = 0.8) +
      labs(title = v, x = NULL, y = "Count") +
      theme_minimal(base_size = 10)
  }
}

p_hist <- wrap_plots(plots, ncol = 4)
ggsave(paste0(eda_path, "histograms.png"), p_hist, width = 16, height = 16, dpi = 150)
cat("\nSaved: histograms.png\n")

# =============================================================================
# 3. Histograms by party
# =============================================================================
key_by_party <- c(
  "green_own", "green_outgroup_pre", "green_outgroup_post",
  "accuracy_pre", "accuracy_post",
  "warmth_outgroup_pre", "warmth_outgroup_post",
  "donation", "political_extremism"
)

plots_party <- list()
for (v in key_by_party) {
  if (v %in% names(dat)) {
    plots_party[[v]] <- ggplot(dat, aes(x = .data[[v]], fill = learner_party)) +
      geom_histogram(bins = 12, alpha = 0.7, position = "identity") +
      scale_fill_manual(values = party_colors) +
      labs(title = v, x = NULL, y = "Count") +
      theme_minimal(base_size = 10) +
      theme(legend.position = "none")
  }
}

p_hist_party <- wrap_plots(plots_party, ncol = 3)
ggsave(paste0(eda_path, "histograms_by_party.png"), p_hist_party, width = 14, height = 12, dpi = 150)
cat("Saved: histograms_by_party.png\n")

# =============================================================================
# 4. Correlation matrix — main variables
# =============================================================================
cor_vars <- dat %>%
  select(
    green_own, green_ingroup, green_outgroup_pre, green_outgroup_post,
    accuracy_pre, accuracy_post,
    warmth_outgroup_pre, warmth_outgroup_post,
    warmth_ingroup_pre, warmth_ingroup_post,
    confidence_outgroup_pre, confidence_outgroup_post,
    donation, political_extremism, age
  ) %>%
  select(where(~ sum(!is.na(.x)) > 5))

cor_mat <- cor(cor_vars, use = "pairwise.complete.obs")

png(paste0(eda_path, "correlation_matrix.png"), width = 1200, height = 1000, res = 120)
corrplot(cor_mat, method = "color", type = "lower",
         addCoef.col = "black", number.cex = 0.6, tl.cex = 0.7,
         title = "Correlation Matrix — Key Variables", mar = c(0, 0, 2, 0))
dev.off()
cat("Saved: correlation_matrix.png\n")

# --- Sub-matrix: pre-post DVs ---
dv_vars <- dat %>%
  select(
    accuracy_pre, accuracy_post,
    warmth_outgroup_pre, warmth_outgroup_post,
    warmth_diff_pre, warmth_diff_post,
    confidence_outgroup_pre, confidence_outgroup_post,
    donation
  )

cor_dv <- cor(dv_vars, use = "pairwise.complete.obs")
png(paste0(eda_path, "correlation_dvs.png"), width = 900, height = 800, res = 120)
corrplot(cor_dv, method = "color", type = "lower",
         addCoef.col = "black", number.cex = 0.7, tl.cex = 0.8,
         title = "Correlation Matrix — DVs", mar = c(0, 0, 2, 0))
dev.off()
cat("Saved: correlation_dvs.png\n")

# =============================================================================
# 4b. Baseline accuracy–warmth correlation
# =============================================================================
cat("\n=== BASELINE ACCURACY–WARMTH CORRELATION ===\n")

# Overall
cor_aw <- cor.test(dat$accuracy_pre, dat$warmth_outgroup_pre, use = "complete.obs")
cat(sprintf("  Overall: r = %.3f, p = %.4f\n", cor_aw$estimate, cor_aw$p.value))

# By party
for (party in c("D→R", "R→D")) {
  sub <- dat %>% filter(learner_party == party)
  ct <- cor.test(sub$accuracy_pre, sub$warmth_outgroup_pre, use = "complete.obs")
  cat(sprintf("  %s: r = %.3f, p = %.4f (n = %d)\n", party, ct$estimate, ct$p.value, nrow(sub)))
}

# Scatterplot
p_baseline_cor <- ggplot(dat, aes(x = accuracy_pre, y = warmth_outgroup_pre, color = learner_party)) +
  geom_point(alpha = 0.6, size = 2.5) +
  geom_smooth(method = "lm", se = TRUE, alpha = 0.15) +
  geom_smooth(aes(group = 1), method = "lm", se = TRUE, alpha = 0.1,
              color = "gray50", linetype = "dashed") +
  scale_color_manual(values = party_colors) +
  labs(
    title = "Baseline Accuracy vs. Outgroup Warmth",
    subtitle = sprintf("Overall r = %.2f, p %s",
                       cor_aw$estimate,
                       ifelse(cor_aw$p.value < .001, "< .001",
                              sprintf("= %.3f", cor_aw$p.value))),
    x = "Baseline Accuracy (neg. abs. error)",
    y = "Baseline Outgroup Warmth (0-100)",
    color = NULL
  ) +
  theme_minimal(base_size = 12) +
  theme(legend.position = "bottom")

ggsave(paste0(eda_path, "baseline_accuracy_warmth.png"), p_baseline_cor,
       width = 7, height = 6, dpi = 150)
cat("Saved: baseline_accuracy_warmth.png\n")

# =============================================================================
# 5. Pre-post paired comparisons
# =============================================================================

# Accuracy pre vs post
p_acc <- dat %>%
  select(ResponseId, learner_party, accuracy_pre, accuracy_post) %>%
  pivot_longer(c(accuracy_pre, accuracy_post), names_to = "time", values_to = "accuracy") %>%
  mutate(time = factor(time, levels = c("accuracy_pre", "accuracy_post"), labels = c("Pre", "Post"))) %>%
  ggplot(aes(x = time, y = accuracy, group = ResponseId, color = learner_party)) +
  geom_line(alpha = 0.4) +
  geom_point(alpha = 0.6) +
  stat_summary(aes(group = learner_party), fun = mean, geom = "line", linewidth = 1.5) +
  stat_summary(aes(group = learner_party), fun = mean, geom = "point", size = 3) +
  scale_color_manual(values = party_colors) +
  labs(title = "Accuracy (Pre vs Post)", y = "Accuracy (neg. abs. error)", x = NULL, color = NULL) +
  theme_minimal(base_size = 12)

# Warmth pre vs post
p_warm <- dat %>%
  select(ResponseId, learner_party, warmth_outgroup_pre, warmth_outgroup_post) %>%
  pivot_longer(c(warmth_outgroup_pre, warmth_outgroup_post), names_to = "time", values_to = "warmth") %>%
  mutate(time = factor(time, levels = c("warmth_outgroup_pre", "warmth_outgroup_post"), labels = c("Pre", "Post"))) %>%
  ggplot(aes(x = time, y = warmth, group = ResponseId, color = learner_party)) +
  geom_line(alpha = 0.4) +
  geom_point(alpha = 0.6) +
  stat_summary(aes(group = learner_party), fun = mean, geom = "line", linewidth = 1.5) +
  stat_summary(aes(group = learner_party), fun = mean, geom = "point", size = 3) +
  scale_color_manual(values = party_colors) +
  labs(title = "Outgroup Warmth (Pre vs Post)", y = "Warmth (0-100)", x = NULL, color = NULL) +
  theme_minimal(base_size = 12)

# Confidence pre vs post
p_conf <- dat %>%
  select(ResponseId, learner_party, confidence_outgroup_pre, confidence_outgroup_post) %>%
  pivot_longer(c(confidence_outgroup_pre, confidence_outgroup_post), names_to = "time", values_to = "confidence") %>%
  mutate(time = factor(time, levels = c("confidence_outgroup_pre", "confidence_outgroup_post"), labels = c("Pre", "Post"))) %>%
  ggplot(aes(x = time, y = confidence, group = ResponseId, color = learner_party)) +
  geom_line(alpha = 0.4) +
  geom_point(alpha = 0.6) +
  stat_summary(aes(group = learner_party), fun = mean, geom = "line", linewidth = 1.5) +
  stat_summary(aes(group = learner_party), fun = mean, geom = "point", size = 3) +
  scale_color_manual(values = party_colors) +
  labs(title = "Outgroup Confidence (Pre vs Post)", y = "Confidence (1-5)", x = NULL, color = NULL) +
  theme_minimal(base_size = 12)

p_prepost <- p_acc + p_warm + p_conf + plot_layout(ncol = 3, guides = "collect") &
  theme(legend.position = "bottom")
ggsave(paste0(eda_path, "prepost_spaghetti.png"), p_prepost, width = 16, height = 6, dpi = 150)
cat("Saved: prepost_spaghetti.png\n")

# =============================================================================
# 6. Donation distribution by party
# =============================================================================
p_donation <- ggplot(dat, aes(x = learner_party, y = donation, fill = learner_party)) +
  geom_boxplot(alpha = 0.7, width = 0.5) +
  geom_jitter(width = 0.15, alpha = 0.5, size = 2) +
  scale_fill_manual(values = party_colors) +
  labs(title = "Dictator Game Donation by Party", y = "Donation ($)", x = NULL) +
  theme_minimal(base_size = 12) +
  theme(legend.position = "none")

ggsave(paste0(eda_path, "donation_by_party.png"), p_donation, width = 6, height = 5, dpi = 150)
cat("Saved: donation_by_party.png\n")

# =============================================================================
# 7. Outlier check
# =============================================================================
cat("\n=== OUTLIER CHECK ===\n")
outlier_vars <- c("accuracy_pre", "accuracy_post", "warmth_outgroup_pre", "warmth_outgroup_post",
                   "donation", "duration_sec", "political_extremism")
for (v in outlier_vars) {
  x <- dat[[v]]
  if (is.numeric(x)) {
    q <- quantile(x, c(0.25, 0.75), na.rm = TRUE)
    iqr <- q[2] - q[1]
    lower <- q[1] - 1.5 * iqr
    upper <- q[2] + 1.5 * iqr
    n_out <- sum(x < lower | x > upper, na.rm = TRUE)
    cat(sprintf("  %s: %d outliers (IQR method)\n", v, n_out))
  }
}

# =============================================================================
# 8. Missing data check
# =============================================================================
cat("\n=== MISSING DATA ===\n")
missing <- colSums(is.na(dat))
missing_nonzero <- missing[missing > 0]
if (length(missing_nonzero) > 0) {
  print(sort(missing_nonzero, decreasing = TRUE))
} else {
  cat("  No missing data in analysis variables.\n")
}

cat("\n=== EDA COMPLETE ===\n")
