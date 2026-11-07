# Investment-game (bandit) pilot: pull fresh data, draw the diagnostic figures, then render the report.
# Run from this folder:  make        (or from the repo root: make -C studies/10_bandit_game_pilot)
.PHONY: all pull figures report clean

all: pull figures report

pull:
	python3 pull_data.py

figures:
	Rscript figures.R

report:
	quarto render analysis.qmd
	rm -rf analysis_files .quarto

clean:
	rm -rf data output analysis.html analysis_files .quarto
