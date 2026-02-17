id = "SV_1Bn8JHpeFDRuu5E"

library(qualtRics)

fetch_survey(
  surveyID = id,
  verbose = TRUE,
  force_request = TRUE,
  convert = FALSE
) -> data


data

attr(data, "column_map")
