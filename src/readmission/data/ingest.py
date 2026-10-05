"""Data ingestion module for loading raw UCI Diabetes dataset into PostgreSQL.

Reads diabetic_data.csv and IDs_mapping.csv and populates raw.diabetic_data
and raw.ids_mapping via high-speed COPY / batch inserts.
Populates staging dimension tables after ingestion.
Follows AGENTS.md §5, §8, §9 and ROADMAP.md P1-03.
"""

from __future__ import annotations

import csv
import logging
import sys
from pathlib import Path
import sqlalchemy as sa

from readmission.config import RAW_DIABETIC_DATA_CSV, RAW_IDS_MAPPING_CSV, SQL_DIR
from readmission.db import execute_sql_file, get_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("readmission.data.ingest")


def ingest_diabetic_data(csv_path: Path | str = RAW_DIABETIC_DATA_CSV) -> int:
    """Stream diabetic_data.csv into raw.diabetic_data using COPY."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Raw dataset file not found: {path}")

    logger.info(f"Ingesting {path} into raw.diabetic_data...")
    engine = get_engine()

    raw_conn = engine.raw_connection()
    try:
        # Obtain underlying DBAPI/psycopg connection
        driver_conn = getattr(raw_conn, "driver_connection", raw_conn)

        with driver_conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE raw.diabetic_data;")
            copy_sql = "COPY raw.diabetic_data FROM STDIN WITH (FORMAT csv, HEADER true, DELIMITER ',')"
            with cur.copy(copy_sql) as copy:
                with open(path, mode="r", encoding="utf-8") as f:
                    while chunk := f.read(65536):
                        copy.write(chunk)
            driver_conn.commit()

        with engine.connect() as conn:
            count = conn.execute(sa.text("SELECT count(*) FROM raw.diabetic_data;")).scalar()
            logger.info(f"raw.diabetic_data loaded successfully with {count:,} rows.")
            return count or 0
    finally:
        raw_conn.close()


def ingest_ids_mapping(csv_path: Path | str = RAW_IDS_MAPPING_CSV) -> int:
    """Load IDs_mapping.csv line-by-line into raw.ids_mapping and populate dim tables."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"IDs mapping file not found: {path}")

    logger.info(f"Ingesting {path} into raw.ids_mapping...")
    engine = get_engine()

    rows: list[dict[str, object]] = []
    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for line_no, row in enumerate(reader, start=1):
            col1 = row[0].strip() if len(row) > 0 and row[0].strip() != "" else None
            col2 = row[1].strip() if len(row) > 1 and row[1].strip() != "" else None
            rows.append({"line_no": line_no, "col1": col1, "col2": col2})

    with engine.begin() as conn:
        conn.execute(sa.text("TRUNCATE TABLE raw.ids_mapping;"))
        if rows:
            insert_stmt = sa.text(
                "INSERT INTO raw.ids_mapping (line_no, col1, col2) VALUES (:line_no, :col1, :col2)"
            )
            conn.execute(insert_stmt, rows)

    logger.info(f"raw.ids_mapping loaded with {len(rows)} lines.")

    # Re-run dim tables creation script to parse raw.ids_mapping into staging.dim_*
    dim_sql_path = SQL_DIR / "02_dim_tables.sql"
    if dim_sql_path.exists():
        logger.info("Populating staging dimension tables from raw.ids_mapping...")
        execute_sql_file(dim_sql_path, engine)

    with engine.connect() as conn:
        adm_type_cnt = conn.execute(sa.text("SELECT count(*) FROM staging.dim_admission_type;")).scalar()
        disch_cnt = conn.execute(sa.text("SELECT count(*) FROM staging.dim_discharge_disposition;")).scalar()
        adm_src_cnt = conn.execute(sa.text("SELECT count(*) FROM staging.dim_admission_source;")).scalar()

        logger.info(
            f"Dimension tables populated: dim_admission_type={adm_type_cnt}, "
            f"dim_discharge_disposition={disch_cnt}, dim_admission_source={adm_src_cnt}"
        )

    return len(rows)


def run_ingest() -> None:
    """Execute complete ingestion pipeline and verify row counts."""
    logger.info("=== Starting Data Ingestion Pipeline ===")
    total_encounters = ingest_diabetic_data()
    total_mappings = ingest_ids_mapping()

    assert total_encounters == 101766, f"Expected 101,766 rows, got {total_encounters}"
    logger.info(f"=== Ingestion Complete: {total_encounters:,} encounters and {total_mappings} mapping lines. ===")


if __name__ == "__main__":
    run_ingest()
