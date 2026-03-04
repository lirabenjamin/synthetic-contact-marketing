# Makefile for Learning from Twins analysis pipeline
# Author: Benjamin Lira
# Description: Reproducible pipeline for data processing and analysis

.PHONY: all clean data analysis report slides help bot-survey docs

# Default target: run entire pipeline
all: report slides

# Help message
help:
	@echo "Learning from Twins - Analysis Pipeline"
	@echo "========================================"
	@echo ""
	@echo "Available targets:"
	@echo "  make all        - Run entire pipeline (download → clean → conversations → analysis → report → slides)"
	@echo "  make data       - Download raw data, clean it, and download conversations"
	@echo "  make analysis   - Create analysis dataset"
	@echo "  make report     - Render the report (HTML and PDF)"
	@echo "  make slides     - Render the presentation slides (PDF)"
	@echo "  make clean      - Remove all processed data and outputs"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Individual steps:"
	@echo "  make download-qualtrics - Download raw Qualtrics data"
	@echo "  make clean-data         - Clean raw Qualtrics data"
	@echo "  make conversations      - Download conversation data from database"
	@echo "  make analysis-data      - Create minimal publication dataset"
	@echo "  make extreme-cases      - Analyze extreme cases"
	@echo "  make bot-survey         - Run bot validity survey (requires OPENAI_API_KEY in .env)"
	@echo "  make report-html        - Render HTML report only"
	@echo "  make report-pdf         - Render PDF report only"

# Clean all processed data and outputs
clean:
	@echo "Cleaning processed data and outputs..."
	rm -f data/raw/qualtrics.parquet
	rm -f data/processed/cleaned_data.parquet
	rm -f data/processed/conversation_metrics.parquet
	rm -rf data/processed/conversations
	rm -f data/processed/analysis_data.parquet
	rm -f data/processed/analysis_data.csv
	rm -f output/extreme_cases.csv
	rm -f output/extreme_cases_summary.md
	rm -f analysis/report.html
	rm -f analysis/report.pdf
	rm -f analysis/slides.pdf
	@echo "Clean complete!"

# Step 0: Download raw Qualtrics data
download-qualtrics: data/raw/qualtrics.parquet

data/raw/qualtrics.parquet: src/r/download_qualtrics.r
	@echo "Step 0: Downloading raw Qualtrics data..."
	Rscript src/r/download_qualtrics.r
	@echo "✓ Qualtrics data downloaded"

# Step 1: Clean raw data (initial pass without conversations)
clean-data-initial: data/raw/qualtrics.parquet src/r/clean_data.R
	@echo "Step 1a: Initial cleaning of raw data..."
	Rscript src/r/clean_data.R
	@echo "✓ Initial cleaned data created"

# Step 2: Download conversations (depends on initial cleaned data)
conversations: data/processed/conversation_metrics.parquet

data/processed/conversation_metrics.parquet: data/raw/qualtrics.parquet src/python/download_conversations.py
	@echo "Step 2: Downloading conversation data..."
	source .venv/bin/activate && python src/python/download_conversations.py
	@echo "✓ Conversations downloaded"

# Step 3: Re-clean data with conversation metrics merged
clean-data: data/processed/cleaned_data.parquet

data/processed/cleaned_data.parquet: data/processed/conversation_metrics.parquet src/r/clean_data.R
	@echo "Step 3: Re-cleaning data with conversation metrics..."
	Rscript src/r/clean_data.R
	@echo "✓ Cleaned data with conversation metrics created"

# Step 4: Process all data (depends on both clean data and conversations)
data: data/processed/cleaned_data.parquet
	@echo "✓ All data processing complete"

# Step 5: Create analysis dataset
analysis-data: data/processed/analysis_data.parquet

data/processed/analysis_data.parquet: data/processed/cleaned_data.parquet src/r/create_analysis_data.R
	@echo "Step 5: Creating analysis dataset for publication..."
	Rscript src/r/create_analysis_data.R
	@echo "✓ Analysis dataset created"

# Bot validity survey (requires OPENAI_API_KEY in .env)
bot-survey: data/processed/bot_survey.csv

data/processed/bot_survey.csv: src/python/bot_survey.py
	@echo "Running bot validity survey via GPT-4o logprobs..."
	.venv/bin/python3.14 src/python/bot_survey.py
	@echo "✓ Bot survey saved to data/processed/bot_survey.csv"

# Step 6: Analyze extreme cases
extreme-cases: output/extreme_cases.csv

output/extreme_cases.csv: data/processed/cleaned_data.parquet src/r/analyze_extreme_cases.R
	@echo "Step 6: Analyzing extreme cases..."
	Rscript src/r/analyze_extreme_cases.R
	@echo "✓ Extreme cases analyzed"

# Aggregate analysis target
analysis: analysis-data extreme-cases
	@echo "✓ All analyses complete"

# Step 7: Render HTML report
report-html: analysis/report.html

analysis/report.html: analysis/report.qmd data/processed/cleaned_data.parquet data/processed/conversation_metrics.parquet
	@echo "Step 7: Rendering HTML report..."
	cd analysis && quarto render report.qmd --to html
	@echo "✓ HTML report generated: analysis/report.html"

# Step 8: Render PDF report
report-pdf: analysis/report.pdf

analysis/report.pdf: analysis/report.qmd data/processed/cleaned_data.parquet data/processed/conversation_metrics.parquet
	@echo "Step 8: Rendering PDF report..."
	cd analysis && quarto render report.qmd --to pdf
	@echo "✓ PDF report generated: analysis/report.pdf"

# Render both reports
report: report-html report-pdf
	@echo "✓ All reports generated"
	@echo ""
	@echo "  - HTML: analysis/report.html"
	@echo "  - PDF:  analysis/report.pdf"

# Step 9: Render presentation slides
slides: analysis/slides.pdf

analysis/slides.pdf: analysis/slides.qmd data/processed/cleaned_data.parquet data/processed/conversation_metrics.parquet
	@echo "Step 9: Rendering presentation slides..."
	cd analysis && quarto render slides.qmd --to beamer
	@echo "✓ Slides generated: analysis/slides.pdf"

# Sync HTML reports into docs/ for GitHub Pages
docs: analysis/report.html
	@echo "Syncing reports to docs/ for GitHub Pages..."
	cp analysis/report.html docs/s1-report.html
	cp "t2 new dv pilot/code.html" docs/p2-pilot.html
	cp "t2 new dv pilot/t3 experiment pilot/code.html" docs/p2-conditions.html
	cp studies/README.md docs/registry.md
	@echo "✓ docs/ updated — push to deploy"

# Development: quick HTML-only render (faster for iteration)
dev: data
	@echo "Development mode: HTML report only..."
	cd analysis && quarto render report.qmd --to html
	@echo "✓ Development report ready: analysis/report.html"
