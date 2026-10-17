library(tidyverse)
library(arrow)
library(lme4)
library(lmerTest)
library(emmeans)
library(patchwork)

DAT_PATH <- "./t3 experiment pilot/analysis_data.parquet"

# Helpers
p_stars <- function(p) ifelse(p < .001, "***", ifelse(p < .01, "**", ifelse(p < .05, "*", "n.s.")))
fmt     <- function(x, d = 3) round(x, d)

condition_colors_4 <- c("RepBot" = "#4DAF4A", "DemBot" = "#984EA3",
                        "Chat" = "#377EB8",   "Game"   = "#E41A1C")


# ── Core function: fit lmer, return all pairwise DiD contrasts ───────────────
# Positive estimate = first-named condition improved more than second.
# Grid order in emmeans: pre×cond1, post×cond1, pre×cond2, post×cond2, ...

did_contrasts <- function(dat, conds) {
  dat <- dat %>% mutate(treatment = factor(treatment, levels = conds))
  n   <- length(conds)

  fit_did <- function(dv_pre, dv_post, dv_name) {
    long <- dat %>%
      select(ResponseId, treatment, all_of(c(dv_pre, dv_post))) %>%
      pivot_longer(c(all_of(dv_pre), all_of(dv_post)),
                   names_to = "time", values_to = "y") %>%
      mutate(time = factor(if_else(str_detect(time, "pre"), "pre", "post"),
                           levels = c("pre", "post")))

    m   <- lmer(y ~ time * treatment + (1 | ResponseId), data = long, REML = FALSE)
    emm <- emmeans(m, ~ time * treatment)

    pairs <- combn(seq_along(conds), 2, simplify = FALSE)
    con_list <- lapply(pairs, function(idx) {
      v <- numeric(2 * n)
      i <- idx[1]; j <- idx[2]
      v[(2*i-1):(2*i)] <- c(-1,  1)
      v[(2*j-1):(2*j)] <- c( 1, -1)
      v
    })
    names(con_list) <- sapply(pairs, function(idx)
      paste0(conds[idx[1]], " vs. ", conds[idx[2]]))

    contrast(emm, con_list) %>%
      as_tibble() %>%
      mutate(dv = dv_name)
  }

  bind_rows(
    fit_did("accuracy_pre",        "accuracy_post",        "accuracy"),
    fit_did("warmth_outgroup_pre", "warmth_outgroup_post", "warmth")
  )
}

# ── Plot DiD results ─────────────────────────────────────────────────────────
plot_did <- function(did_tbl, title) {
  did_tbl %>%
    mutate(
      ymin     = estimate - SE,
      ymax     = estimate + SE,
      dv       = factor(dv, levels = c("accuracy", "warmth"),
                        labels = c("Accuracy", "Warmth")),
      contrast = fct_reorder(contrast, estimate)
    ) %>%
    ggplot(aes(x = contrast, y = estimate)) +
    geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
    geom_pointrange(aes(ymin = ymin, ymax = ymax), size = 0.6, linewidth = 0.9,
                    color = "gray25") +
    geom_text(aes(y = ymax + (max(ymax) - min(ymin)) * 0.13,
                  label = p_stars(p.value)),
              size = 3.5, fontface = "bold") +
    coord_flip() +
    facet_wrap(~dv, scales = "free_x") +
    labs(x = NULL,
         y = "DiD estimate (positive = row condition improved more)",
         title = title) +
    theme_minimal(base_size = 12) +
    theme(panel.spacing = unit(1.5, "lines"))
}

### BEN

dat %>% 
  select(matches("acc"), treatment, participant_party) %>% 
  lm(accuracy_post ~ accuracy_pre + treatment, data = .) %>% summary()

dat %>% 
  select(matches("acc"), treatment, participant_party) %>% 
  lm(accuracy_post ~ accuracy_pre + treatment * participant_party, data = .) %>% summary()

dat %>% 
  select( treatment, participant_party,matches("warm")) %>% 
  filter(treatment %in% c("Contact", "Chat"), participant_party == "Democrat") %>%
  mutate(treatment = ifelse(treatment == "Contact", "Contact", "Control")) %>%
  lm(warmth_outgroup_post ~ warmth_outgroup_pre + treatment, data = .) %>% summary()

dat %>% select(matches("party"))

dat %>% 
  select( treatment, participant_party,matches("warm")) %>% 
  filter(treatment %in% c("Contact", "Chat"))  %>% 
  lm(warmth_outgroup_post ~ warmth_outgroup_pre + treatment * participant_party, data = .) %>% summary()
  pivot_longer(cols = c(warmth_outgroup_pre, warmth_outgroup_post), names_to = "time", values_to = "warmth") %>%
  mutate(time = ifelse(time == "warmth_outgroup_pre", "pre", "post")) %>%
  mutate(time = factor(time, levels = c("pre", "post"))) %>%
  ggplot(aes(x = time, y = warmth, group = treatment, color = treatment)) +
  geom_line(stat = "summary", fun = "mean") +
  geom_point(stat = "summary", fun = "mean") +
  geom_errorbar(stat = "summary", fun.data = mean_se, width = 0.2) +
  labs(x = "Time", y = "Warmth towards outgroup", title = "Warmth change by treatment (Democrats only)") +
  theme_minimal() +
  scale_color_manual(values = c("Contact" = "#4DAF4A", "Chat" = "#377EB8")) +
  theme(legend.title = element_blank())###


# =============================================================================
# SECTION 1: OUTLIER ROBUSTNESS
# Strategy: flag outliers using two principled criteria —
#   (a) |within-condition z-score| > 2.5 on change scores
#   (b) Cook's D > 4/n from the ANCOVA model
# Then compare DiD estimates across: full / z removed / Cook removed / both
# =============================================================================

cat("\n══════════════════════════════════════════════════════════════\n")
cat("SECTION 1: OUTLIER ROBUSTNESS\n")
cat("══════════════════════════════════════════════════════════════\n")

dat <- read_parquet(DAT_PATH) %>%
  mutate(
    treatment   = factor(treatment, levels = c("Contact", "Chat", "Game")),
    acc_change  = accuracy_post - accuracy_pre,
    warm_change = warmth_outgroup_post - warmth_outgroup_pre
  )

# (a) Z-score outliers
z_thresh <- 2.5
dat <- dat %>%
  group_by(treatment) %>%
  mutate(acc_z  = scale(acc_change)[, 1],
         warm_z = scale(warm_change)[, 1]) %>%
  ungroup()

ids_z <- dat %>% filter(abs(acc_z) > z_thresh | abs(warm_z) > z_thresh) %>% pull(ResponseId)

cat(sprintf("\nZ-score outliers (|z| > %.1f on acc or warmth change): n = %d\n\n", z_thresh, length(ids_z)))
dat %>%
  filter(ResponseId %in% ids_z) %>%
  select(ResponseId, treatment, acc_change, acc_z, warm_change, warm_z) %>%
  mutate(across(where(is.double), ~ round(.x, 2))) %>%
  arrange(treatment, desc(abs(warm_z))) %>%
  print()

# (b) Cook's D outliers from ANCOVA
ancova_acc  <- lm(accuracy_post          ~ accuracy_pre          + treatment, data = dat)
ancova_warm <- lm(warmth_outgroup_post   ~ warmth_outgroup_pre   + treatment, data = dat)

thresh_cooks <- 4 / nrow(dat)
ids_cooks <- dat$ResponseId[
  cooks.distance(ancova_acc)  > thresh_cooks |
  cooks.distance(ancova_warm) > thresh_cooks
]

cat(sprintf("\nCook's D outliers (> 4/n = %.4f): n = %d\n\n", thresh_cooks, length(ids_cooks)))
dat %>%
  filter(ResponseId %in% ids_cooks) %>%
  mutate(
    cooks_acc  = cooks.distance(ancova_acc) [match(ResponseId, dat$ResponseId)],
    cooks_warm = cooks.distance(ancova_warm)[match(ResponseId, dat$ResponseId)]
  ) %>%
  select(ResponseId, treatment, acc_change, warm_change, cooks_acc, cooks_warm) %>%
  mutate(across(where(is.double), ~ round(.x, 3))) %>%
  arrange(desc(cooks_warm)) %>%
  print()

ids_union <- union(ids_z, ids_cooks)
cat(sprintf("\nUnion (either criterion): n = %d\n", length(ids_union)))

# Compare DiD estimates across exclusion strategies
conds_3 <- c("Contact", "Chat", "Game")

did_robust <- bind_rows(
  did_contrasts(dat,                                     conds_3) %>% mutate(sample = "Full sample"),
  did_contrasts(dat %>% filter(!ResponseId %in% ids_z),     conds_3) %>% mutate(sample = "Z > 2.5 removed"),
  did_contrasts(dat %>% filter(!ResponseId %in% ids_cooks), conds_3) %>% mutate(sample = "Cook's D removed"),
  did_contrasts(dat %>% filter(!ResponseId %in% ids_union), conds_3) %>% mutate(sample = "Both removed")
) %>%
  mutate(sample = factor(sample, levels = c("Full sample", "Z > 2.5 removed",
                                            "Cook's D removed", "Both removed")))

cat("\n── DiD sensitivity: estimates by exclusion strategy ──\n")
did_robust %>%
  select(dv, contrast, sample, estimate, SE, p.value) %>%
  mutate(across(c(estimate, SE), fmt),
         p.value = fmt(p.value),
         sig = p_stars(as.numeric(p.value))) %>%
  arrange(dv, contrast, sample) %>%
  print(n = Inf)

# Plot: DiD across exclusion strategies
p_robust <- did_robust %>%
  mutate(
    ymin = estimate - SE,
    ymax = estimate + SE,
    dv   = factor(dv, levels = c("accuracy", "warmth"), labels = c("Accuracy", "Warmth"))
  ) %>%
  ggplot(aes(x = sample, y = estimate, color = sample)) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
  geom_pointrange(aes(ymin = ymin, ymax = ymax), size = 0.6, linewidth = 0.9) +
  geom_text(aes(y = ymax + (max(ymax) - min(ymin)) * 0.18,
                label = p_stars(p.value)),
            size = 3, fontface = "bold") +
  facet_grid(dv ~ contrast, scales = "free_y") +
  scale_color_brewer(palette = "Dark2") +
  labs(x = NULL, y = "DiD estimate", color = NULL,
       title = "Condition DiD estimates: sensitivity to outlier exclusion strategy") +
  theme_minimal(base_size = 11) +
  theme(axis.text.x = element_blank(), axis.ticks.x = element_blank(),
        legend.position = "bottom", panel.spacing = unit(1, "lines"))

print(p_robust)
ggsave("./t3 experiment pilot/eda_outlier_robustness.png", p_robust,
       width = 11, height = 6, dpi = 150)


# =============================================================================
# SECTION 2: 4-CONDITION SPLIT — RepBot vs. DemBot
# Democrats talked to a RepBot; Republicans talked to a DemBot.
# Do the two contact arms show different DiD effects vs. controls?
# Key contrast: RepBot vs. DemBot
# =============================================================================

cat("\n\n══════════════════════════════════════════════════════════════\n")
cat("SECTION 2: 4-CONDITION SPLIT (RepBot / DemBot / Chat / Game)\n")
cat("══════════════════════════════════════════════════════════════\n")

dat4 <- read_parquet(DAT_PATH) %>%
  mutate(treatment = case_when(
    treatment == "Contact" & participant_party == "Democrat"   ~ "RepBot",
    treatment == "Contact" & participant_party == "Republican" ~ "DemBot",
    TRUE ~ treatment
  ))

cat("\n── N by condition ──\n")
dat4 %>% count(treatment) %>% print()

conds_4 <- c("RepBot", "DemBot", "Chat", "Game")
did_4 <- did_contrasts(dat4, conds_4)

cat("\n── DiD contrasts: accuracy (sorted by p) ──\n")
did_4 %>%
  filter(dv == "accuracy") %>%
  select(contrast, estimate, SE, df, t.ratio, p.value) %>%
  mutate(across(c(estimate, SE, t.ratio), fmt), p.value = fmt(p.value),
         sig = p_stars(as.numeric(p.value))) %>%
  arrange(p.value) %>% print()

cat("\n── DiD contrasts: warmth (sorted by p) ──\n")
did_4 %>%
  filter(dv == "warmth") %>%
  select(contrast, estimate, SE, df, t.ratio, p.value) %>%
  mutate(across(c(estimate, SE, t.ratio), fmt), p.value = fmt(p.value),
         sig = p_stars(as.numeric(p.value))) %>%
  arrange(p.value) %>% print()

p_4cond <- plot_did(did_4, "Pairwise DiD contrasts: 4-condition split")
print(p_4cond)
ggsave("./t3 experiment pilot/eda_4condition_did.png", p_4cond,
       width = 11, height = 5, dpi = 150)
