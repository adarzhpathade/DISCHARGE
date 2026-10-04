# Model Training Guide — From Raw Hospital Data to Readmission Risk Predictions

> A hands-on, step-by-step walkthrough. Follow it in order. Every step has:
> **▶ Run** (what to execute) · **✔ Expect** (what you should see) · **🚩 Checkpoint** (don't continue until this is true).
>
> Paths, table names and conventions follow `AGENTS.md`. Roadmap task IDs are shown as `[P4-02]`, etc.
> The code snippets are the reference implementation for the modules in `src/readmission/`.

---

## Contents
0. [What we are building (in plain words)](#0-what-we-are-building-in-plain-words)
1. [Prerequisites](#1-prerequisites)
2. [Get the data](#2-get-the-data)
3. [Load raw data into PostgreSQL](#3-load-raw-data-into-postgresql)
4. [Clean the data in SQL](#4-clean-the-data-in-sql)
5. [Check the clean data in Python](#5-check-the-clean-data-in-python)
6. [Engineer features](#6-engineer-features)
7. [Split by patient (prevent leakage)](#7-split-by-patient-prevent-leakage)
8. [Build the preprocessing + model pipeline](#8-build-the-preprocessing--model-pipeline)
9. [Train baselines with cross-validation](#9-train-baselines-with-cross-validation)
10. [Tune the best models](#10-tune-the-best-models)
11. [Calibrate probabilities](#11-calibrate-probabilities)
12. [Choose the decision threshold & risk tiers](#12-choose-the-decision-threshold--risk-tiers)
13. [Final evaluation on the test set (once!)](#13-final-evaluation-on-the-test-set-once)
14. [Explain the model](#14-explain-the-model)
15. [Check fairness](#15-check-fairness)
16. [Save the model artifacts](#16-save-the-model-artifacts)
17. [Use the model: get readmission risk for patients](#17-use-the-model-get-readmission-risk-for-patients)
18. [How to read and report the results](#18-how-to-read-and-report-the-results)
19. [Troubleshooting](#19-troubleshooting)
20. [Retraining checklist](#20-retraining-checklist)

---

## 0. What we are building (in plain words)

```
Historical encounters (101k rows)                       New patient at discharge
  with known outcome  ──► clean ──► features ──► train ──►  model  ──►  P(readmit ≤ 30 days) = 0.27
  readmitted = <30 / >30 / NO                                          Risk tier = HIGH
                                                                       Top factors: 3 prior inpatient visits, ...
```

- **Input (X):** what is known about a patient **at or before discharge**: demographics, admission type, length of stay, lab/procedure counts, prior visits, diagnoses, HbA1c/glucose tests, medications, discharge destination.
- **Output (y):** `readmitted_30d` = 1 if the patient was readmitted within 30 days (`readmitted == '<30'`), else 0.
- **Model output:** a **probability** (0–1), which we turn into a **risk tier** (Low / Medium / High) for follow-up prioritisation.
- **What the model does NOT do:** it does not tell you whether a patient *will* return. It gives a risk estimate learned from past patterns.

**Realistic target:** ROC-AUC around **0.64–0.70** on this dataset. That is normal and comparable to the clinical LACE index (C-statistic ≈ 0.68). A much higher score means something leaked (see §19).

---

## 1. Prerequisites

▶ **Run** (once, see `docs/environment_setup.md` for details)
```bash
cd "/Users/pranav/Project Folder/Adarzsh"
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
docker compose up -d          # or start Postgres.app
cp .env.example .env          # then edit if needed
psql "postgresql://readmit:readmit@localhost:5432/readmission_db" -c "select version();"
```

✔ **Expect:** PostgreSQL 16.x version string. `python -c "import sklearn, pandas; print(sklearn.__version__)"` prints ≥ 1.6.

🚩 **Checkpoint:** venv active, DB reachable, `import readmission` works.

---

## 2. Get the data `[P0-05]`

**Option A — manual download (recommended):** download *"Diabetes 130-US Hospitals for Years 1999–2008"* from the UCI ML Repository (id 296). Unzip it, then:
```bash
mkdir -p data/raw
mv ~/Downloads/diabetic_data.csv ~/Downloads/IDs_mapping.csv data/raw/
shasum -a 256 data/raw/*.csv     # record in MEMORY.md
wc -l data/raw/diabetic_data.csv  # header + rows
```

**Option B — Python:** `pip install ucimlrepo`, then `fetch_ucirepo(id=296)`. Note that this version may store `A1Cresult`/`max_glu_serum` "None" as NaN. Our cleaning handles both forms, but Option A keeps the original CSV for the SQL stage.

✔ **Expect:** `wc -l` ≈ 101,767 (101,766 rows + header).

🚩 **Checkpoint:** both files exist in `data/raw/`.

---

## 3. Load raw data into PostgreSQL `[P1-01 … P1-05]`

**Principle:** load everything **as TEXT, unchanged**. Cleaning happens in the next step, and the raw table is our audit trail.

▶ **Run**
```bash
make db-init     # runs sql/00_create_schemas.sql, 01_raw_tables.sql, 02_dim_tables.sql, 04_ml_tables.sql
make ingest      # python -m readmission.data.ingest
```

Reference: `sql/01_raw_tables.sql` (abridged; all 50 columns follow this pattern)
```sql
CREATE TABLE IF NOT EXISTS raw.diabetic_data (
    encounter_id TEXT, patient_nbr TEXT, race TEXT, gender TEXT, age TEXT, weight TEXT,
    admission_type_id TEXT, discharge_disposition_id TEXT, admission_source_id TEXT,
    time_in_hospital TEXT, payer_code TEXT, medical_specialty TEXT,
    num_lab_procedures TEXT, num_procedures TEXT, num_medications TEXT,
    number_outpatient TEXT, number_emergency TEXT, number_inpatient TEXT,
    diag_1 TEXT, diag_2 TEXT, diag_3 TEXT, number_diagnoses TEXT,
    max_glu_serum TEXT, "A1Cresult" TEXT,
    metformin TEXT, repaglinide TEXT, /* … all 23 medication columns … */
    "glyburide-metformin" TEXT, "glipizide-metformin" TEXT, "glimepiride-pioglitazone" TEXT,
    "metformin-rosiglitazone" TEXT, "metformin-pioglitazone" TEXT,
    change TEXT, "diabetesMed" TEXT, readmitted TEXT
);
```

Reference: `src/readmission/data/ingest.py` (core)
```python
import psycopg
from readmission.config import RAW_DIR, DATABASE_URL

def copy_csv(table: str, path) -> int:
    dsn = DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")  # psycopg wants plain URL
    with psycopg.connect(dsn) as conn, conn.cursor() as cur, open(path, encoding="utf-8") as f:
        cur.execute(f"TRUNCATE {table}")
        with cur.copy(f"COPY {table} FROM STDIN WITH (FORMAT csv, HEADER true)") as copy:
            while chunk := f.read(1 << 16):
                copy.write(chunk)
        cur.execute(f"SELECT count(*) FROM {table}")
        return cur.fetchone()[0]

if __name__ == "__main__":
    n = copy_csv("raw.diabetic_data", RAW_DIR / "diabetic_data.csv")
    print(f"raw.diabetic_data: {n:,} rows")
    # IDs_mapping.csv: three stacked tables → load line-by-line into raw.ids_mapping(line_no, col1, col2)
```

✔ **Expect:** `raw.diabetic_data: 101,766 rows`.

🚩 **Checkpoint** (in psql):
```sql
SELECT count(*), count(DISTINCT encounter_id), count(DISTINCT patient_nbr) FROM raw.diabetic_data;
-- ≈ 101766 | 101766 | ≈ 71518
SELECT readmitted, count(*) FROM raw.diabetic_data GROUP BY 1;   -- <30 ≈ 11.4k, >30 ≈ 35.5k, NO ≈ 54.9k
```

---

## 4. Clean the data in SQL `[P2-01, P2-02]`

▶ **Run** `make stage` (runs `sql/03_staging_encounters.sql`, then `sql/99_quality_checks.sql`).

Reference: `sql/03_staging_encounters.sql` (excerpt showing each rule C1–C13 from AGENTS.md §5)
```sql
DROP TABLE IF EXISTS staging.encounters;
CREATE TABLE staging.encounters AS
WITH src AS (
    SELECT * FROM raw.diabetic_data
    WHERE gender <> 'Unknown/Invalid'                                         -- C3
      AND discharge_disposition_id::int NOT IN (11, 13, 14, 19, 20, 21)       -- C4 expired/hospice
)
SELECT
    encounter_id::bigint                                   AS encounter_id,
    patient_nbr::bigint                                    AS patient_nbr,
    COALESCE(NULLIF(race, '?'), 'Unknown')                 AS race,           -- C2, C6
    gender,
    age                                                    AS age_bucket,
    admission_type_id::int, discharge_disposition_id::int, admission_source_id::int,
    time_in_hospital::int,
    COALESCE(NULLIF(medical_specialty, '?'), 'Missing')    AS medical_specialty,  -- C7
    num_lab_procedures::int, num_procedures::int, num_medications::int,
    number_outpatient::int, number_emergency::int, number_inpatient::int,
    COALESCE(NULLIF(diag_1, '?'), 'Missing') AS diag_1,                       -- C12
    COALESCE(NULLIF(diag_2, '?'), 'Missing') AS diag_2,
    COALESCE(NULLIF(diag_3, '?'), 'Missing') AS diag_3,
    number_diagnoses::int,
    CASE WHEN max_glu_serum IS NULL OR max_glu_serum IN ('None','?') THEN 'NotMeasured'
         ELSE max_glu_serum END                            AS max_glu_serum,  -- C8
    CASE WHEN "A1Cresult" IS NULL OR "A1Cresult" IN ('None','?') THEN 'NotMeasured'
         ELSE "A1Cresult" END                              AS a1c_result,     -- C8
    metformin, repaglinide, /* … */ "glyburide-metformin" AS glyburide_metformin, /* … */
    change, "diabetesMed" AS diabetes_med,
    readmitted,
    (readmitted = '<30')::int                              AS readmitted_30d
    -- C9/C10: weight, payer_code, examide, citoglipton intentionally NOT selected
FROM src;

ALTER TABLE staging.encounters ADD PRIMARY KEY (encounter_id);              -- C5 (fails if duplicates)
```
Then join `staging.dim_*` (C13) in the analytics views, or add the description columns here.

✔ **Expect:** ≈ **99,340** rows (101,766 − 3 invalid gender − ≈ 2,423 expired/hospice). Record the exact number.

🚩 **Checkpoint:**
```sql
SELECT count(*) FILTER (WHERE race = '?' OR diag_1 = '?') AS leftover_q,              -- 0
       count(*) FILTER (WHERE discharge_disposition_id IN (11,13,14,19,20,21)) AS dead,  -- 0
       round(avg(readmitted_30d)::numeric, 4) AS base_rate                              -- ≈ 0.11
FROM staging.encounters;
```

---

## 5. Check the clean data in Python `[P2-03, P2-04]`

```python
import pandas as pd
from readmission.db import get_engine

df = pd.read_sql("SELECT * FROM staging.encounters", get_engine())
print(df.shape)                                   # (~99340, ~45)
print(df["readmitted_30d"].mean())                # ~0.11
print(df.isna().sum().loc[lambda s: s > 0])       # should be empty
print(df["a1c_result"].value_counts())            # NotMeasured, >8, Norm, >7
```

> ⚠ **If you ever read the original CSV with pandas**, use
> `pd.read_csv(path, keep_default_na=False, na_values=["?"])`.
> pandas ≥ 2.0 otherwise turns the string `"None"` (meaning *test not done*) into NaN. See MEMORY.md G-001.

▶ **Run** `python -m readmission.data.quality` → writes `reports/eda/data_quality_report.md`.

🚩 **Checkpoint:** no unexpected NaNs, base rate ≈ 11%, report generated.

---

## 6. Engineer features `[P3-04, P4-01]`

▶ **Run** `make features` (`python -m readmission.features.build`).

Reference: `src/readmission/features/icd9.py`
```python
def icd9_group(code: str | None) -> str:
    if code is None or code in ("Missing", "?", ""):
        return "Missing"
    if code[0] in ("V", "E"):
        return "Other"
    if code.startswith("250"):
        return "Diabetes"
    x = float(code)
    if 390 <= x <= 459 or int(x) == 785: return "Circulatory"
    if 460 <= x <= 519 or int(x) == 786: return "Respiratory"
    if 520 <= x <= 579 or int(x) == 787: return "Digestive"
    if 800 <= x <= 999:                  return "Injury"
    if 710 <= x <= 739:                  return "Musculoskeletal"
    if 580 <= x <= 629 or int(x) == 788: return "Genitourinary"
    if 140 <= x <= 239:                  return "Neoplasms"
    return "Other"
```

Reference: `src/readmission/features/build.py` (core transformations)
```python
import numpy as np
import pandas as pd
from readmission.features.icd9 import icd9_group

MED_COLS = ["metformin", "repaglinide", "nateglinide", "chlorpropamide", "glimepiride",
            "acetohexamide", "glipizide", "glyburide", "tolbutamide", "pioglitazone",
            "rosiglitazone", "acarbose", "miglitol", "troglitazone", "tolazamide", "insulin",
            "glyburide_metformin", "glipizide_metformin", "glimepiride_pioglitazone",
            "metformin_rosiglitazone", "metformin_pioglitazone"]        # 21 (examide, citoglipton dropped)

def build_features(df: pd.DataFrame, specialty_top10: list[str] | None = None) -> pd.DataFrame:
    """specialty_top10=None -> compute from df (training); pass the saved list at prediction time."""
    out = df.copy()
    for c in MED_COLS:                      # single records may omit meds -> default "No"
        if c not in out:
            out[c] = "No"
    # Age: "[70-80)" -> 75
    lo = out["age_bucket"].str.extract(r"\[(\d+)-")[0].astype(int)
    out["age_mid"] = lo + 5
    out["age_group"] = pd.cut(out["age_mid"], [0, 40, 60, 80, 200],
                              right=False, labels=["<40", "40-59", "60-79", "80+"]).astype(str)
    # Utilisation
    out["service_utilization"] = out[["number_outpatient", "number_emergency", "number_inpatient"]].sum(axis=1)
    out["any_prior_inpatient"] = (out["number_inpatient"] > 0).astype(int)
    # Diagnoses
    for c in ("diag_1", "diag_2", "diag_3"):
        out[f"{c}_group"] = out[c].map(icd9_group)
    # Medications
    meds = out[MED_COLS]
    out["num_meds_active"] = (meds != "No").sum(axis=1)
    out["num_med_changes"] = meds.isin(["Up", "Down"]).sum(axis=1)
    # Labs
    out["a1c_measured"] = (out["a1c_result"] != "NotMeasured").astype(int)
    out["glu_measured"] = (out["max_glu_serum"] != "NotMeasured").astype(int)
    # Grouped codes (verify ids against staging.dim_* descriptions before finalising)
    out["admission_type_grp"] = out["admission_type_id"].map(
        {1: "Emergency", 7: "Emergency", 2: "Urgent", 3: "Elective"}).fillna("Other-Unknown")
    out["admission_source_grp"] = out["admission_source_id"].map(
        {7: "Emergency room", 1: "Referral", 2: "Referral", 3: "Referral",
         4: "Transfer", 5: "Transfer", 6: "Transfer"}).fillna("Other-Unknown")
    out["discharge_grp"] = out["discharge_disposition_id"].map(
        {1: "Home", 6: "Home-health", 8: "Home-health",
         3: "Facility", 4: "Facility", 5: "Facility", 22: "Facility", 24: "Facility",
         2: "Transfer-hospital", 23: "Transfer-hospital", 28: "Transfer-hospital"}
    ).fillna("Other-Unknown")
    # Specialty: top 10 + Other + Missing
    top10 = specialty_top10 if specialty_top10 is not None else list(
        out.loc[out["medical_specialty"] != "Missing", "medical_specialty"].value_counts().nlargest(10).index)
    out["medical_specialty_grp"] = np.where(
        out["medical_specialty"].isin(top10) | (out["medical_specialty"] == "Missing"),
        out["medical_specialty"], "Other")
    return out
```

> 💡 **Leakage note on `top10`:** the specialty list is computed on the full data. That's acceptable because it only uses frequency, not the target. Save the list to `models/<version>/metadata.json` so the API can reuse **exactly** the same list.

✔ **Expect:** `features.model_input` with ≈ 99k rows and all columns from AGENTS.md §6.1.

🚩 **Checkpoint:** `tests/test_icd9.py` passes. No NaNs in the engineered columns.

---

## 7. Split by patient (prevent leakage) `[P4-02]`

**Why:** about 30% of patients have several encounters. If the same patient appears in both train and test, the model "recognises" them and the scores look better than they really are.

Reference: `src/readmission/features/split.py`
```python
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold
from readmission.config import RANDOM_STATE

def assign_split(df, target="readmitted_30d", group="patient_nbr"):
    """20 patient-grouped, stratified folds -> 3 test (15%), 3 val (15%), 14 train (70%)."""
    sgkf = StratifiedGroupKFold(n_splits=20, shuffle=True, random_state=RANDOM_STATE)
    fold = np.empty(len(df), dtype=int)
    for i, (_, idx) in enumerate(sgkf.split(df, df[target], groups=df[group])):
        fold[idx] = i
    df = df.copy()
    df["split"] = np.select([fold < 3, fold < 6], ["test", "val"], default="train")
    return df
```

🚩 **Checkpoint** (`tests/test_split.py`):
```python
s = {k: set(g["patient_nbr"]) for k, g in df.groupby("split")}
assert not (s["train"] & s["val"]) and not (s["train"] & s["test"]) and not (s["val"] & s["test"])
print(df.groupby("split")["readmitted_30d"].agg(["size", "mean"]))   # ~70/15/15, mean ≈ 0.11 each
```

---

## 8. Build the preprocessing + model pipeline `[P4-03]`

Reference: `src/readmission/models/pipeline.py`
```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from readmission.config import RANDOM_STATE

NUMERIC = ["time_in_hospital", "num_lab_procedures", "num_procedures", "num_medications",
           "number_outpatient", "number_emergency", "number_inpatient", "number_diagnoses",
           "age_mid", "service_utilization", "any_prior_inpatient", "num_meds_active",
           "num_med_changes", "a1c_measured", "glu_measured"]
CATEGORICAL = ["race", "gender", "admission_type_grp", "discharge_grp", "admission_source_grp",
               "medical_specialty_grp", "diag_1_group", "diag_2_group", "diag_3_group",
               "max_glu_serum", "a1c_result", "change", "diabetes_med", *MED_COLS]
FEATURES = NUMERIC + CATEGORICAL
TARGET = "readmitted_30d"

def build_preprocessor(scale: bool = True) -> ColumnTransformer:
    num_steps = [("impute", SimpleImputer(strategy="median"))]
    if scale:
        num_steps.append(("scale", StandardScaler()))
    cat = Pipeline([("impute", SimpleImputer(strategy="constant", fill_value="Missing")),
                    ("onehot", OneHotEncoder(handle_unknown="infrequent_if_exist",
                                             min_frequency=50, sparse_output=False))])
    return ColumnTransformer([("num", Pipeline(num_steps), NUMERIC), ("cat", cat, CATEGORICAL)])

def build_model(key: str) -> Pipeline:
    est = {
        "dummy":  DummyClassifier(strategy="stratified", random_state=RANDOM_STATE),
        "logreg": LogisticRegression(class_weight="balanced", max_iter=2000),
        "dtree":  DecisionTreeClassifier(class_weight="balanced", max_depth=6, random_state=RANDOM_STATE),
        "rf":     RandomForestClassifier(n_estimators=300, class_weight="balanced_subsample",
                                         min_samples_leaf=20, n_jobs=-1, random_state=RANDOM_STATE),
        "hgb":    HistGradientBoostingClassifier(class_weight="balanced", random_state=RANDOM_STATE),
    }[key]
    return Pipeline([("prep", build_preprocessor(scale=(key == "logreg"))), ("clf", est)])
```

> Why a `Pipeline`? The imputers, encoders and scalers are then **fitted only on training folds** during CV. This is a core leakage rule (AGENTS.md §2.3).

---

## 9. Train baselines with cross-validation `[P4-04, P4-05]`

```python
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold, cross_validate

df = pd.read_parquet("data/processed/model_input.parquet")
train = df[df.split == "train"]
X, y, g = train[FEATURES], train[TARGET], train["patient_nbr"]
cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)

rows = []
for key in ["dummy", "logreg", "dtree", "rf", "hgb"]:
    res = cross_validate(build_model(key), X, y, groups=g, cv=cv, n_jobs=-1,
                         scoring=["roc_auc", "average_precision", "recall", "precision", "f1"])
    rows.append({"model": key, **{m: res[f"test_{m}"].mean() for m in
                 ["roc_auc", "average_precision", "recall", "precision", "f1"]}})
pd.DataFrame(rows).to_csv("reports/metrics/model_comparison.csv", index=False)
```

✔ **Expect (rough ranges):**
| model | ROC-AUC | PR-AUC |
|---|---|---|
| dummy | ≈ 0.50 | ≈ 0.11 |
| dtree | 0.60–0.64 | 0.16–0.19 |
| logreg | 0.63–0.67 | 0.19–0.22 |
| rf | 0.64–0.68 | 0.20–0.23 |
| hgb | 0.65–0.69 | 0.21–0.24 |

> Recall/precision at the default 0.5 cut-off are not meaningful here (the classes are imbalanced). Compare models with **ROC-AUC and PR-AUC**. The threshold is chosen in Step 12.

🚩 **Checkpoint:** every real model beats `dummy`. Nothing is above ≈ 0.75 (otherwise, see §19 leakage). Leakage checklist `[P4-06]` done.

---

## 10. Tune the best models `[P5-01, P5-02]`

```python
from scipy.stats import loguniform, randint, uniform
from sklearn.model_selection import RandomizedSearchCV

spaces = {
    "logreg": {"clf__C": loguniform(1e-3, 10)},
    "rf":  {"clf__max_depth": [None, 8, 12, 16], "clf__min_samples_leaf": randint(5, 60),
            "clf__max_features": ["sqrt", 0.3, 0.5]},
    "hgb": {"clf__learning_rate": loguniform(0.02, 0.2), "clf__max_leaf_nodes": randint(15, 63),
            "clf__min_samples_leaf": randint(20, 200), "clf__l2_regularization": loguniform(1e-3, 10),
            "clf__max_iter": randint(150, 600)},
}
best = {}
for key, space in spaces.items():
    search = RandomizedSearchCV(build_model(key), space, n_iter=40, scoring="roc_auc",
                                cv=cv, n_jobs=-1, random_state=42, refit=True, verbose=1)
    search.fit(X, y, groups=g)                     # groups → patient-grouped folds
    best[key] = search
    print(key, round(search.best_score_, 4), search.best_params_)
```

- Save `pd.DataFrame(search.cv_results_)` for each model → `reports/metrics/cv_results.csv` (add a `model` column).
- **Pick the winner** by mean CV ROC-AUC (tie-breaker: PR-AUC). Usually that's `hgb`. If `logreg` is within ≈ 0.01, consider it, since it is easier to explain.
- *(Optional `[P5-02]`)* Compare `class_weight="balanced"` vs `None` vs SMOTE (`imblearn.pipeline.Pipeline([... ("smote", SMOTE()), ("clf", ...)])`). Report PR-AUC and recall.

⏱ `hgb` with 40 iterations × 5 folds takes ≈ 5–15 minutes on a laptop.

---

## 11. Calibrate probabilities `[P5-03]`

Class weighting distorts probabilities: a "0.6" no longer means a 60% chance. Calibration fixes that, so the risk number stays honest.

```python
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import brier_score_loss

winner = best["hgb"].best_estimator_
splits = list(cv.split(X, y, groups=g))                         # group-aware folds
calibrated = CalibratedClassifierCV(winner, method="isotonic", cv=splits).fit(X, y)

val = df[df.split == "val"]
Xv, yv = val[FEATURES], val[TARGET]
p_val = calibrated.predict_proba(Xv)[:, 1]
print("Brier:", brier_score_loss(yv, p_val))
frac_pos, mean_pred = calibration_curve(yv, p_val, n_bins=10, strategy="quantile")
# plot mean_pred vs frac_pos with the diagonal → reports/figures/07_calibration.png
```

Compare `isotonic` and `sigmoid`, and keep the one with the lower Brier score on val.

✔ **Expect:** after calibration, the mean predicted probability ≈ base rate (≈ 0.11), and the curve hugs the diagonal.

---

## 12. Choose the decision threshold & risk tiers `[P5-04]`

All on the **validation** set, never the test set.

```python
import json, numpy as np
from sklearn.metrics import (precision_recall_curve, roc_auc_score, average_precision_score,
                             recall_score, precision_score, f1_score, brier_score_loss)

prec, rec, thr = precision_recall_curve(yv, p_val)
f2 = (5 * prec * rec) / (4 * prec + rec + 1e-12)
ok = rec[:-1] >= 0.60                                   # recall floor for a screening tool
idx = np.argmax(np.where(ok, f2[:-1], -1))
decision_threshold = float(thr[idx])

tier_cutoffs = {"medium": float(np.quantile(p_val, 0.70)),   # top 30% = Medium or High
                "high":   float(np.quantile(p_val, 0.90))}   # top 10% = High

def tier(p):
    return "High" if p >= tier_cutoffs["high"] else "Medium" if p >= tier_cutoffs["medium"] else "Low"

val_tiers = pd.Series([tier(p) for p in p_val], index=val.index)
print(pd.DataFrame({"tier": val_tiers, "y": yv}).groupby("tier")["y"].agg(["size", "mean"]))

yhat_val = (p_val >= decision_threshold).astype(int)
metrics_val = {"roc_auc": roc_auc_score(yv, p_val), "pr_auc": average_precision_score(yv, p_val),
               "recall": recall_score(yv, yhat_val), "precision": precision_score(yv, yhat_val),
               "f1": f1_score(yv, yhat_val), "brier": brier_score_loss(yv, p_val)}
```

✔ **Expect:** observed readmission rate climbs from Low → Medium → High, e.g. Low ≈ 8%, Medium ≈ 13%, High ≈ 22–28%. **This lift is the most useful operational result**: "patients we flag High are readmitted ~2.5× as often as average."

**Why two concepts?**
- **Decision threshold** → a yes/no "flag for follow-up". Tuned to catch most readmissions (recall ≥ 60%).
- **Risk tiers** → match the hospital's *capacity*. If staff can call only 10% of discharged patients, call the High tier.

Save `thresholds.json`:
```json
{"decision_threshold": 0.118, "tier_cutoffs": {"medium": 0.135, "high": 0.205},
 "selected_on": "val", "rule": "max F2 s.t. recall>=0.60; tiers at p70/p90"}
```
*(These numbers are illustrative. Use your own.)*

---

## 13. Final evaluation on the test set (once!) `[P5-07]`

> 🔒 Run this **one time**, after every decision is frozen. If you change the model afterwards, the
> test result is no longer an unbiased estimate. Say so in the report if that happens.

```python
from sklearn.metrics import (roc_auc_score, average_precision_score, precision_score, recall_score,
                             f1_score, fbeta_score, brier_score_loss, confusion_matrix,
                             RocCurveDisplay, PrecisionRecallDisplay)

test = df[df.split == "test"]
Xt, yt = test[FEATURES], test[TARGET]
p_test = calibrated.predict_proba(Xt)[:, 1]
yhat = (p_test >= decision_threshold).astype(int)

metrics_test = {
    "roc_auc": roc_auc_score(yt, p_test), "pr_auc": average_precision_score(yt, p_test),
    "precision": precision_score(yt, yhat), "recall": recall_score(yt, yhat),
    "f1": f1_score(yt, yhat), "f2": fbeta_score(yt, yhat, beta=2),
    "brier": brier_score_loss(yt, p_test), "base_rate": float(yt.mean()),
    "confusion_matrix": confusion_matrix(yt, yhat).tolist(),
}
RocCurveDisplay.from_predictions(yt, p_test)          # save → reports/figures/07_roc_test.png
PrecisionRecallDisplay.from_predictions(yt, p_test)   # save → reports/figures/07_pr_test.png
```

✔ **Expect:** test metrics within ≈ ±0.02 of validation. A big drop means overfitting to val, and a big jump is suspicious.

---

## 14. Explain the model `[P5-05]`

**Global importance (works for any model):**
```python
from sklearn.inspection import permutation_importance
r = permutation_importance(calibrated, Xv, yv, scoring="roc_auc", n_repeats=10,
                           random_state=42, n_jobs=-1)
imp = (pd.DataFrame({"feature": FEATURES, "importance": r.importances_mean, "std": r.importances_std})
         .sort_values("importance", ascending=False))
# saved in Step 16 as models/<version>/feature_importance.csv (method="permutation")
```
✔ **Typically on top:** `number_inpatient`, `discharge_grp`, `number_emergency`, `diag_1_group`, `time_in_hospital`, `num_medications`, `age_mid`, `number_diagnoses`.

**Odds ratios (logistic regression, easiest to explain in a viva):** `np.exp(coef_)` per one-hot feature, e.g. "each prior inpatient visit multiplies the odds of 30-day readmission by ≈ 1.3."

**Per-patient top factors (used by `/predict`):**
- If the final model is `hgb`/`rf`: SHAP `TreeExplainer` on the uncalibrated `winner` → top 5 |SHAP| values for that row.
- Fallback without SHAP: for `logreg`, contribution = coefficient × standardised value. Return the top 5.

---

## 15. Check fairness `[P5-06]`

```python
rows = []
for col in ["race", "gender", "age_group"]:
    for grp, d in test.assign(p=p_test, yhat=yhat).groupby(col):
        if d[TARGET].nunique() < 2 or len(d) < 200:
            continue
        rows.append({"attribute": col, "group": grp, "n": len(d), "base_rate": d[TARGET].mean(),
                     "roc_auc": roc_auc_score(d[TARGET], d.p),
                     "recall": recall_score(d[TARGET], d.yhat),
                     "precision": precision_score(d[TARGET], d.yhat, zero_division=0)})
pd.DataFrame(rows).to_csv("reports/metrics/fairness.csv", index=False)
```
Report any group whose recall differs from the overall recall by more than about 10 points, and discuss why (sample size, different base rates). We **do not** remove `race` silently. Discuss whether to keep it and justify the choice in the model card.

---

## 16. Save the model artifacts `[P5-08]`

```python
import joblib, json, datetime, sklearn
from pathlib import Path

version = f"v{datetime.date.today():%Y%m%d}_hgb"
out = Path("models") / version
out.mkdir(parents=True, exist_ok=True)

joblib.dump(calibrated, out / "model.joblib")
json.dump({"model_version": version, "algorithm": "HistGradientBoostingClassifier+isotonic",
           "params": best["hgb"].best_params_, "features": {"numeric": NUMERIC, "categorical": CATEGORICAL},
           "specialty_top10": list(top10), "train_rows": int(len(train)),
           "base_rate_train": float(y.mean()), "sklearn_version": sklearn.__version__,
           "random_state": 42, "trained_at": datetime.datetime.now().isoformat()},
          open(out / "metadata.json", "w"), indent=2, default=str)
json.dump({"cv": {"roc_auc": best["hgb"].best_score_}, "val": metrics_val, "test": metrics_test},
          open(out / "metrics.json", "w"), indent=2)
json.dump({"decision_threshold": decision_threshold, "tier_cutoffs": tier_cutoffs},
          open(out / "thresholds.json", "w"), indent=2)
imp.assign(method="permutation").to_csv(out / "feature_importance.csv", index=False)
Path("models/CURRENT").write_text(version)
# + INSERT INTO ml.model_registry (...) and ml.feature_importance (...)
```

▶ **Or simply:** `make train && make evaluate`. `train.py` / `evaluate.py` implement Steps 9–16.

🚩 **Checkpoint:** `models/CURRENT` exists. Reloading `model.joblib` in a fresh Python session gives identical probabilities for 5 sample rows.

---

## 17. Use the model: get readmission risk for patients `[P6-01, P6-05, P6-07]`

### 17a. One new patient (Python)
```python
import joblib, json, pandas as pd
from readmission.features.build import build_features
from readmission.models.pipeline import FEATURES

v = open("models/CURRENT").read().strip()
model = joblib.load(f"models/{v}/model.joblib")
thr = json.load(open(f"models/{v}/thresholds.json"))
meta = json.load(open(f"models/{v}/metadata.json"))

patient = {  # raw-style fields, as staff would enter them at discharge
    "race": "Caucasian", "gender": "Female", "age_bucket": "[70-80)",
    "admission_type_id": 1, "discharge_disposition_id": 3, "admission_source_id": 7,
    "time_in_hospital": 6, "medical_specialty": "InternalMedicine",
    "num_lab_procedures": 55, "num_procedures": 1, "num_medications": 18,
    "number_outpatient": 0, "number_emergency": 1, "number_inpatient": 2, "number_diagnoses": 9,
    "diag_1": "428", "diag_2": "250.02", "diag_3": "401",
    "max_glu_serum": "NotMeasured", "a1c_result": ">8",
    "insulin": "Up", "metformin": "Steady",  # all other meds default to "No"
    "change": "Ch", "diabetes_med": "Yes",
}
row = build_features(pd.DataFrame([patient]), specialty_top10=meta["specialty_top10"])  # meds default to "No"
p = float(model.predict_proba(row[FEATURES])[:, 1][0])
tier = "High" if p >= thr["tier_cutoffs"]["high"] else "Medium" if p >= thr["tier_cutoffs"]["medium"] else "Low"
print(f"30-day readmission risk: {p:.1%} → {tier} tier; flagged_for_follow_up={p >= thr['decision_threshold']}")
```
> For single records, always pass the **saved** `specialty_top10` from `metadata.json`. A list recomputed from one row would be wrong.

### 17b. Through the API (after Phase 6)
```bash
curl -X POST http://localhost:8000/api/v1/predict -H "Content-Type: application/json" -d @patient.json
```
```json
{ "model_version": "v20261106_hgb", "probability": 0.27, "risk_tier": "High",
  "flagged_for_follow_up": true, "decision_threshold": 0.118,
  "top_factors": [{"feature": "number_inpatient", "value": 2, "direction": "increases_risk"}, "..."],
  "disclaimer": "This is a statistical risk estimate ..." }
```

### 17c. All patients at once → database → Power BI
```bash
make score        # writes every encounter's probability + tier to ml.predictions
make views        # refreshes analytics.vw_*
make export-bi    # writes powerbi/data/*.csv for the dashboard
```

### 17d. Questions you can now answer with SQL
```sql
-- Who are the high-risk patients (test split, to show honest results)?
SELECT encounter_id, probability, risk_tier, actual_label
FROM ml.predictions WHERE split = 'test' AND risk_tier = 'High' ORDER BY probability DESC LIMIT 50;

-- Does the model rank risk well? (observed rate per tier)
SELECT risk_tier, count(*) AS n, round(avg(actual_label)::numeric, 3) AS observed_rate
FROM ml.predictions WHERE split = 'test' GROUP BY risk_tier ORDER BY observed_rate DESC;

-- How many follow-up calls are needed per 1,000 discharges if we contact High + Medium?
SELECT round(1000.0 * avg((risk_tier IN ('High','Medium'))::int)) FROM ml.predictions WHERE split='test';
```

---

## 18. How to read and report the results

| Metric | Plain-language meaning | How to phrase it |
|---|---|---|
| ROC-AUC 0.68 | Pick one readmitted and one non-readmitted patient at random. 68% of the time the model ranks the readmitted one higher | "Moderate discrimination, comparable to the LACE index (0.68)" |
| PR-AUC 0.23 | Average precision across thresholds; random = 0.11 | "≈ 2× better than random at finding readmissions" |
| Recall 0.62 @ thr | We flag 62% of the patients who were actually readmitted | "Catches about 6 in 10 readmissions" |
| Precision 0.18 @ thr | 18% of flagged patients were readmitted (vs 11% base) | "Flagged group is enriched 1.6×" |
| High-tier rate 25% | Patients in the top 10% were readmitted 25% of the time | "Top-decile patients readmitted at 2.3× the average rate" |
| Brier 0.09 | Mean squared error of the probabilities (lower is better) | "Probabilities are well calibrated" |

**Always state the limitations:** diabetic encounters only, 1999–2008 US data, no lab values beyond HbA1c/glucose, no social determinants, observational data (the factors are **associations, not causes**), and the dataset can't tell planned from unplanned readmissions.

---

## 19. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| ROC-AUC > 0.80 | Leakage: patient overlap, target in features, `encounter_id`/`patient_nbr` used as a feature | Re-run the AGENTS.md §6.4 checklist |
| `A1Cresult` almost all NaN | pandas read `"None"` as NaN | `keep_default_na=False, na_values=["?"]` (MEMORY.md G-001) |
| `could not convert string to float` in `icd9_group` | V/E codes, or a code like `"250.8"` vs `"V45"` | Check the V/E branch runs first |
| `ValueError: Found unknown categories` | Encoder saw a new value at predict time | `handle_unknown="infrequent_if_exist"` |
| HGB error about sparse input | One-hot output is sparse | `sparse_output=False` (already set) |
| Recall ≈ 0 at threshold 0.5 | Imbalance; 0.5 is meaningless here | Use the tuned threshold from Step 12 |
| `COPY` fails with "extra data after last expected column" | Column count mismatch in `raw.diabetic_data` | Compare against the CSV header (50 columns) |
| `psycopg.OperationalError` | DB not running / wrong URL | `docker compose ps`; check `.env` |
| Calibrated probs all ≈ 0.11 | Model has no signal / features dropped | Check that the `X` columns are not empty and that the feature list matches |
| Different results each run | Missing `random_state` | Set 42 on CV, models, search, SMOTE |

---

## 20. Retraining checklist

1. New data → `data/raw/` → `make ingest stage features`.
2. Re-split (new patients go to their own groups). Keep the old test set if you want comparable numbers.
3. `make train evaluate` → creates a new `models/vYYYYMMDD_<key>/`.
4. Compare it with the previous version in MEMORY.md §4 (experiment log).
5. Update `models/CURRENT` only if the new model is better on val **and** has calibration/fairness at least as good.
6. `make score views export-bi` → refresh the Power BI data.
7. Update `reports/model_card.md` and the PROGRESS.md key results.
