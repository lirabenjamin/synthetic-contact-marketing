# Ideal-Bayesian-learner simulation for the multi-round allocation game redesign.
# Purpose: before launch, check (1) parameter recovery and (2) power for condition
# differences in learning parameters, across candidate designs.
#
# Usage: Rscript simulate.R <output_dir>
#
# Model (per participant)
#   Latent quantity: l = log(R receptivity / D receptivity). Truth l = 0 (equal receptivity).
#   Prior belief: mean mu0, strength n0 (pseudo-observations).
#   Each round t the participant allocates share s_t of the budget to the R market, then sees
#   revenue in both markets, which yields a noisy signal y_t = l + e_t, e_t ~ N(0, sig_e).
#   Belief update (conjugate normal): m_{t+1} = m_t + (y_t - m_t) / (n0 + t).
#   Choice: s_t = s*(m_t) + N(0, sig_s), clipped to [0.05, 0.95] (min 5% per market keeps
#   feedback flowing from both markets). s*(m) maximises expected revenue given belief m.
#   Optional per-round belief report: b_t = m_t + N(0, sig_b).
#
# Hypotheses about condition (twin chat vs control bot)
#   H1: twin raises mu0 (less pessimistic prior about Republican receptivity).
#   H2: twin lowers n0 (weaker prior, faster learning).
# All population values below are ASSUMPTIONS for planning, not estimates from data.

suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
  library(purrr)
  library(ggplot2)
})

args <- commandArgs(trailingOnly = TRUE)
out_dir <- if (length(args) > 0) args[1] else "output"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
set.seed(20261016)

# ── Game constants (2-market redesign) ───────────────────────────────────────
BUDGET <- 1e5
HALF_MAX <- 3e4          # S-curve half-saturation, as in the current game engine
H_R <- 6e4               # households, R-leaning market (visible to participants)
H_D <- 4e4               # households, D-leaning market (visible to participants)
L_TRUE <- 0              # true log receptivity ratio (R = D)
N_ROUNDS <- 10
S_MIN <- 0.05
S_MAX <- 0.95
SIG_E_2MKT <- 0.30 * sqrt(2)   # log-revenue noise 0.30 per market, difference of two markets

# Current 4-market engine (pilots/02_green_market_game/simulation/simulate.py)
towns <- tibble(
  market = c("harlan", "williamson", "burlington", "middlesex"),
  rS = c(0.78, 0.72, 0.32, 0.28),
  comp = c(0.20, 0.35, 0.45, 0.85)
)
K_COMP <- 2
# Hidden competition adds market-specific noise to any inference about party receptivity
SIG_COMP <- K_COMP * sd(towns$comp)
SIG_E_4MKT <- sqrt(SIG_E_2MKT^2 + SIG_COMP^2)

# ── Population assumptions ───────────────────────────────────────────────────
POP <- list(
  mu0_mean_ctrl = log(0.6), mu0_sd = 0.35,     # control believes R about 60% as receptive
  ln0_mean_ctrl = log(4),   ln0_sd = 0.6,      # prior worth about 4 rounds of feedback
  d_mu0 = 0.30,                                 # H1 effect size (Cohen's d on mu0)
  d_ln0 = -0.30,                                # H2 effect size (Cohen's d on log n0)
  sig_s = 0.10,                                 # allocation noise (share of budget)
  sig_b = 0.15                                  # belief-report noise (log-ratio units)
)

# ── Optimal share given a belief ─────────────────────────────────────────────
s_curve <- function(a) a^2 / (a^2 + HALF_MAX^2)
s_grid <- seq(S_MIN, S_MAX, by = 0.005)
best_share <- function(m) {
  v <- exp(m) * H_R / H_D
  s_grid[which.max(v * s_curve(s_grid * BUDGET) + s_curve((1 - s_grid) * BUDGET))]
}
m_grid <- seq(-3, 3, by = 0.01)
sstar <- approxfun(m_grid, map_dbl(m_grid, best_share), rule = 2)

belief_path <- function(mu0, ln0, y) {
  n0 <- exp(ln0)
  m <- numeric(length(y))
  m[1] <- mu0
  for (t in seq_len(length(y) - 1)) m[t + 1] <- m[t] + (y[t] - m[t]) / (n0 + t)
  m
}

simulate_person <- function(mu0, ln0, sig_e) {
  y <- rnorm(N_ROUNDS, L_TRUE, sig_e)
  m <- belief_path(mu0, ln0, y)
  s <- pmin(pmax(sstar(m) + rnorm(N_ROUNDS, 0, POP$sig_s), S_MIN), S_MAX)
  b <- m + rnorm(N_ROUNDS, 0, POP$sig_b)
  list(y = y, s = s, b = b)
}

negll <- function(par, d, elicit) {
  m <- belief_path(par[1], par[2], d$y)
  pred <- sstar(m)
  sig_s <- exp(par[3])
  ll <- ifelse(d$s <= S_MIN + 1e-9, pnorm((S_MIN - pred) / sig_s, log.p = TRUE),
        ifelse(d$s >= S_MAX - 1e-9, pnorm((S_MAX - pred) / sig_s, lower.tail = FALSE, log.p = TRUE),
               dnorm(d$s, pred, sig_s, log = TRUE)))
  if (elicit) ll <- c(ll, dnorm(d$b, m, exp(par[4]), log = TRUE))
  -sum(ll)
}

fit_person <- function(d, elicit) {
  lower <- c(-3, log(0.2), log(0.01), log(0.01))
  upper <- c(3, log(200), log(1), log(2))
  starts <- expand_grid(mu0 = c(-0.5, 0), ln0 = c(log(2), log(20)))
  fits <- pmap(starts, function(mu0, ln0) {
    p0 <- c(mu0, ln0, log(0.1), log(0.2))
    k <- if (elicit) 4 else 3
    tryCatch(optim(p0[1:k], negll, d = d, elicit = elicit, method = "L-BFGS-B",
                   lower = lower[1:k], upper = upper[1:k]),
             error = function(e) list(value = Inf, par = rep(NA, k)))
  })
  best <- fits[[which.min(map_dbl(fits, "value"))]]
  c(mu0_hat = best$par[1], ln0_hat = best$par[2])
}

# ── Run each design variant on a large pool ──────────────────────────────────
variants <- tribble(
  ~variant,                      ~sig_e,      ~elicit,
  "2-market, allocation only",   SIG_E_2MKT,  FALSE,
  "2-market + belief reports",   SIG_E_2MKT,  TRUE,
  "4-market, allocation only",   SIG_E_4MKT,  FALSE,
  "4-market + belief reports",   SIG_E_4MKT,  TRUE
)
N_POOL <- 1500

pool <- pmap(variants, function(variant, sig_e, elicit) {
  people <- tibble(
    id = seq_len(2 * N_POOL),
    cond = rep(c("Control", "Twin"), each = N_POOL),
    mu0 = rnorm(2 * N_POOL, POP$mu0_mean_ctrl + (cond == "Twin") * POP$d_mu0 * POP$mu0_sd, POP$mu0_sd),
    ln0 = rnorm(2 * N_POOL, POP$ln0_mean_ctrl + (cond == "Twin") * POP$d_ln0 * POP$ln0_sd, POP$ln0_sd)
  )
  sims <- map2(people$mu0, people$ln0, simulate_person, sig_e = sig_e)
  est <- map(sims, fit_person, elicit = elicit) |> do.call(what = rbind)
  people |>
    mutate(variant = variant, s1 = map_dbl(sims, \(d) d$s[1]),
           s_last = map_dbl(sims, \(d) d$s[N_ROUNDS]),
           traj = map(sims, "s")) |>
    bind_cols(as_tibble(est))
}) |> list_rbind()

# ── Parameter recovery ───────────────────────────────────────────────────────
recovery <- pool |>
  group_by(variant) |>
  summarise(r_mu0 = cor(mu0, mu0_hat),
            rho_ln0 = cor(ln0, ln0_hat, method = "spearman"),
            pct_ln0_at_bound = mean(ln0_hat <= log(0.2) + 1e-3 | ln0_hat >= log(200) - 1e-3),
            .groups = "drop")

# ── Power by resampling the pool ─────────────────────────────────────────────
N_PER_CELL <- c(100, 150, 200, 300, 400)
N_RESAMPLES <- 500
pval <- function(x, g) wilcox.test(x[g == "Twin"], x[g == "Control"], exact = FALSE)$p.value
power <- expand_grid(variant = variants$variant, n = N_PER_CELL) |>
  mutate(res = map2(variant, n, function(v, n) {
    pv <- pool |> filter(variant == v)
    ctrl <- which(pv$cond == "Control")
    twin <- which(pv$cond == "Twin")
    reps <- map(seq_len(N_RESAMPLES), function(i) {
      d <- pv[c(sample(ctrl, n), sample(twin, n)), ]
      c(H1_mu0_model = pval(d$mu0_hat, d$cond),
        H2_n0_model = pval(d$ln0_hat, d$cond),
        H1_round1_share = pval(d$s1, d$cond))
    }) |> do.call(what = rbind)
    tibble(test = colnames(reps), power = colMeans(reps < 0.05))
  })) |>
  unnest(res)

# ── Expected trajectories (2-market + belief reports pool) ───────────────────
traj <- pool |>
  filter(variant == "2-market + belief reports") |>
  select(cond, traj) |>
  mutate(traj = map(traj, \(s) tibble(round = seq_along(s), share = s))) |>
  unnest(traj) |>
  group_by(cond, round) |>
  summarise(share = mean(share), se = sd(share) / sqrt(n()), .groups = "drop")

constants <- tibble(
  quantity = c("optimal_share_R_true", "share_R_at_control_prior_mean", "share_R_at_twin_prior_mean",
               "sig_e_2mkt", "sig_e_4mkt", "sd_log_receptivity_current_engine",
               "sd_log_competition_current_engine", "n_pool_per_cond", "n_resamples"),
  value = c(sstar(L_TRUE), sstar(POP$mu0_mean_ctrl), sstar(POP$mu0_mean_ctrl + POP$d_mu0 * POP$mu0_sd),
            SIG_E_2MKT, SIG_E_4MKT, sd(log(towns$rS * 0.65 + (1 - towns$rS) * 0.75)),
            SIG_COMP, N_POOL, N_RESAMPLES)
)

write.csv(recovery, file.path(out_dir, "recovery.csv"), row.names = FALSE)
write.csv(power, file.path(out_dir, "power.csv"), row.names = FALSE)
write.csv(traj, file.path(out_dir, "trajectories.csv"), row.names = FALSE)
write.csv(constants, file.path(out_dir, "constants.csv"), row.names = FALSE)

p <- ggplot(traj, aes(round, 100 * share, color = cond)) +
  geom_hline(yintercept = 100 * sstar(L_TRUE), linetype = "dashed", color = "grey40") +
  annotate("text", x = 1, y = 100 * sstar(L_TRUE), label = "Revenue-maximising share",
           hjust = 0, vjust = -0.5, color = "grey40") +
  geom_line(linewidth = 1) +
  geom_point(size = 2) +
  scale_x_continuous(breaks = seq_len(N_ROUNDS)) +
  scale_color_manual(values = c(Control = "#9ca3af", Twin = "#2563eb"), name = NULL) +
  labs(x = "Round", y = "% budget to R market (simulated)") +
  theme_minimal(base_size = 13) +
  theme(legend.position = "top")
ggsave(file.path(out_dir, "simulated_trajectories.png"), p, width = 7, height = 4.5, dpi = 200)

cat("Done. Wrote recovery.csv, power.csv, trajectories.csv, constants.csv, simulated_trajectories.png to", out_dir, "\n")
