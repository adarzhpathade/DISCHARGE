# API Contract — FastAPI `/api/v1`

> The frontend depends **only** on this contract. Change it here first, then regenerate
> `frontend/src/lib/api-types.ts` from `openapi.json`. Base URL: `http://localhost:8000/api/v1`.

## Conventions
- `risk_tier` (capacity ranking: High = top 10%) and `flagged_for_follow_up` (probability ≥ decision threshold, recall-oriented) are **independent**. A `Medium` or `Low` patient can be flagged (AGENTS.md §7.4).
- JSON, snake_case keys. Errors use FastAPI's standard shape `{"detail": ...}`. Validation errors return **422**.
- Every risk-bearing response includes `disclaimer` (AGENTS.md §10.4).
- CORS allows `API_CORS_ORIGINS` (default `http://localhost:3000`).

---

### GET `/health`
```json
{ "status": "ok", "database": "ok", "model_loaded": true, "model_version": "v20261106_hgb" }
```

### GET `/model/info`
```json
{ "model_version": "v20261106_hgb", "algorithm": "HistGradientBoostingClassifier+isotonic",
  "trained_at": "2026-11-06T18:20:00", "decision_threshold": 0.118,
  "tier_cutoffs": {"medium": 0.135, "high": 0.205}, "train_rows": 69500, "base_rate": 0.112 }
```

### GET `/model/metrics`
```json
{ "cv":  {"roc_auc": 0.672},
  "val": {"roc_auc": 0.674, "pr_auc": 0.228, "recall": 0.63, "precision": 0.18, "f1": 0.28, "brier": 0.094},
  "test": {"roc_auc": 0.669, "pr_auc": 0.221, "recall": 0.61, "precision": 0.18, "f1": 0.27, "brier": 0.095,
           "confusion_matrix": [[9800, 3400], [650, 1050]]} }
```
*(numbers illustrative)*

### GET `/model/feature-importance?top=15`
```json
{ "method": "permutation", "features": [ {"feature": "number_inpatient", "importance": 0.031, "rank": 1}, … ] }
```

### POST `/predict`
**Request — `PatientInput`**
| Field | Type | Constraint |
|---|---|---|
| race | enum | Caucasian, AfricanAmerican, Hispanic, Asian, Other, Unknown |
| gender | enum | Male, Female |
| age_bucket | enum | `[0-10)` … `[90-100)` |
| admission_type_id | int | 1–8 |
| discharge_disposition_id | int | 1–30, **not** in {11,13,14,19,20,21} (422 with an explanatory message) |
| admission_source_id | int | 1–26 |
| time_in_hospital | int | 1–14 |
| medical_specialty | string | free text; unknown values → Other |
| num_lab_procedures | int | 0–200 |
| num_procedures | int | 0–10 |
| num_medications | int | 0–100 |
| number_outpatient, number_emergency, number_inpatient | int | 0–100 |
| number_diagnoses | int | 1–20 |
| diag_1, diag_2, diag_3 | string | ICD-9 code or `Missing` |
| max_glu_serum | enum | NotMeasured, Norm, >200, >300 |
| a1c_result | enum | NotMeasured, Norm, >7, >8 |
| medications | object | optional `{ "<med_name>": "No"|"Steady"|"Up"|"Down" }`. Omitted meds = "No" |
| change | enum | Ch, No |
| diabetes_med | enum | Yes, No |

**Response — `PredictionResult`**
```json
{
  "request_id": "6f1c…",
  "model_version": "v20261106_hgb",
  "probability": 0.27,
  "risk_tier": "High",
  "flagged_for_follow_up": true,
  "decision_threshold": 0.118,
  "base_rate": 0.112,
  "relative_risk": 2.4,
  "top_factors": [
    {"feature": "number_inpatient", "label": "Prior inpatient visits (past year)", "value": 2, "direction": "increases_risk", "contribution": 0.041},
    {"feature": "discharge_grp", "label": "Discharge destination", "value": "Facility", "direction": "increases_risk", "contribution": 0.022}
  ],
  "disclaimer": "This is a statistical risk estimate based on historical patterns, intended to support — not replace — clinical judgement. It does not determine whether this patient will be readmitted."
}
```

### POST `/predict/batch`
`multipart/form-data`, field `file` = CSV with the `PatientInput` columns (meds as separate columns). Max 5,000 rows.
```json
{ "model_version": "...", "count": 120, "summary": {"High": 14, "Medium": 25, "Low": 81},
  "results": [ {"row": 0, "probability": 0.08, "risk_tier": "Low"}, … ],
  "errors": [ {"row": 7, "detail": "time_in_hospital must be 1–14"} ], "disclaimer": "…" }
```

### GET `/patients/high-risk`
Query: `tier` (High|Medium|Low, default High), `split` (default test), `age_group`, `diag_group`, `limit` (≤100, default 25), `offset`.
```json
{ "total": 1490, "limit": 25, "offset": 0,
  "items": [ {"encounter_id": 123, "age_group": "60-79", "gender": "Female", "diag_1_group": "Circulatory",
              "time_in_hospital": 6, "number_inpatient": 2, "discharge_grp": "Facility",
              "probability": 0.41, "risk_tier": "High", "actual_label": 1} ] }
```

### GET `/stats/overview`
```json
{ "total_encounters": 99340, "total_patients": 69990, "readmission_rate_30d": 0.112,
  "avg_length_of_stay": 4.4, "high_risk_share": 0.10, "model_version": "v20261106_hgb" }
```
