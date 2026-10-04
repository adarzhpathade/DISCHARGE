# Power BI Dashboard Specification

> Data source: `powerbi/data/*.csv` (exported by `make export-bi` from `analytics.vw_*`) or a direct
> PostgreSQL connection on Windows. If design references for the dashboard are supplied, replicate
> them exactly (AGENTS.md §11–12). This spec only defines **content**, not visual style.

## 1. Platform (decided in P0-08)
| Option | How |
|---|---|
| College lab Windows PC | Copy `powerbi/data/` over on a USB drive or cloud drive. Build the `.pbix` there |
| Windows VM on Mac | Parallels Desktop / UTM with Windows 11 ARM → install Power BI Desktop |
| Power BI Service (web) | app.powerbi.com → upload the CSVs (or an Excel workbook built from them) → create the report in the browser. Needs a work/school account |

## 2. Data model
- Tables: one per exported CSV (`vw_readmission_overview.csv`, …, `vw_high_risk_patients.csv`).
- For detailed slicing, also export `ml.predictions` joined with key features → `patients_scored.csv` (one row per encounter). Make it the **fact table**.
- Dimension tables: `dim_age_group`, `dim_diag_group`, `dim_risk_tier` (sort order Low < Medium < High).

## 3. DAX measures (create in a `_Measures` table)
```DAX
Encounters          = COUNTROWS ( patients_scored )
Readmissions 30d    = SUM ( patients_scored[actual_label] )
Readmission Rate    = DIVIDE ( [Readmissions 30d], [Encounters] )
Avg LOS             = AVERAGE ( patients_scored[time_in_hospital] )
High Risk Count     = CALCULATE ( [Encounters], patients_scored[risk_tier] = "High" )
High Risk Share     = DIVIDE ( [High Risk Count], [Encounters] )
Avg Predicted Risk  = AVERAGE ( patients_scored[probability] )
Flagged             = CALCULATE ( [Encounters], patients_scored[predicted_label] = 1 )
True Positives      = CALCULATE ( [Encounters], patients_scored[predicted_label] = 1, patients_scored[actual_label] = 1 )
Recall              = DIVIDE ( [True Positives], [Readmissions 30d] )
Precision           = DIVIDE ( [True Positives], [Flagged] )
Lift vs Base        = DIVIDE ( [Readmission Rate], CALCULATE ( [Readmission Rate], ALL ( patients_scored[risk_tier] ) ) )
```
> Model-performance visuals should filter `split = "test"` to show honest numbers.

## 4. Pages
| # | Page | Visuals | Answers |
|---|---|---|---|
| 1 | **Executive Overview** | KPI cards (Encounters, Patients, Readmission Rate, Avg LOS, High-Risk Share). Rate by age group. Rate by diagnosis group. Risk-tier donut | "How big is the problem and where?" |
| 2 | **Patient Demographics** | Rate by age group × gender (clustered bar). Rate by race. Encounter-count histogram by age | "Who gets readmitted?" |
| 3 | **Clinical Factors** | Rate by primary diagnosis group. A1C result × rate. Insulin status × rate. Med changes vs rate. Number of diagnoses vs rate | "Which clinical factors matter?" |
| 4 | **Admissions & Utilisation** | Rate by admission type/source. Rate by discharge destination. Rate vs prior inpatient/emergency visits (line). LOS distribution | "How do care pathways and prior use relate to readmission?" (resource planning) |
| 5 | **Model Performance** | Cards: ROC-AUC, PR-AUC, Recall, Precision (test). Confusion-matrix table. ROC & calibration images from `reports/figures/`. Observed rate by tier (bar) | "Can we trust the risk scores?" |
| 6 | **Risk Stratification & High-Risk List** | Tier distribution. Observed vs predicted rate per tier. Table of High-tier patients with drill-through. Slicers: age group, diag group, discharge group | "Whom should we follow up first?" |
| 7 | **Key Risk Drivers** | Feature-importance bar (top 15). Short explanatory text box per top driver | "Why does the model flag patients?" |

## 5. Interactivity
- Global slicers (synced): split, age_group, gender, diag_1_group.
- Drill-through from any bar → page 6 filtered list.
- Tooltips: encounters, rate, and lift vs base.
- Disclaimer text box on pages 5–7 (AGENTS.md §10.4).

## 6. Deliverables
- `powerbi/readmission_dashboard.pbix`
- `powerbi/theme.json` (from design refs, if supplied)
- Page screenshots/PDF → `reports/figures/powerbi_<n>_<page>.png` (for the report & PPT)
