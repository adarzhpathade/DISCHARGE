# Makefile — Hospital Readmission Risk Prediction System (DISCHARGE)
# Follows AGENTS.md §9 targets exactly

.PHONY: help setup db-up db-init ingest stage features train evaluate score views export-bi api web test pipeline

help:
	@echo "Available commands:"
	@echo "  make setup      - Install dependencies and package in editable mode"
	@echo "  make db-up      - Start PostgreSQL via docker compose"
	@echo "  make db-init    - Run schema and table initialization SQL scripts"
	@echo "  make ingest     - Ingest raw CSV data into raw.* tables"
	@echo "  make stage      - Clean and stage encounters (C1-C13 rules)"
	@echo "  make features   - Build engineered features and stratified split"
	@echo "  make train      - Train scikit-learn models (logreg, rf, hgb)"
	@echo "  make evaluate   - Evaluate active model metrics"
	@echo "  make score      - Batch score encounters into ml.predictions"
	@echo "  make views      - Create analytics.vw_* views"
	@echo "  make export-bi  - Export analytics views and scored fact table to CSV for Power BI"
	@echo "  make api        - Start FastAPI development server (port 8000)"
	@echo "  make web        - Start Next.js development server (port 3000)"
	@echo "  make test       - Run test suite (pytest)"
	@echo "  make pipeline   - Run full pipeline: ingest -> stage -> features -> train -> evaluate -> score -> views -> export-bi"

setup:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .

db-up:
	docker compose up -d

db-init:
	python -c "from readmission.db import execute_sql_file; [execute_sql_file(f'sql/{f}.sql') for f in ['00_create_schemas', '01_raw_tables', '02_dim_tables', '04_ml_tables']]"

ingest:
	python -m readmission.data.ingest

stage:
	python -c "from readmission.db import execute_sql_file; execute_sql_file('sql/03_staging_encounters.sql'); execute_sql_file('sql/99_quality_checks.sql')"

features:
	python -m readmission.features.build

train:
	python -m readmission.models.train --models logreg rf hgb

evaluate:
	python -m readmission.models.evaluate

score:
	python -m readmission.models.predict --batch

views:
	python -c "from readmission.db import execute_sql_file; execute_sql_file('sql/05_analytics_views.sql')"

export-bi:
	python -m readmission.export.powerbi

api:
	uvicorn backend.app.main:app --reload --port 8000

web:
	cd frontend && npm run dev

test:
	pytest tests backend/tests

eda:
	python -m readmission.eda_pipeline

pipeline: ingest stage features train evaluate score views export-bi
