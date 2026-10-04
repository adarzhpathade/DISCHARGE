# System Architecture

> This doc follows `AGENTS.md`. If the two disagree, AGENTS.md wins.

## 1. High-level flow

```
                ┌───────────────────────────── OFFLINE (batch, Python CLI / Makefile) ─────────────────────────────┐
                │                                                                                                  │
 data/raw/*.csv ──► raw.*  ──SQL──►  staging.encounters ──Python──► features.model_input ──► sklearn training       │
   (UCI 296)     (TEXT, as-is)   (clean, typed, C1–C13)        (engineered + split col)      (CV, tune, calibrate)  │
                                                                                                    │              │
                                                                                                    ▼              │
                                                         models/<version>/model.joblib + metadata/metrics/thresholds │
                                                                                                    │              │
                                                     batch scoring (predict.py --batch) ◄───────────┘              │
                                                                    │                                              │
                                                                    ▼                                              │
                                    ml.predictions, ml.feature_importance, ml.model_registry                      │
                                                                    │                                              │
                                                     analytics.vw_* (SQL views)                                    │
                                                                    │                                              │
                                                export/powerbi.py ──► powerbi/data/*.csv ──► Power BI (.pbix)      │
                └──────────────────────────────────────────────────────────────────────────────────────────────────┘

                ┌──────────────────────────────── ONLINE (request/response) ────────────────────────────────┐
                │  Next.js frontend (from design-references/)                                                │
                │        │  fetch  (src/lib/api.ts, NEXT_PUBLIC_API_URL)                                     │
                │        ▼                                                                                   │
                │  FastAPI  /api/v1/*  ── model_service (loads models/CURRENT once at startup)               │
                │        │                      └─ build_features() (same code as training) → predict_proba │
                │        └── db_service ── PostgreSQL (ml.predictions, analytics.vw_*, ml.prediction_log)    │
                └────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 2. Components

| Layer | Tech | Responsibility | Key files |
|---|---|---|---|
| Storage | PostgreSQL 16 | Raw → staging → features → ml → analytics schemas | `sql/*.sql` |
| Ingestion | Python + psycopg COPY | Load CSVs unchanged | `src/readmission/data/ingest.py` |
| Cleaning | SQL | Rules C1–C13 | `sql/03_staging_encounters.sql` |
| Quality | SQL + Python | Audit + report | `sql/99_quality_checks.sql`, `src/readmission/data/quality.py` |
| Features | Pandas/NumPy | Engineered features, patient-grouped split | `src/readmission/features/` |
| Modeling | scikit-learn | Pipelines, CV, tuning, calibration, threshold | `src/readmission/models/` |
| Explainability | sklearn / SHAP | Global + per-patient factors | `src/readmission/models/explain.py` |
| Serving | FastAPI | REST API (contract: `docs/api_contract.md`) | `backend/app/` |
| UI | Next.js + Tailwind | Replicates user designs | `frontend/` |
| BI | Power BI | Dashboard | `powerbi/` |

## 3. Key design decisions
- **Training/serving parity:** the API imports `readmission.features.build.build_features` and the saved `specialty_top10`, so features are computed identically in both paths.
- **Model loaded once** at FastAPI startup (lifespan event). Swapping models = change `models/CURRENT` + restart.
- **Analytics through views:** Power BI and `/stats/*` read the same `analytics.vw_*` views, so the numbers stay consistent everywhere.
- **CSV bridge to Power BI:** works on macOS-only setups (see AGENTS.md §12).
- **Stateless API:** every prediction is logged to `ml.prediction_log` for audit. No PHI is involved (the dataset is de-identified).

## 4. Deployment (local demo)
| Service | Port | Command |
|---|---|---|
| PostgreSQL | 5432 | `make db-up` |
| FastAPI | 8000 | `make api` (Swagger at `/docs`) |
| Next.js | 3000 | `make web` |
| Power BI | — | open `powerbi/readmission_dashboard.pbix` |
