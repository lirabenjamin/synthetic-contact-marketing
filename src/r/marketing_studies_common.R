# Shared data loading and plot helpers for the three marketing studies
# (political experiment, age experiment, single-round allocation game) plus the pre-post study.
# Used by src/r/jobtalk_bar_figures.R and paper/marketing_brief/brief.qmd.
# Paths are relative to the repo root; set the working directory there before sourcing.

suppressMessages({
  library(tidyverse)
  library(arrow)
  library(effectsize)
  library(patchwork)
})

# Talk palette
cond_colors <- c("Control" = "#95A5A6", "Persona" = "#E9C46A", "Twin" = "#2563EB",
                 "Atypical\ntwin" = "#F97316", "Typical\ntwin" = "#2563EB")
prepost_colors <- c("Pre" = "#AEB6BF", "Post" = "#2C3E50")

likert <- c("Strongly disagree" = 1, "Somewhat disagree" = 2, "Neither agree nor disagree" = 3,
            "Somewhat agree" = 4, "Strongly agree" = 5)
persuasive_levels <- c("Not at all persuasive" = 1, "Slightly persuasive" = 2, "Moderately persuasive" = 3,
                       "Very persuasive" = 4, "Extremely persuasive" = 5)

# ---- Data ------------------------------------------------------------------

# Pre-post (twins1, N = 500)
prepost <- read_parquet("data/processed/analysis_data.parquet") |>
  filter(!is.na(accuracy_pre), !is.na(accuracy_post)) |>
  transmute(pre = -accuracy_pre, post = -accuracy_post)   # accuracy = -|error|

# Political experiment (Democrats predicting Republicans)
pol <- read_parquet("studies/02_experimental/data/processed/analysis_data.parquet") |>
  transmute(cond = recode(as.character(treatment), "GPT Persona" = "Persona", "Digital Twin" = "Twin"),
            error = abs_error, persuasive, green_estimate)

# Age experiment (non-seniors predicting seniors; same rules as studies/03_noah_age/analysis.qmd)
gt <- read_csv("data/processed/ground_truth_twin2k.csv", show_col_types = FALSE)
senior_truth <- gt |> filter(type == "age", group == "65+") |> pull(M)
age <- read_csv(list.files("studies/03_noah_age/data/raw", full.names = TRUE), show_col_types = FALSE)[-(1:2), ] |>
  filter(Finished == "True") |>
  mutate(across(green1:green6, ~ unname(likert[.x])),
         green_estimate = rowMeans(pick(green1:green6)),
         age = as.numeric(age)) |>
  filter(is.na(age) | age < 65, !is.na(green_estimate)) |>
  transmute(cond = recode(condition, control = "Control", persona = "Persona", twin = "Twin"),
            error = abs(green_estimate - senior_truth),
            persuasive = unname(persuasive_levels[persuasive]),
            twin_dist = abs(as.numeric(green_score) - senior_truth),
            green_estimate, twin_green = as.numeric(green_score), twin_id = chatbot_persona_id)

# ---- Helpers ---------------------------------------------------------------

stars <- function(p) case_when(p < .001 ~ "***", p < .01 ~ "**", p < .05 ~ "*", p < .10 ~ "\u2020", TRUE ~ " n.s.")

summarise_cond <- function(df, var, levels) {
  df |>
    filter(cond %in% levels, !is.na({{ var }})) |>
    group_by(cond) |>
    summarise(m = mean({{ var }}), se = sd({{ var }}) / sqrt(n()), n = n(), .groups = "drop") |>
    mutate(cond = factor(cond, levels = levels)) |>
    arrange(cond)
}

# Cohen's d vs. control, signed so that positive = improvement in the plotted direction
contrast_vs_control <- function(df, var, level, higher_is_better) {
  sub <- df |> filter(cond %in% c("Control", level), !is.na({{ var }})) |>
    mutate(cond = factor(cond, levels = c("Control", level)))
  y <- pull(sub, {{ var }})
  d <- cohens_d(y ~ sub$cond)$Cohens_d * if (higher_is_better) -1 else 1
  p <- t.test(y ~ sub$cond)$p.value
  tibble(level = level, label = paste0("d = ", sprintf("%.2f", d), stars(p)))
}

# Bars + SE + value labels + brackets from Control to each comparison condition
# ref = the bar each bracket starts from (default: the first bar, i.e. Control)
cond_bars <- function(summ, contrasts, ylab, title = NULL, subtitle = NULL, ymin = 0, ymax = NULL,
                      digits = 2, ref = levels(summ$cond)[1]) {
  top <- max(summ$m + summ$se)
  ymax <- ymax %||% (top * 1.45)
  step <- 0.09 * (ymax - ymin)
  x_ref <- match(ref, levels(summ$cond))
  brackets <- contrasts |>
    mutate(x_end = match(level, levels(summ$cond)),
           y = top + step * (1.1 + 0.95 * (row_number() - 1)))
  ggplot(summ, aes(x = cond, y = m, fill = cond)) +
    geom_col(width = 0.6) +
    geom_errorbar(aes(ymin = m - se, ymax = m + se), width = 0.15, linewidth = 0.6) +
    geom_text(aes(y = m + se, label = sprintf(paste0("%.", digits, "f"), m)),
              vjust = -0.6, fontface = "bold", size = 5) +
    geom_segment(data = brackets, aes(x = x_ref, xend = x_end, y = y, yend = y), inherit.aes = FALSE) +
    geom_segment(data = brackets, aes(x = x_ref, xend = x_ref, y = y, yend = y - step * 0.25), inherit.aes = FALSE) +
    geom_segment(data = brackets, aes(x = x_end, xend = x_end, y = y, yend = y - step * 0.25), inherit.aes = FALSE) +
    geom_text(data = brackets, aes(x = (x_ref + x_end) / 2, y = y, label = label),
              vjust = -0.5, fontface = "bold", size = 4, inherit.aes = FALSE) +
    scale_fill_manual(values = cond_colors, guide = "none") +
    scale_y_continuous(expand = expansion(mult = c(0, 0))) +
    coord_cartesian(ylim = c(ymin, ymax)) +
    labs(x = NULL, y = ylab, title = title, subtitle = subtitle) +
    theme_minimal(base_size = 15) +
    theme(panel.grid.major.x = element_blank(), panel.grid.minor = element_blank(),
          plot.title = element_text(face = "bold", hjust = 0.5, size = 15),
          plot.subtitle = element_text(color = "grey45", hjust = 0.5, size = 13))
}


err_lab <- "Misperception\n(|error|, lower = better)"
pers_lab <- "Predicted ad persuasiveness (1-5)"
three <- c("Control", "Persona", "Twin")
acc_ymax <- 1.75
acc_contrasts <- function(df) bind_rows(contrast_vs_control(df, error, "Persona", FALSE),
                                        contrast_vs_control(df, error, "Twin", FALSE))
pers_contrasts <- function(df) bind_rows(contrast_vs_control(df, persuasive, "Persona", TRUE),
                                         contrast_vs_control(df, persuasive, "Twin", TRUE))

# Single-round allocation game (Democrats only; src/r/pull_game_data.R)
game <- read_parquet("data/processed/game_single_round.parquet") |>
  mutate(cond = recode(condition, control = "Control", treatment = "Twin"))

# Full stats for one comparison vs. control (for tables)
contrast_stats <- function(df, var, level, higher_is_better) {
  sub <- df |> filter(cond %in% c("Control", level), !is.na({{ var }})) |>
    mutate(cond = factor(cond, levels = c("Control", level)))
  y <- pull(sub, {{ var }})
  sgn <- if (higher_is_better) -1 else 1
  cd <- cohens_d(y ~ sub$cond)
  tt <- t.test(y ~ sub$cond)
  tibble(Comparison = paste(level, "vs. Control"),
         Difference = sgn * -diff(tt$estimate),
         d = sgn * cd$Cohens_d,
         `95% CI` = sprintf("[%.2f, %.2f]", min(sgn * c(cd$CI_low, cd$CI_high)), max(sgn * c(cd$CI_low, cd$CI_high))),
         t = abs(tt$statistic), p = tt$p.value)
}

