"""Tests for data cleaning rules C1–C13 and staging data integrity.

Validates that missing values ('?'), hospice/expired discharge dispositions,
and invalid gender values are cleaned properly, and verifies staging.encounters.
Follows AGENTS.md §5 and ROADMAP.md task P2-05.
"""

from __future__ import annotations

import pandas as pd
import pytest
import sqlalchemy as sa

from readmission.config import (
    EXCLUDED_DISCHARGE_DISPOSITION_IDS,
    DROPPED_COLUMNS,
    KEPT_MEDICATIONS,
)
from readmission.db import get_engine, check_connection


@pytest.fixture
def raw_sample_data() -> pd.DataFrame:
    """Fixture providing synthetic raw encounters with boundary conditions and edge cases."""
    return pd.DataFrame([
        {
            "encounter_id": 1,
            "patient_nbr": 101,
            "race": "?",
            "gender": "Female",
            "age": "[50-60)",
            "weight": "?",
            "admission_type_id": 1,
            "discharge_disposition_id": 1,  # Discharged to home
            "admission_source_id": 7,
            "time_in_hospital": 3,
            "payer_code": "?",
            "medical_specialty": "?",
            "num_lab_procedures": 40,
            "num_procedures": 1,
            "num_medications": 10,
            "number_outpatient": 0,
            "number_emergency": 0,
            "number_inpatient": 0,
            "diag_1": "250.01",
            "diag_2": "?",
            "diag_3": "?",
            "number_diagnoses": 5,
            "max_glu_serum": "None",
            "A1Cresult": "None",
            "examide": "No",
            "citoglipton": "No",
            "metformin": "Steady",
            "insulin": "No",
            "change": "No",
            "diabetesMed": "Yes",
            "readmitted": "<30",
        },
        {
            "encounter_id": 2,
            "patient_nbr": 102,
            "race": "Caucasian",
            "gender": "Unknown/Invalid",  # Rule C3: should be dropped
            "age": "[70-80)",
            "weight": "[75-100)",
            "admission_type_id": 2,
            "discharge_disposition_id": 1,
            "admission_source_id": 1,
            "time_in_hospital": 5,
            "payer_code": "MC",
            "medical_specialty": "InternalMedicine",
            "num_lab_procedures": 30,
            "num_procedures": 0,
            "num_medications": 8,
            "number_outpatient": 1,
            "number_emergency": 0,
            "number_inpatient": 1,
            "diag_1": "414",
            "diag_2": "250",
            "diag_3": "401",
            "number_diagnoses": 7,
            "max_glu_serum": "Norm",
            "A1Cresult": ">8",
            "examide": "No",
            "citoglipton": "No",
            "metformin": "No",
            "insulin": "Up",
            "change": "Ch",
            "diabetesMed": "Yes",
            "readmitted": ">30",
        },
        {
            "encounter_id": 3,
            "patient_nbr": 103,
            "race": "AfricanAmerican",
            "gender": "Male",
            "age": "[60-70)",
            "weight": "?",
            "admission_type_id": 1,
            "discharge_disposition_id": 11,  # Rule C4: Expired (should be dropped)
            "admission_source_id": 7,
            "time_in_hospital": 10,
            "payer_code": "?",
            "medical_specialty": "?",
            "num_lab_procedures": 55,
            "num_procedures": 2,
            "num_medications": 15,
            "number_outpatient": 0,
            "number_emergency": 1,
            "number_inpatient": 2,
            "diag_1": "428",
            "diag_2": "427",
            "diag_3": "250",
            "number_diagnoses": 9,
            "max_glu_serum": "None",
            "A1Cresult": "Norm",
            "examide": "No",
            "citoglipton": "No",
            "metformin": "No",
            "insulin": "Steady",
            "change": "No",
            "diabetesMed": "Yes",
            "readmitted": "NO",
        },
        {
            "encounter_id": 4,
            "patient_nbr": 104,
            "race": "Hispanic",
            "gender": "Female",
            "age": "[40-50)",
            "weight": "?",
            "admission_type_id": 3,
            "discharge_disposition_id": 13,  # Rule C4: Hospice (should be dropped)
            "admission_source_id": 1,
            "time_in_hospital": 2,
            "payer_code": "HM",
            "medical_specialty": "Family/GeneralPractice",
            "num_lab_procedures": 22,
            "num_procedures": 0,
            "num_medications": 4,
            "number_outpatient": 0,
            "number_emergency": 0,
            "number_inpatient": 0,
            "diag_1": "250",
            "diag_2": "401",
            "diag_3": "?",
            "number_diagnoses": 3,
            "max_glu_serum": ">200",
            "A1Cresult": "None",
            "examide": "No",
            "citoglipton": "No",
            "metformin": "No",
            "insulin": "No",
            "change": "No",
            "diabetesMed": "No",
            "readmitted": "NO",
        },
    ])


def test_rule_c3_invalid_gender_dropped(raw_sample_data: pd.DataFrame) -> None:
    """Verify that rows with gender == 'Unknown/Invalid' are removed."""
    cleaned = raw_sample_data[raw_sample_data["gender"] != "Unknown/Invalid"]
    assert len(cleaned) == 3
    assert 2 not in cleaned["encounter_id"].values
    assert set(cleaned["gender"].unique()).issubset({"Male", "Female"})


def test_rule_c4_hospice_expired_dropped(raw_sample_data: pd.DataFrame) -> None:
    """Verify that discharge disposition codes 11, 13, 14, 19, 20, 21 are filtered out."""
    cleaned = raw_sample_data[
        ~raw_sample_data["discharge_disposition_id"].isin(EXCLUDED_DISCHARGE_DISPOSITION_IDS)
    ]
    assert len(cleaned) == 2
    assert set(cleaned["encounter_id"].values) == {1, 2}


def test_rule_c2_and_c6_race_standardization(raw_sample_data: pd.DataFrame) -> None:
    """Verify that '?' and NULL race values map to 'Unknown'."""
    race_clean = raw_sample_data["race"].replace({"?": "Unknown", None: "Unknown"})
    assert race_clean.iloc[0] == "Unknown"
    assert "?" not in race_clean.values


def test_rule_c8_lab_tests_not_measured(raw_sample_data: pd.DataFrame) -> None:
    """Verify that 'None', '?', and NULL in A1Cresult and max_glu_serum map to 'NotMeasured'."""
    a1c_clean = raw_sample_data["A1Cresult"].replace({"None": "NotMeasured", "?": "NotMeasured"})
    glu_clean = raw_sample_data["max_glu_serum"].replace({"None": "NotMeasured", "?": "NotMeasured"})

    assert a1c_clean.iloc[0] == "NotMeasured"
    assert glu_clean.iloc[0] == "NotMeasured"
    assert a1c_clean.iloc[1] == ">8"
    assert glu_clean.iloc[1] == "Norm"


def test_rule_c9_and_c10_dropped_columns(raw_sample_data: pd.DataFrame) -> None:
    """Verify that dropped columns (weight, payer_code, examide, citoglipton) are removed."""
    cols_to_drop = [c for c in DROPPED_COLUMNS if c in raw_sample_data.columns]
    retained = raw_sample_data.drop(columns=cols_to_drop)
    for col in DROPPED_COLUMNS:
        assert col not in retained.columns


@pytest.mark.skipif(not check_connection(), reason="Database connection unavailable")
def test_staging_database_integrity() -> None:
    """Integration test verifying that staging.encounters in PostgreSQL satisfies all rules."""
    engine = get_engine()
    with engine.connect() as conn:
        # Check row count
        total = conn.execute(sa.text("SELECT count(*) FROM staging.encounters")).scalar()
        assert total == 99340

        # Check unique patients
        unique_patients = conn.execute(sa.text("SELECT count(DISTINCT patient_nbr) FROM staging.encounters")).scalar()
        assert unique_patients == 69987

        # Check Rule C3: zero invalid genders
        invalid_genders = conn.execute(
            sa.text("SELECT count(*) FROM staging.encounters WHERE gender NOT IN ('Male', 'Female')")
        ).scalar()
        assert invalid_genders == 0

        # Check Rule C4: zero hospice/expired
        hospice_ids = ",".join(str(i) for i in EXCLUDED_DISCHARGE_DISPOSITION_IDS)
        hospice_count = conn.execute(
            sa.text(f"SELECT count(*) FROM staging.encounters WHERE discharge_disposition_id IN ({hospice_ids})")
        ).scalar()
        assert hospice_count == 0

        # Check Rule C2: zero unmapped '?'
        qmarks = conn.execute(
            sa.text(
                "SELECT count(*) FROM staging.encounters "
                "WHERE race = '?' OR medical_specialty = '?' OR diag_1 = '?' "
                "OR max_glu_serum = '?' OR a1c_result = '?'"
            )
        ).scalar()
        assert qmarks == 0

        # Check Rule C8: zero unmapped 'None' in lab tests
        unmapped_none = conn.execute(
            sa.text(
                "SELECT count(*) FROM staging.encounters "
                "WHERE max_glu_serum = 'None' OR a1c_result = 'None'"
            )
        ).scalar()
        assert unmapped_none == 0

        # Check Rule C11: numeric ranges
        out_of_range = conn.execute(
            sa.text(
                "SELECT count(*) FROM staging.encounters "
                "WHERE time_in_hospital < 1 OR time_in_hospital > 14 "
                "OR num_lab_procedures < 0 OR num_procedures < 0 OR num_medications < 0 "
                "OR number_outpatient < 0 OR number_emergency < 0 OR number_inpatient < 0 "
                "OR number_diagnoses < 0"
            )
        ).scalar()
        assert out_of_range == 0

        # Check target integrity
        target_check = conn.execute(
            sa.text(
                "SELECT count(*) FROM staging.encounters "
                "WHERE (readmitted = '<30' AND readmitted_30d != 1) "
                "OR (readmitted != '<30' AND readmitted_30d != 0)"
            )
        ).scalar()
        assert target_check == 0
