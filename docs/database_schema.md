# Database Schema — PostgreSQL 16 `readmission_db`

> Schemas and object names follow AGENTS.md §8. All SQL files are idempotent and live in `sql/`.

## Schema map
```
raw ───────────► staging ─────────► features ─────────► ml ──────────► analytics (views)
diabetic_data    encounters         model_input         model_registry  vw_* (10 views)
ids_mapping      dim_admission_type                     predictions
                 dim_discharge_disposition              feature_importance
                 dim_admission_source                   prediction_log
```

## raw (`sql/01_raw_tables.sql`)
| Table | Columns | Notes |
|---|---|---|
| `raw.diabetic_data` | 50 columns, all TEXT, original CSV names (quote `"A1Cresult"`, `"diabetesMed"`, hyphenated meds) | Loaded by `ingest.py` with COPY |
| `raw.ids_mapping` | `line_no INT, col1 TEXT, col2 TEXT` | Every line of `IDs_mapping.csv`; parsed in `02_dim_tables.sql` |

## staging (`sql/02_dim_tables.sql`, `sql/03_staging_encounters.sql`)
| Table | Key columns |
|---|---|
| `staging.dim_admission_type` | `admission_type_id INT PK`, `description TEXT` |
| `staging.dim_discharge_disposition` | `discharge_disposition_id INT PK`, `description TEXT` |
| `staging.dim_admission_source` | `admission_source_id INT PK`, `description TEXT` |
| `staging.encounters` | `encounter_id BIGINT PK`, `patient_nbr BIGINT`, typed and cleaned columns (see `docs/data_dictionary.md`), `readmitted TEXT`, `readmitted_30d INT` |

Indexes: `staging.encounters(patient_nbr)`.

## features (written by `src/readmission/features/build.py`)
| Table | Columns |
|---|---|
| `features.model_input` | `encounter_id PK`, `patient_nbr`, all model features (AGENTS.md §6.1 + kept columns), `readmitted_30d`, `split TEXT CHECK (split IN ('train','val','test'))` |

## ml (`sql/04_ml_tables.sql`)
```sql
CREATE TABLE IF NOT EXISTS ml.model_registry (
    model_version   TEXT PRIMARY KEY,           -- e.g. v20261106_hgb
    algorithm       TEXT NOT NULL,
    params          JSONB,
    metrics         JSONB,                      -- cv / val / test
    decision_threshold NUMERIC(6,4),
    tier_cutoff_medium NUMERIC(6,4),
    tier_cutoff_high   NUMERIC(6,4),
    artifact_path   TEXT NOT NULL,
    is_current      BOOLEAN DEFAULT FALSE,
    trained_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ml.predictions (
    encounter_id    BIGINT REFERENCES staging.encounters(encounter_id),
    model_version   TEXT REFERENCES ml.model_registry(model_version),
    probability     NUMERIC(6,4) NOT NULL,
    risk_tier       TEXT CHECK (risk_tier IN ('Low','Medium','High')),
    predicted_label SMALLINT,                   -- probability >= decision_threshold
    actual_label    SMALLINT,                   -- readmitted_30d (historical)
    split           TEXT,
    scored_at       TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (encounter_id, model_version)
);

CREATE TABLE IF NOT EXISTS ml.feature_importance (
    model_version TEXT REFERENCES ml.model_registry(model_version),
    feature       TEXT,
    importance    NUMERIC,
    importance_std NUMERIC,
    method        TEXT,                         -- permutation | shap | coef
    rank          INT,
    PRIMARY KEY (model_version, feature, method)
);

CREATE TABLE IF NOT EXISTS ml.prediction_log (
    request_id    UUID PRIMARY KEY,
    model_version TEXT,
    input_payload JSONB,
    probability   NUMERIC(6,4),
    risk_tier     TEXT,
    created_at    TIMESTAMPTZ DEFAULT now()
);
```

## analytics (`sql/05_analytics_views.sql`) — feeds Power BI and `/stats/*`
| View | Grain | Main columns |
|---|---|---|
| `analytics.vw_readmission_overview` | 1 row | total_encounters, total_patients, readmissions_30d, readmission_rate, avg_los, avg_medications |
| `analytics.vw_readmission_by_demographics` | age_group × gender × race | encounters, readmissions_30d, readmission_rate |
| `analytics.vw_readmission_by_diagnosis` | diag_1_group | encounters, readmission_rate, avg_los |
| `analytics.vw_readmission_by_admission` | admission_type_grp × admission_source_grp × discharge_grp | encounters, readmission_rate |
| `analytics.vw_utilization` | number_inpatient / number_emergency bins | encounters, readmission_rate |
| `analytics.vw_medication_summary` | medication × status | encounters, readmission_rate; plus a1c_result, insulin, change |
| `analytics.vw_risk_distribution` | risk_tier × split (current model) | n, avg_probability, observed_rate |
| `analytics.vw_model_performance` | metric × split | value (from `ml.model_registry.metrics` JSONB) |
| `analytics.vw_feature_importance` | feature (current model) | importance, rank, method |
| `analytics.vw_high_risk_patients` | encounter (current model, tier = High) | encounter_id, patient_nbr, age_group, gender, diag_1_group, time_in_hospital, number_inpatient, discharge_grp, probability, actual_label, split |

"Current model" = `ml.model_registry.is_current = TRUE` (kept in sync with `models/CURRENT`).
