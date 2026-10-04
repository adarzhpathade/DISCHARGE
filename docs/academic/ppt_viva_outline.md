# Presentation Outline & Viva Preparation (P8-05, P8-06)

## Part A — Slide outline (≈15 slides, 12–15 minutes)

| # | Slide | Content (keep it to 3–5 bullets or 1 visual) |
|---|---|---|
| 1 | Title | Project title, name, guide, institute, date |
| 2 | Problem | Cost/bed/staff burden of readmissions. Hard to spot high-risk patients at discharge |
| 3 | Objectives | 4–6 objectives from the synopsis |
| 4 | Literature & gap | LACE (C≈0.68), HOSPITAL score, ML reviews. Gap: transparent, reproducible, end-to-end decision-support |
| 5 | Dataset | UCI Diabetes 130-US: 101,766 encounters, 50 attributes, 11% readmitted < 30 days |
| 6 | Architecture | Diagram: PostgreSQL → Python → scikit-learn → FastAPI/Next.js → Power BI |
| 7 | Data cleaning | Issues found → rules applied → rows before/after (table) |
| 8 | Key EDA insights | 3 charts: prior inpatient visits, discharge destination, diagnosis group |
| 9 | Statistical evidence | Chi-square/Cramér's V top factors. Odds ratios |
| 10 | Modelling approach | Grouped split, pipelines, class weighting, tuning, calibration |
| 11 | Results | Model comparison table + test ROC/PR curves |
| 12 | Risk tiers | Observed rate Low/Medium/High (lift chart). "Top 10% readmitted at ≈2.5× average" |
| 13 | Explainability & fairness | Top drivers. Subgroup recall table |
| 14 | Demo | Power BI pages + web prediction (live or video) |
| 15 | Conclusion, limitations, future work | Honest limits + next steps. Thank you / Q&A |

**Demo script (5 min, P8-07):** (1) Power BI Executive Overview → filter age 80+ → (2) Risk Stratification page → drill into a High-risk patient → (3) web app: enter a patient → show probability, tier, top factors, disclaimer → (4) change "prior inpatient visits" from 0 to 3 → the risk increases. Keep a recorded backup video.

---

## Part B — Likely viva questions & model answers

### Problem & data
1. **Why 30 days?** It is the standard window used in readmission policy (e.g., the US CMS Hospital Readmissions Reduction Program) and in the literature (Kansagara 2011). Early readmissions are more likely to relate to the index stay or the discharge process.
2. **Why this dataset?** Public, large (≈100k encounters), real hospital data with a ready outcome label, realistic data-quality problems, and an established paper (Strack 2014) to compare against.
3. **Limitations of the dataset?** Diabetic patients only, US hospitals 1999–2008, no detailed labs/vitals/social factors, de-identified codes, and no distinction between planned and unplanned readmissions.
4. **Why remove expired/hospice discharges?** Those patients cannot be readmitted. Keeping them would label them "not readmitted" and bias the model.
5. **How did you handle missing values?** `?` → NULL. Dropped columns with ≈97% (weight) or ≈40% administrative (payer code) missingness. Explicit `Unknown`/`Missing` categories for race/specialty/diagnosis. HbA1c "None" kept as **NotMeasured** because not testing is itself informative.

### Methodology
6. **Why split by patient instead of by row?** Many patients have several encounters. A row split puts the same person in train and test, so the model can memorise patient-specific patterns and the test score is inflated (data leakage).
7. **What is data leakage? How did you prevent it?** Information from outside the training data (or from the future) influencing the model. Prevention: grouped split, preprocessing inside sklearn Pipelines fitted on training folds only, no outcome-derived features, and the test set used exactly once.
8. **How did you handle class imbalance?** `class_weight="balanced"` plus tuning the decision threshold for recall (F2). SMOTE was compared as an option. Accuracy is not used because a "predict nobody" model would score 89%.
9. **Why ROC-AUC and PR-AUC rather than accuracy?** With 11% positives, accuracy is misleading. ROC-AUC measures ranking ability. PR-AUC focuses on the rare positive class (random = 0.11).
10. **Why prioritise recall?** Missing a high-risk patient (false negative) means no follow-up for someone who needed it. A false positive costs only an extra phone call or check-up.
11. **What is calibration and why do it?** It makes predicted probabilities match the observed frequencies, so "25% risk" really means about 25 in 100. Class weighting distorts probabilities, and isotonic/sigmoid calibration fixes that.
12. **How did you choose the threshold?** On the validation set: maximise F2 subject to recall ≥ 60%. Risk tiers are percentile-based (top 10% High, next 20% Medium) to match follow-up capacity.
13. **Why gradient boosting / random forest?** They capture non-linear effects and interactions on tabular data. Logistic regression is kept as an interpretable baseline. I compared them on the same grouped CV folds.
14. **What does cross-validation do here?** 5-fold StratifiedGroupKFold estimates performance and tunes hyperparameters without touching validation/test data, while keeping each patient within one fold.

### Results & interpretation
15. **Your ROC-AUC is ≈0.68. Isn't that low?** It is in line with the literature for this dataset and comparable to the clinically used LACE index (C-statistic ≈ 0.68). Readmission depends on many factors not in the data (social support, adherence). The practical value is in the **tier lift**: high-risk patients are readmitted at a much higher rate than average.
16. **What are the most important factors?** Typically: number of prior inpatient visits, discharge destination, emergency visits, primary diagnosis group, length of stay, number of medications/diagnoses, and age.
17. **Do these factors cause readmission?** No. They are associations learned from observational data. The model supports prioritisation, not causal conclusions.
18. **Is the model fair?** I compared recall, precision and AUC across race, gender and age groups and report the gaps and their likely causes (sample size, base-rate differences). Bias in healthcare algorithms is a known risk (Obermeyer et al., 2019).
19. **How would a hospital use this?** At discharge, staff enter (or the EHR sends) the patient's data, and the system returns risk + tier + top factors. High-tier patients get priority follow-up calls, earlier clinic visits, or medication reconciliation. Administrators use the dashboard for bed and staff planning.

### Technical
20. **Why PostgreSQL + SQL for cleaning?** Hospitals store data in relational databases. SQL cleaning is transparent, auditable and reproducible, and the views feed both Power BI and the API.
21. **How does the API make sure features match training?** It imports the same `build_features` function and the saved metadata (e.g., the specialty list), and loads the full sklearn Pipeline including preprocessing.
22. **How would you deploy or retrain in production?** Version models (`models/vYYYYMMDD_*`), register them in `ml.model_registry`, monitor calibration and drift, retrain periodically, and validate on recent data before switching `CURRENT`.
23. **What would you improve with more time?** Recent multi-disease EHR data, temporal validation, clinical notes (NLP), social determinants, cost-sensitive thresholds, and a prospective pilot.
24. **Ethics & privacy?** The dataset is public and de-identified. Results are presented as decision support with a disclaimer, and a clinician makes the final judgement. Fairness was checked across subgroups.
