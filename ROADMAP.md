# ROADMAP.md — 8-Week Plan (Solo)

> Every task has an ID (`P<phase>-<nn>`). `PROGRESS.md` tracks the same IDs. Names, paths, and
> tables follow `AGENTS.md`. Dates assume Week 1 starts **Mon 2026-10-05**. Shift them all if your
> start date differs.
>
> **Ordering principle:** data, model, and evaluation come first, because these are graded the
> heaviest. The API and batch scoring are finished **before** any UI work, so the UI (which waits
> on your design references) never blocks anything else. Week 8 is reserved for the report, PPT,
> and viva.

---

## Timeline overview

| Week | Dates | Phase(s) | Main output |
|---|---|---|---|
| 1 | Oct 05 – Oct 11 | **P0** Setup & Planning · **P1** Ingestion & SQL | Env ready, data in PostgreSQL `raw`, synopsis submitted |
| 2 | Oct 12 – Oct 18 | **P2** Cleaning & Data Quality | `staging.encounters`, data-quality report |
| 3 | Oct 19 – Oct 25 | **P3** EDA & Statistical Analysis | EDA figures, stats tests, insight summary |
| 4 | Oct 26 – Nov 01 | **P4** Feature Engineering & Baselines | `features.model_input`, baseline comparison |
| 5 | Nov 02 – Nov 08 | **P5** Tuning, Evaluation & Explainability | Final model, metrics, model card |
| 6 | Nov 09 – Nov 15 | **P6** Batch Scoring, Analytics Views & API | `ml.predictions`, CSV exports, working FastAPI |
| 7 | Nov 16 – Nov 22 | **P7** Power BI Dashboard + Frontend (gated) | `.pbix` dashboard, Next.js app from designs |
| 8 | Nov 23 – Nov 29 | **P8** Testing, Report, PPT & Viva | Submission package |

```
W1 ███ P0 ██ P1
W2        ████████ P2
W3                 ████████ P3
W4                          ████████ P4
W5                                   ████████ P5
W6                                            ████████ P6
W7                                                     ████ P7 (Power BI) ░░░░ P7 (UI, gated on designs)
W8                                                              ████████ P8
```

### Critical path
`P1-03 ingest` → `P2-02 staging` → `P4-01 features` → `P4-02 split` → `P5-01 tuning` → `P5-07 final test` → `P6-01 batch scoring` → `P6-02 views` → `P7-01 Power BI` → `P8-04 report`

### Cut list (if you fall behind, drop in this order)
1. Optional XGBoost/LightGBM (`P5-01` extra)
2. SMOTE comparison (`P5-02`)
3. `/predict/batch` endpoint (`P6-07` partial)
4. SHAP per-patient factors (fall back to LR contributions)
5. Power BI page 7 (merge drivers into page 5)

**Never cut:** grouped split, leakage checklist, test-set evaluation, disclaimer, report.

---

## Phase 0 — Setup & Planning · Week 1 (Mon–Wed)

**Goal:** a working environment and the project formally approved.

| ID | Task | Details / acceptance criteria |
|---|---|---|
| P0-01 | Initialise repo & folder structure | `git init`. Create the full tree from AGENTS.md §3 (empty dirs get `.gitkeep`). Add `.gitignore` (`.venv/`, `data/**`, `!data/**/.gitkeep`, `models/*/model.joblib`, `.env`, `node_modules/`, `.next/`, `__pycache__/`, `.ipynb_checkpoints/`). First commit |
| P0-02 | Python environment | Python 3.12 venv in `.venv`. Write `requirements.txt` (see `docs/environment_setup.md`) and `pyproject.toml`. `pip install -e .`. `python -c "import readmission"` works |
| P0-03 | PostgreSQL 16 | `docker compose up -d` **or** Postgres.app/Homebrew. Create role `readmit` and DB `readmission_db`. `.env` + `.env.example` with `DATABASE_URL`. `psql $DATABASE_URL -c 'select 1'` works |
| P0-04 | Node.js & tooling | Node LTS (via `nvm`), VS Code + Python, Jupyter, Ruff, SQLTools, ESLint, and Tailwind extensions. Install pgAdmin or DBeaver |
| P0-05 | Download dataset | UCI id 296 → `data/raw/diabetic_data.csv`, `data/raw/IDs_mapping.csv`. Record the SHA-256 and row count in `MEMORY.md` |
| P0-06 | Core reading | Read Strack 2014 (dataset paper), Kansagara 2011, van Walraven 2010 (LACE), Donzé 2013 (HOSPITAL). Fill their entries in `literature/annotated_bibliography.md` |
| P0-07 | Synopsis | Finalise `docs/academic/synopsis.md` and submit it to your guide |
| P0-08 | Decide Power BI platform | Lab PC / Windows VM / Power BI Service web. Record the choice in MEMORY.md D-0xx. Test-open Power BI once |
| P0-09 | Get college templates | Report format, citation style, PPT template, deadlines → MEMORY.md §5 |
| P0-10 | Config & DB helpers | `src/readmission/config.py` (paths, `RANDOM_STATE=42`, column lists), `src/readmission/db.py` (engine from `DATABASE_URL`), `Makefile` skeleton with the target names from AGENTS.md §9 |

**Exit criteria:** `make setup` and `make db-up` work, the dataset is in `data/raw/`, and the synopsis has been sent.

---

## Phase 1 — Data Ingestion & SQL Foundation · Week 1 (Thu–Sun)

**Goal:** raw data loaded unchanged into PostgreSQL, and the schemas created.

| ID | Task | Details / acceptance criteria |
|---|---|---|
| P1-01 | `sql/00_create_schemas.sql` | `CREATE SCHEMA IF NOT EXISTS raw, staging, features, ml, analytics;` |
| P1-02 | `sql/01_raw_tables.sql` | `raw.diabetic_data` with all 50 columns as TEXT (original names, quoted). `raw.ids_mapping (line_no INT, col1 TEXT, col2 TEXT)` |
| P1-03 | `src/readmission/data/ingest.py` | Stream the CSV into `raw.diabetic_data` with `COPY ... FROM STDIN WITH CSV HEADER` (psycopg). Load `IDs_mapping.csv` line-by-line into `raw.ids_mapping`. Idempotent (`TRUNCATE` first). Logs row counts |
| P1-04 | `sql/02_dim_tables.sql` | Parse `raw.ids_mapping` into `staging.dim_admission_type`, `staging.dim_discharge_disposition`, `staging.dim_admission_source` (id INT PK, description TEXT) |
| P1-05 | Load verification | `SELECT count(*)` = 101,766. 50 columns. `encounter_id` distinct = row count. Dim tables have 8 / 26 / 17 rows (approx; record the actual values) |
| P1-06 | Notebook `01_data_understanding.ipynb` | Shape, dtypes, `value_counts` for every categorical, target distribution (`<30`/`>30`/`NO`), encounters per patient, first observations |
| P1-07 | `sql/04_ml_tables.sql` | Create `ml.model_registry`, `ml.predictions`, `ml.feature_importance`, `ml.prediction_log` (definitions in `docs/database_schema.md`) |

**Exit criteria:** `make db-init && make ingest` works from scratch and reproduces the exact row counts.

---

## Phase 2 — Data Cleaning & Data Quality · Week 2

**Goal:** a clean, typed, documented `staging.encounters`, with every cleaning decision justified.

| ID | Task | Details / acceptance criteria |
|---|---|---|
| P2-01 | `sql/99_quality_checks.sql` (audit) | Per column: `?` count, NULL count, distinct count. Duplicate `encounter_id`. Out-of-range numerics. Invalid gender. Results saved as CSV in `reports/eda/` |
| P2-02 | `sql/03_staging_encounters.sql` | Implement rules **C1–C13** (AGENTS.md §5). Rename columns to snake_case. Cast types. Join dims for descriptions. `CREATE TABLE staging.encounters AS ...` (drop & recreate) |
| P2-03 | Notebook `02_data_quality_cleaning.ipynb` | Pull raw and staging. Assert each rule held (no `?`, no hospice/expired, no invalid gender, types correct). Rows before → after per rule |
| P2-04 | `src/readmission/data/quality.py` | Generates `reports/eda/data_quality_report.md`: missingness table, rule-by-rule impact, final shape (expected ≈ 99.3k rows) |
| P2-05 | `tests/test_cleaning.py` | Small fixture DataFrame/SQL. Checks that `?` → NULL, `None` → `NotMeasured`, hospice rows removed |
| P2-06 | Update `docs/data_dictionary.md` | Final cleaned column list, types, allowed values, % missing |
| P2-07 | Literature: ML papers | Read Huang 2021 (scoping review) and Artetxe 2018. Add to the bibliography |

**Exit criteria:** `make stage` reproduces `staging.encounters`, and the data-quality report exists.

---

## Phase 3 — Exploratory Data Analysis & Statistical Analysis · Week 3

**Goal:** understand which factors relate to readmission, with evidence (figures and tests).

| ID | Task | Details / acceptance criteria |
|---|---|---|
| P3-01 | Univariate analysis | Target imbalance chart. Distributions of age, LOS, lab procedures, medications, prior visits → `reports/figures/03_*.png` |
| P3-02 | Categorical vs readmission rate | Rate (%) with 95% CI by age, race, gender, admission type, discharge group, admission source, specialty, A1C, glucose, insulin, change, diabetesMed |
| P3-03 | Numeric vs target | Box/violin plots. Readmission rate by binned `number_inpatient`, `number_emergency`, `time_in_hospital`, `num_medications` |
| P3-04 | `src/readmission/features/icd9.py` + tests | ICD-9 grouping from AGENTS.md §6.2. `tests/test_icd9.py` covers 250.83 → Diabetes, V57 → Other, 786 → Respiratory, None → Missing |
| P3-05 | Diagnosis analysis | Readmission rate by `diag_1_group`. Top 15 raw primary diagnoses |
| P3-06 | Correlation & multicollinearity | Spearman heatmap of numeric features. Optional VIF |
| P3-07 | Statistical tests (notebook `04_statistical_analysis.ipynb`) | Chi-square + Cramér's V (categorical), Mann-Whitney U + effect size (numeric), Bonferroni correction → `reports/eda/stats_tests.csv` |
| P3-08 | Odds ratios | Multivariable logistic regression (statsmodels) on key factors. Table of OR + 95% CI. Comment on HbA1c (cf. Strack 2014) |
| P3-09 | EDA summary | `reports/eda/eda_summary.md`: top 10 findings in plain language (feeds report chapter 5 and the PPT) |
| P3-10 | SQL analytics prototypes | Write the GROUP BY queries that will become `analytics.vw_*` (rates by demographic / diagnosis / admission). Save drafts in `sql/05_analytics_views.sql` |

**Exit criteria:** ≥ 12 saved figures, `stats_tests.csv`, `eda_summary.md`.

---

## Phase 4 — Feature Engineering & Baseline Models · Week 4

**Goal:** a model-ready table, a leak-proof split, and honest baselines.

| ID | Task | Details / acceptance criteria |
|---|---|---|
| P4-01 | `src/readmission/features/build.py` | Build every feature in AGENTS.md §6.1 from `staging.encounters` → `features.model_input` (Postgres) + `data/processed/model_input.parquet` |
| P4-02 | `src/readmission/features/split.py` | Patient-grouped stratified 70/15/15 split (seed 42). Writes the `split` column. `tests/test_split.py`: zero patient overlap, positive rate per split within ±1 pt |
| P4-03 | `src/readmission/models/pipeline.py` | `build_preprocessor()`, `build_model(key)` for `dummy`, `logreg`, `dtree`, `rf`, `hgb` (AGENTS.md §7.1–7.2) |
| P4-04 | Baselines (notebook `05_baseline_models.ipynb`) | 5-fold `StratifiedGroupKFold` CV on train for `dummy`, `logreg`, `dtree`. Metrics: ROC-AUC, PR-AUC, recall, precision, F1 |
| P4-05 | Stronger defaults | Same CV for `rf`, `hgb` with default params → `reports/metrics/model_comparison.csv` |
| P4-06 | Leakage checklist | Run every item in AGENTS.md §6.4. Record the result in MEMORY.md |
| P4-07 | `tests/test_pipeline.py` | Fit/predict on a 2k-row sample. Output probabilities lie in [0, 1]. Unseen categories don't crash |
| P4-08 | Literature review draft | First full draft of `literature/literature_review.md` |

**Exit criteria:** a comparison table showing `hgb`/`rf`/`logreg` beating `dummy`, with ROC-AUC in the realistic range.

---

## Phase 5 — Tuning, Evaluation & Explainability · Week 5

**Goal:** a final, calibrated, explained model with an honest test-set evaluation.

| ID | Task | Details / acceptance criteria |
|---|---|---|
| P5-01 | Hyperparameter tuning (notebook `06_model_tuning.ipynb`, `train.py`) | `RandomizedSearchCV` (≈30–50 iterations), group CV, `scoring="roc_auc"` for `logreg`, `rf`, `hgb` (optional `xgb`). Save `reports/metrics/cv_results.csv` |
| P5-02 | Imbalance comparison | class_weight vs none vs (optional) SMOTE-in-pipeline. Compare PR-AUC and recall |
| P5-03 | Calibration | Isotonic vs sigmoid `CalibratedClassifierCV` with group splits. Calibration curve + Brier score → `reports/figures/07_calibration.png` |
| P5-04 | Threshold & tiers | On **val**: choose the threshold maximising F2 with recall ≥ 0.60. Tier cutoffs at the p70/p90 val probabilities → `thresholds.json`. Report the observed readmission rate per tier |
| P5-05 | Explainability (`explain.py`) | Permutation importance (val). LR odds ratios. Optional SHAP summary plot. Per-patient top-5 factor function (used by the API) |
| P5-06 | Fairness (`fairness.py`) | Recall / precision / AUC by race, gender, age_group → `reports/metrics/fairness.csv`. Comment on gaps |
| P5-07 | **Final test evaluation (run once)** | Apply the final model and threshold to **test**. ROC curve, PR curve, confusion matrix, metrics table → `metrics.json`, `reports/figures/07_*.png` |
| P5-08 | Persist & register | Save `models/<model_version>/` (all files in AGENTS.md §7.5), insert the `ml.model_registry` row, write `models/CURRENT`, save top features to `ml.feature_importance` |
| P5-09 | Model card | `reports/model_card.md`: intended use, data, metrics, threshold, tiers, fairness, limitations, disclaimer |

**Exit criteria:** `make train && make evaluate` reproduces the model. The model card is written. The experiment log in MEMORY.md is filled.

---

## Phase 6 — Batch Scoring, Analytics Views & API · Week 6

**Goal:** predictions are in the database, Power BI-ready CSVs exist, and a working, tested FastAPI is up.

| ID | Task | Details / acceptance criteria |
|---|---|---|
| P6-01 | Batch scoring (`predict.py --batch`) | Score every encounter in `features.model_input` → `ml.predictions` (probability, risk_tier, predicted_label, actual_label, split, model_version, scored_at) |
| P6-02 | `sql/05_analytics_views.sql` | All 10 `analytics.vw_*` views (AGENTS.md §8, columns in `docs/database_schema.md`) |
| P6-03 | `src/readmission/export/powerbi.py` | Each view → `powerbi/data/<view_name>.csv`, plus `patients_scored.csv` (ml.predictions joined with key features: the Power BI fact table), plus `powerbi/data/README.md` with the export timestamp and model_version |
| P6-04 | FastAPI skeleton | `backend/app/main.py`, `core/config.py`, CORS for `http://localhost:3000`, `/api/v1/health` |
| P6-05 | `services/model_service.py` | Loads `models/CURRENT` at startup. `predict_one(dict)` → probability, tier, top factors. Builds features from raw-style input using the **same** `build.py` functions |
| P6-06 | Model routes | `/model/info`, `/model/metrics`, `/model/feature-importance` |
| P6-07 | Prediction routes | `/predict` (Pydantic `PatientInput` with enums and ranges), `/predict/batch` (CSV). Log to `ml.prediction_log`. Include the disclaimer |
| P6-08 | Data routes | `/patients/high-risk` (pagination + filters), `/stats/overview` |
| P6-09 | API tests & types | `backend/tests/` with TestClient: health, valid predict, invalid input → 422, batch. Export `openapi.json`. Generate TS types for the frontend (`openapi-typescript`) |

**Exit criteria:** `make score && make views && make export-bi` works. `make api` serves `/docs`, and every endpoint returns the documented shapes.

---

## Phase 7 — Power BI Dashboard + Frontend · Week 7

**Goal:** a decision-support dashboard, and a web app that replicates your designs.

### 7A — Power BI (not gated)
| ID | Task | Details / acceptance criteria |
|---|---|---|
| P7-01 | Data model | Import `powerbi/data/*.csv` (or connect to PostgreSQL if on Windows). Set relationships. DAX measures (Readmission Rate, Encounters, Avg LOS, High-Risk Count, Recall, Precision) |
| P7-02 | Pages 1–4 | Executive Overview, Patient Demographics, Clinical Factors, Admissions & Utilisation (spec in `docs/powerbi_dashboard.md`) |
| P7-03 | Pages 5–7 | Model Performance, Risk Stratification & High-Risk List, Key Risk Drivers |
| P7-04 | Polish | Slicers, drill-through to the patient list, tooltips, `powerbi/theme.json`. Export page screenshots/PDF → `reports/figures/powerbi_*.png` |

### 7B — Frontend (GATED: starts only when `design-references/` has the designs)
| ID | Task | Details / acceptance criteria |
|---|---|---|
| P7-05 | Intake design references | Inventory the screens. Extract tokens (colours, fonts, spacing, radii). List missing states and **ask the user**. Record the answers in MEMORY.md |
| P7-06 | Next.js scaffold | `frontend/` with App Router, TypeScript, Tailwind. Tokens in config/CSS variables. `src/lib/api.ts` using the generated types. Env `NEXT_PUBLIC_API_URL` |
| P7-07 | Build screens | Pixel-match each reference screen (components first, then pages) |
| P7-08 | Wire to API | Forms → `/predict`. Lists → `/patients/high-risk`. KPIs → `/stats/overview`. Loading/error states per the designs. Disclaimer shown |
| P7-09 | Visual QA | Side-by-side screenshots of the references vs the build at each breakpoint. Fix diffs. Save the comparisons in `reports/figures/ui_*.png` |

**Exit criteria:** the `.pbix` file is saved with 7 pages. If designs were received, the web app runs end-to-end against the API.

---

## Phase 8 — Testing, Documentation, Report & Viva · Week 8

| ID | Task | Details / acceptance criteria |
|---|---|---|
| P8-01 | Clean-room run | Drop the DB → `make db-init && make pipeline` → everything regenerates. Fix any breakage |
| P8-02 | Quality gate | `make test` green. `ruff check` clean. Notebooks run top-to-bottom |
| P8-03 | README | Overview, architecture diagram, quickstart, screenshots, results table, limitations |
| P8-04 | Final report | Follow `docs/academic/report_outline.md`. Figures from `reports/figures/`. Export to PDF |
| P8-05 | Presentation | Follow `docs/academic/ppt_viva_outline.md` (≈15 slides) |
| P8-06 | Viva preparation | Rehearse the Q&A in `docs/academic/ppt_viva_outline.md`. Be ready to explain every metric and decision |
| P8-07 | Demo script + backup video | 5-minute live demo flow (Power BI → web app predict → explain). Record a backup screen capture |
| P8-08 | Submission package | Code (GitHub/zip without data), report PDF, PPT, `.pbix`, model card, README |
| P8-09 | Verify citations | Check every reference in `literature/` against its DOI/PubMed entry. Format in the required style |

**Exit criteria:** everything submitted, and the demo rehearsed twice.

---

## Dependencies & risks

| Risk | Impact | Mitigation |
|---|---|---|
| Power BI unavailable on macOS | Dashboard blocked | CSV export path (P6-03). Decide the platform in P0-08 |
| Design references arrive late | UI blocked | UI is the last phase and fully gated. The API, Power BI, and Swagger `/docs` still demo the system |
| Low model performance (AUC ≈ 0.65) | Looks "weak" | Expected for this data. Frame it with the literature (LACE C ≈ 0.68). Emphasise the tier lift and recall |
| Leakage producing fake-high scores | Invalid results | Grouped split + checklist P4-06 |
| Docker issues on Mac | DB setup delay | Postgres.app fallback |
| Scope creep | Missed deadline | Cut list above |
