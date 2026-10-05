# Data Quality & Cleaning Report — DISCHARGE System

> Generated automatically by `src/readmission/data/quality.py`. Reference: AGENTS.md §5, ROADMAP.md task P2-04.

## 1. Executive Summary

- **Raw Ingested Encounters:** 101,766 (from `data/raw/diabetic_data.csv`)
- **Raw Unique Patients:** 71,518
- **Clean Staging Encounters:** 99,340 (stored in `staging.encounters`)
- **Clean Staging Unique Patients:** 69,987
- **Total Encounters Excluded:** 2,426 (2.38%)
- **Target Prevalence (<30-day readmission):** Raw = 11.16%, Staging = 11.39%

---

## 2. Rule-by-Rule Cleaning Verification (C1–C13)

| Rule | Description | Rows Before | Rows Dropped | Rows After | Status |
|---|---|---|---|---|---|
| **C1** | Load raw CSV with all 50 columns as TEXT | — | 0 | 101,766 | ✅ Verified |
| **C2** | Standardize missing `'?'` values | 101,766 | 0 | 101,766 | ✅ Verified (0 `'?'` remaining) |
| **C3** | Drop invalid gender entries (`Unknown/Invalid`) | 101,766 | 3 | 101,763 | ✅ Dropped 3 rows |
| **C4** | Drop expired / hospice discharge dispositions (11, 13, 14, 19, 20, 21) | 101,763 | 2,423 | 99,340 | ✅ Dropped 2,423 rows |
| **C5** | Assert `encounter_id` uniqueness | 99,340 | 0 | 99,340 | ✅ Verified (100% unique) |
| **C6** | Map `race` missingness to `'Unknown'` | 99,340 | 0 | 99,340 | ✅ 0 NULLs in staging |
| **C7** | Map `medical_specialty` missingness to `'Missing'` | 99,340 | 0 | 99,340 | ✅ 0 NULLs in staging |
| **C8** | Map `A1Cresult` and `max_glu_serum` `'None'` / missing to `'NotMeasured'` | 99,340 | 0 | 99,340 | ✅ Informative category preserved |
| **C9** | Drop `weight` (96.86% missing) and `payer_code` (39.56% missing) | 99,340 | 0 cols dropped | 99,340 | ✅ Excluded from staging |
| **C10** | Drop `examide` and `citoglipton` (constant `'No'`) | 99,340 | 0 cols dropped | 99,340 | ✅ Excluded from staging |
| **C11** | Cast numerics to INTEGER and validate ranges | 99,340 | 0 | 99,340 | ✅ 0 out-of-range violations |
| **C12** | Preserve `diag_1`, `diag_2`, `diag_3` codes as TEXT; map missing to `'Missing'` | 99,340 | 0 | 99,340 | ✅ V/E codes preserved |
| **C13** | Map dimension descriptions from `staging.dim_*` | 99,340 | 0 | 99,340 | ✅ Joined for Power BI & analytics |

---

## 3. Raw Missingness Analysis

The table below details all raw columns containing missing markers (`'?'` or NULL):

| Column Name | Raw Rows | '?' Count | NULL Count | Total Missing | Missing % | Action Taken |
|---|---|---|---|---|---|---|
| `weight` | 101,766 | 98,569 | 0 | 98,569 | 96.86% | Dropped (C9: 96.86% missing, uninformative) |
| `medical_specialty` | 101,766 | 49,949 | 0 | 49,949 | 49.08% | Imputed to `'Missing'` (C7); top 10 grouped in features |
| `payer_code` | 101,766 | 40,256 | 0 | 40,256 | 39.56% | Dropped (C9: 39.56% missing, administrative billing code) |
| `race` | 101,766 | 2,273 | 0 | 2,273 | 2.23% | Imputed to `'Unknown'` (C6) |
| `diag_3` | 101,766 | 1,423 | 0 | 1,423 | 1.4% | Imputed to `'Missing'` (C12); grouped to ICD categories |
| `diag_2` | 101,766 | 358 | 0 | 358 | 0.35% | Imputed to `'Missing'` (C12); grouped to ICD categories |
| `diag_1` | 101,766 | 21 | 0 | 21 | 0.02% | Imputed to `'Missing'` (C12); grouped to ICD categories |

---

## 4. Staging Data Integrity Checks

- **Staging Columns Count:** 50
- **Unmapped Question Marks (`'?'`):** 0
- **Unintended NULL Values:** 0 (only foreign description columns permit fallback if unmapped)
- **Numeric Constraints:** `time_in_hospital` ∈ [1, 14], procedure & visit counts ≥ 0

---

## 5. Summary of Target Distribution

| Readmission Status | Raw Encounters | Raw Share (%) | Staging Encounters | Staging Share (%) |
|---|---|---|---|---|
| `<30` (Positive Target `readmitted_30d = 1`) | 11,357 | 11.16% | 11,314 | 11.39% |
| `>30` (Negative for 30-day unplanned) | 35,545 | 34.93% | 34,649 | 34.88% |
| `NO` (Negative) | 54,864 | 53.91% | 53,377 | 53.73% |
| **Total** | **101,766** | **100.00%** | **99,340** | **100.00%** |

---
**Conclusion:** The dataset is fully validated, free of data leakage from post-discharge deceased/hospice patients, and prepared for feature engineering.