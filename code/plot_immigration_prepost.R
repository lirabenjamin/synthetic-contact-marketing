library(tidyverse)
library(arrow)
library(patchwork)

# ── Helpers ──────────────────────────────────────────────────────────────────
cohens_d_paired <- function(pre, post) {
  diff <- post - pre
  mean(diff, na.rm = TRUE) / sd(diff, na.rm = TRUE)
}

p_stars <- function(p) {
  if (p < .001) return("***")
  if (p < .01)  return("**")
  if (p < .05)  return("*")
  return("")
}

palette <- c("D_to_R" = "#1660CE", "R_to_D" = "#CC0000")
party_labels <- c(
  "D_to_R" = "Democrats learning\nabout Republicans",
  "R_to_D" = "Republicans learning\nabout Democrats"
)

# ── Load & prep ──────────────────────────────────────────────────────────────
d <- read_parquet("data/raw/immigration_qualtrics.parquet") |>
  mutate(
    warmth_pre     = as.numeric(warmth_pre_1),
    warmth_post    = as.numeric(warmth_post_1),
    willing_pre_n  = as.numeric(willing_pre) - 5,
    willing_post_n = as.numeric(willing_post) - 5,
    recaptcha      = as.numeric(Q_RecaptchaScore),
    learner_party  = case_when(
      self_party == "Closer to the Democratic Party"  ~ "D_to_R",
      self_party == "Closer to the Republican Party"  ~ "R_to_D"
    )
  ) |>
  filter(recaptcha >= 0.5 | is.na(recaptcha))

cat("N =", nrow(d), "\n")

# ── Plot function ────────────────────────────────────────────────────────────
make_prepost_plot <- function(data, pre_col, post_col, y_label, y_limits) {
  # Per-group summaries
  summ <- data |>
    group_by(learner_party) |>
    summarise(
      pre_m   = mean(.data[[pre_col]],  na.rm = TRUE),
      pre_se  = sd(.data[[pre_col]],    na.rm = TRUE) / sqrt(n()),
      post_m  = mean(.data[[post_col]], na.rm = TRUE),
      post_se = sd(.data[[post_col]],   na.rm = TRUE) / sqrt(n()),
      .groups = "drop"
    ) |>
    pivot_longer(
      cols = c(pre_m, post_m, pre_se, post_se),
      names_to  = c("time", ".value"),
      names_pattern = "^(pre|post)_(m|se)$"
    ) |>
    mutate(time = factor(time, levels = c("pre", "post"), labels = c("Pre", "Post")))

  # Overall summary
  summ_all <- data |>
    summarise(
      pre_m   = mean(.data[[pre_col]],  na.rm = TRUE),
      pre_se  = sd(.data[[pre_col]],    na.rm = TRUE) / sqrt(n()),
      post_m  = mean(.data[[post_col]], na.rm = TRUE),
      post_se = sd(.data[[post_col]],   na.rm = TRUE) / sqrt(n())
    ) |>
    pivot_longer(
      cols = everything(),
      names_to  = c("time", ".value"),
      names_pattern = "^(pre|post)_(m|se)$"
    ) |>
    mutate(
      time = factor(time, levels = c("pre", "post"), labels = c("Pre", "Post")),
      learner_party = "Overall"
    )

  # Annotations
  d_overall   <- cohens_d_paired(data[[pre_col]], data[[post_col]])
  tt_overall  <- t.test(data[[post_col]], data[[pre_col]], paired = TRUE)
  p_overall   <- tt_overall$p.value
  pct_overall <- (mean(data[[post_col]], na.rm = TRUE) - mean(data[[pre_col]], na.rm = TRUE)) /
                   mean(data[[pre_col]], na.rm = TRUE) * 100
  overall_pre  <- mean(data[[pre_col]], na.rm = TRUE)
  overall_post <- mean(data[[post_col]], na.rm = TRUE)

  ann <- data |>
    group_by(learner_party) |>
    summarise(
      pre_m   = mean(.data[[pre_col]],  na.rm = TRUE),
      post_m  = mean(.data[[post_col]], na.rm = TRUE),
      d       = cohens_d_paired(.data[[pre_col]], .data[[post_col]]),
      p_val   = t.test(.data[[post_col]], .data[[pre_col]], paired = TRUE)$p.value,
      pct_chg = (mean(.data[[post_col]], na.rm = TRUE) - mean(.data[[pre_col]], na.rm = TRUE)) /
                  mean(.data[[pre_col]], na.rm = TRUE) * 100,
      .groups = "drop"
    ) |>
    mutate(
      stars = sapply(p_val, p_stars),
      label = sprintf("d=%.2f%s %+.0f%%", d, stars, pct_chg)
    )

  ann_dtor <- ann |> filter(learner_party == "D_to_R")
  ann_rtod <- ann |> filter(learner_party == "R_to_D")

  y_range      <- diff(y_limits)
  x_data_range <- 1.6

  ann_on_line <- data.frame(
    x = 1.5,
    y = c(
      (ann_dtor$pre_m + ann_dtor$post_m) / 2,
      (overall_pre + overall_post) / 2,
      (ann_rtod$pre_m + ann_rtod$post_m) / 2
    ),
    label = c(
      ann_dtor$label,
      sprintf("d=%.2f%s %+.0f%%", d_overall, p_stars(p_overall), pct_overall),
      ann_rtod$label
    ),
    color_val = c(palette[["D_to_R"]], "grey50", palette[["R_to_D"]]),
    angle = c(
      atan2((ann_dtor$post_m - ann_dtor$pre_m) / y_range, 1 / x_data_range) * 180 / pi,
      atan2((overall_post - overall_pre) / y_range, 1 / x_data_range) * 180 / pi,
      atan2((ann_rtod$post_m - ann_rtod$pre_m) / y_range, 1 / x_data_range) * 180 / pi
    ),
    stringsAsFactors = FALSE
  )

  palette_full <- c(palette, "Overall" = "grey50")
  labels_full  <- c(party_labels, "Overall" = "Overall")

  ggplot(summ, aes(x = time, y = m, color = learner_party, group = learner_party)) +
    geom_line(data = summ_all,
              aes(x = time, y = m, color = learner_party, group = learner_party),
              inherit.aes = FALSE, linewidth = 1.2, linetype = "dashed") +
    geom_point(data = summ_all,
               aes(x = time, y = m, color = learner_party),
               inherit.aes = FALSE, size = 3, shape = 18) +
    geom_errorbar(data = summ_all,
                  aes(x = time, ymin = m - se, ymax = m + se, color = learner_party),
                  inherit.aes = FALSE, width = 0.08, linewidth = 0.6) +
    geom_line(linewidth = 0.8) +
    geom_point(size = 2.5) +
    geom_errorbar(aes(ymin = m - se, ymax = m + se), width = 0.08, linewidth = 0.6) +
    geom_text(data = ann_on_line,
              aes(x = x, y = y, label = label),
              inherit.aes = FALSE, hjust = 0.5, vjust = -0.5, size = 2.8,
              color = ann_on_line$color_val, angle = ann_on_line$angle) +
    scale_color_manual(values = palette_full, labels = labels_full) +
    scale_x_discrete(expand = expansion(add = c(0.3, 0.3))) +
    scale_y_continuous(limits = y_limits) +
    labs(x = NULL, y = y_label, color = NULL) +
    theme(legend.position = "bottom", panel.grid.minor = element_blank(),
          legend.text = element_text(size = 9))
}

# ── Create plots ─────────────────────────────────────────────────────────────
p_warmth  <- make_prepost_plot(d, "warmth_pre", "warmth_post",
                               "Outgroup warmth (0\u2013100)", c(0, 50))
p_willing <- make_prepost_plot(d, "willing_pre_n", "willing_post_n",
                               "Willingness to interact (\u22125 to +5)", c(-1, 5))

p_combined <- (p_warmth + p_willing) +
  plot_layout(guides = "collect") &
  theme(legend.position = "bottom")

# Save
dir.create("output/figures", recursive = TRUE, showWarnings = FALSE)
ggsave("output/figures/immigration_warmth_willing_prepost.pdf", p_combined,
       width = 7, height = 3.5, device = cairo_pdf)
ggsave("output/figures/immigration_warmth_willing_prepost.png", p_combined,
       width = 7, height = 3.5, dpi = 300)
cat("Saved to output/figures/immigration_warmth_willing_prepost.pdf & .png\n")
