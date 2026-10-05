# Data Dictionary

> Source: UCI Diabetes 130-US Hospitals (1999–2008), Strack et al. 2014.
> Updated with exact measured values from the data quality audit (`reports/eda/raw_data_quality_audit.csv`).

## 1. Raw columns → staging columns

| Raw column | Staging column (`staging.encounters`) | Type | Description | Values / range | % missing (raw) | Used as feature? |
|---|---|---|---|---|---|---|
| encounter_id | encounter_id | BIGINT PK | Unique encounter identifier | 12578–443867222 | 0.00% | No (ID) |
| patient_nbr | patient_nbr | BIGINT | Patient identifier | 135–189502619 | 0.00% | No (split groups) |
| race | race | TEXT | Patient race/ethnicity | Caucasian, AfricanAmerican, Hispanic, Asian, Other, Unknown | 2.23% (2,273 '?') | Yes (+fairness) |
| gender | gender | TEXT | Biological sex | Male, Female | <0.01% (3 'Unknown/Invalid' dropped) | Yes (+fairness) |
| age | age_bucket | TEXT | 10-year age interval | [0-10) … [90-100) | 0.00% | via `age_mid`, `age_group` |
| weight | — (dropped, C9) | — | Weight interval in lbs | [0-25) … [175-200) | 96.86% (98,569 '?') | No (dropped) |
| admission_type_id | admission_type_id, admission_type_desc | INT, TEXT | Admission type code & description | 1–8 | 0.00% | via `admission_type_grp` |
| discharge_disposition_id | discharge_disposition_id, discharge_disposition_desc | INT, TEXT | Discharge destination code & description | 1–30 (11,13,14,19,20,21 dropped) | 0.00% | via `discharge_grp` |
| admission_source_id | admission_source_id, admission_source_desc | INT, TEXT | Admission source code & description | 1–26 | 0.00% | via `admission_source_grp` |
| time_in_hospital | time_in_hospital | INT | Length of stay (days) | 1–14 | 0.00% | Yes |
| payer_code | — (dropped, C9) | — | Insurance payer | 17 codes (MC, MD, HM, etc.) | 39.56% (40,256 '?') | No (dropped) |
| medical_specialty | medical_specialty | TEXT | Admitting physician specialty | 72 specialties + Missing | 49.08% (49,949 '?') | via `medical_specialty_grp` |
| num_lab_procedures | num_lab_procedures | INT | Lab tests during encounter | 1–132 | 0.00% | Yes |
| num_procedures | num_procedures | INT | Non-lab procedures | 0–6 | 0.00% | Yes |
| num_medications | num_medications | INT | Distinct generic medications | 1–81 | 0.00% | Yes |
| number_outpatient | number_outpatient | INT | Outpatient visits in prior year | 0–42 | 0.00% | Yes |
| number_emergency | number_emergency | INT | Emergency visits in prior year | 0–76 | 0.00% | Yes |
| number_inpatient | number_inpatient | INT | Inpatient visits in prior year | 0–21 | 0.00% | Yes |
| diag_1 | diag_1 | TEXT | Primary ICD-9 diagnosis | ICD-9 codes, V/E codes, Missing | 0.02% (21 '?') | via `diag_1_group` |
| diag_2 | diag_2 | TEXT | Secondary ICD-9 diagnosis | ICD-9 codes, V/E codes, Missing | 0.35% (358 '?') | via `diag_2_group` |
| diag_3 | diag_3 | TEXT | Additional ICD-9 diagnosis | ICD-9 codes, V/E codes, Missing | 1.40% (1,423 '?') | via `diag_3_group` |
| number_diagnoses | number_diagnoses | INT | Total diagnoses entered | 1–16 | 0.00% | Yes |
| max_glu_serum | max_glu_serum | TEXT | Max glucose serum test result | NotMeasured, Norm, >200, >300 | 0.00% ('None' 94.7% = test not run) | Yes |
| A1Cresult | a1c_result | TEXT | HbA1c test result | NotMeasured, Norm, >7, >8 | 0.00% ('None' 83.3% = test not run) | Yes |
| examide, citoglipton | — (dropped, C10) | — | Diabetes oral medication | Constant 'No' | 0.00% | No (zero variance) |
| 21 medication cols | snake_case names | TEXT | Dosage status / change | No, Steady, Up, Down | 0.00% | Yes |
| change | change | TEXT | Change in diabetic medications | Ch, No | 0.00% | Yes |
| diabetesMed | diabetes_med | TEXT | Any diabetic medication prescribed | Yes, No | 0.00% | Yes |
| readmitted | readmitted | TEXT | Readmission outcome in raw data | <30, >30, NO | 0.00% | No (source of target) |
| — | readmitted_30d | INT | **Target**: 1 if readmitted == '<30' | 0 or 1 (11.39% in staging) | — | Target |

## 2. Engineered columns (`features.model_input`)
See AGENTS.md §6.1 for the definitions: `age_mid`, `age_group`, `service_utilization`, `any_prior_inpatient`, `diag_1_group`, `diag_2_group`, `diag_3_group`, `num_meds_active`, `num_med_changes`, `a1c_measured`, `glu_measured`, `admission_type_grp`, `discharge_grp`, `admission_source_grp`, `medical_specialty_grp`, `split`.

## 3. Lookup codes (from `IDs_mapping.csv` → `staging.dim_*`)
Key lookup mappings populated in database:
- **admission_type_id (8 codes):** 1 Emergency, 2 Urgent, 3 Elective, 4 Newborn, 5 Not Available, 6 NULL, 7 Trauma Center, 8 Not Mapped
- **discharge_disposition_id (30 codes, 6 excluded per C4):**
  - Retained: 1 Discharged to home, 2 Discharged/transferred to another short term hospital, 3 SNF, 4 ICF, 5 Another type of inpatient care institution, 6 Home with home health care, 7 Left AMA, 8 Home IV provider, 9 Admitted as inpatient to this hospital, etc.
  - Excluded (Rule C4): 11 Expired, 13 Hospice / home, 14 Hospice / medical facility, 19 Expired at home (Medicaid), 20 Expired in medical facility (Medicaid), 21 Expired place unknown
- **admission_source_id (25 codes):** 1 Physician Referral, 2 Clinic Referral, 3 HMO Referral, 4 Transfer from hospital, 5 Transfer from SNF, 6 Transfer from other health care facility, 7 Emergency Room, …

