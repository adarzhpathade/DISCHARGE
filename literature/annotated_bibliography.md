# Annotated Bibliography

> ⚠ **VERIFY BEFORE SUBMISSION (P8-09).** Entries marked ✅ were checked online on 2026-10-04 against
> PubMed or the publisher page. Entries marked 🔎 were written from memory. Their details (volume, pages,
> DOI) must be checked before they appear in your report. A wrong citation costs more than a missing one.

## Template
```
### [Key] Short title
- **Citation:** Authors, "Title," Journal, vol., no., pp., year. doi:
- **Verified:** ✅/🔎  · **PDF:** papers/<file>.pdf
- **Summary:** 2–3 sentences
- **Key findings / numbers:**
- **Relevance to this project:**
```

---

## A. Dataset & directly related work

### [Strack2014] Impact of HbA1c measurement on hospital readmission rates
- **Citation:** B. Strack, J. P. DeShazo, C. Gennings, J. L. Olmo, S. Ventura, K. J. Cios, J. N. Clore, "Impact of HbA1c Measurement on Hospital Readmission Rates: Analysis of 70,000 Clinical Database Patient Records," *BioMed Research International*, vol. 2014, Article ID 781670, 2014. doi:10.1155/2014/781670 (PMC3996476)
- **Verified:** ✅ (title, journal, year, article ID, DOI)
- **Summary:** Introduces the Diabetes 130-US dataset (extracted from the Health Facts database) and studies whether measuring HbA1c during the hospital stay is associated with early readmission. The authors use multivariable logistic regression on ≈70,000 encounters.
- **Key findings:** HbA1c was measured in only ≈18.4% of encounters. The association between HbA1c measurement and readmission depends on the primary diagnosis.
- **Relevance:** Source of our dataset, the ICD-9 grouping, and the preprocessing ideas (first encounter, hospice removal). Our EDA (P3-08) partly replicates their HbA1c analysis.

## B. Clinical readmission risk scores & reviews

### [vanWalraven2010] LACE index
- **Citation:** C. van Walraven, I. A. Dhalla, C. Bell, E. Etchells, I. G. Stiell, K. Zarnke, P. C. Austin, A. J. Forster, "Derivation and validation of an index to predict early death or unplanned readmission after discharge from hospital to the community," *CMAJ*, vol. 182, no. 6, pp. 551–557, 2010. doi:10.1503/cmaj.091117
- **Verified:** ✅ (journal, year, vol/issue/pages, DOI). 🔎 Confirm the full author list
- **Summary:** Derives the LACE index: **L**ength of stay, **A**cuity of admission, **C**omorbidity (Charlson), **E**mergency visits in the prior 6 months. It predicts death or unplanned readmission within 30 days.
- **Key findings:** C-statistic ≈ **0.684** in validation. Scores 0–19 map to ≈2%–44% expected risk.
- **Relevance:** Clinical benchmark for our ROC-AUC. Our features include analogues of L (time_in_hospital), A (admission type), C (number_diagnoses/diag groups) and E (number_emergency).

### [Donze2013] HOSPITAL score
- **Citation:** J. Donzé, D. Aujesky, D. Williams, J. L. Schnipper, "Potentially avoidable 30-day hospital readmissions in medical patients: derivation and validation of a prediction model," *JAMA Internal Medicine*, vol. 173, no. 8, pp. 632–638, 2013.
- **Verified:** ✅ (title, journal, year). 🔎 Check the author list, volume, pages, and DOI
- **Summary:** Seven predictors available at discharge: **H**emoglobin, discharge from **O**ncology, **S**odium, **P**rocedure during stay, **I**ndex admission **T**ype (urgent), number of **A**dmissions in the past 12 months, **L**ength of stay.
- **Key findings:** Low (0–4), intermediate (5–6) and high (≥7) risk groups with ≈5% / 10% / 20% potentially avoidable readmission rates.
- **Relevance:** Supports our "information available at discharge" design and the risk-tier presentation.

### [Kansagara2011] Systematic review of readmission risk models
- **Citation:** D. Kansagara, H. Englander, A. Salanitro, D. Kagen, C. Theobald, M. Freeman, S. Kripalani, "Risk prediction models for hospital readmission: a systematic review," *JAMA*, vol. 306, no. 15, pp. 1688–1698, 2011. doi:10.1001/jama.2011.1515
- **Verified:** ✅ (journal, date, vol/issue/pages). 🔎 Confirm the author list and DOI
- **Summary:** Reviews 30 studies of 26 unique models.
- **Key findings:** Most models performed poorly (C-statistics often 0.6–0.7). 30-day readmission was the most common outcome. Few models included social/functional variables.
- **Relevance:** Justifies our realistic performance expectations and the limitations section.

### [Jencks2009] Rehospitalizations among Medicare patients
- **Citation:** S. F. Jencks, M. V. Williams, E. A. Coleman, "Rehospitalizations among patients in the Medicare fee-for-service program," *New England Journal of Medicine*, vol. 360, no. 14, pp. 1418–1428, 2009.
- **Verified:** 🔎
- **Summary / findings:** About one in five Medicare patients was rehospitalised within 30 days, with a large cost burden.
- **Relevance:** Motivation (Chapter 1) for the scale of the problem.

## C. Machine learning for readmission

### [Huang2021] ML for readmission: scoping review
- **Citation:** Y. Huang, A. Talwar, S. Chatterjee, R. R. Aparasu, "Application of machine learning in predicting hospital readmissions: a scoping review of the literature," *BMC Medical Research Methodology*, vol. 21, no. 1, Art. 96, pp. 1–13, 2021. doi:10.1186/s12874-021-01284-z
- **Verified:** ✅ (title, journal, volume, article ID, DOI, PMC8117326)
- **Summary:** Maps machine learning methodologies, data sources, predictors, and validation strategies in 62 hospital readmission prediction studies. Identifies standard modeling workflows, reporting gaps, and class imbalance approaches.
- **Key findings / numbers:** Logistic Regression and Tree Ensembles (Random Forest, Gradient Boosting) were the most frequently applied architectures. Discriminative ability (ROC-AUC) across administrative data consistently centered between 0.62 and 0.72. Highlighted pervasive reporting omissions in class imbalance handling and calibration.
- **Relevance:** Serves as the primary methodological reference for Chapter 2.3. Justifies our choice of scikit-learn models (LogisticRegression, RandomForest, HistGradientBoosting) and reinforces the necessity of reporting PR-AUC, calibration curves, and Brier scores.

### [Artetxe2018] Predictive models for readmission: methods review
- **Citation:** A. Artetxe, A. Beristain, M. Graña, "Predictive models for hospital readmission risk: A systematic review of methods," *Computer Methods and Programs in Biomedicine*, vol. 164, pp. 49–64, Oct. 2018. doi:10.1016/j.cmpb.2018.06.006
- **Verified:** ✅ (journal, volume, pages, year, DOI)
- **Summary:** Comprehensive review of data science and statistical pipelines for hospital readmission risk, surveying 41 studies. Categorizes data sources into claims/administrative, EHR, and survey data.
- **Key findings / numbers:** 30-day readmission is the predominant prediction horizon. The target condition is intrinsically imbalanced (typically 8–15% base rate). Tree ensembles and nonlinear models provide moderate gains over baseline regression models, but operational deployment requires threshold tuning and calibrated probabilities rather than raw 0.5 decision thresholds.
- **Relevance:** Validates our clinical framing as a decision-support tool, supports threshold optimization for recall (F2), and informs our discussion of class imbalance in Chapter 4.

### [Futoma2015] Comparison of models for early readmission
- **Citation:** J. Futoma, J. Morris, J. Lucas, "A comparison of models for predicting early hospital readmissions," *Journal of Biomedical Informatics*, vol. 56, pp. 229–238, 2015.
- **Verified:** 🔎
- **Relevance:** Shows that ML models give modest gains over regression on administrative data.

### [Rajkomar2018] Deep learning with EHRs
- **Citation:** A. Rajkomar et al., "Scalable and accurate deep learning with electronic health records," *npj Digital Medicine*, vol. 1, Art. 18, 2018.
- **Verified:** 🔎
- **Relevance:** Future work: richer EHR data (notes, time series) improves readmission prediction.

## D. Methods: imbalance, calibration, explainability, fairness, reporting

### [Chawla2002] SMOTE
- **Citation:** N. V. Chawla, K. W. Bowyer, L. O. Hall, W. P. Kegelmeyer, "SMOTE: Synthetic Minority Over-sampling Technique," *Journal of Artificial Intelligence Research*, vol. 16, pp. 321–357, 2002.
- **Verified:** 🔎 · **Relevance:** Optional imbalance comparison (P5-02).

### [NiculescuMizil2005] Calibration
- **Citation:** A. Niculescu-Mizil, R. Caruana, "Predicting good probabilities with supervised learning," in *Proc. 22nd International Conference on Machine Learning (ICML)*, 2005.
- **Verified:** 🔎 · **Relevance:** Justifies isotonic/sigmoid calibration (P5-03).

### [Lundberg2017] SHAP
- **Citation:** S. M. Lundberg, S.-I. Lee, "A unified approach to interpreting model predictions," in *Advances in Neural Information Processing Systems 30 (NeurIPS)*, 2017.
- **Verified:** 🔎 · **Relevance:** Per-patient explanations (P5-05).

### [Obermeyer2019] Racial bias in a health algorithm
- **Citation:** Z. Obermeyer, B. Powers, C. Vogeli, S. Mullainathan, "Dissecting racial bias in an algorithm used to manage the health of populations," *Science*, vol. 366, no. 6464, pp. 447–453, 2019.
- **Verified:** 🔎 · **Relevance:** Motivates the fairness analysis (P5-06).

### [Pedregosa2011] scikit-learn
- **Citation:** F. Pedregosa et al., "Scikit-learn: Machine learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, 2011.
- **Verified:** 🔎 · **Relevance:** Core ML library.

### [Collins2015] TRIPOD reporting guideline
- **Citation:** G. S. Collins, J. B. Reitsma, D. G. Altman, K. G. M. Moons, "Transparent reporting of a multivariable prediction model for individual prognosis or diagnosis (TRIPOD): the TRIPOD statement," *Annals of Internal Medicine*, vol. 162, no. 1, pp. 55–63, 2015.
- **Verified:** 🔎 · **Relevance:** Checklist for reporting our model honestly (report Ch. 6–7, model card).

---

## To add (search during P2-07 / P4-08)
- [ ] 2–3 recent (2020+) papers that applied ML to the UCI Diabetes 130-US dataset (look for reported ROC-AUC values to compare against)
- [ ] A paper on Indian hospital readmission or healthcare resource planning (if your guide wants local context)
- [ ] CMS Hospital Readmissions Reduction Program (HRRP) official page (policy context)
