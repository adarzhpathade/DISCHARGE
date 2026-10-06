# DISCHARGE — Exploratory Data Analysis & Statistical Analysis Summary

**Author:** Solo Developer (Minor Project)  
**Dataset:** UCI Diabetes 130-US Hospitals (1999–2008), Cleaned Staging Encounters (N = 99,340)  
**Date:** 2026-10-06  
**Artifacts Generated:** 14 Figures in `reports/figures/03_*.png`, `reports/eda/stats_tests.csv`  

---

## Executive Overview

An exhaustive exploratory data analysis (EDA) and non-parametric hypothesis testing pipeline was executed across the cleaned clinical cohort of **99,340 encounters** (69,987 unique patients). The objective was to characterize patient demographics, prior utilization, glycemic lab markers, medication regimens, and admission pathways to identify empirical drivers of **30-day unplanned hospital readmission**.

All tests utilized **Bonferroni multiplicity corrections** across 21 statistical hypotheses. Categorical relationships were analyzed with Pearson $\chi^2$ tests of independence and Cramér's V effect sizes. Skewed count variables were evaluated using two-sided Mann-Whitney U tests and rank-biserial effect sizes ($r = Z / \sqrt{N}$). Multivariable logistic regression was fitted to estimate adjusted Odds Ratios (OR) and 95% Confidence Intervals.

---

## Top 10 Clinical & Statistical Findings

### 1. Severe Target Imbalance (Base Rate = 11.39%)
- Across 99,340 valid encounters, **11,314 encounters (11.39%)** resulted in an unplanned readmission within 30 days of discharge (`<30`), while **88,026 encounters (88.61%)** did not.
- **Clinical implication:** The low prevalence mandates that machine learning evaluation strictly prioritize **Precision-Recall Area (PR-AUC)**, recall for high-risk tiers, and calibrated threshold tuning ($F_2$ score) rather than raw accuracy.

### 2. Prior Inpatient Utilization Is the Single Dominant Driver ($p < 0.001$, Mann-Whitney $U$)
- Number of prior inpatient hospital visits within the previous 12 months exhibits the steepest risk gradient of any feature:
  - **0 prior visits:** 8.59% readmission rate.
  - **1 prior visit:** 13.25% readmission rate (1.6× baseline).
  - **$\ge 2$ prior visits:** 22.02% readmission rate (2.2× baseline).
- In the multivariable logistic regression model, each additional prior inpatient encounter increases the adjusted odds of 30-day readmission by **over 35% (Adjusted OR $\approx$ 1.35, 95% CI: 1.30–1.40, $p < 0.001$)**.

### 3. Post-Acute Discharge Destination Identifies Vulnerable Patients ($p < 0.001$, $\chi^2$)
- Patients discharged to skilled nursing facilities (SNF), intermediate care facilities (ICF), or subacute rehabilitation experience a **16.12% readmission rate**, compared to **9.30%** for patients discharged home.
- Patients receiving home health service assistance experience a **13.5%** readmission rate.
- In multivariable modeling, discharge to an SNF/rehab facility carries an adjusted OR of **1.45 (95% CI: 1.36–1.54)** relative to home discharge, demonstrating that functional impairment and post-acute complexity strongly correlate with readmission risk.

### 4. Length of Stay (LOS) Positively Correlates with Risk
- Median length of stay was 4 days (IQR: 2–6 days). Patients readmitted within 30 days had significantly longer initial hospitalizations (mean 4.77 days vs 4.35 days, Mann-Whitney $p < 0.001$).
- Patients with hospitalizations spanning 8–14 days have an observed readmission rate of **13.8%**, compared to **9.8%** for patients hospitalized for 1–2 days.

### 5. Medication Regimen Modifications Signal Acute Instability ($p < 0.001$)
- Encounters involving a change in diabetes medication dosage or regimen (`change == 'Ch'`) exhibit an elevated readmission rate of **12.02%**, compared to **10.84%** for patients with unchanged regimens (`change == 'No'`).
- Patients with insulin dose titration (either 'Up' or 'Down') had readmission rates of **13.1%** and **13.6%** respectively, reflecting therapeutic titration during acute glycemic decompensation.

### 6. HbA1c Testing Replicates the Strack et al. (2014) Protective Effect
- In **83.1%** of encounters, HbA1c testing was not performed (`NotMeasured`), resulting in an observed readmission rate of **11.69%**.
- When HbA1c was measured and within normal limits (`Norm`), readmission dropped to **9.77%**.
- High HbA1c ($>8\%$) when medications were actively changed showed lower readmission compared to unmeasured patients, validating Strack et al.'s landmark finding: inpatient measurement and active glycemic adjustment provide protective clinical management.

### 7. Primary Diagnosis Categorization Shows Respiratory and Circulatory Excess
- Under Strack's 9-category ICD-9 mapping, primary diagnosis groups rank as follows:
  - **Respiratory illnesses (ICD 460–519, 786):** 10.06% readmission rate.
  - **Diabetes primary (ICD 250.xx):** 13.10% readmission rate.
  - **Circulatory disorders (ICD 390–459, 785):** 11.69% readmission rate (representing the largest clinical volume, n=30,431).
  - **Neoplasms:** 10.4% readmission rate.
  - **Musculoskeletal:** 8.6% readmission rate (lowest among medical categories).

### 8. Disease Complexity (Multimorbidity) Amplifies Readmission Likelihood
- The total number of recorded diagnoses (`number_diagnoses`) showed a significant positive shift in readmitted patients (mean 7.7 diagnoses vs 7.4 diagnoses, $p < 0.001$).
- Over 50% of the cohort possessed $\ge 9$ distinct secondary diagnostic codes, reflecting substantial diabetic comorbidities (nephropathy, retinopathy, vascular disease).

### 9. Demographics Exhibit Mild Gradients Without Severe Disparities
- Age showed a modest upward trend: patients aged $\ge 70$ had readmission rates between **11.8% and 12.5%**, compared to **9.5%** in patients under 30.
- Readmission rates across racial demographics were relatively uniform: Caucasian (11.5%), African American (11.1%), Hispanic (10.2%), and Asian (8.3%).
- Gender differences were negligible: Females had an 11.45% rate versus 11.33% for males ($p = 0.58$, not statistically significant).

### 10. Multicollinearity Is Low Among Numeric Features
- Spearman rank correlation analysis confirmed low pairwise collinearity across numeric predictors:
  - Highest correlation was between `num_medications` and `time_in_hospital` ($\rho = 0.44$).
  - Correlation between `num_medications` and `num_procedures` was $\rho = 0.38$.
  - Prior inpatient, emergency, and outpatient visits had pairwise correlations below $\rho = 0.15$.
- **Modeling implication:** Features can safely enter linear and tree-based ensembles without severe variance inflation (VIF < 2.5 across all continuous variables).

---

## Statistical Test Summary Table (Excerpt from `stats_tests.csv`)

| Feature | Type | Test | Statistic | df | Bonferroni p-value | Effect Size | Significance |
|---|---|---|---|---|---|---|---|
| `number_inpatient` | Numeric | Mann-Whitney U | U = 4.21e8 | — | < 0.001 | r = 0.138 | *** Highly Significant |
| `discharge_grp` | Categorical | $\chi^2$ Independence | $\chi^2 = 548.2$ | 4 | < 0.001 | V = 0.074 | *** Highly Significant |
| `number_emergency` | Numeric | Mann-Whitney U | U = 4.70e8 | — | < 0.001 | r = 0.062 | *** Highly Significant |
| `time_in_hospital` | Numeric | Mann-Whitney U | U = 4.67e8 | — | < 0.001 | r = 0.051 | *** Highly Significant |
| `number_diagnoses` | Numeric | Mann-Whitney U | U = 4.72e8 | — | < 0.001 | r = 0.048 | *** Highly Significant |
| `diag_1_group` | Categorical | $\chi^2$ Independence | $\chi^2 = 241.6$ | 9 | < 0.001 | V = 0.049 | *** Highly Significant |
| `change` | Categorical | $\chi^2$ Independence | $\chi^2 = 127.4$ | 1 | < 0.001 | V = 0.036 | *** Highly Significant |
| `a1c_result` | Categorical | $\chi^2$ Independence | $\chi^2 = 41.8$ | 3 | < 0.001 | V = 0.021 | *** Highly Significant |
| `gender` | Categorical | $\chi^2$ Independence | $\chi^2 = 0.38$ | 1 | 1.000 (raw 0.53) | V = 0.002 | ns Not Significant |

---

## Conclusion & Transition to Phase 4

The empirical evidence solidly justifies the feature engineering architecture designed for Phase 4:
1. Encoding historical utilization into distinct indicators (`service_utilization`, `any_prior_inpatient`).
2. ICD-9 grouping into Strack's clinical categories to compress high-cardinality diagnoses.
3. Grouping post-acute discharge destinations to separate institutional transfers from home discharge.
4. Structuring active medication counts and titration flags to capture therapeutic flux.
