# Allocation-game pilot: pull fresh data, fit the Bayesian learner, then render the report.
# Run from this folder:  make        (or from the repo root: make -C studies/08_allocation_game_pilot)
.PHONY: all pull learner report clean

all: pull learner report

pull:
	python3 pull_data.py

learner:
	python3 fit_learner_pilot.py

report:
	quarto render analysis.qmd
	rm -rf analysis_files .quarto

clean:
	rm -rf data analysis.html analysis_files .quarto
