"""Configuration and constants for the Hospital Readmission Risk Prediction System (DISCHARGE).

Single source of truth for paths, column lists, hyperparameters, and environment variables.
Follows AGENTS.md specifications.
"""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
REPO_ROOT: Path = Path(__file__).resolve().parents[2]

DATA_DIR: Path = REPO_ROOT / "data"
DATA_RAW_DIR: Path = DATA_DIR / "raw"
DATA_INTERIM_DIR: Path = DATA_DIR / "interim"
DATA_PROCESSED_DIR: Path = DATA_DIR / "processed"

SQL_DIR: Path = REPO_ROOT / "sql"
MODELS_DIR: Path = REPO_ROOT / "models"

REPORTS_DIR: Path = REPO_ROOT / "reports"
REPORTS_FIGURES_DIR: Path = REPORTS_DIR / "figures"
REPORTS_METRICS_DIR: Path = REPORTS_DIR / "metrics"
REPORTS_EDA_DIR: Path = REPORTS_DIR / "eda"

POWERBI_DIR: Path = REPO_ROOT / "powerbi"
POWERBI_DATA_DIR: Path = POWERBI_DIR / "data"

# Key files
RAW_DIABETIC_DATA_CSV: Path = DATA_RAW_DIR / "diabetic_data.csv"
RAW_IDS_MAPPING_CSV: Path = DATA_RAW_DIR / "IDs_mapping.csv"
PROCESSED_PARQUET: Path = DATA_PROCESSED_DIR / "model_input.parquet"
CURRENT_MODEL_POINTER: Path = MODELS_DIR / "CURRENT"

# Load environment variables
load_dotenv(REPO_ROOT / ".env")

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://readmit:readmit@localhost:5432/readmission_db",
)
API_CORS_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv("API_CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

# Reproducibility
RANDOM_STATE: int = 42

# Target definitions
TARGET_COL: str = "readmitted_30d"
RAW_TARGET_COL: str = "readmitted"

# Identifiers (never used as features)
ID_COLS: list[str] = ["encounter_id", "patient_nbr"]

# Rules C4 & C9 & C10 exclusions
EXCLUDED_DISCHARGE_DISPOSITION_IDS: tuple[int, ...] = (11, 13, 14, 19, 20, 21)
DROPPED_COLUMNS: list[str] = ["weight", "payer_code", "examide", "citoglipton"]

# Raw 23 medications
ALL_RAW_MEDICATIONS: list[str] = [
    "metformin",
    "repaglinide",
    "nateglinide",
    "chlorpropamide",
    "glimepiride",
    "acetohexamide",
    "glipizide",
    "glyburide",
    "tolbutamide",
    "pioglitazone",
    "rosiglitazone",
    "acarbose",
    "miglitol",
    "troglitazone",
    "tolazamide",
    "examide",
    "citoglipton",
    "insulin",
    "glyburide-metformin",
    "glipizide-metformin",
    "glimepiride-pioglitazone",
    "metformin-rosiglitazone",
    "metformin-pioglitazone",
]

# 21 kept medications in snake_case (staging and feature space)
KEPT_MEDICATIONS: list[str] = [
    "metformin",
    "repaglinide",
    "nateglinide",
    "chlorpropamide",
    "glimepiride",
    "acetohexamide",
    "glipizide",
    "glyburide",
    "tolbutamide",
    "pioglitazone",
    "rosiglitazone",
    "acarbose",
    "miglitol",
    "troglitazone",
    "tolazamide",
    "insulin",
    "glyburide_metformin",
    "glipizide_metformin",
    "glimepiride_pioglitazone",
    "metformin_rosiglitazone",
    "metformin_pioglitazone",
]

# Raw to staging column rename map for medication names with hyphens
RAW_TO_STAGING_RENAME: dict[str, str] = {
    "A1Cresult": "a1c_result",
    "diabetesMed": "diabetes_med",
    "glyburide-metformin": "glyburide_metformin",
    "glipizide-metformin": "glipizide_metformin",
    "glimepiride-pioglitazone": "glimepiride_pioglitazone",
    "metformin-rosiglitazone": "metformin_rosiglitazone",
    "metformin-pioglitazone": "metformin_pioglitazone",
    "age": "age_bucket",
}

# Feature definitions (features.model_input)
NUMERIC_FEATURES: list[str] = [
    "time_in_hospital",
    "num_lab_procedures",
    "num_procedures",
    "num_medications",
    "number_outpatient",
    "number_emergency",
    "number_inpatient",
    "number_diagnoses",
    "age_mid",
    "service_utilization",
    "num_meds_active",
    "num_med_changes",
]

CATEGORICAL_FEATURES: list[str] = [
    "race",
    "gender",
    "age_group",
    "admission_type_grp",
    "discharge_grp",
    "admission_source_grp",
    "medical_specialty_grp",
    "diag_1_group",
    "diag_2_group",
    "diag_3_group",
    "max_glu_serum",
    "a1c_result",
    "change",
    "diabetes_med",
    "any_prior_inpatient",
    "a1c_measured",
    "glu_measured",
] + KEPT_MEDICATIONS

ALL_MODEL_FEATURES: list[str] = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# Diagnosis categories
DIAGNOSIS_GROUPS: list[str] = [
    "Circulatory",
    "Respiratory",
    "Digestive",
    "Diabetes",
    "Injury",
    "Musculoskeletal",
    "Genitourinary",
    "Neoplasms",
    "Other",
    "Missing",
]

# Age brackets
AGE_GROUPS: list[str] = ["<40", "40-59", "60-79", "80+"]

# Risk tiers
RISK_TIERS: list[str] = ["Low", "Medium", "High"]

# Mandatory clinical disclaimer
CLINICAL_DISCLAIMER: str = (
    "This is a statistical risk estimate based on historical patterns, "
    "intended to support — not replace — clinical judgement. "
    "It does not determine whether this patient will be readmitted."
)
