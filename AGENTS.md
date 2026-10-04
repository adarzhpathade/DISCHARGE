# AGENTS.md — Hospital Readmission Risk Prediction System

> **Read this file first.** It is the single source of truth for this repository.
> Every other context file, doc, and generated file must use the names, paths, tables, IDs,
> and conventions defined here. If something here conflicts with another file, **this file wins**;
> fix the other file. If you change a decision, update this file **and** log it in `MEMORY.md`.

---

## 1. Project at a glance

| Item | Value |
|---|---|
| Project | Hospital Readmission Risk Prediction System (college **minor project**) |
| Team | Solo developer |
| Timeline | 8 weeks — Week 1 starts **Mon 2026-10-05**, Week 8 ends **Sun 2026-11-29** |
| Goal | Estimate the **probability of unplanned readmission within 30 days of discharge** for a patient, using only information available **at or before discharge** |
| Nature | **Decision-support tool.** It produces a risk estimate, never a certain prediction or a diagnosis |
| Dataset | UCI **Diabetes 130-US Hospitals (1999–2008)**, about 101,766 encounters, 50 columns |
| Database | **PostgreSQL 16**, database `readmission_db` |
| Data / ML | Python 3.12, Pandas, NumPy, SciPy, statsmodels, **scikit-learn** (core), matplotlib/seaborn, joblib. Optional: SHAP, XGBoost, LightGBM |
| Backend | **FastAPI** + Pydantic v2 + SQLAlchemy 2 + psycopg 3, served by uvicorn |
| Frontend | **Next.js** (latest stable, App Router, TypeScript, Tailwind CSS). **The UI is built ONLY from user-supplied design references (see §11)** |
| BI | **Power BI** dashboard, fed from PostgreSQL `analytics` views exported to CSV (see §12) |
| Dev OS | macOS (Apple Silicon assumed). Power BI Desktop is Windows-only, see §12 |

### Problem in one paragraph
Hospital readmissions raise costs, occupy beds, and strain staff and resources. Hospitals hold
historical records where the outcome (readmitted in under 30 days or not) is known. We clean and
analyse that data (SQL + Pandas/NumPy), run EDA and statistical tests, and train scikit-learn
classifiers evaluated with Precision, Recall, F1, ROC-AUC, and PR-AUC, with emphasis on **recall
for high-risk patients**. We serve the model through a FastAPI service and a Next.js web app, and
present trends, risk distributions, drivers, and predictions in Power BI. The output supports
**follow-up prioritisation and resource planning**.

---

## 2. Non-negotiable rules for any agent working here

1. **Honesty framing.** Never claim the model "knows" or "predicts with certainty" that a patient will return. Always say *risk estimate* or *probability*. Every prediction response and UI result must carry the disclaimer in §10.4.
2. **Realistic performance.** On this dataset, a good model gets **ROC-AUC ≈ 0.64–0.70**. Do not claim 0.90+ results. A suspiciously high score means **leakage**, so investigate it (see §6.4).
3. **No leakage.** Split by **`patient_nbr` groups**, never by row. Fit every transformation (imputation, encoding, scaling) inside an sklearn `Pipeline` on training data only. Never use `readmitted` or anything derived from post-discharge events as a feature.
4. **The test set is touched once.** Use it only for the final evaluation in Phase 5 (task `P5-07`). All tuning and threshold selection happen on train (CV) and validation.
5. **Reproducibility.** `RANDOM_STATE = 42` everywhere. Pin package versions in `requirements.txt`. Every trained model saves its metadata (§7.5).
6. **Never invent UI.** Do not design screens, colours, fonts, or layouts. Wait for files in `design-references/` and replicate them exactly (§11).
7. **Core ML is scikit-learn.** XGBoost/LightGBM are optional extras and are never required for the pipeline to run.
8. **No secrets in git.** DB credentials live in `.env` (gitignored). Commit only `.env.example`.
9. **Keep trackers in sync.** When you finish a task, tick it in `PROGRESS.md` (using the ID from `ROADMAP.md`) and add any non-obvious decision or gotcha to `MEMORY.md`.
10. **Data files are not committed.** `data/` contents and `models/*/model.joblib` are gitignored.

---

## 3. Directory structure (canonical)

```
Adarzsh/                                  # repo root
├── AGENTS.md                             # ← this file (source of truth)
├── MEMORY.md                             # decisions log, gotchas, current state
├── ROADMAP.md                            # phases, tasks (IDs P0-01 …), deliverables
├── PROGRESS.md                           # checkbox tracker mirroring ROADMAP task IDs
├── README.md                             # short public-facing overview + quickstart
├── .env.example                          # DB + API config template
├── .gitignore
├── requirements.txt                      # pinned Python deps (data/ML + backend)
├── Makefile                              # one-command pipeline steps (§9)
├── docker-compose.yml                    # PostgreSQL 16 service (optional path)
│
├── data/                                 # gitignored contents
│   ├── raw/                              # diabetic_data.csv, IDs_mapping.csv (untouched)
│   ├── interim/                          # temporary dumps during cleaning
│   └── processed/                        # model_input.parquet, splits
│
├── sql/
│   ├── 00_create_schemas.sql             # raw, staging, features, ml, analytics
│   ├── 01_raw_tables.sql                 # raw.* tables, ALL columns TEXT
│   ├── 02_dim_tables.sql                 # staging.dim_* lookup tables from IDs_mapping
│   ├── 03_staging_encounters.sql         # typed + cleaned staging.encounters
│   ├── 04_ml_tables.sql                  # ml.model_registry, ml.predictions, ...
│   ├── 05_analytics_views.sql            # analytics.vw_* for Power BI + API stats
│   └── 99_quality_checks.sql             # row counts, nulls, duplicates, ranges
│
├── src/readmission/                      # installable package (pip install -e .)
│   ├── __init__.py
│   ├── config.py                         # paths, RANDOM_STATE, column lists, env loading
│   ├── db.py                             # SQLAlchemy engine factory
│   ├── data/
│   │   ├── ingest.py                     # CSV → raw.* (COPY)
│   │   ├── load.py                       # read staging/features tables into DataFrames
│   │   └── quality.py                    # data-quality report (Python side)
│   ├── features/
│   │   ├── icd9.py                       # ICD-9 → diagnosis group mapping
│   │   ├── build.py                      # staging.encounters → features.model_input
│   │   └── split.py                      # patient-grouped train/val/test split
│   ├── models/
│   │   ├── pipeline.py                   # ColumnTransformer + estimator factories
│   │   ├── train.py                      # CV, tuning, calibration, saving artifacts
│   │   ├── evaluate.py                   # metrics, curves, threshold & tier selection
│   │   ├── explain.py                    # permutation importance, SHAP, per-patient factors
│   │   ├── fairness.py                   # subgroup metrics (race, gender, age_group)
│   │   └── predict.py                    # load model + score DataFrame / single record
│   └── export/
│       └── powerbi.py                    # analytics.vw_* → powerbi/data/*.csv
├── pyproject.toml                        # makes src/readmission installable
│
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_quality_cleaning.ipynb
│   ├── 03_eda.ipynb
│   ├── 04_statistical_analysis.ipynb
│   ├── 05_baseline_models.ipynb
│   ├── 06_model_tuning.ipynb
│   └── 07_evaluation_explainability.ipynb
│
├── models/                               # artifacts; model.joblib gitignored
│   ├── CURRENT                           # text file: active model_version
│   └── <model_version>/                  # e.g. v20261106_hgb/
│       ├── model.joblib
│       ├── metadata.json
│       ├── metrics.json
│       ├── thresholds.json
│       └── feature_importance.csv
│
├── reports/
│   ├── figures/                          # EDA + evaluation PNGs (used in report/PPT)
│   ├── metrics/                          # model_comparison.csv, fairness.csv, cv_results.csv
│   ├── eda/                              # data_quality_report.md, stats_tests.csv, eda_summary.md
│   └── model_card.md                     # intended use, metrics, limits, fairness (P5-09)
│
├── backend/
│   ├── app/
│   │   ├── main.py                       # FastAPI app, CORS, router include
│   │   ├── core/config.py                # pydantic-settings
│   │   ├── api/routes/                   # health.py, model.py, predict.py, patients.py, stats.py
│   │   ├── schemas/                      # patient.py, prediction.py, model.py, stats.py
│   │   └── services/                     # model_service.py, db_service.py
│   └── tests/                            # pytest + httpx TestClient
│
├── frontend/                             # Next.js app, built ONLY from design-references/
│   └── src/
│       ├── app/                          # routes (defined by designs)
│       ├── components/
│       └── lib/api.ts                    # typed client for §10 API
│
├── powerbi/
│   ├── data/                             # CSV exports: one per analytics.vw_* + patients_scored.csv (fact table)
│   ├── readmission_dashboard.pbix
│   └── theme.json
│
├── design-references/                    # USER-SUPPLIED UI designs (screens, tokens, Figma links)
│   └── README.md
│
├── tests/                                # pytest for src/readmission
│
├── docs/
│   ├── MODEL_TRAINING_GUIDE.md           # step-by-step: raw data → trained model → predictions
│   ├── architecture.md
│   ├── environment_setup.md
│   ├── data_dictionary.md
│   ├── database_schema.md
│   ├── api_contract.md
│   ├── powerbi_dashboard.md
│   └── academic/
│       ├── synopsis.md
│       ├── report_outline.md
│       └── ppt_viva_outline.md
│
└── literature/
    ├── README.md                         # how to use this folder + PDF naming convention
    ├── annotated_bibliography.md
    ├── literature_review.md
    └── papers/                           # downloaded PDFs
```

---

## 4. Dataset facts (UCI Diabetes 130-US Hospitals, 1999–2008)

- **Source:** UCI ML Repository, dataset id **296** ("Diabetes 130-US Hospitals for Years 1999–2008"). Kaggle mirrors exist. Files: `diabetic_data.csv` (≈101,766 rows × 50 cols) and `IDs_mapping.csv` (three lookup tables stacked in one file, separated by blank lines).
- **Paper:** Strack B. et al., *Impact of HbA1c Measurement on Hospital Readmission Rates: Analysis of 70,000 Clinical Database Patient Records*, BioMed Research International, 2014, Article 781670. doi:10.1155/2014/781670.
- **Unit of observation:** one row per **encounter** (`encounter_id`, unique). One patient (`patient_nbr`) can have many encounters. About 71.5k unique patients.
- **Target source column:** `readmitted` ∈ {`<30`, `>30`, `NO`}. **Our target: `readmitted_30d = 1 if readmitted == '<30' else 0`.** Prevalence is about **11%**, so the data is imbalanced.
- **Missing-value marker:** `?` (string).
- **⚠ The `"None"` gotcha:** In `A1Cresult` and `max_glu_serum`, the string `None` means **"test not performed"**, which is a real category and not missing data. pandas ≥ 2.0 treats `"None"` as NaN by default. **Always read with `keep_default_na=False, na_values=["?"]`**, then map `None`/NaN → `NotMeasured`. The `ucimlrepo` package version may already contain NaN for these columns, so map NaN → `NotMeasured` as well.
- **Columns (50):**
  - IDs: `encounter_id`, `patient_nbr`
  - Demographics: `race`, `gender`, `age` (10-year buckets like `[70-80)`), `weight` (≈97% missing)
  - Admission: `admission_type_id`, `discharge_disposition_id`, `admission_source_id` (integer codes → `IDs_mapping.csv`)
  - Stay: `time_in_hospital` (1–14 days), `payer_code` (≈40% missing), `medical_specialty` (≈49% missing)
  - Counts: `num_lab_procedures`, `num_procedures`, `num_medications`, `number_outpatient`, `number_emergency`, `number_inpatient` (prior-year visits), `number_diagnoses`
  - Diagnoses: `diag_1`, `diag_2`, `diag_3` (ICD-9 codes, including `V`/`E` codes)
  - Labs: `max_glu_serum`, `A1Cresult`
  - 23 medication columns, each ∈ {`No`, `Steady`, `Up`, `Down`}: `metformin`, `repaglinide`, `nateglinide`, `chlorpropamide`, `glimepiride`, `acetohexamide`, `glipizide`, `glyburide`, `tolbutamide`, `pioglitazone`, `rosiglitazone`, `acarbose`, `miglitol`, `troglitazone`, `tolazamide`, `examide`, `citoglipton`, `insulin`, `glyburide-metformin`, `glipizide-metformin`, `glimepiride-pioglitazone`, `metformin-rosiglitazone`, `metformin-pioglitazone`
  - Flags: `change` (`Ch`/`No`), `diabetesMed` (`Yes`/`No`)
  - Target: `readmitted`
- **Limitation (state it in the report):** this data covers **diabetic inpatient encounters** in US hospitals from 1999 to 2008 only. Results may not generalise to other populations or to current practice.

---

## 5. Data cleaning rules (applied in `sql/03_staging_encounters.sql`, verified in notebook 02)

| # | Rule | Reason |
|---|---|---|
| C1 | Load raw CSV into `raw.diabetic_data` with **all columns TEXT** | Never lose data at load time; cast later |
| C2 | `'?'` → `NULL` in every column | Standardise missing values |
| C3 | Drop rows where `gender = 'Unknown/Invalid'` (3 rows) | Invalid entry |
| C4 | **Drop rows with `discharge_disposition_id IN (11, 13, 14, 19, 20, 21)`** (expired / hospice) | These patients cannot be readmitted, so keeping them biases the label |
| C5 | Assert `encounter_id` unique; dedupe if any duplicates appear | Data integrity |
| C6 | `race` NULL → `'Unknown'` | Keep rows, make missingness explicit |
| C7 | `medical_specialty` NULL → `'Missing'`; collapse to top 10 + `'Other'` in feature step | High cardinality |
| C8 | `A1Cresult`, `max_glu_serum` NULL/`'None'` → `'NotMeasured'` | "Not tested" is informative |
| C9 | Drop `weight` (≈97% missing) and `payer_code` (≈40% missing, administrative, not clinical) | Too sparse or irrelevant |
| C10 | Drop `examide`, `citoglipton` (constant `No`) | Zero variance |
| C11 | Cast numeric columns to INTEGER; range-check `time_in_hospital` 1–14 and counts ≥ 0 | Type safety, catch invalid values |
| C12 | `diag_*` NULL → `'Missing'`; keep codes as TEXT | ICD-9 contains letters (`V`, `E`) |
| C13 | Map `admission_type_id`, `discharge_disposition_id`, `admission_source_id` to descriptions through `staging.dim_*` | Readability in Power BI |

Every rule's row impact (rows before → after) must be logged in `reports/eda/data_quality_report.md`.

---

## 6. Feature engineering & splitting

### 6.1 Engineered features (built in `src/readmission/features/build.py` → table `features.model_input`)
| Feature | Definition |
|---|---|
| `age_mid` | Midpoint of the age bucket (`[70-80)` → 75) |
| `age_group` | `<40`, `40-59`, `60-79`, `80+` (used for fairness slices and Power BI) |
| `service_utilization` | `number_outpatient + number_emergency + number_inpatient` |
| `any_prior_inpatient` | `number_inpatient > 0` |
| `diag_1_group`, `diag_2_group`, `diag_3_group` | ICD-9 → {Circulatory, Respiratory, Digestive, Diabetes, Injury, Musculoskeletal, Genitourinary, Neoplasms, Other, Missing} (§6.2) |
| `num_meds_active` | Count of the 21 remaining medication columns ≠ `No` |
| `num_med_changes` | Count of medication columns ∈ {`Up`, `Down`} |
| `a1c_measured`, `glu_measured` | Lab result ≠ `NotMeasured` |
| `admission_type_grp` | Emergency / Urgent / Elective / Other-Unknown |
| `discharge_grp` | Home / Home-health / Facility (SNF/ICF/rehab) / Transfer-hospital / Other-Unknown |
| `admission_source_grp` | Emergency room / Referral / Transfer / Other-Unknown |
| `medical_specialty_grp` | Top 10 specialties + `Other` + `Missing` |
| `readmitted_30d` | **Target** (0/1) |
| `split` | `train` / `val` / `test` (§6.3) |

Kept as-is: `race`, `gender`, `time_in_hospital`, `num_lab_procedures`, `num_procedures`, `num_medications`, `number_outpatient`, `number_emergency`, `number_inpatient`, `number_diagnoses`, `max_glu_serum`, `A1Cresult`, the 21 medication columns, `change`, `diabetesMed`.
Identifier columns kept but **never used as features**: `encounter_id`, `patient_nbr`.

### 6.2 ICD-9 grouping (Strack et al. 2014)
| Group | ICD-9 codes |
|---|---|
| Circulatory | 390–459, 785 |
| Respiratory | 460–519, 786 |
| Digestive | 520–579, 787 |
| Diabetes | 250.xx |
| Injury | 800–999 |
| Musculoskeletal | 710–739 |
| Genitourinary | 580–629, 788 |
| Neoplasms | 140–239 |
| Other | everything else, including `V*` and `E*` codes |
| Missing | NULL / `?` |

### 6.3 Split strategy
- **Patient-grouped, stratified:** `StratifiedGroupKFold(n_splits=20, shuffle=True, random_state=42)` with `groups = patient_nbr`. Folds 0–2 → `test`, folds 3–5 → `val`, folds 6–19 → `train`.
- Proportions: **70% train / 15% val / 15% test** (by patient). Store the result in `features.model_input.split` and `data/processed/model_input.parquet`.
- **Cross-validation** inside train uses `StratifiedGroupKFold(n_splits=5)` with the same groups.
- Verify: zero `patient_nbr` overlap between splits, and similar positive rates (≈11%) in each split.

### 6.4 Leakage checklist (run before trusting any metric)
- [ ] No `patient_nbr` appears in more than one split
- [ ] `readmitted`, `readmitted_30d`, `encounter_id`, `patient_nbr` are excluded from `X`
- [ ] All encoders/scalers/imputers live inside the sklearn `Pipeline`
- [ ] The test set was not used in tuning, thresholding, or calibration
- [ ] ROC-AUC on val is within ≈0.62–0.72 (a much higher value means something leaked)

---

## 7. Modeling specification

### 7.1 Models (all scikit-learn)
| Key | Estimator | Notes |
|---|---|---|
| `dummy` | `DummyClassifier(strategy="stratified")` | Sanity floor |
| `logreg` | `LogisticRegression(class_weight="balanced", max_iter=2000)` | Interpretable baseline; tune `C`, penalty |
| `dtree` | `DecisionTreeClassifier(class_weight="balanced")` | Teaching baseline |
| `rf` | `RandomForestClassifier(class_weight="balanced_subsample", n_jobs=-1)` | |
| `hgb` | `HistGradientBoostingClassifier(class_weight="balanced")` | Expected best sklearn model |
| `xgb` *(optional)* | `XGBClassifier(scale_pos_weight≈8)` | Only if time allows |

### 7.2 Preprocessing (`src/readmission/models/pipeline.py`)
`ColumnTransformer`:
- numeric → `SimpleImputer(median)` → `StandardScaler` (scaling only needed for `logreg`)
- categorical → `SimpleImputer(constant="Missing")` → `OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=50, sparse_output=False)` (dense output, because HGB rejects sparse input)
- For `hgb`: `OrdinalEncoder` + `categorical_features` is allowed as an alternative

### 7.3 Imbalance
Primary approach: `class_weight` + **threshold tuning**. Optional comparison: `imblearn` SMOTE **inside** an `imblearn.pipeline.Pipeline` (never applied before splitting).

### 7.4 Evaluation & selection
- Metrics (on val during development, on test once at the end): **ROC-AUC, PR-AUC (average precision), Precision, Recall, F1, F2, Brier score**, confusion matrix, calibration curve.
- **Model selection metric:** mean CV **ROC-AUC** (tie-breaker: PR-AUC).
- **Calibration:** `CalibratedClassifierCV(method="isotonic" or "sigmoid")` with group-aware CV splits on train.
- **Decision threshold:** chosen on **val** to maximise **F2** (recall weighted 2×), with a floor of recall ≥ 0.60. Stored in `thresholds.json`.
- **Risk tiers** (for follow-up capacity planning), set by val-set probability percentiles:
  - **High** = top 10% of predicted probability
  - **Medium** = next 20% (70th–90th percentile)
  - **Low** = bottom 70%
  - Report the observed readmission rate per tier. High should be roughly 2–3× the base rate.
- **Flag vs tier are independent views of the same probability.** `flagged_for_follow_up = probability ≥ decision_threshold` is a recall-oriented screening flag and can cover 30–40% of patients. The tier is a capacity-oriented ranking (High = top 10%). A patient may be `Low`/`Medium` tier **and** flagged. The UI and API must never call the flag "high risk".
- **Fairness:** report recall, precision, and AUC by `race`, `gender`, `age_group` → `reports/metrics/fairness.csv`.
- **Explainability:** permutation importance (global), LR coefficients / odds ratios, and optionally SHAP (global + per-patient top 5 factors).

### 7.5 Artifacts (per trained model) in `models/<model_version>/`
- `model_version` format: `v<YYYYMMDD>_<key>`, e.g. `v20261106_hgb`
- `model.joblib` — the full fitted sklearn Pipeline (preprocessing + calibrated estimator)
- `metadata.json` — model_version, algorithm, hyperparameters, feature lists, training rows, positive rate, sklearn version, git commit, trained_at
- `metrics.json` — CV, val, and (final) test metrics
- `thresholds.json` — `{"decision_threshold": x, "tier_cutoffs": {"medium": p70, "high": p90}}`
- `feature_importance.csv` — feature, importance, method
- `models/CURRENT` holds the active `model_version` string. The API and batch scoring read it.
- Each model is also registered as a row in `ml.model_registry`.

---

## 8. Database (PostgreSQL 16, `readmission_db`)

| Schema | Objects |
|---|---|
| `raw` | `raw.diabetic_data` (50 TEXT cols), `raw.ids_mapping` (TEXT, as loaded) |
| `staging` | `staging.encounters` (clean, typed), `staging.dim_admission_type`, `staging.dim_discharge_disposition`, `staging.dim_admission_source` |
| `features` | `features.model_input` (engineered features + `readmitted_30d` + `split`) |
| `ml` | `ml.model_registry`, `ml.predictions`, `ml.feature_importance`, `ml.prediction_log` |
| `analytics` | `analytics.vw_readmission_overview`, `vw_readmission_by_demographics`, `vw_readmission_by_diagnosis`, `vw_readmission_by_admission`, `vw_utilization`, `vw_medication_summary`, `vw_risk_distribution`, `vw_model_performance`, `vw_feature_importance`, `vw_high_risk_patients` |

Full column-level definitions: `docs/database_schema.md`. Connection string env var: `DATABASE_URL=postgresql+psycopg://readmit:readmit@localhost:5432/readmission_db`.

---

## 9. Commands (Makefile targets — keep these names)

| Target | Does |
|---|---|
| `make setup` | create `.venv`, `pip install -r requirements.txt`, `pip install -e .` |
| `make db-up` | start PostgreSQL (docker compose) |
| `make db-init` | run `sql/00`–`02`, `04` |
| `make ingest` | `python -m readmission.data.ingest` (CSV → raw.*) |
| `make stage` | run `sql/03_staging_encounters.sql` + `sql/99_quality_checks.sql` |
| `make features` | `python -m readmission.features.build` |
| `make train` | `python -m readmission.models.train --models logreg rf hgb` |
| `make evaluate` | `python -m readmission.models.evaluate --version $(shell cat models/CURRENT)` |
| `make score` | `python -m readmission.models.predict --batch` → `ml.predictions` |
| `make views` | run `sql/05_analytics_views.sql` |
| `make export-bi` | `python -m readmission.export.powerbi` → `powerbi/data/*.csv` |
| `make api` | `uvicorn backend.app.main:app --reload --port 8000` |
| `make web` | `cd frontend && npm run dev` (port 3000) |
| `make test` | `pytest tests backend/tests` |
| `make pipeline` | ingest → stage → features → train → evaluate → score → views → export-bi |

---

## 10. API contract (summary — full spec in `docs/api_contract.md`)

Base URL: `http://localhost:8000/api/v1`

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness + DB + model loaded |
| GET | `/model/info` | model_version, algorithm, trained_at, threshold, tier cutoffs |
| GET | `/model/metrics` | val/test metrics from `metrics.json` |
| GET | `/model/feature-importance` | top-N global drivers |
| POST | `/predict` | single patient → probability, risk tier, top factors |
| POST | `/predict/batch` | CSV upload (≤ 5,000 rows) → per-row results |
| GET | `/patients/high-risk` | paginated list from `ml.predictions` (filters: tier, age_group, diag group) |
| GET | `/stats/overview` | KPI numbers (encounters, patients, readmission rate, avg LOS) |

### 10.4 Mandatory disclaimer (returned by `/predict` and shown in the UI)
> "This is a statistical risk estimate based on historical patterns, intended to support — not replace — clinical judgement. It does not determine whether this patient will be readmitted."

---

## 11. UI policy — REPLICATE, DON'T DESIGN

- The user will put design references (images, Figma links, PDFs, HTML) in `design-references/`.
- **Do not start frontend work until references exist.** Until then, Phase 7 frontend tasks stay blocked.
- Replicate **exactly**: layout, spacing, typography, colours, radii, shadows, icons, copy, and responsive behaviour. Pull design tokens (colours, font sizes, spacing) into `frontend/tailwind.config.*` / CSS variables first, then build components.
- If a state is not shown in the designs (loading, empty, error, validation, mobile), **ask the user** rather than guessing. If told to proceed, follow the closest existing pattern in the references and note it in `MEMORY.md`.
- The frontend talks only to the API in §10 through `frontend/src/lib/api.ts`. No business logic in the frontend.
- The disclaimer (§10.4) must appear wherever a risk score is shown, styled as the designs dictate.

---

## 12. Power BI (decision-support dashboard)

- **Platform constraint:** Power BI Desktop runs on **Windows only**. The developer is on macOS. Options, to be decided by the end of Week 1 (`P0-08`): (a) a college lab Windows PC, (b) a Windows VM (Parallels / UTM on Apple Silicon), (c) the Power BI Service web editor with CSV upload.
- **Data path that works for all options:** `analytics.vw_*` views → `make export-bi` → `powerbi/data/*.csv` → Power BI. A direct PostgreSQL connection is a bonus when on Windows.
- Pages: (1) Executive Overview, (2) Patient Demographics, (3) Clinical Factors, (4) Admissions & Utilisation, (5) Model Performance, (6) Risk Stratification & High-Risk List, (7) Key Risk Drivers. Full spec: `docs/powerbi_dashboard.md`.
- If the user supplies Power BI design references, replicate them (same rule as §11).

---

## 13. Coding conventions

- Python: PEP 8, type hints, `ruff` for lint+format, docstrings on public functions. Modules are runnable via `python -m readmission.<module>`.
- All paths come from `readmission.config` (no hard-coded absolute paths). Use `pathlib`.
- SQL: lowercase snake_case identifiers, schema-qualified names, one file per stage, idempotent (`CREATE ... IF NOT EXISTS`, `DROP VIEW IF EXISTS`, `CREATE OR REPLACE VIEW`).
- Column names in staging/features: snake_case (`a1c_result`, `diabetes_med`, `glyburide_metformin`, etc.). The raw table keeps the original CSV names (quoted where needed: `"A1Cresult"`, `"diabetesMed"`, `"glyburide-metformin"`).
- Notebooks: exploratory only. Logic that is reused moves to `src/readmission/`. Each notebook starts with a markdown cell stating its purpose and its inputs and outputs.
- Figures: save to `reports/figures/<nn>_<name>.png` at 150 dpi (numbered by notebook).
- Tests: `pytest`. Minimum coverage includes: ICD-9 mapping, cleaning rules, no-patient-overlap split, pipeline fit/predict on a sample, API `/predict` schema validation.
- Git: conventional commits (`feat:`, `fix:`, `data:`, `docs:`, `test:`). Commit at the end of every task.

---

## 14. Where things are documented

| Need | File |
|---|---|
| What to do next / phase plan | `ROADMAP.md` |
| What's done | `PROGRESS.md` |
| Why something was decided, gotchas | `MEMORY.md` |
| Step-by-step training walkthrough | `docs/MODEL_TRAINING_GUIDE.md` |
| Install & environment | `docs/environment_setup.md` |
| Columns & meanings | `docs/data_dictionary.md` |
| Tables & views | `docs/database_schema.md` |
| API request/response | `docs/api_contract.md` |
| Dashboard spec | `docs/powerbi_dashboard.md` |
| System design | `docs/architecture.md` |
| Synopsis / report / PPT / viva | `docs/academic/` |
| Papers & review | `literature/` |
| UI designs | `design-references/` |
