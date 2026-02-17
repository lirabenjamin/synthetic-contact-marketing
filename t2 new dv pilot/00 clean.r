# =============================================================================
# 00 clean.r — Data cleaning for T2 New DV Pilot (SV_1Bn8JHpeFDRuu5E)
# =============================================================================
# This survey uses a counterbalanced design:
#   - Block 1 (g1-g6): _2 = republican, _3 = democrat
#   - Block 2 (Q46-Q51): _2 = democrat, _3 = republican
# Participants see only one block pre-interaction (controlled by rep_first).
# Both blocks measure the same 6 environmental attitude items.
# Post-interaction outgroup beliefs are in post_1 through post_6.
# New DV: Q39_1 = dictator game (donation to outgroup member, 0-50 scale)
# =============================================================================

library(arrow)
library(dplyr)
library(tidyr)
library(qualtRics)

# --- 1. Download data from Qualtrics ---
id <- "SV_1Bn8JHpeFDRuu5E"

raw <- fetch_survey(
  surveyID = id,
  verbose = TRUE,
  force_request = TRUE,
  convert = FALSE
)

# --- 2. Filter to valid participants ---
dat <- raw %>%
  filter(
    Status == "IP Address",
    !is.na(PROLIFIC_PID),
    PROLIFIC_PID != ""
  )

cat("After filtering: n =", nrow(dat), "\n")

# --- 3. Determine participant party ---
dat <- dat %>%
  mutate(
    participant_party = case_when(
      politicalorientation == "Democratic" ~ "Democrat",
      politicalorientation == "Republican" ~ "Republican",
      TRUE ~ NA_character_
    ),
    learner_party = case_when(
      participant_party == "Democrat" ~ "D→R",
      participant_party == "Republican" ~ "R→D",
      TRUE ~ NA_character_
    )
  )

# --- 4. Political extremism ---
# politicalextremity_1...20 = how strongly identify as republican
# politicalextremity_1...21 = how strongly identify as democrat
# Use the relevant one based on participant party
dat <- dat %>%
  mutate(
    political_extremism = case_when(
      participant_party == "Republican" ~ `politicalextremity_1...20`,
      participant_party == "Democrat" ~ `politicalextremity_1...21`,
      TRUE ~ NA_real_
    )
  )

# --- 5. Unify counterbalanced environmental items (pre-interaction) ---
# Block 1 (g1-g6): _1=own, _2=republican, _3=democrat
# Block 2 (Q46-Q51): _1=own, _2=democrat, _3=republican
# We unify into: env{1-6}_own, env{1-6}_republican, env{1-6}_democrat

# Map Q46→g1, Q47→g2, Q48→g3, Q49→g4, Q50→g5, Q51→g6
dat <- dat %>%
  mutate(
    # Own opinion: coalesce g{i}_1 and Q{j}_1
    env1_own = coalesce(g1_1, Q46_1),
    env2_own = coalesce(g2_1, Q47_1),
    env3_own = coalesce(g3_1, Q48_1),
    env4_own = coalesce(g4_1, Q49_1),
    env5_own = coalesce(g5_1, Q50_1),
    env6_own = coalesce(g6_1, Q51_1),

    # Republican rating: g{i}_2 or Q{j}_3
    env1_republican = coalesce(g1_2, Q46_3),
    env2_republican = coalesce(g2_2, Q47_3),
    env3_republican = coalesce(g3_2, Q48_3),
    env4_republican = coalesce(g4_2, Q49_3),
    env5_republican = coalesce(g5_2, Q50_3),
    env6_republican = coalesce(g6_2, Q51_3),

    # Democrat rating: g{i}_3 or Q{j}_2
    env1_democrat = coalesce(g1_3, Q46_2),
    env2_democrat = coalesce(g2_3, Q47_2),
    env3_democrat = coalesce(g3_3, Q48_2),
    env4_democrat = coalesce(g4_3, Q49_2),
    env5_democrat = coalesce(g5_3, Q50_2),
    env6_democrat = coalesce(g6_3, Q51_2)
  )

# --- 6. Recode to ingroup/outgroup ---
dat <- dat %>%
  mutate(
    # Ingroup beliefs (pre)
    env1_ingroup = if_else(participant_party == "Republican", env1_republican, env1_democrat),
    env2_ingroup = if_else(participant_party == "Republican", env2_republican, env2_democrat),
    env3_ingroup = if_else(participant_party == "Republican", env3_republican, env3_democrat),
    env4_ingroup = if_else(participant_party == "Republican", env4_republican, env4_democrat),
    env5_ingroup = if_else(participant_party == "Republican", env5_republican, env5_democrat),
    env6_ingroup = if_else(participant_party == "Republican", env6_republican, env6_democrat),

    # Outgroup beliefs (pre)
    env1_outgroup_pre = if_else(participant_party == "Republican", env1_democrat, env1_republican),
    env2_outgroup_pre = if_else(participant_party == "Republican", env2_democrat, env2_republican),
    env3_outgroup_pre = if_else(participant_party == "Republican", env3_democrat, env3_republican),
    env4_outgroup_pre = if_else(participant_party == "Republican", env4_democrat, env4_republican),
    env5_outgroup_pre = if_else(participant_party == "Republican", env5_democrat, env5_republican),
    env6_outgroup_pre = if_else(participant_party == "Republican", env6_democrat, env6_republican),

    # Outgroup beliefs (post) — post_1 through post_6 are already about outgroup
    env1_outgroup_post = post_1,
    env2_outgroup_post = post_2,
    env3_outgroup_post = post_3,
    env4_outgroup_post = post_4,
    env5_outgroup_post = post_5,
    env6_outgroup_post = post_6
  )

# --- 7. Convert Likert responses to numeric (1-5) ---
likert_recode <- function(x) {
  case_when(
    x == "Disagree strongly" ~ 1,
    x == "Disagree a little" ~ 2,
    x == "Neither agree nor disagree" ~ 3,
    x == "Agree a little" ~ 4,
    x == "Agree strongly" ~ 5,
    TRUE ~ NA_real_
  )
}

dat <- dat %>%
  mutate(
    across(
      c(starts_with("env") & matches("_(own|ingroup|outgroup_pre|outgroup_post)$")),
      likert_recode
    )
  )

# --- 8. Convert confidence to numeric (1-5) ---
confidence_recode <- function(x) {
  case_when(
    x == "Not at all confident" ~ 1,
    x == "Slightly confident" ~ 2,
    x == "Moderately confident" ~ 3,
    x == "Very confident" ~ 4,
    x == "Extremely confident" ~ 5,
    TRUE ~ NA_real_
  )
}

dat <- dat %>%
  mutate(
    confidence_ingroup = confidence_recode(confidence_in1),
    confidence_outgroup_pre = confidence_recode(confidence_out1),
    confidence_outgroup_post = confidence_recode(confidence_out2)
  )

# --- 9. Warmth measures ---
dat <- dat %>%
  mutate(
    warmth_outgroup_pre = warmth_pre_1,
    warmth_ingroup_pre = warmth_pre_2,
    warmth_outgroup_post = warmth_post_1,
    warmth_ingroup_post = warmth_post_2,
    warmth_diff_pre = warmth_outgroup_pre - warmth_ingroup_pre,
    warmth_diff_post = warmth_outgroup_post - warmth_ingroup_post
  )

# --- 10. Create composite scores ---
dat <- dat %>%
  rowwise() %>%
  mutate(
    green_own = mean(c(env1_own, env2_own, env3_own, env4_own, env5_own, env6_own), na.rm = TRUE),
    green_ingroup = mean(c(env1_ingroup, env2_ingroup, env3_ingroup, env4_ingroup, env5_ingroup, env6_ingroup), na.rm = TRUE),
    green_outgroup_pre = mean(c(env1_outgroup_pre, env2_outgroup_pre, env3_outgroup_pre, env4_outgroup_pre, env5_outgroup_pre, env6_outgroup_pre), na.rm = TRUE),
    green_outgroup_post = mean(c(env1_outgroup_post, env2_outgroup_post, env3_outgroup_post, env4_outgroup_post, env5_outgroup_post, env6_outgroup_post), na.rm = TRUE)
  ) %>%
  ungroup()

# --- 11. Compute accuracy (negative absolute error) ---
actual_outgroup_attitudes <- dat %>%
  group_by(participant_party) %>%
  summarise(actual_green = mean(green_own, na.rm = TRUE), .groups = "drop")

dat <- dat %>%
  mutate(outgroup_party = if_else(participant_party == "Democrat", "Republican", "Democrat")) %>%
  left_join(actual_outgroup_attitudes, by = c("outgroup_party" = "participant_party")) %>%
  mutate(
    accuracy_pre = -abs(green_outgroup_pre - actual_green),
    accuracy_post = -abs(green_outgroup_post - actual_green)
  )

# --- 12. New DV: Dictator game donation ---
dat <- dat %>%
  mutate(
    donation = as.numeric(Q39_1)
  )

# --- 13. Demographics ---
dat <- dat %>%
  mutate(
    age = as.numeric(age),
    gender = gender
  )

# --- 14. Counterbalance indicator ---
dat <- dat %>%
  mutate(
    rep_first = as.numeric(rep_first),
    block = if_else(rep_first == 1, "rep_first", "dem_first")
  )

# --- 15. Engagement and attention ---
dat <- dat %>%
  mutate(
    tab_switch_count = as.numeric(tabSwitchCount),
    time_hidden_ms = as.numeric(timeHiddenMs),
    tab_switch_count_bot = as.numeric(tabSwitchCountBot),
    time_hidden_ms_bot = as.numeric(timeHiddenMsBot),
    duration_sec = as.numeric(`Duration (in seconds)`)
  )

# --- 16. Select final variables ---
clean <- dat %>%
  select(
    # Identifiers
    ResponseId,
    PROLIFIC_PID,

    # Political
    participant_party,
    learner_party,
    political_extremism,

    # Counterbalance
    block,
    condition,

    # Environmental items (own, ingroup, outgroup pre, outgroup post)
    starts_with("env") & matches("_(own|ingroup|outgroup_pre|outgroup_post)$"),

    # Composites
    green_own,
    green_ingroup,
    green_outgroup_pre,
    green_outgroup_post,

    # Accuracy
    accuracy_pre,
    accuracy_post,
    actual_green,

    # Warmth
    warmth_outgroup_pre,
    warmth_ingroup_pre,
    warmth_outgroup_post,
    warmth_ingroup_post,
    warmth_diff_pre,
    warmth_diff_post,

    # Confidence
    confidence_ingroup,
    confidence_outgroup_pre,
    confidence_outgroup_post,

    # New DV: dictator game
    donation,

    # Demographics
    age,
    gender,
    starts_with("race_"),

    # Engagement
    tab_switch_count,
    time_hidden_ms,
    tab_switch_count_bot,
    time_hidden_ms_bot,
    duration_sec,

    # Other
    talk_partner,
    comments
  )

# --- 17. Save ---
write_parquet(clean, "t2 new dv pilot/analysis_data.parquet")
write.csv(clean, "t2 new dv pilot/analysis_data.csv", row.names = FALSE)

cat("\nCleaned data saved to t2 new dv pilot/\n")
cat("Final sample size:", nrow(clean), "\n")
cat("Variables:", ncol(clean), "\n")
cat("\nBy party:\n")
print(table(clean$learner_party))
cat("\nBy block:\n")
print(table(clean$block))
cat("\nDonation summary:\n")
print(summary(clean$donation))
