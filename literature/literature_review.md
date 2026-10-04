# Literature Review (Draft — Report Chapter 2)

> ⚠ **Draft. Verify every citation before submission (P8-09).** Keys refer to `annotated_bibliography.md`.
> Paragraphs marked *[expand]* need more sources or your own numbers. Rewrite in your own words before
> submitting to avoid plagiarism flags.

## 2.1 Hospital readmission as a healthcare problem
Readmission soon after discharge is widely used as an indicator of care quality and a driver of cost. In a landmark analysis of US Medicare claims, roughly one in five patients was rehospitalised within 30 days of discharge [Jencks2009]. This led to policy responses that financially penalise hospitals with excess readmissions, such as the US Hospital Readmissions Reduction Program. Beyond cost, readmissions take up beds, staff time and diagnostic capacity, which is why early identification of high-risk patients is valuable for both patient care and resource planning. *[expand: add an Indian/local healthcare-capacity source if your guide expects one]*

## 2.2 Clinical risk scores
The earliest practical tools were simple additive scores computed at discharge. The **LACE index** [vanWalraven2010] combines length of stay, acuity of admission, comorbidity (Charlson index) and emergency-department visits in the previous six months. It achieved a C-statistic of about 0.68 for death or unplanned readmission within 30 days. The **HOSPITAL score** [Donze2013] uses seven routinely available discharge variables (haemoglobin, oncology discharge, sodium, procedures, admission type, prior admissions, length of stay) to sort patients into low, intermediate and high risk groups for potentially avoidable readmission. These scores are easy to use but compress complex patient information into a few variables. Their discrimination is moderate.

## 2.3 Systematic reviews of readmission prediction
Kansagara et al. [Kansagara2011] reviewed 26 unique readmission models and found that most had poor-to-moderate discrimination. 30-day readmission was the most common outcome, and few models included social or functional factors, which are thought to drive many readmissions. Later reviews of machine-learning approaches [Artetxe2018], [Huang2021] report a rapid growth in the use of tree ensembles, boosting, and neural networks. They also report recurring methodological issues: class imbalance, inconsistent evaluation metrics, limited external validation, and limited attention to calibration and interpretability.

## 2.4 Machine learning for readmission
Comparative studies show that ML models (random forests, gradient boosting, neural networks) often give modest but consistent improvements over logistic regression on administrative data [Futoma2015]. Larger gains appear when richer EHR data such as clinical notes and time-series vitals are available [Rajkomar2018]. For tabular, administrative-style data such as ours, gradient-boosted trees are a strong default. Logistic regression stays valuable for interpretability. *[expand with 2–3 recent UCI-dataset ML papers and their reported ROC-AUC]*

## 2.5 The Diabetes 130-US Hospitals dataset
Strack et al. [Strack2014] introduced the dataset used in this project: about 100,000 inpatient encounters of diabetic patients from 130 US hospitals (1999–2008), extracted from a large clinical database. Their analysis found that HbA1c was measured in only ≈18% of encounters, and that the relationship between HbA1c measurement and early readmission depended on the primary diagnosis. They also set preprocessing conventions we follow, including grouping ICD-9 codes into broad disease categories and excluding encounters that ended in death or hospice discharge. Since then, the dataset has become a common benchmark. Studies predicting `<30`-day readmission on it typically report ROC-AUC values in the mid-0.6 range, which is consistent with the clinical scores above. *[verify with sources found in P2-07]*

## 2.6 Methodological considerations
- **Class imbalance:** about 11% of encounters in our data are positive. Remedies include class weighting, threshold moving, and resampling such as SMOTE [Chawla2002], which must be applied only inside training folds.
- **Calibration:** risk scores are only useful for decision support if probabilities are reliable. Isotonic and Platt (sigmoid) scaling are standard post-hoc calibration methods [NiculescuMizil2005].
- **Explainability:** clinicians need to know why a patient is flagged. Model-agnostic tools such as permutation importance and SHAP [Lundberg2017] provide global and per-patient explanations.
- **Fairness:** algorithms trained on healthcare data can encode existing disparities [Obermeyer2019], so performance should be reported by demographic subgroup.
- **Reporting:** the TRIPOD statement [Collins2015] recommends transparent reporting of data, predictors, missing-data handling, model development and validation.

## 2.7 Research gap and contribution of this project
Existing clinical scores are simple but only moderately accurate. Many ML studies focus on maximising a single metric without addressing leakage (the same patient appearing in train and test), calibration, interpretability, or how results would be used operationally. This project contributes an **end-to-end, reproducible decision-support pipeline** that:
1. performs auditable SQL-based cleaning with documented data-quality rules,
2. prevents patient-level leakage through grouped splitting,
3. reports recall-oriented, calibrated risk estimates with honest test-set evaluation,
4. translates probabilities into capacity-aware **risk tiers**, with per-patient explanations and subgroup fairness checks, and
5. delivers the results to clinicians and administrators through an API, a web interface, and a Power BI dashboard.
