-- 04_ml_tables.sql
-- ML registry, batch predictions, feature importance, and inference audit logging
-- Reference: AGENTS.md §7.5, §8, and docs/database_schema.md

CREATE SCHEMA IF NOT EXISTS ml;

CREATE TABLE IF NOT EXISTS ml.model_registry (
    model_version      TEXT PRIMARY KEY,
    algorithm          TEXT NOT NULL,
    params             JSONB,
    metrics            JSONB,
    decision_threshold NUMERIC(6,4),
    tier_cutoff_medium NUMERIC(6,4),
    tier_cutoff_high   NUMERIC(6,4),
    artifact_path      TEXT NOT NULL,
    is_current         BOOLEAN DEFAULT FALSE,
    trained_at         TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ml.predictions (
    encounter_id       BIGINT NOT NULL,
    model_version      TEXT NOT NULL REFERENCES ml.model_registry(model_version),
    probability        NUMERIC(6,4) NOT NULL,
    risk_tier          TEXT CHECK (risk_tier IN ('Low', 'Medium', 'High')),
    predicted_label    SMALLINT,
    actual_label       SMALLINT,
    split              TEXT,
    scored_at          TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (encounter_id, model_version)
);

CREATE INDEX IF NOT EXISTS idx_predictions_encounter_id ON ml.predictions(encounter_id);
CREATE INDEX IF NOT EXISTS idx_predictions_model_version ON ml.predictions(model_version);

CREATE TABLE IF NOT EXISTS ml.feature_importance (
    model_version  TEXT NOT NULL REFERENCES ml.model_registry(model_version),
    feature        TEXT NOT NULL,
    importance     NUMERIC,
    importance_std NUMERIC,
    method         TEXT NOT NULL,
    rank           INT,
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
