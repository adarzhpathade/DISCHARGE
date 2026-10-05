-- 02_dim_tables.sql
-- Lookup dimension tables extracted and parsed from raw.ids_mapping
-- Reference: AGENTS.md §5 (Rule C13), §8, and docs/database_schema.md

DROP TABLE IF EXISTS staging.dim_admission_type CASCADE;

CREATE TABLE staging.dim_admission_type (
    admission_type_id INT PRIMARY KEY,
    description       TEXT
);

DROP TABLE IF EXISTS staging.dim_discharge_disposition CASCADE;

CREATE TABLE staging.dim_discharge_disposition (
    discharge_disposition_id INT PRIMARY KEY,
    description              TEXT
);

DROP TABLE IF EXISTS staging.dim_admission_source CASCADE;

CREATE TABLE staging.dim_admission_source (
    admission_source_id INT PRIMARY KEY,
    description         TEXT
);

-- Populate if raw.ids_mapping contains data
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'raw' AND table_name = 'ids_mapping') THEN
        IF EXISTS (SELECT 1 FROM raw.ids_mapping) THEN
            WITH bounds AS (
                SELECT
                    COALESCE(MAX(CASE WHEN col1 = 'admission_type_id' THEN line_no END), 0) AS adm_type_start,
                    COALESCE(MAX(CASE WHEN col1 = 'discharge_disposition_id' THEN line_no END), 0) AS disch_disp_start,
                    COALESCE(MAX(CASE WHEN col1 = 'admission_source_id' THEN line_no END), 0) AS adm_src_start
                FROM raw.ids_mapping
            )
            INSERT INTO staging.dim_admission_type (admission_type_id, description)
            SELECT
                col1::INT,
                TRIM(col2)
            FROM raw.ids_mapping, bounds
            WHERE line_no > bounds.adm_type_start
              AND line_no < bounds.disch_disp_start
              AND col1 IS NOT NULL
              AND col1 ~ '^[0-9]+$'
            ON CONFLICT (admission_type_id) DO UPDATE SET description = EXCLUDED.description;

            WITH bounds AS (
                SELECT
                    COALESCE(MAX(CASE WHEN col1 = 'admission_type_id' THEN line_no END), 0) AS adm_type_start,
                    COALESCE(MAX(CASE WHEN col1 = 'discharge_disposition_id' THEN line_no END), 0) AS disch_disp_start,
                    COALESCE(MAX(CASE WHEN col1 = 'admission_source_id' THEN line_no END), 0) AS adm_src_start
                FROM raw.ids_mapping
            )
            INSERT INTO staging.dim_discharge_disposition (discharge_disposition_id, description)
            SELECT
                col1::INT,
                TRIM(col2)
            FROM raw.ids_mapping, bounds
            WHERE line_no > bounds.disch_disp_start
              AND line_no < bounds.adm_src_start
              AND col1 IS NOT NULL
              AND col1 ~ '^[0-9]+$'
            ON CONFLICT (discharge_disposition_id) DO UPDATE SET description = EXCLUDED.description;

            WITH bounds AS (
                SELECT
                    COALESCE(MAX(CASE WHEN col1 = 'admission_type_id' THEN line_no END), 0) AS adm_type_start,
                    COALESCE(MAX(CASE WHEN col1 = 'discharge_disposition_id' THEN line_no END), 0) AS disch_disp_start,
                    COALESCE(MAX(CASE WHEN col1 = 'admission_source_id' THEN line_no END), 0) AS adm_src_start
                FROM raw.ids_mapping
            )
            INSERT INTO staging.dim_admission_source (admission_source_id, description)
            SELECT
                col1::INT,
                TRIM(col2)
            FROM raw.ids_mapping, bounds
            WHERE line_no > bounds.adm_src_start
              AND col1 IS NOT NULL
              AND col1 ~ '^[0-9]+$'
            ON CONFLICT (admission_source_id) DO UPDATE SET description = EXCLUDED.description;
        END IF;
    END IF;
END $$;
