# Investment-game (bandit) pilot: pull fresh data, then render the report.
# Run from this folder:  make        (or from the repo root: make -C studies/10_bandit_game_pilot)
.PHONY: all pull report clean

all: pull report

pull:
	python3 pull_data.py

report:
	quarto render analysis.qmd
	rm -rf analysis_files .quarto

clean:
	rm -rf data analysis.html analysis_files .quarto
