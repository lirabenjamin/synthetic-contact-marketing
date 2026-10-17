# Figures for Part 2 (marketing) of the BU job talk and for paper/marketing_brief.
# One effect per figure; every bar chart has the same size and style.
#   prepost_accuracy.png            pre-post study: misperception before vs. after the chat
#   s1_political_accuracy.png       Study 1: misperception of Republicans by condition
#   s1_political_persuasiveness.png Study 1: predicted ad persuasiveness by condition
#   s2_age_gap.png                  Study 2: actual vs. perceived senior GREEN vs. twin bots
#   s2_age_accuracy.png             Study 2: misperception of seniors by condition
#   s2_age_persuasiveness.png       Study 2: predicted ad persuasiveness by condition
#   s2_prototypicality.png          Study 2: typical vs. atypical twins
#   s3_allocation.png               Study 3: % budget to Republican markets
#   belief_vs_ad_rating.png         Studies 1-2: estimated outgroup GREEN vs. ad rating
# Accuracy is plotted as misperception = |estimate - truth| (lower = better) so bars start at 0.
# Effect sizes: paired d_z for pre-post; pooled-SD Cohen's d vs. control for between-subjects.
# Run from the repo root: Rscript src/r/jobtalk_bar_figures.R

source("src/r/marketing_studies_common.R")

out_dir <- "output/figures/jobtalk"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

save_fig <- function(p, file, width = 8, height = 5.5) {
  ggsave(file.path(out_dir, file), p, width = width, height = height, dpi = 256, bg = "white")
}

sig_note <- "Error bars = SE  |  † p < .10, * p < .05, ** p < .01, *** p < .001"
finish <- function(p) {
  p + labs(caption = sig_note) +
    theme(plot.caption = element_text(color = "grey45", hjust = 0.5, size = 11))
}

# ---- Pre-post study --------------------------------------------------------

pp_summ <- tibble(cond = factor(c("Pre", "Post"), levels = c("Pre", "Post")),
                  m = c(mean(prepost$pre), mean(prepost$post)),
                  se = c(sd(prepost$pre), sd(prepost$post)) / sqrt(nrow(prepost)),
                  n = c(nrow(prepost), 0))
diffs <- prepost$pre - prepost$post
pp_contrast <- tibble(level = "Post",
                      label = paste0("d = ", sprintf("%.2f", mean(diffs) / sd(diffs)), stars(t.test(diffs)$p.value)))
p_prepost <- finish(cond_bars(pp_summ, pp_contrast, ylab = err_lab, ymax = acc_ymax,
                              subtitle = "Same participants before and after the chat") +
                      scale_fill_manual(values = prepost_colors, guide = "none"))
save_fig(p_prepost, "prepost_accuracy.png")

# ---- Study 1: political ----------------------------------------------------

pol_acc <- summarise_cond(pol, error, three)
pol_pers <- summarise_cond(pol, persuasive, three)
p_pol_acc <- finish(cond_bars(pol_acc, acc_contrasts(pol), ylab = err_lab, ymax = acc_ymax,
                              subtitle = "Democrats predicting Republicans"))
p_pol_pers <- finish(cond_bars(pol_pers, pers_contrasts(pol), ylab = pers_lab, ymin = 1, ymax = 5,
                               subtitle = "How persuasive would Republicans find the ad?"))
save_fig(p_pol_acc, "s1_political_accuracy.png")
save_fig(p_pol_pers, "s1_political_persuasiveness.png")

# ---- Study 2: age ----------------------------------------------------------

age_acc <- summarise_cond(age, error, three)
age_pers <- summarise_cond(age, persuasive, three)
p_age_acc <- finish(cond_bars(age_acc, acc_contrasts(age), ylab = err_lab, ymax = acc_ymax,
                              subtitle = "Adults under 65 predicting seniors"))
p_age_pers <- finish(cond_bars(age_pers, pers_contrasts(age), ylab = pers_lab, ymin = 1, ymax = 5,
                               subtitle = "How persuasive would seniors find the ad?"))
save_fig(p_age_acc, "s2_age_accuracy.png")
save_fig(p_age_pers, "s2_age_persuasiveness.png")

# Misperception gap. Actual = Twin-2K-500 respondents 65+; Perceived = control participants;
# Twin bots = GREEN of the distinct senior twins participants talked to.
senior_gt <- gt |> filter(type == "age", group == "65+")
perceived <- age |> filter(cond == "Control") |> pull(green_estimate)
bots <- age |> filter(cond == "Twin", !is.na(twin_green)) |> distinct(twin_id, twin_green) |> pull(twin_green)
gap_levels <- c("Actual seniors", "Perceived\n(control group)", "Senior twin bots")
gap <- tibble(cond = factor(gap_levels, levels = gap_levels),
              m  = c(senior_gt$M, mean(perceived), mean(bots)),
              se = c(senior_gt$SE, sd(perceived) / sqrt(length(perceived)), sd(bots) / sqrt(length(bots))),
              n  = c(senior_gt$n, length(perceived), length(bots)))
gap_t <- t.test(perceived, mu = senior_gt$M)
gap_label <- paste0("d = ", sprintf("%.2f", (senior_gt$M - mean(perceived)) / senior_gt$SD), stars(gap_t$p.value))
p_gap <- finish(
  cond_bars(gap, tibble(level = gap_levels[1], label = gap_label), ref = gap_levels[2],
            ylab = "Pro-environmental attitudes\n(GREEN, 1-5)", ymin = 1, ymax = 5,
            subtitle = "d = gap between perceived and actual, in actual-senior SDs") +
    scale_fill_manual(values = setNames(c("#2C3E50", "#95A5A6", "#2563EB"), gap_levels), guide = "none"))
save_fig(p_gap, "s2_age_gap.png")

# Prototypicality: median split on the twin's distance from the true senior mean
proto <- age |>
  filter(cond == "Control" | (cond == "Twin" & !is.na(twin_dist))) |>
  mutate(cond = case_when(cond == "Control" ~ "Control",
                          twin_dist <= median(twin_dist, na.rm = TRUE) ~ "Typical\ntwin",
                          TRUE ~ "Atypical\ntwin"))
proto_levels <- c("Control", "Atypical\ntwin", "Typical\ntwin")
proto_summ <- summarise_cond(proto, error, proto_levels)
p_proto <- finish(cond_bars(proto_summ,
                            bind_rows(contrast_vs_control(proto, error, proto_levels[2], FALSE),
                                      contrast_vs_control(proto, error, proto_levels[3], FALSE)),
                            ylab = err_lab, ymax = acc_ymax,
                            subtitle = "Median split on the twin's distance from the senior mean"))
save_fig(p_proto, "s2_prototypicality.png")

# ---- Study 3: allocation game ----------------------------------------------

game_summ <- summarise_cond(game, pct_R, c("Control", "Twin"))
p_game <- finish(cond_bars(game_summ, contrast_vs_control(game, pct_R, "Twin", TRUE),
                           ylab = "% budget to Republican markets", ymax = 100, digits = 1,
                           subtitle = "Democrats splitting a $100,000 budget"))
save_fig(p_game, "s3_allocation.png")

# ---- Belief vs. ad rating (Studies 1-2) ------------------------------------
# Ad ratings track how green participants think the outgroup is.

belief_df <- bind_rows(
  pol |> mutate(study = "Democrats rating Republicans",
                truth = gt$M[gt$type == "party" & gt$group == "Republican"]),
  age |> mutate(study = "Under-65s rating seniors", truth = senior_truth)
) |>
  filter(!is.na(persuasive), !is.na(green_estimate)) |>
  mutate(study = fct_inorder(study), cond = factor(cond, levels = three))

belief_r <- belief_df |>
  group_by(study) |>
  summarise(r = cor(green_estimate, persuasive), n = n(), p = cor.test(green_estimate, persuasive)$p.value,
            .groups = "drop") |>
  mutate(label = paste0("r = ", sprintf("%.2f", r), stars(p)))
belief_means <- belief_df |>
  group_by(study, cond) |>
  summarise(green_estimate = mean(green_estimate), persuasive = mean(persuasive), .groups = "drop")

p_belief <- ggplot(belief_df, aes(x = green_estimate, y = persuasive)) +
  geom_vline(aes(xintercept = truth), linetype = "dashed", color = "grey50") +
  geom_jitter(aes(color = cond), width = 0.04, height = 0.18, alpha = 0.45, size = 1.8) +
  geom_smooth(method = "lm", formula = y ~ x, color = "black", fill = "grey70", linewidth = 0.9, show.legend = FALSE) +
  geom_point(data = belief_means, aes(fill = cond), shape = 21, size = 5.5, stroke = 1.2, color = "black") +
  geom_text(data = belief_r, aes(x = 1, y = 5.45, label = label), hjust = 0, fontface = "bold", size = 4.5) +
  geom_text(data = distinct(belief_df, study, truth), aes(x = truth, y = 0.7, label = "True mean"),
            hjust = 1.05, color = "grey40", size = 3.8) +
  facet_wrap(~ study) +
  scale_color_manual(values = cond_colors, name = NULL) +
  scale_fill_manual(values = cond_colors, guide = "none") +
  scale_x_continuous(breaks = 1:5) +
  scale_y_continuous(breaks = 1:5) +
  coord_cartesian(xlim = c(0.9, 5.1), ylim = c(0.6, 5.6)) +
  guides(color = guide_legend(override.aes = list(alpha = 1, size = 4))) +
  labs(x = "Estimated outgroup GREEN (1-5)", y = pers_lab,
       subtitle = "Small dots = participants (jittered) | Large dots = condition means | Line = linear fit") +
  theme_minimal(base_size = 15) +
  theme(legend.position = "bottom", panel.grid.minor = element_blank(),
        strip.text = element_text(face = "bold", size = 14),
        plot.subtitle = element_text(color = "grey45", hjust = 0.5, size = 12))
save_fig(p_belief, "belief_vs_ad_rating.png", width = 12, height = 6)

# Numbers for checking against the slide text
bind_rows(pp_summ |> mutate(fig = "pre-post"),
          pol_acc |> mutate(fig = "political accuracy"), pol_pers |> mutate(fig = "political persuasiveness"),
          age_acc |> mutate(fig = "age accuracy"), age_pers |> mutate(fig = "age persuasiveness"),
          gap |> mutate(fig = "age gap"), proto_summ |> mutate(fig = "prototypicality"),
          game_summ |> mutate(fig = "allocation")) |>
  mutate(cond = str_replace(as.character(cond), "\n", " ")) |>
  print(n = Inf)
