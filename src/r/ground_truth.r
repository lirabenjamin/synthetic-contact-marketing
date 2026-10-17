library(rstatix)
library(arrow)

d1 = read_parquet("data/processed/analysis_data.parquet")%>% select(participant_party, g1_own:g6_own)
d2 = read_parquet("t3 experiment pilot/analysis_data.parquet")%>% select(participant_party, env1_own:env6_own)

d1 = d1 %>% mutate(g = rowMeans(select(., -1)))
d2 = d2 %>% mutate(g = rowMeans(select(., -1)))

d = bind_rows(d1, d2) %>% select(participant_party, g)

d %>% group_by(participant_party) %>%
  summarise(M = mean(g, na.rm = TRUE), SE = sd(g, na.rm = TRUE) / sqrt(n())) %>%
  mutate(ymin = M - SE, ymax = M + SE) %>% 
  write_csv("data/processed/ground_truth.csv")

d %>% t_test(g ~ participant_party)
d %>% cohens_d(g ~ participant_party)
