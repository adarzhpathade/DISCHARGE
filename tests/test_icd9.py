"""Unit tests for ICD-9 diagnosis classification (P3-04).

Follows AGENTS.md §6.2 and Strack et al. (2014).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from readmission.config import DIAGNOSIS_GROUPS
from readmission.features.icd9 import (
    map_icd9_to_group,
    map_icd9_series,
    add_diagnosis_groups,
)


def test_required_acceptance_cases():
    """Verify exact acceptance criteria from ROADMAP.md P3-04."""
    assert map_icd9_to_group("250.83") == "Diabetes"
    assert map_icd9_to_group("V57") == "Other"
    assert map_icd9_to_group("786") == "Respiratory"
    assert map_icd9_to_group(None) == "Missing"


def test_diabetes_variants():
    """All 250.xx codes map to Diabetes."""
    assert map_icd9_to_group("250") == "Diabetes"
    assert map_icd9_to_group("250.0") == "Diabetes"
    assert map_icd9_to_group("250.02") == "Diabetes"
    assert map_icd9_to_group("250.93") == "Diabetes"
    assert map_icd9_to_group(250) == "Diabetes"


def test_circulatory_group():
    """Circulatory: 390-459, 785."""
    assert map_icd9_to_group("414") == "Circulatory"
    assert map_icd9_to_group("428") == "Circulatory"
    assert map_icd9_to_group("401") == "Circulatory"
    assert map_icd9_to_group("390") == "Circulatory"
    assert map_icd9_to_group("459") == "Circulatory"
    assert map_icd9_to_group("785") == "Circulatory"
    assert map_icd9_to_group("785.51") == "Circulatory"


def test_respiratory_group():
    """Respiratory: 460-519, 786."""
    assert map_icd9_to_group("466") == "Respiratory"
    assert map_icd9_to_group("486") == "Respiratory"
    assert map_icd9_to_group("493") == "Respiratory"
    assert map_icd9_to_group("519.9") == "Respiratory"
    assert map_icd9_to_group("786") == "Respiratory"
    assert map_icd9_to_group("786.5") == "Respiratory"


def test_digestive_group():
    """Digestive: 520-579, 787."""
    assert map_icd9_to_group("574") == "Digestive"
    assert map_icd9_to_group("555") == "Digestive"
    assert map_icd9_to_group("520") == "Digestive"
    assert map_icd9_to_group("579") == "Digestive"
    assert map_icd9_to_group("787") == "Digestive"
    assert map_icd9_to_group("787.91") == "Digestive"


def test_injury_group():
    """Injury: 800-999."""
    assert map_icd9_to_group("800") == "Injury"
    assert map_icd9_to_group("820") == "Injury"
    assert map_icd9_to_group("996") == "Injury"
    assert map_icd9_to_group("999.9") == "Injury"


def test_musculoskeletal_group():
    """Musculoskeletal: 710-739."""
    assert map_icd9_to_group("710") == "Musculoskeletal"
    assert map_icd9_to_group("715") == "Musculoskeletal"
    assert map_icd9_to_group("728") == "Musculoskeletal"
    assert map_icd9_to_group("733") == "Musculoskeletal"
    assert map_icd9_to_group("739") == "Musculoskeletal"


def test_genitourinary_group():
    """Genitourinary: 580-629, 788."""
    assert map_icd9_to_group("580") == "Genitourinary"
    assert map_icd9_to_group("584") == "Genitourinary"
    assert map_icd9_to_group("599") == "Genitourinary"
    assert map_icd9_to_group("629") == "Genitourinary"
    assert map_icd9_to_group("788") == "Genitourinary"
    assert map_icd9_to_group("788.2") == "Genitourinary"


def test_neoplasms_group():
    """Neoplasms: 140-239."""
    assert map_icd9_to_group("140") == "Neoplasms"
    assert map_icd9_to_group("197") == "Neoplasms"
    assert map_icd9_to_group("208") == "Neoplasms"
    assert map_icd9_to_group("239") == "Neoplasms"


def test_other_group():
    """Other: all unmapped numbers, V-codes, and E-codes."""
    assert map_icd9_to_group("V45") == "Other"
    assert map_icd9_to_group("E888") == "Other"
    assert map_icd9_to_group("e888") == "Other"
    assert map_icd9_to_group("38") == "Other"  # septicemia
    assert map_icd9_to_group("276") == "Other"  # fluid/electrolyte disorders


def test_missing_values():
    """Missing: None, NaN, '?', 'Missing', empty strings."""
    assert map_icd9_to_group(None) == "Missing"
    assert map_icd9_to_group(np.nan) == "Missing"
    assert map_icd9_to_group("?") == "Missing"
    assert map_icd9_to_group("Missing") == "Missing"
    assert map_icd9_to_group("") == "Missing"
    assert map_icd9_to_group("   ") == "Missing"


def test_all_outputs_in_diagnosis_groups():
    """Ensure mapped outputs are strictly constrained to DIAGNOSIS_GROUPS."""
    test_codes = [
        "250.02", "414", "486", "574", "820", "715", "584", "197", "V57",
        "E888", None, "?", "785", "786", "787", "788", "999", "38"
    ]
    for code in test_codes:
        result = map_icd9_to_group(code)
        assert result in DIAGNOSIS_GROUPS, f"{code} produced unrecognised group: {result}"


def test_map_icd9_series_and_add_groups():
    """Test Pandas series and DataFrame mapping helpers."""
    df = pd.DataFrame({
        "diag_1": ["250.83", "414", "V57"],
        "diag_2": ["786", None, "584"],
        "diag_3": ["?", "197", "715"],
    })
    result = add_diagnosis_groups(df)
    assert result["diag_1_group"].tolist() == ["Diabetes", "Circulatory", "Other"]
    assert result["diag_2_group"].tolist() == ["Respiratory", "Missing", "Genitourinary"]
    assert result["diag_3_group"].tolist() == ["Missing", "Neoplasms", "Musculoskeletal"]
