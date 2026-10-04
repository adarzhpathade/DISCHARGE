# Data Dictionary

> Source: UCI Diabetes 130-US Hospitals (1999–2008), Strack et al. 2014. **Update the "% missing (raw)"
> column with your measured values in task P2-06.** The values shown are approximate.

## 1. Raw columns → staging columns

| Raw column | Staging column (`staging.encounters`) | Type | Description | Values / range | % missing (raw) | Used as feature? |
|---|---|---|---|---|---|---|
| encounter_id | encounter_id | BIGINT PK | Unique encounter ID | — | 0 | No (ID) |
| patient_nbr | patient_nbr | BIGINT | Patient ID | — | 0 | No (split groups) |
| race | race | TEXT | Race | Caucasian, AfricanAmerican, Hispanic, Asian, Other, Unknown | ≈2 | Yes (+fairness) |
| gender | gender | TEXT | Gender | Male, Female | <0.01 (invalid) | Yes (+fairness) |
| age | age_bucket | TEXT | 10-year age bucket | [0-10) … [90-100) | 0 | via `age_mid`, `age_group` |
| weight | — (dropped, C9) | — | Weight bucket | — | ≈97 | No |
| admission_type_id | admission_type_id | INT | Admission type code | 1–8 | 0 | via `admission_type_grp` |
| discharge_disposition_id | discharge_disposition_id | INT | Discharge destination code | 1–30 | 0 | via `discharge_grp` |
| admission_source_id | admission_source_id | INT | Admission source code | 1–26 | 0 | via `admission_source_grp` |
| time_in_hospital | time_in_hospital | INT | Length of stay (days) | 1–14 | 0 | Yes |
| payer_code | — (dropped, C9) | — | Insurance payer | — | ≈40 | No |
| medical_specialty | medical_specialty | TEXT | Admitting physician specialty | ≈70 values + Missing | ≈49 | via `medical_specialty_grp` |
| num_lab_procedures | num_lab_procedures | INT | Lab tests during the encounter | 1–132 | 0 | Yes |
| num_procedures | num_procedures | INT | Non-lab procedures | 0–6 | 0 | Yes |
| num_medications | num_medications | INT | Distinct generic medications | 1–81 | 0 | Yes |
| number_outpatient | number_outpatient | INT | Outpatient visits, prior year | 0+ | 0 | Yes |
| number_emergency | number_emergency | INT | Emergency visits, prior year | 0+ | 0 | Yes |
| number_inpatient | number_inpatient | INT | Inpatient visits, prior year | 0+ | 0 | Yes |
| diag_1 / diag_2 / diag_3 | diag_1 / diag_2 / diag_3 | TEXT | Primary / secondary / additional ICD-9 diagnosis | ICD-9 codes, V/E codes | ≈0 / 0.4 / 1.4 | via `diag_*_group` |
| number_diagnoses | number_diagnoses | INT | Diagnoses entered | 1–16 | 0 | Yes |
| max_glu_serum | max_glu_serum | TEXT | Max glucose serum test | NotMeasured, Norm, >200, >300 | "None" ≈95 (a category, not missing) | Yes |
| A1Cresult | a1c_result | TEXT | HbA1c test result | NotMeasured, Norm, >7, >8 | "None" ≈83 (a category) | Yes |
| 23 medication cols | snake_case names (21 kept) | TEXT | Prescribed / dosage change | No, Steady, Up, Down | 0 | Yes (examide, citoglipton dropped, C10) |
| change | change | TEXT | Any diabetic medication change | Ch, No | 0 | Yes |
| diabetesMed | diabetes_med | TEXT | Any diabetic medication prescribed | Yes, No | 0 | Yes |
| readmitted | readmitted | TEXT | Readmission outcome | <30, >30, NO | 0 | No (source of target) |
| — | readmitted_30d | INT | **Target**: 1 if readmitted == '<30' | 0/1 (≈11% = 1) | — | Target |

## 2. Engineered columns (`features.model_input`)
See AGENTS.md §6.1 for the definitions: `age_mid`, `age_group`, `service_utilization`, `any_prior_inpatient`, `diag_1_group`, `diag_2_group`, `diag_3_group`, `num_meds_active`, `num_med_changes`, `a1c_measured`, `glu_measured`, `admission_type_grp`, `discharge_grp`, `admission_source_grp`, `medical_specialty_grp`, `split`.

## 3. Lookup codes (from `IDs_mapping.csv` → `staging.dim_*`)
Fill the exact descriptions after P1-04. Key codes used in the cleaning and grouping rules:
- **admission_type_id:** 1 Emergency, 2 Urgent, 3 Elective, 4 Newborn, 5 Not Available, 6 NULL, 7 Trauma Center, 8 Not Mapped
- **discharge_disposition_id removed (C4):** 11 Expired, 13 Hospice/home, 14 Hospice/medical facility, 19/20/21 Expired (home / medical facility / place unknown)
- **admission_source_id:** 1 Physician Referral, 2 Clinic Referral, 3 HMO Referral, 4 Transfer from a hospital, 5 Transfer from a SNF, 6 Transfer from another health care facility, 7 Emergency Room, …

> ⚠ Verify every grouping in `build.py` against the actual `staging.dim_*` descriptions before finalising (P4-01).
