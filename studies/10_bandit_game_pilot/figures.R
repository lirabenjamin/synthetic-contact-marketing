# Diagnostic figures for the investment-game (bandit) pilot.
# Run from this folder after pull_data.py:  Rscript figures.R   (writes output/figures/*.png)
suppressPackageStartupMessages({ library(tidyverse); library(patchwork) })

PROC <- "data/processed"; OUT <- "output/figures"
dir.create(OUT, recursive = TRUE, showWarnings = FALSE)
COND_COLORS <- c(control = "#9ca3af", treatment = "#2563eb")
COND_LABELS <- c(control = "Control (cats-vs-dogs bot)", treatment = "Treatment (Republican bot)")
COUNTY_COLORS <- c(Riverton = "#d97706", Lakewood = "#0f766e")
theme_set(theme_minimal(base_size = 12) + theme(panel.grid.minor = element_blank()))

parts <- read_csv(file.path(PROC, "participants.csv"), show_col_types = FALSE) |> filter(!is.na(completed_at))
inv <- read_csv(file.path(PROC, "investments.csv"), show_col_types = FALSE) |>
  filter(participant_id %in% parts$participant_id) |>
  mutate(County = if_else(county == "R", "Riverton", "Lakewood"), R = county == "R") |>
  arrange(participant_id, n)
per <- inv |> group_by(participant_id, condition) |>
  summarise(share_R = mean(R), profit = sum(back) - 1e5, .groups = "drop") |>
  mutate(cond_lab = COND_LABELS[condition])

# 1. Every click of every participant, sorted by Riverton share within condition
ord <- per |> arrange(condition, share_R) |> mutate(row = row_number())
p1 <- inv |> left_join(select(ord, participant_id, row, cond_lab), by = "participant_id") |>
  ggplot(aes(n, reorder(participant_id, row), fill = County)) +
  geom_tile(height = 0.85) +
  facet_grid(cond_lab ~ ., scales = "free_y", space = "free_y") +
  scale_fill_manual(values = COUNTY_COLORS, name = "County chosen") +
  scale_x_continuous(breaks = c(1, 25, 50, 75, 100), expand = c(0, 0)) +
  labs(x = "Click", y = "Participant (sorted by Riverton share)",
       title = "Every click: which county each participant chose",
       subtitle = "Riverton is the better county (on average $1.35 back per $1, vs $1.00 in Lakewood)") +
  theme(axis.text.y = element_blank(), panel.grid = element_blank(), legend.position = "bottom",
        strip.text.y = element_text(angle = 0, hjust = 0))
ggsave(file.path(OUT, "1_every_click.png"), p1, width = 10, height = 6.5, dpi = 150, bg = "white")

# 2. Running Riverton share per person, with condition means
run <- inv |> group_by(participant_id) |> mutate(cum_R = cummean(R)) |> ungroup()
p2 <- run |> ggplot(aes(n, cum_R, colour = condition)) +
  geom_hline(yintercept = 0.5, colour = "grey80") +
  geom_line(aes(group = participant_id), alpha = 0.35) +
  stat_summary(fun = mean, geom = "line", linewidth = 1.6) +
  scale_colour_manual(values = COND_COLORS, labels = COND_LABELS, name = NULL) +
  scale_y_continuous(labels = scales::percent, limits = c(0, 1)) +
  labs(x = "Click", y = "Share of clicks so far sent to Riverton",
       title = "Running Riverton share: thin lines are people, thick lines are condition means") +
  theme(legend.position = "bottom")
ggsave(file.path(OUT, "2_running_share.png"), p2, width = 9, height = 5, dpi = 150, bg = "white")

# 3. What people saw vs what they did: experienced average return per $1,000 in each county
exp_ret <- inv |> group_by(participant_id, County) |> summarise(avg = mean(back), k = n(), .groups = "drop") |>
  pivot_wider(names_from = County, values_from = c(avg, k)) |>
  mutate(gap = avg_Riverton - avg_Lakewood) |> left_join(per, by = "participant_id")
p3 <- exp_ret |> filter(!is.na(gap)) |>
  ggplot(aes(gap, share_R, colour = condition)) +
  geom_vline(xintercept = 0, colour = "grey80") + geom_hline(yintercept = 0.5, colour = "grey80") +
  geom_point(size = 3.5, alpha = 0.85) +
  scale_colour_manual(values = COND_COLORS, labels = COND_LABELS, name = NULL) +
  scale_x_continuous(labels = scales::dollar) + scale_y_continuous(labels = scales::percent, limits = c(0, 1)) +
  labs(x = "Riverton minus Lakewood: average money back per $1,000 the person actually saw",
       y = "Share of all clicks to Riverton",
       title = "What people saw vs what they did",
       subtitle = "Right of zero: Riverton paid this person more on average. Low dots kept investing in Lakewood anyway.\nThe one person who never tried Riverton is not shown.") +
  theme(legend.position = "bottom")
ggsave(file.path(OUT, "3_saw_vs_did.png"), p3, width = 9, height = 5.5, dpi = 150, bg = "white")

# 4. Win-stay / lose-shift: P(same county next click) after a good or bad return
fb <- inv |> group_by(participant_id) |> mutate(stay = lead(county) == county, good = back >= 1000) |>
  ungroup() |> filter(!is.na(stay)) |>
  group_by(participant_id, condition, County, good) |> summarise(stay = mean(stay), .groups = "drop") |>
  mutate(Return = if_else(good, "Last return\n$1,000 or more", "Last return\nunder $1,000"))
p4 <- fb |> group_by(condition, County, Return) |>
  summarise(m = mean(stay), se = sd(stay) / sqrt(n()), .groups = "drop") |>
  ggplot(aes(Return, m, fill = condition)) +
  geom_col(position = position_dodge(0.8), width = 0.7) +
  geom_errorbar(aes(ymin = m - se, ymax = m + se), position = position_dodge(0.8), width = 0.2) +
  facet_wrap(~ paste("Last click in", County)) +
  scale_fill_manual(values = COND_COLORS, labels = COND_LABELS, name = NULL) +
  scale_y_continuous(labels = scales::percent, limits = c(0, 1)) +
  labs(x = NULL, y = "Clicked the same county again", title = "How people react to a good or bad return (mean ± 1 SE)") +
  theme(legend.position = "bottom")
ggsave(file.path(OUT, "4_react_to_returns.png"), p4, width = 9, height = 5, dpi = 150, bg = "white")

# 5. Profit by condition, and profit vs Riverton share
p5a <- per |> ggplot(aes(condition, profit, colour = condition)) +
  geom_hline(yintercept = c(0, 35000), colour = "grey80", linetype = c("solid", "dashed")) +
  geom_jitter(width = 0.08, size = 3, alpha = 0.8) +
  stat_summary(fun.data = mean_se, colour = "black", size = 0.6) +
  scale_colour_manual(values = COND_COLORS, guide = "none") + scale_x_discrete(labels = c("Control", "Treatment")) +
  scale_y_continuous(labels = scales::dollar) + labs(x = NULL, y = "Profit on the $100,000 budget")
p5b <- per |> ggplot(aes(share_R, profit, colour = condition)) +
  geom_point(size = 3, alpha = 0.85) +
  scale_colour_manual(values = COND_COLORS, labels = COND_LABELS, name = NULL) +
  scale_x_continuous(labels = scales::percent) + scale_y_continuous(labels = scales::dollar) +
  labs(x = "Share of clicks to Riverton", y = NULL) + theme(legend.position = "bottom")
p5 <- (p5a | p5b) + plot_annotation(title = "Who made money: profit by condition (mean ± 1 SE) and by Riverton share",
                                     subtitle = "Dashed line: expected profit if every click goes to Riverton ($35,000)")
ggsave(file.path(OUT, "5_profit.png"), p5, width = 10, height = 5, dpi = 150, bg = "white")
cat("Wrote", length(list.files(OUT)), "figures to", OUT, "\n")
