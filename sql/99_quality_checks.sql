-- 99_quality_checks.sql
-- Quality validation assertions and audit checks for staging.encounters
-- Reference: AGENTS.md §5, §9, and ROADMAP.md task P2-01

DO $$
DECLARE
    v_raw_count BIGINT;
    v_staging_count BIGINT;
    v_expected_staging_count BIGINT := 99340;
    v_dupes BIGINT;
    v_invalid_gender BIGINT;
    v_hospice_expired BIGINT;
    v_qmarks BIGINT;
    v_null_critical BIGINT;
    v_out_of_range BIGINT;
    v_target_mismatch BIGINT;
    v_c8_unmapped BIGINT;
BEGIN
    -- Check 1: Raw row count
    SELECT count(*) INTO v_raw_count FROM raw.diabetic_data;
    IF v_raw_count != 101766 THEN
        RAISE EXCEPTION 'Quality check failed: expected 101766 raw rows, found %', v_raw_count;
    END IF;

    -- Check 2: Staging row count
    SELECT count(*) INTO v_staging_count FROM staging.encounters;
    IF v_staging_count != v_expected_staging_count THEN
        RAISE EXCEPTION 'Quality check failed: expected % staging rows (101766 - 3 gender - 2423 hospice), found %',
            v_expected_staging_count, v_staging_count;
    END IF;

    -- Check 3: Unique encounter_id (C5)
    SELECT count(*) - count(DISTINCT encounter_id) INTO v_dupes FROM staging.encounters;
    IF v_dupes > 0 THEN
        RAISE EXCEPTION 'Rule C5 violation: found % duplicate encounter_ids in staging.encounters', v_dupes;
    END IF;

    -- Check 4: Invalid gender (C3)
    SELECT count(*) INTO v_invalid_gender FROM staging.encounters WHERE gender NOT IN ('Male', 'Female');
    IF v_invalid_gender > 0 THEN
        RAISE EXCEPTION 'Rule C3 violation: found % invalid gender rows in staging.encounters', v_invalid_gender;
    END IF;

    -- Check 5: Hospice and expired discharge dispositions (C4)
    SELECT count(*) INTO v_hospice_expired FROM staging.encounters
    WHERE discharge_disposition_id IN (11, 13, 14, 19, 20, 21);
    IF v_hospice_expired > 0 THEN
        RAISE EXCEPTION 'Rule C4 violation: found % hospice/expired rows in staging.encounters', v_hospice_expired;
    END IF;

    -- Check 6: Unmapped question marks '?' (C2)
    SELECT count(*) INTO v_qmarks FROM staging.encounters
    WHERE race = '?'
       OR medical_specialty = '?'
       OR diag_1 = '?' OR diag_2 = '?' OR diag_3 = '?'
       OR max_glu_serum = '?' OR a1c_result = '?'
       OR change = '?' OR diabetes_med = '?' OR readmitted = '?';
    IF v_qmarks > 0 THEN
        RAISE EXCEPTION 'Rule C2 violation: found % unmapped question marks in staging.encounters', v_qmarks;
    END IF;

    -- Check 7: Lab 'None' unmapped (C8)
    SELECT count(*) INTO v_c8_unmapped FROM staging.encounters
    WHERE max_glu_serum = 'None' OR a1c_result = 'None';
    IF v_c8_unmapped > 0 THEN
        RAISE EXCEPTION 'Rule C8 violation: found % unmapped ''None'' lab results in staging.encounters', v_c8_unmapped;
    END IF;

    -- Check 8: Numeric ranges and bounds (C11)
    SELECT count(*) INTO v_out_of_range FROM staging.encounters
    WHERE time_in_hospital < 1 OR time_in_hospital > 14
       OR num_lab_procedures < 0
       OR num_procedures < 0
       OR num_medications < 0
       OR number_outpatient < 0
       OR number_emergency < 0
       OR number_inpatient < 0
       OR number_diagnoses < 0;
    IF v_out_of_range > 0 THEN
        RAISE EXCEPTION 'Rule C11 violation: found % out-of-range numeric rows in staging.encounters', v_out_of_range;
    END IF;

    -- Check 9: Target integrity (D-005)
    SELECT count(*) INTO v_target_mismatch FROM staging.encounters
    WHERE (readmitted = '<30' AND readmitted_30d != 1)
       OR (readmitted != '<30' AND readmitted_30d != 0);
    IF v_target_mismatch > 0 THEN
        RAISE EXCEPTION 'Target mismatch: found % rows where readmitted_30d contradicts readmitted', v_target_mismatch;
    END IF;

    RAISE NOTICE 'SUCCESS: All quality checks passed. Staging contains % verified clean encounters.', v_staging_count;
END $$;

-- Audit view summarizing quality metrics across staging
CREATE OR REPLACE VIEW staging.vw_quality_audit AS
SELECT
    'total_encounters' AS metric,
    count(*)::TEXT AS value
FROM staging.encounters
UNION ALL
SELECT
    'unique_patients' AS metric,
    count(DISTINCT patient_nbr)::TEXT AS value
FROM staging.encounters
UNION ALL
SELECT
    'positive_readmitted_30d' AS metric,
    count(*) FILTER (WHERE readmitted_30d = 1)::TEXT AS value
FROM staging.encounters
UNION ALL
SELECT
    'readmission_30d_rate_pct' AS metric,
    ROUND((count(*) FILTER (WHERE readmitted_30d = 1)::NUMERIC / count(*)) * 100, 2)::TEXT AS value
FROM staging.encounters
UNION ALL
SELECT
    'encounters_with_prior_inpatient' AS metric,
    count(*) FILTER (WHERE number_inpatient > 0)::TEXT AS value
FROM staging.encounters
UNION ALL
SELECT
    'a1c_measured_encounters' AS metric,
    count(*) FILTER (WHERE a1c_result != 'NotMeasured')::TEXT AS value
FROM staging.encounters
UNION ALL
SELECT
    'glucose_measured_encounters' AS metric,
    count(*) FILTER (WHERE max_glu_serum != 'NotMeasured')::TEXT AS value
FROM staging.encounters;
