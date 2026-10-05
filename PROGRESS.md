# PROGRESS.md — Progress Tracker

> Mirrors `ROADMAP.md` task IDs exactly. When a task is done: tick it, fill the date, and add a note
> (commit hash / output file). Update the **Dashboard** and **Weekly log** every Sunday.
> Status legend: ⬜ Not started · 🟨 In progress · ✅ Done · ⛔ Blocked · ✂️ Cut (from the cut list)

---

## Dashboard

| Phase | Week | Tasks | Done | Status | % |
|---|---|---|---|---|---|
| P0 Setup & Planning | 1 | 10 | 8 | 🟨 | 80% |
| P1 Ingestion & SQL | 1 | 7 | 7 | ✅ | 100% |
| P2 Cleaning & Quality | 2 | 7 | 7 | ✅ | 100% |
| P3 EDA & Statistics | 3 | 10 | 0 | ⬜ | 0% |
| P4 Features & Baselines | 4 | 8 | 0 | ⬜ | 0% |
| P5 Tuning & Evaluation | 5 | 9 | 0 | ⬜ | 0% |
| P6 Scoring, Views & API | 6 | 9 | 0 | ⬜ | 0% |
| P7 Power BI + Frontend | 7 | 9 | 0 | ⬜ (7B ⛔ awaiting designs) | 0% |
| P8 Testing, Report & Viva | 8 | 9 | 0 | ⬜ | 0% |
| **Total** | | **78** | **22** | | **28%** |

**Overall:** `[██████░░░░░░░░░░░░░░] 28%`

### Key results (fill as they become available)
| Metric | CV (train) | Validation | Test (final, once) |
|---|---|---|---|
| ROC-AUC | | | |
| PR-AUC | | | |
| Recall @ threshold | | | |
| Precision @ threshold | | | |
| F1 | | | |
| Brier score | | | |
| Decision threshold | — | | — |
| High-tier observed readmission rate | — | | |
| Base rate | 11.16% (raw) / 11.39% (staging) | | |

---

## Phase 0 — Setup & Planning (Week 1: Oct 05 – Oct 07)
| ✓ | ID | Task | Date | Notes |
|---|---|---|---|---|
| ✅ | P0-01 | Initialise repo & folder structure | 2026-10-04 | Commit 13842d6; tree & .gitignore created |
| ✅ | P0-02 | Python environment | 2026-10-05 | .venv (Python 3.13), requirements.txt, pyproject.toml; pip install -e . verified |
| ✅ | P0-03 | PostgreSQL 16 | 2026-10-05 | Neon Postgres 18 project twilight-unit-85400243; DATABASE_URL in .env, connection verified |
| ✅ | P0-04 | Node.js & tooling | 2026-10-05 | Node v24.15.0, npm 11.12.1 installed |
| ✅ | P0-05 | Download dataset | 2026-10-05 | 101,766 encounters; diabetic_data.csv sha256: 0689e7ec...; IDs_mapping.csv sha256: f1bb82b4... |
| ✅ | P0-06 | Core reading (4 papers) | 2026-10-05 | Strack 2014, van Walraven 2010, Donzé 2013, Kansagara 2011 in literature/annotated_bibliography.md |
| ⬜ | P0-07 | Synopsis submitted | | |
| ✅ | P0-08 | Decide Power BI platform | 2026-10-04 | Native Power BI Desktop on Windows (D-015) |
| ⬜ | P0-09 | Get college templates | | |
| ✅ | P0-10 | Config & DB helpers + Makefile | 2026-10-05 | src/readmission/config.py, db.py, Makefile created and verified |

## Phase 1 — Ingestion & SQL (Week 1: Oct 08 – Oct 11)
| ✓ | ID | Task | Date | Notes |
|---|---|---|---|---|
| ✅ | P1-01 | `sql/00_create_schemas.sql` | 2026-10-05 | Created raw, staging, features, ml, analytics schemas |
| ✅ | P1-02 | `sql/01_raw_tables.sql` | 2026-10-05 | raw.diabetic_data (50 TEXT cols), raw.ids_mapping created |
| ✅ | P1-03 | `ingest.py` (COPY into raw) | 2026-10-05 | 101,766 encounters streamed via COPY; 68 mapping lines |
| ✅ | P1-04 | `sql/02_dim_tables.sql` | 2026-10-05 | Populated staging.dim_* (admission_type=8, discharge=30, source=25) |
| ✅ | P1-05 | Load verification | 2026-10-05 | Verified 101,766 encounters, 71,518 unique patients, 100% unique encounter_id |
| ✅ | P1-06 | Notebook 01 data understanding | 2026-10-05 | Executed notebooks/01_data_understanding.ipynb (target=11.16% <30) |
| ✅ | P1-07 | `sql/04_ml_tables.sql` | 2026-10-05 | Created ml.model_registry, ml.predictions, feature_importance, prediction_log |

## Phase 2 — Cleaning & Data Quality (Week 2: Oct 12 – Oct 18)
| ✓ | ID | Task | Date | Notes |
|---|---|---|---|---|
| ✅ | P2-01 | Quality audit SQL | 2026-10-06 | `sql/99_quality_checks.sql` assertions & audit views verified; CSVs in `reports/eda/` |
| ✅ | P2-02 | `sql/03_staging_encounters.sql` (C1–C13) | 2026-10-06 | Cleaned rows: 99,340 (dropped 3 gender, 2,423 hospice/expired); verified in Postgres |
| ✅ | P2-03 | Notebook 02 validation | 2026-10-06 | `notebooks/02_data_quality_cleaning.ipynb` executed top-to-bottom with all assertions |
| ✅ | P2-04 | `quality.py` → data_quality_report.md | 2026-10-06 | `src/readmission/data/quality.py` generated `reports/eda/data_quality_report.md` |
| ✅ | P2-05 | `tests/test_cleaning.py` | 2026-10-06 | 6 unit and DB integration tests passing (pytest) |
| ✅ | P2-06 | Update data dictionary | 2026-10-06 | Updated `docs/data_dictionary.md` with measured raw missingness & dim descriptions |
| ✅ | P2-07 | Literature: ML papers | 2026-10-06 | Verified Huang 2021 & Artetxe 2018 in `literature/annotated_bibliography.md` |

## Phase 3 — EDA & Statistics (Week 3: Oct 19 – Oct 25)
| ✓ | ID | Task | Date | Notes |
|---|---|---|---|---|
| ⬜ | P3-01 | Univariate analysis | | |
| ⬜ | P3-02 | Categorical vs readmission rate | | |
| ⬜ | P3-03 | Numeric vs target | | |
| ⬜ | P3-04 | `icd9.py` + tests | | |
| ⬜ | P3-05 | Diagnosis analysis | | |
| ⬜ | P3-06 | Correlation & multicollinearity | | |
| ⬜ | P3-07 | Statistical tests | | |
| ⬜ | P3-08 | Odds ratios | | |
| ⬜ | P3-09 | EDA summary | | |
| ⬜ | P3-10 | SQL analytics prototypes | | |

## Phase 4 — Features & Baselines (Week 4: Oct 26 – Nov 01)
| ✓ | ID | Task | Date | Notes |
|---|---|---|---|---|
| ⬜ | P4-01 | `build.py` → features.model_input | | |
| ⬜ | P4-02 | `split.py` grouped split + test | | train/val/test rows: |
| ⬜ | P4-03 | `pipeline.py` | | |
| ⬜ | P4-04 | Baselines (dummy, logreg, dtree) | | |
| ⬜ | P4-05 | rf, hgb defaults | | |
| ⬜ | P4-06 | Leakage checklist | | |
| ⬜ | P4-07 | `tests/test_pipeline.py` | | |
| ⬜ | P4-08 | Literature review draft | | |

## Phase 5 — Tuning, Evaluation & Explainability (Week 5: Nov 02 – Nov 08)
| ✓ | ID | Task | Date | Notes |
|---|---|---|---|---|
| ⬜ | P5-01 | Hyperparameter tuning | | best model: |
| ⬜ | P5-02 | Imbalance comparison | | |
| ⬜ | P5-03 | Calibration | | |
| ⬜ | P5-04 | Threshold & tiers | | thr: |
| ⬜ | P5-05 | Explainability | | |
| ⬜ | P5-06 | Fairness | | |
| ⬜ | P5-07 | **Final test evaluation (once)** | | |
| ⬜ | P5-08 | Persist & register model | | model_version: |
| ⬜ | P5-09 | Model card | | |

## Phase 6 — Scoring, Views & API (Week 6: Nov 09 – Nov 15)
| ✓ | ID | Task | Date | Notes |
|---|---|---|---|---|
| ⬜ | P6-01 | Batch scoring → ml.predictions | | |
| ⬜ | P6-02 | `sql/05_analytics_views.sql` | | |
| ⬜ | P6-03 | `export/powerbi.py` | | |
| ⬜ | P6-04 | FastAPI skeleton | | |
| ⬜ | P6-05 | `model_service.py` | | |
| ⬜ | P6-06 | Model routes | | |
| ⬜ | P6-07 | Prediction routes | | |
| ⬜ | P6-08 | Data routes | | |
| ⬜ | P6-09 | API tests & TS types | | |

## Phase 7 — Power BI + Frontend (Week 7: Nov 16 – Nov 22)
| ✓ | ID | Task | Date | Notes |
|---|---|---|---|---|
| ⬜ | P7-01 | Power BI data model & DAX | | |
| ⬜ | P7-02 | Pages 1–4 | | |
| ⬜ | P7-03 | Pages 5–7 | | |
| ⬜ | P7-04 | Polish & export screenshots | | |
| ⛔ | P7-05 | Intake design references | | waiting for `design-references/` |
| ⛔ | P7-06 | Next.js scaffold | | gated on P7-05 |
| ⛔ | P7-07 | Build screens | | gated on P7-05 |
| ⛔ | P7-08 | Wire to API | | gated on P7-05 |
| ⛔ | P7-09 | Visual QA | | gated on P7-05 |

## Phase 8 — Testing, Report & Viva (Week 8: Nov 23 – Nov 29)
| ✓ | ID | Task | Date | Notes |
|---|---|---|---|---|
| ⬜ | P8-01 | Clean-room pipeline run | | |
| ⬜ | P8-02 | Quality gate | | |
| ⬜ | P8-03 | README | | |
| ⬜ | P8-04 | Final report | | |
| ⬜ | P8-05 | Presentation | | |
| ⬜ | P8-06 | Viva preparation | | |
| ⬜ | P8-07 | Demo script + backup video | | |
| ⬜ | P8-08 | Submission package | | |
| ⬜ | P8-09 | Verify citations | | |

---

## Milestones
| # | Milestone | Target date | Achieved |
|---|---|---|---|
| M1 | Data in PostgreSQL + synopsis submitted | 2026-10-11 | |
| M2 | Clean staging table + quality report | 2026-10-18 | 2026-10-06 |
| M3 | EDA & stats complete | 2026-10-25 | |
| M4 | Baselines beat dummy, no leakage | 2026-11-01 | |
| M5 | Final model evaluated on test | 2026-11-08 | |
| M6 | API live + Power BI data exported | 2026-11-15 | |
| M7 | Dashboard (+ UI if designs received) | 2026-11-22 | |
| M8 | Submission | 2026-11-29 | |

---

## Weekly log
> Each Sunday: what was done, what slipped, blockers, and the plan for next week.

### Week 1 (Oct 05 – Oct 11)
- Done:
- Slipped:
- Blockers:
- Next week:

### Week 2 (Oct 12 – Oct 18)
- Done:
- Slipped:
- Blockers:
- Next week:

### Week 3 (Oct 19 – Oct 25)
- Done:
- Slipped:
- Blockers:
- Next week:

### Week 4 (Oct 26 – Nov 01)
- Done:
- Slipped:
- Blockers:
- Next week:

### Week 5 (Nov 02 – Nov 08)
- Done:
- Slipped:
- Blockers:
- Next week:

### Week 6 (Nov 09 – Nov 15)
- Done:
- Slipped:
- Blockers:
- Next week:

### Week 7 (Nov 16 – Nov 22)
- Done:
- Slipped:
- Blockers:
- Next week:

### Week 8 (Nov 23 – Nov 29)
- Done:
- Slipped:
- Blockers:

---

## Blockers register
| Date raised | Blocker | Affects | Owner | Resolved on |
|---|---|---|---|---|
| 2026-10-04 | UI design references not yet supplied | P7-05 … P7-09 | User | |
| 2026-10-04 | Power BI platform undecided (macOS) | P7-01 … P7-04 | User | |
