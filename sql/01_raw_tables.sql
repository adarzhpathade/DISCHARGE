-- 01_raw_tables.sql
-- Raw staging tables holding verbatim CSV extracts with all columns as TEXT.
-- Reference: AGENTS.md §5 (Rule C1), §8, and docs/database_schema.md

DROP TABLE IF EXISTS raw.diabetic_data CASCADE;

CREATE TABLE raw.diabetic_data (
    "encounter_id"              TEXT,
    "patient_nbr"               TEXT,
    "race"                      TEXT,
    "gender"                    TEXT,
    "age"                       TEXT,
    "weight"                    TEXT,
    "admission_type_id"         TEXT,
    "discharge_disposition_id"  TEXT,
    "admission_source_id"       TEXT,
    "time_in_hospital"          TEXT,
    "payer_code"                TEXT,
    "medical_specialty"         TEXT,
    "num_lab_procedures"        TEXT,
    "num_procedures"            TEXT,
    "num_medications"           TEXT,
    "number_outpatient"         TEXT,
    "number_emergency"          TEXT,
    "number_inpatient"          TEXT,
    "diag_1"                    TEXT,
    "diag_2"                    TEXT,
    "diag_3"                    TEXT,
    "number_diagnoses"          TEXT,
    "max_glu_serum"             TEXT,
    "A1Cresult"                 TEXT,
    "metformin"                 TEXT,
    "repaglinide"               TEXT,
    "nateglinide"               TEXT,
    "chlorpropamide"            TEXT,
    "glimepiride"               TEXT,
    "acetohexamide"             TEXT,
    "glipizide"                 TEXT,
    "glyburide"                 TEXT,
    "tolbutamide"               TEXT,
    "pioglitazone"              TEXT,
    "rosiglitazone"             TEXT,
    "acarbose"                  TEXT,
    "miglitol"                  TEXT,
    "troglitazone"              TEXT,
    "tolazamide"                TEXT,
    "examide"                   TEXT,
    "citoglipton"               TEXT,
    "insulin"                   TEXT,
    "glyburide-metformin"       TEXT,
    "glipizide-metformin"       TEXT,
    "glimepiride-pioglitazone"  TEXT,
    "metformin-rosiglitazone"   TEXT,
    "metformin-pioglitazone"    TEXT,
    "change"                    TEXT,
    "diabetesMed"               TEXT,
    "readmitted"                TEXT
);

DROP TABLE IF EXISTS raw.ids_mapping CASCADE;

CREATE TABLE raw.ids_mapping (
    line_no INT,
    col1    TEXT,
    col2    TEXT
);
