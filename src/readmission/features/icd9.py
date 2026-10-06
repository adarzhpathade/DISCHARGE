"""ICD-9 diagnosis classification for the DISCHARGE readmission system.

Maps primary, secondary, and tertiary ICD-9 codes to the 9 high-level clinical categories
defined by Strack et al. (2014) plus 'Missing'.
Follows AGENTS.md §6.2.
"""

from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd

from readmission.config import DIAGNOSIS_GROUPS


def map_icd9_to_group(code: Any) -> str:
    """Classify a single ICD-9 code into its standard Strack et al. (2014) clinical group.

    Parameters
    ----------
    code : Any
        Raw ICD-9 string, integer, float, or null-like value.

    Returns
    -------
    str
        One of the 10 DIAGNOSIS_GROUPS:
        - 'Circulatory' (390-459, 785)
        - 'Respiratory' (460-519, 786)
        - 'Digestive' (520-579, 787)
        - 'Diabetes' (250.xx)
        - 'Injury' (800-999)
        - 'Musculoskeletal' (710-739)
        - 'Genitourinary' (580-629, 788)
        - 'Neoplasms' (140-239)
        - 'Other' (all other valid codes including V-codes and E-codes)
        - 'Missing' (null, empty, '?', or 'Missing')
    """
    if code is None:
        return "Missing"

    if isinstance(code, float) and np.isnan(code):
        return "Missing"

    s = str(code).strip()
    if not s or s in ("?", "None", "Missing", "nan", "NaN", "null", "NULL"):
        return "Missing"

    # Diabetes: 250.xx (e.g. 250, 250.0, 250.83)
    if s.startswith("250"):
        return "Diabetes"

    # Supplementary classification codes: V-codes (health status/contact) and E-codes (injury causes)
    if s.startswith(("V", "v", "E", "e")):
        return "Other"

    # Extract integer prefix before decimal point
    prefix = s.split(".")[0]
    try:
        num = int(prefix)
    except ValueError:
        return "Other"

    if (390 <= num <= 459) or num == 785:
        return "Circulatory"
    if (460 <= num <= 519) or num == 786:
        return "Respiratory"
    if (520 <= num <= 579) or num == 787:
        return "Digestive"
    if 800 <= num <= 999:
        return "Injury"
    if 710 <= num <= 739:
        return "Musculoskeletal"
    if (580 <= num <= 629) or num == 788:
        return "Genitourinary"
    if 140 <= num <= 239:
        return "Neoplasms"

    return "Other"


def map_icd9_series(series: pd.Series) -> pd.Series:
    """Vectorized / batch mapping of a Pandas Series of ICD-9 codes."""
    return series.map(map_icd9_to_group)


def add_diagnosis_groups(
    df: pd.DataFrame,
    cols: tuple[str, ...] = ("diag_1", "diag_2", "diag_3"),
) -> pd.DataFrame:
    """Add diag_1_group, diag_2_group, diag_3_group columns to DataFrame in place or copy.

    Returns the modified DataFrame.
    """
    df = df.copy()
    for col in cols:
        if col in df.columns:
            group_col = f"{col}_group"
            df[group_col] = map_icd9_series(df[col])
    return df
