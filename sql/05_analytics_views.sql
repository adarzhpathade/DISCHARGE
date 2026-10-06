-- 05_analytics_views.sql
-- Analytics views powering Power BI dashboards and FastAPI /stats endpoints.
-- Reference: AGENTS.md §8, docs/database_schema.md, and ROADMAP.md P3-10

CREATE SCHEMA IF NOT EXISTS analytics;

-- 1. High-level clinical overview KPI (1 row)
CREATE OR REPLACE VIEW analytics.vw_readmission_overview AS
SELECT
    COUNT(*) AS total_encounters,
    COUNT(DISTINCT patient_nbr) AS total_patients,
    SUM(readmitted_30d) AS readmissions_30d,
    ROUND(AVG(readmitted_30d)::numeric, 4) AS readmission_rate,
    ROUND(AVG(time_in_hospital)::numeric, 2) AS avg_los,
    ROUND(AVG(num_medications)::numeric, 2) AS avg_medications
FROM staging.encounters;

-- 2. Readmission rates stratified by demographics
CREATE OR REPLACE VIEW analytics.vw_readmission_by_demographics AS
SELECT
    CASE
        WHEN age_bucket IN ('[0-10)', '[10-20)', '[20-30)', '[30-40)') THEN '<40'
        WHEN age_bucket IN ('[40-50)', '[50-60)') THEN '40-59'
        WHEN age_bucket IN ('[60-70)', '[70-80)') THEN '60-79'
        ELSE '80+'
    END AS age_group,
    gender,
    race,
    COUNT(*) AS encounters,
    SUM(readmitted_30d) AS readmissions_30d,
    ROUND(AVG(readmitted_30d)::numeric, 4) AS readmission_rate
FROM staging.encounters
GROUP BY 1, gender, race;

-- 3. Readmission rates by primary ICD-9 diagnosis group (Strack et al. 2014)
CREATE OR REPLACE VIEW analytics.vw_readmission_by_diagnosis AS
WITH classified AS (
    SELECT
        encounter_id,
        readmitted_30d,
        time_in_hospital,
        CASE
            WHEN diag_1 IS NULL OR diag_1 IN ('?', 'Missing', '') THEN 'Missing'
            WHEN diag_1 LIKE '250%' THEN 'Diabetes'
            WHEN diag_1 ~* '^[ve]' THEN 'Other'
            WHEN diag_1 ~ '^[0-9]+' AND (
                (split_part(diag_1, '.', 1)::int BETWEEN 390 AND 459) OR split_part(diag_1, '.', 1)::int = 785
            ) THEN 'Circulatory'
            WHEN diag_1 ~ '^[0-9]+' AND (
                (split_part(diag_1, '.', 1)::int BETWEEN 460 AND 519) OR split_part(diag_1, '.', 1)::int = 786
            ) THEN 'Respiratory'
            WHEN diag_1 ~ '^[0-9]+' AND (
                (split_part(diag_1, '.', 1)::int BETWEEN 520 AND 579) OR split_part(diag_1, '.', 1)::int = 787
            ) THEN 'Digestive'
            WHEN diag_1 ~ '^[0-9]+' AND (split_part(diag_1, '.', 1)::int BETWEEN 800 AND 999) THEN 'Injury'
            WHEN diag_1 ~ '^[0-9]+' AND (split_part(diag_1, '.', 1)::int BETWEEN 710 AND 739) THEN 'Musculoskeletal'
            WHEN diag_1 ~ '^[0-9]+' AND (
                (split_part(diag_1, '.', 1)::int BETWEEN 580 AND 629) OR split_part(diag_1, '.', 1)::int = 788
            ) THEN 'Genitourinary'
            WHEN diag_1 ~ '^[0-9]+' AND (split_part(diag_1, '.', 1)::int BETWEEN 140 AND 239) THEN 'Neoplasms'
            ELSE 'Other'
        END AS diag_1_group
    FROM staging.encounters
)
SELECT
    diag_1_group,
    COUNT(*) AS encounters,
    SUM(readmitted_30d) AS readmissions_30d,
    ROUND(AVG(readmitted_30d)::numeric, 4) AS readmission_rate,
    ROUND(AVG(time_in_hospital)::numeric, 2) AS avg_los
FROM classified
GROUP BY diag_1_group;

-- 4. Readmission rates by admission pathways and discharge dispositions
CREATE OR REPLACE VIEW analytics.vw_readmission_by_admission AS
SELECT
    CASE
        WHEN admission_type_id = 1 THEN 'Emergency'
        WHEN admission_type_id = 2 THEN 'Urgent'
        WHEN admission_type_id = 3 THEN 'Elective'
        ELSE 'Other-Unknown'
    END AS admission_type_grp,
    CASE
        WHEN LOWER(admission_source_desc) LIKE '%emergency%' THEN 'Emergency Room'
        WHEN LOWER(admission_source_desc) LIKE '%referral%' THEN 'Referral'
        WHEN LOWER(admission_source_desc) LIKE '%transfer%' THEN 'Transfer'
        ELSE 'Other-Unknown'
    END AS admission_source_grp,
    CASE
        WHEN LOWER(discharge_disposition_desc) LIKE '%home with home health%' THEN 'Home Health'
        WHEN LOWER(discharge_disposition_desc) LIKE '%home%' AND LOWER(discharge_disposition_desc) NOT LIKE '%iv%' THEN 'Home'
        WHEN LOWER(discharge_disposition_desc) LIKE '%snf%'
             OR LOWER(discharge_disposition_desc) LIKE '%nursing%'
             OR LOWER(discharge_disposition_desc) LIKE '%icf%'
             OR LOWER(discharge_disposition_desc) LIKE '%rehab%' THEN 'Facility (SNF/ICF/Rehab)'
        WHEN LOWER(discharge_disposition_desc) LIKE '%short term hospital%'
             OR LOWER(discharge_disposition_desc) LIKE '%inpatient care%' THEN 'Transfer Hospital'
        ELSE 'Other-Unknown'
    END AS discharge_grp,
    COUNT(*) AS encounters,
    SUM(readmitted_30d) AS readmissions_30d,
    ROUND(AVG(readmitted_30d)::numeric, 4) AS readmission_rate
FROM staging.encounters
GROUP BY 1, 2, 3;

-- 5. Prior healthcare utilization risk gradients
CREATE OR REPLACE VIEW analytics.vw_utilization AS
SELECT
    CASE
        WHEN number_inpatient = 0 THEN '0 visits'
        WHEN number_inpatient = 1 THEN '1 visit'
        WHEN number_inpatient = 2 THEN '2 visits'
        ELSE '3+ visits'
    END AS inpatient_bin,
    CASE
        WHEN number_emergency = 0 THEN '0 visits'
        WHEN number_emergency = 1 THEN '1 visit'
        ELSE '2+ visits'
    END AS emergency_bin,
    COUNT(*) AS encounters,
    SUM(readmitted_30d) AS readmissions_30d,
    ROUND(AVG(readmitted_30d)::numeric, 4) AS readmission_rate,
    ROUND(AVG(time_in_hospital)::numeric, 2) AS avg_los
FROM staging.encounters
GROUP BY 1, 2;

-- 6. Glycemic testing and diabetic medication therapy summary
CREATE OR REPLACE VIEW analytics.vw_medication_summary AS
SELECT
    a1c_result,
    insulin,
    change AS med_change,
    diabetes_med,
    COUNT(*) AS encounters,
    SUM(readmitted_30d) AS readmissions_30d,
    ROUND(AVG(readmitted_30d)::numeric, 4) AS readmission_rate
FROM staging.encounters
GROUP BY a1c_result, insulin, change, diabetes_med;

-- 7. Risk tier distribution for active ML model (Phase 6 link)
CREATE OR REPLACE VIEW analytics.vw_risk_distribution AS
SELECT
    p.risk_tier,
    p.split,
    COUNT(*) AS n,
    ROUND(AVG(p.probability)::numeric, 4) AS avg_probability,
    ROUND(AVG(p.actual_label)::numeric, 4) AS observed_rate
FROM ml.predictions p
JOIN ml.model_registry m ON p.model_version = m.model_version
WHERE m.is_current = TRUE
GROUP BY p.risk_tier, p.split;

-- 8. Current model performance metrics (Phase 6 link)
CREATE OR REPLACE VIEW analytics.vw_model_performance AS
SELECT
    m.model_version,
    m.algorithm,
    m.decision_threshold,
    m.metrics
FROM ml.model_registry m
WHERE m.is_current = TRUE;

-- 9. Feature importance ranking of current model (Phase 6 link)
CREATE OR REPLACE VIEW analytics.vw_feature_importance AS
SELECT
    f.feature,
    f.importance,
    f.rank,
    f.method
FROM ml.feature_importance f
JOIN ml.model_registry m ON f.model_version = m.model_version
WHERE m.is_current = TRUE
ORDER BY f.rank ASC;

-- 10. High-risk cohort worklist for follow-up prioritisation (Phase 6 link)
CREATE OR REPLACE VIEW analytics.vw_high_risk_patients AS
WITH classified AS (
    SELECT
        encounter_id,
        patient_nbr,
        gender,
        CASE
            WHEN age_bucket IN ('[0-10)', '[10-20)', '[20-30)', '[30-40)') THEN '<40'
            WHEN age_bucket IN ('[40-50)', '[50-60)') THEN '40-59'
            WHEN age_bucket IN ('[60-70)', '[70-80)') THEN '60-79'
            ELSE '80+'
        END AS age_group,
        CASE
            WHEN diag_1 IS NULL OR diag_1 IN ('?', 'Missing', '') THEN 'Missing'
            WHEN diag_1 LIKE '250%' THEN 'Diabetes'
            WHEN diag_1 ~* '^[ve]' THEN 'Other'
            WHEN diag_1 ~ '^[0-9]+' AND (
                (split_part(diag_1, '.', 1)::int BETWEEN 390 AND 459) OR split_part(diag_1, '.', 1)::int = 785
            ) THEN 'Circulatory'
            WHEN diag_1 ~ '^[0-9]+' AND (
                (split_part(diag_1, '.', 1)::int BETWEEN 460 AND 519) OR split_part(diag_1, '.', 1)::int = 786
            ) THEN 'Respiratory'
            WHEN diag_1 ~ '^[0-9]+' AND (
                (split_part(diag_1, '.', 1)::int BETWEEN 520 AND 579) OR split_part(diag_1, '.', 1)::int = 787
            ) THEN 'Digestive'
            WHEN diag_1 ~ '^[0-9]+' AND (split_part(diag_1, '.', 1)::int BETWEEN 800 AND 999) THEN 'Injury'
            WHEN diag_1 ~ '^[0-9]+' AND (split_part(diag_1, '.', 1)::int BETWEEN 710 AND 739) THEN 'Musculoskeletal'
            WHEN diag_1 ~ '^[0-9]+' AND (
                (split_part(diag_1, '.', 1)::int BETWEEN 580 AND 629) OR split_part(diag_1, '.', 1)::int = 788
            ) THEN 'Genitourinary'
            WHEN diag_1 ~ '^[0-9]+' AND (split_part(diag_1, '.', 1)::int BETWEEN 140 AND 239) THEN 'Neoplasms'
            ELSE 'Other'
        END AS diag_1_group,
        time_in_hospital,
        number_inpatient,
        CASE
            WHEN LOWER(discharge_disposition_desc) LIKE '%home with home health%' THEN 'Home Health'
            WHEN LOWER(discharge_disposition_desc) LIKE '%home%' AND LOWER(discharge_disposition_desc) NOT LIKE '%iv%' THEN 'Home'
            WHEN LOWER(discharge_disposition_desc) LIKE '%snf%'
                 OR LOWER(discharge_disposition_desc) LIKE '%nursing%'
                 OR LOWER(discharge_disposition_desc) LIKE '%icf%'
                 OR LOWER(discharge_disposition_desc) LIKE '%rehab%' THEN 'Facility (SNF/ICF/Rehab)'
            WHEN LOWER(discharge_disposition_desc) LIKE '%short term hospital%'
                 OR LOWER(discharge_disposition_desc) LIKE '%inpatient care%' THEN 'Transfer Hospital'
            ELSE 'Other-Unknown'
        END AS discharge_grp
    FROM staging.encounters
)
SELECT
    p.encounter_id,
    c.patient_nbr,
    c.age_group,
    c.gender,
    c.diag_1_group,
    c.time_in_hospital,
    c.number_inpatient,
    c.discharge_grp,
    p.probability,
    p.actual_label,
    p.split
FROM ml.predictions p
JOIN ml.model_registry m ON p.model_version = m.model_version
JOIN classified c ON p.encounter_id = c.encounter_id
WHERE m.is_current = TRUE AND p.risk_tier = 'High';
