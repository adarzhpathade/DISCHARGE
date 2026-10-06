"""Data loading utilities for the DISCHARGE readmission system.

Loads staging encounters, dimension lookups, and feature tables into Pandas DataFrames.
Follows AGENTS.md §3.
"""

from __future__ import annotations

from typing import Optional
import pandas as pd
import sqlalchemy as sa

from readmission.db import get_engine


def load_staging_encounters(
    engine: Optional[sa.Engine] = None,
    limit: Optional[int] = None,
) -> pd.DataFrame:
    """Load cleaned staging encounters from staging.encounters.

    Parameters
    ----------
    engine : sa.Engine, optional
        SQLAlchemy engine. Defaults to readmission.db.get_engine().
    limit : int, optional
        Optional row limit for quick testing.

    Returns
    -------
    pd.DataFrame
        DataFrame of staging encounters (99,340 rows expected when full).
    """
    eng = engine or get_engine()
    query = "SELECT * FROM staging.encounters ORDER BY encounter_id"
    if limit is not None and limit > 0:
        query += f" LIMIT {limit}"

    with eng.connect() as conn:
        df = pd.read_sql(sa.text(query), conn)

    return df


def load_dim_tables(
    engine: Optional[sa.Engine] = None,
) -> dict[str, pd.DataFrame]:
    """Load dimensional lookup tables from staging.dim_*.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary with keys 'admission_type', 'discharge_disposition', 'admission_source'.
    """
    eng = engine or get_engine()
    tables = {
        "admission_type": "staging.dim_admission_type",
        "discharge_disposition": "staging.dim_discharge_disposition",
        "admission_source": "staging.dim_admission_source",
    }
    dims = {}
    with eng.connect() as conn:
        for key, tbl in tables.items():
            dims[key] = pd.read_sql(sa.text(f"SELECT * FROM {tbl} ORDER BY 1"), conn)
    return dims
