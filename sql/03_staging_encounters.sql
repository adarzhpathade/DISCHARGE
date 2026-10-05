-- 03_staging_encounters.sql
-- Cleaned, typed staging encounters table implementing rules C1–C13
-- Reference: AGENTS.md §5, §8, and docs/database_schema.md

DROP TABLE IF EXISTS staging.encounters CASCADE;

CREATE TABLE staging.encounters (
    encounter_id               BIGINT PRIMARY KEY,
    patient_nbr                BIGINT NOT NULL,
    race                       TEXT NOT NULL,
    gender                     TEXT NOT NULL,
    age_bucket                 TEXT NOT NULL,
    admission_type_id          INT NOT NULL,
    admission_type_desc        TEXT,
    discharge_disposition_id   INT NOT NULL,
    discharge_disposition_desc TEXT,
    admission_source_id        INT NOT NULL,
    admission_source_desc      TEXT,
    time_in_hospital           INT NOT NULL,
    medical_specialty          TEXT NOT NULL,
    num_lab_procedures         INT NOT NULL,
    num_procedures             INT NOT NULL,
    num_medications            INT NOT NULL,
    number_outpatient          INT NOT NULL,
    number_emergency           INT NOT NULL,
    number_inpatient           INT NOT NULL,
    diag_1                     TEXT NOT NULL,
    diag_2                     TEXT NOT NULL,
    diag_3                     TEXT NOT NULL,
    number_diagnoses           INT NOT NULL,
    max_glu_serum              TEXT NOT NULL,
    a1c_result                 TEXT NOT NULL,
    metformin                  TEXT NOT NULL,
    repaglinide                TEXT NOT NULL,
    nateglinide                TEXT NOT NULL,
    chlorpropamide             TEXT NOT NULL,
    glimepiride                TEXT NOT NULL,
    acetohexamide              TEXT NOT NULL,
    glipizide                  TEXT NOT NULL,
    glyburide                  TEXT NOT NULL,
    tolbutamide                TEXT NOT NULL,
    pioglitazone               TEXT NOT NULL,
    rosiglitazone              TEXT NOT NULL,
    acarbose                   TEXT NOT NULL,
    miglitol                   TEXT NOT NULL,
    troglitazone               TEXT NOT NULL,
    tolazamide                 TEXT NOT NULL,
    insulin                    TEXT NOT NULL,
    glyburide_metformin        TEXT NOT NULL,
    glipizide_metformin        TEXT NOT NULL,
    glimepiride_pioglitazone   TEXT NOT NULL,
    metformin_rosiglitazone    TEXT NOT NULL,
    metformin_pioglitazone     TEXT NOT NULL,
    change                     TEXT NOT NULL,
    diabetes_med               TEXT NOT NULL,
    readmitted                 TEXT NOT NULL,
    readmitted_30d             INT NOT NULL,
    CONSTRAINT chk_staging_time_in_hospital CHECK (time_in_hospital >= 1 AND time_in_hospital <= 14),
    CONSTRAINT chk_staging_num_lab_procedures CHECK (num_lab_procedures >= 0),
    CONSTRAINT chk_staging_num_procedures CHECK (num_procedures >= 0),
    CONSTRAINT chk_staging_num_medications CHECK (num_medications >= 0),
    CONSTRAINT chk_staging_number_outpatient CHECK (number_outpatient >= 0),
    CONSTRAINT chk_staging_number_emergency CHECK (number_emergency >= 0),
    CONSTRAINT chk_staging_number_inpatient CHECK (number_inpatient >= 0),
    CONSTRAINT chk_staging_number_diagnoses CHECK (number_diagnoses >= 0),
    CONSTRAINT chk_staging_gender CHECK (gender IN ('Male', 'Female')),
    CONSTRAINT chk_staging_readmitted_30d CHECK (readmitted_30d IN (0, 1))
);

INSERT INTO staging.encounters (
    encounter_id,
    patient_nbr,
    race,
    gender,
    age_bucket,
    admission_type_id,
    admission_type_desc,
    discharge_disposition_id,
    discharge_disposition_desc,
    admission_source_id,
    admission_source_desc,
    time_in_hospital,
    medical_specialty,
    num_lab_procedures,
    num_procedures,
    num_medications,
    number_outpatient,
    number_emergency,
    number_inpatient,
    diag_1,
    diag_2,
    diag_3,
    number_diagnoses,
    max_glu_serum,
    a1c_result,
    metformin,
    repaglinide,
    nateglinide,
    chlorpropamide,
    glimepiride,
    acetohexamide,
    glipizide,
    glyburide,
    tolbutamide,
    pioglitazone,
    rosiglitazone,
    acarbose,
    miglitol,
    troglitazone,
    tolazamide,
    insulin,
    glyburide_metformin,
    glipizide_metformin,
    glimepiride_pioglitazone,
    metformin_rosiglitazone,
    metformin_pioglitazone,
    change,
    diabetes_med,
    readmitted,
    readmitted_30d
)
SELECT
    r.encounter_id::BIGINT,
    r.patient_nbr::BIGINT,
    -- Rule C6: race NULL or '?' -> 'Unknown'
    CASE WHEN r.race IS NULL OR r.race = '?' THEN 'Unknown' ELSE r.race END AS race,
    -- Rule C3: gender (Unknown/Invalid dropped in WHERE)
    r.gender,
    r.age AS age_bucket,
    -- Rule C13: join with dim_admission_type
    r.admission_type_id::INT,
    COALESCE(dat.description, 'Not Available') AS admission_type_desc,
    -- Rule C4 & C13: discharge_disposition (expired/hospice dropped in WHERE)
    r.discharge_disposition_id::INT,
    COALESCE(ddd.description, 'Not Available') AS discharge_disposition_desc,
    -- Rule C13: join with dim_admission_source
    r.admission_source_id::INT,
    COALESCE(das.description, 'Not Available') AS admission_source_desc,
    -- Rule C11: cast to INT
    r.time_in_hospital::INT,
    -- Rule C7: medical_specialty NULL or '?' -> 'Missing'
    CASE WHEN r.medical_specialty IS NULL OR r.medical_specialty = '?' THEN 'Missing' ELSE r.medical_specialty END AS medical_specialty,
    -- Rule C11: counts cast to INT
    r.num_lab_procedures::INT,
    r.num_procedures::INT,
    r.num_medications::INT,
    r.number_outpatient::INT,
    r.number_emergency::INT,
    r.number_inpatient::INT,
    -- Rule C12: diag_* NULL or '?' -> 'Missing' (text preserved)
    CASE WHEN r.diag_1 IS NULL OR r.diag_1 = '?' THEN 'Missing' ELSE r.diag_1 END AS diag_1,
    CASE WHEN r.diag_2 IS NULL OR r.diag_2 = '?' THEN 'Missing' ELSE r.diag_2 END AS diag_2,
    CASE WHEN r.diag_3 IS NULL OR r.diag_3 = '?' THEN 'Missing' ELSE r.diag_3 END AS diag_3,
    r.number_diagnoses::INT,
    -- Rule C8: max_glu_serum & A1Cresult NULL/'?'/'None' -> 'NotMeasured'
    CASE WHEN r.max_glu_serum IS NULL OR r.max_glu_serum = '?' OR r.max_glu_serum = 'None' THEN 'NotMeasured' ELSE r.max_glu_serum END AS max_glu_serum,
    CASE WHEN r."A1Cresult" IS NULL OR r."A1Cresult" = '?' OR r."A1Cresult" = 'None' THEN 'NotMeasured' ELSE r."A1Cresult" END AS a1c_result,
    -- Rule C10: examide and citoglipton dropped. 21 kept meds in snake_case
    r.metformin,
    r.repaglinide,
    r.nateglinide,
    r.chlorpropamide,
    r.glimepiride,
    r.acetohexamide,
    r.glipizide,
    r.glyburide,
    r.tolbutamide,
    r.pioglitazone,
    r.rosiglitazone,
    r.acarbose,
    r.miglitol,
    r.troglitazone,
    r.tolazamide,
    r.insulin,
    r."glyburide-metformin" AS glyburide_metformin,
    r."glipizide-metformin" AS glipizide_metformin,
    r."glimepiride-pioglitazone" AS glimepiride_pioglitazone,
    r."metformin-rosiglitazone" AS metformin_rosiglitazone,
    r."metformin-pioglitazone" AS metformin_pioglitazone,
    r.change,
    r."diabetesMed" AS diabetes_med,
    -- Target definition (D-005)
    r.readmitted,
    CASE WHEN r.readmitted = '<30' THEN 1 ELSE 0 END AS readmitted_30d
FROM raw.diabetic_data r
LEFT JOIN staging.dim_admission_type dat
    ON r.admission_type_id::INT = dat.admission_type_id
LEFT JOIN staging.dim_discharge_disposition ddd
    ON r.discharge_disposition_id::INT = ddd.discharge_disposition_id
LEFT JOIN staging.dim_admission_source das
    ON r.admission_source_id::INT = das.admission_source_id
WHERE
    -- Rule C3: drop rows where gender = 'Unknown/Invalid' (3 rows)
    r.gender != 'Unknown/Invalid'
    -- Rule C4: drop rows with discharge_disposition_id in (11, 13, 14, 19, 20, 21) (expired / hospice)
    AND r.discharge_disposition_id::INT NOT IN (11, 13, 14, 19, 20, 21);

-- Indexes for performance and downstream joins
CREATE INDEX IF NOT EXISTS idx_staging_encounters_patient_nbr ON staging.encounters(patient_nbr);
CREATE INDEX IF NOT EXISTS idx_staging_encounters_readmitted_30d ON staging.encounters(readmitted_30d);
CREATE INDEX IF NOT EXISTS idx_staging_encounters_adm_type ON staging.encounters(admission_type_id);
CREATE INDEX IF NOT EXISTS idx_staging_encounters_disch_disp ON staging.encounters(discharge_disposition_id);
CREATE INDEX IF NOT EXISTS idx_staging_encounters_adm_src ON staging.encounters(admission_source_id);
