# Synopsis — Hospital Readmission Risk Prediction System

> Draft for submission in Week 1 (P0-07). Adapt it to your college's synopsis template (P0-09). Fill the bracketed fields.

**Student:** [Name] · **Roll No.:** [ ] · **Programme/Semester:** [ ] · **Guide:** [ ] · **Department/Institute:** [ ] · **Date:** [ ]

---

## 1. Title
**Hospital Readmission Risk Prediction System: A Machine-Learning-Based Decision-Support Tool for 30-Day Readmission Risk Assessment**

## 2. Introduction
Unplanned hospital readmissions shortly after discharge increase healthcare costs, occupy beds, add to staff workload, and put pressure on emergency and diagnostic services. Hospitals already keep large historical records of admissions, diagnoses, medications, laboratory tests and discharge details, in which the readmission outcome is known. This project uses such historical data to estimate, at the time of discharge, the probability that a patient will have an unplanned readmission within 30 days. Clinicians and administrators can then prioritise follow-up and plan resources.

## 3. Problem Statement
At discharge, it is hard to consistently identify which patients are at higher risk of readmission. The relevant information is large in volume, spread across systems, and affected by missing, inconsistent and invalid entries. A reliable, data-driven way is needed to turn this historical data into an individual risk estimate and into aggregate insights for resource planning, while being transparent that the output is a probability and not a certainty.

## 4. Objectives
1. Build a reproducible data pipeline (PostgreSQL + Python) that ingests, cleans and validates hospital encounter data.
2. Run exploratory and statistical analysis to identify factors associated with 30-day readmission.
3. Train and compare machine-learning classifiers (scikit-learn) that estimate the probability of 30-day readmission using only information available at or before discharge.
4. Evaluate the models with Precision, Recall, F1-score, ROC-AUC and PR-AUC, with emphasis on identifying high-risk patients, and check calibration and subgroup fairness.
5. Stratify patients into Low/Medium/High risk tiers to support follow-up prioritisation.
6. Deliver the results through a REST API, a web application, and an interactive Power BI dashboard.

## 5. Scope
**In scope:** 30-day all-cause readmission risk for adult diabetic inpatient encounters (public UCI dataset). Data cleaning, EDA, statistical tests, ML modelling, explainability, dashboard, and a web-based risk calculator.
**Out of scope:** real-time EHR integration, clinical deployment, causal claims, and treatment recommendations.

## 6. Dataset
*Diabetes 130-US Hospitals for Years 1999–2008* (UCI Machine Learning Repository; Strack et al., 2014): ≈101,766 encounters, 50 attributes (demographics, admission/discharge details, length of stay, lab and procedure counts, prior visits, ICD-9 diagnoses, HbA1c/glucose tests, 23 diabetic medications), and the readmission outcome (<30 days, >30 days, none).

## 7. Methodology
1. **Data ingestion:** load the raw CSVs into PostgreSQL unchanged.
2. **Cleaning (SQL + Pandas/NumPy):** standardise missing values, remove invalid records and patients discharged to hospice/expired, drop sparse attributes, cast types, map codes to descriptions, and produce a data-quality report.
3. **EDA & statistics:** distributions and readmission rates by factor. Chi-square tests with Cramér's V, Mann–Whitney U tests, and logistic-regression odds ratios.
4. **Feature engineering:** age midpoint, service utilisation, ICD-9 diagnosis groups, medication counts and changes, lab-test indicators, grouped admission/discharge categories.
5. **Modelling:** patient-grouped train/validation/test split (no patient in more than one set). Baselines (dummy, logistic regression, decision tree) and ensembles (random forest, histogram gradient boosting). Class weighting for imbalance. Hyperparameter tuning with grouped cross-validation. Probability calibration.
6. **Evaluation:** ROC-AUC, PR-AUC, Precision, Recall, F1/F2, Brier score, confusion matrix. Recall-oriented threshold selection. Risk-tier lift. Subgroup analysis by age, gender and race.
7. **Explainability:** permutation importance, odds ratios, and per-patient contributing factors.
8. **Deployment:** FastAPI service, Next.js web interface, Power BI dashboard.

## 8. Tools & Technologies
PostgreSQL 16 · Python 3.12 · Pandas · NumPy · SciPy · statsmodels · scikit-learn · Matplotlib/Seaborn · FastAPI · Next.js · Power BI · Git

## 9. Expected Outcomes
- A cleaned, documented dataset and a reproducible pipeline.
- A calibrated model with ROC-AUC in the range reported in the literature for this data (≈0.65–0.70), and risk tiers in which high-risk patients show substantially higher observed readmission rates than average.
- An interactive dashboard and a web tool that support follow-up prioritisation and resource planning.

## 10. Timeline (8 weeks)
| Week | Activity |
|---|---|
| 1 | Setup, data acquisition, ingestion into PostgreSQL, synopsis |
| 2 | Data cleaning and quality report |
| 3 | EDA and statistical analysis |
| 4 | Feature engineering, baseline models |
| 5 | Model tuning, evaluation, explainability |
| 6 | Batch scoring, analytics views, REST API |
| 7 | Power BI dashboard, web interface |
| 8 | Testing, report, presentation |

## 11. References (abridged; see `literature/annotated_bibliography.md`)
1. B. Strack et al., "Impact of HbA1c measurement on hospital readmission rates: Analysis of 70,000 clinical database patient records," *BioMed Res. Int.*, vol. 2014, Art. 781670, 2014.
2. D. Kansagara et al., "Risk prediction models for hospital readmission: A systematic review," *JAMA*, vol. 306, no. 15, pp. 1688–1698, 2011.
3. C. van Walraven et al., "Derivation and validation of an index to predict early death or unplanned readmission after discharge from hospital to the community," *CMAJ*, vol. 182, no. 6, pp. 551–557, 2010.
4. Y. Huang, A. Talwar, S. Chatterjee, R. R. Aparasu, "Application of machine learning in predicting hospital readmissions: a scoping review of the literature," *BMC Med. Res. Methodol.*, vol. 21, Art. 96, 2021.
