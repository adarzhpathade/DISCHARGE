# Final Report Outline (P8-04)

> Adapt the chapter names and formatting to your college template (P0-09). Target ≈ 50–70 pages.
> Figures come from `reports/figures/`, tables from `reports/metrics/` and `reports/eda/`.
> The **Source** column says where each section's content is produced.

## Front matter
Title page · Certificate · Declaration · Acknowledgement · Abstract (≈250 words: problem, data, method, best ROC-AUC/PR-AUC/recall, tier lift, deliverables) · Table of contents · List of figures · List of tables · List of abbreviations (EHR, ICD-9, LOS, ROC-AUC, PR-AUC, SMOTE, SHAP, API, BI)

| Ch. | Title | Contents | Source |
|---|---|---|---|
| 1 | **Introduction** | 1.1 Background (readmission burden). 1.2 Motivation. 1.3 Problem statement. 1.4 Objectives. 1.5 Scope & limitations. 1.6 Report organisation | `docs/academic/synopsis.md` |
| 2 | **Literature Review** | 2.1 Clinical risk scores (LACE, HOSPITAL). 2.2 Systematic reviews of readmission models. 2.3 ML for readmission. 2.4 Studies on the UCI diabetes dataset. 2.5 Imbalance, calibration, explainability, fairness. 2.6 Research gap & how this project addresses it | `literature/literature_review.md` |
| 3 | **System Analysis & Requirements** | 3.1 Existing approach & limitations. 3.2 Proposed system. 3.3 Functional requirements. 3.4 Non-functional requirements (reproducibility, privacy, explainability). 3.5 Hardware/software requirements. 3.6 Feasibility | AGENTS.md §1, `docs/environment_setup.md` |
| 4 | **System Design** | 4.1 Architecture diagram. 4.2 Data-flow diagram (levels 0/1). 4.3 Database schema (ER diagram of raw → staging → features → ml → analytics). 4.4 Use-case diagram (clinician, administrator). 4.5 API design. 4.6 Dashboard design | `docs/architecture.md`, `docs/database_schema.md`, `docs/api_contract.md` |
| 5 | **Data Understanding, Cleaning & EDA** | 5.1 Dataset description. 5.2 Data-quality issues found (table). 5.3 Cleaning rules C1–C13 with row impact. 5.4 EDA findings (≈10 figures). 5.5 Statistical tests & odds ratios | `reports/eda/*`, notebooks 01–04 |
| 6 | **Methodology & Implementation** | 6.1 Target definition. 6.2 Feature engineering. 6.3 Patient-grouped split & leakage prevention. 6.4 Pipelines & models. 6.5 Imbalance handling. 6.6 Tuning. 6.7 Calibration. 6.8 Threshold & risk tiers. 6.9 API & web implementation. 6.10 Power BI implementation | `docs/MODEL_TRAINING_GUIDE.md`, `src/` |
| 7 | **Results & Discussion** | 7.1 Model comparison table (CV). 7.2 Final test metrics. 7.3 ROC/PR/calibration curves. 7.4 Confusion matrix at the chosen threshold. 7.5 Risk-tier lift. 7.6 Feature importance & interpretation. 7.7 Fairness analysis. 7.8 Comparison with the literature (LACE ≈ 0.68). 7.9 Dashboard & app screenshots | `reports/metrics/*`, `reports/figures/*`, `reports/model_card.md` |
| 8 | **Testing** | 8.1 Unit tests (cleaning, ICD-9, split, pipeline). 8.2 API tests. 8.3 Test-case table (input → expected → actual) | `tests/`, `backend/tests/` |
| 9 | **Conclusion & Future Work** | 9.1 Summary of contributions. 9.2 Limitations (single disease cohort, 1999–2008, no social determinants, associations ≠ causes). 9.3 Future work (more recent multi-disease EHR data, temporal validation, clinical notes/NLP, prospective evaluation, cost-sensitive thresholds) | — |
| — | **References** | IEEE style (or as the college requires); all verified (P8-09) | `literature/annotated_bibliography.md` |
| — | **Appendices** | A. Data dictionary. B. Full SQL cleaning script. C. Hyperparameter grids. D. API spec. E. User manual (run instructions). F. Model card | `docs/*`, `sql/*`, `reports/model_card.md` |

## Must-have figures (checklist)
- [ ] System architecture diagram
- [ ] ER / schema diagram
- [ ] Target class distribution
- [ ] Readmission rate by age group
- [ ] Readmission rate by primary diagnosis group
- [ ] Readmission rate vs prior inpatient visits
- [ ] Readmission rate by discharge destination
- [ ] Correlation heatmap
- [ ] Model comparison bar chart (ROC-AUC, PR-AUC)
- [ ] ROC curve (test) and PR curve (test)
- [ ] Calibration curve
- [ ] Confusion matrix at the threshold
- [ ] Observed readmission rate by risk tier
- [ ] Feature-importance chart
- [ ] Power BI screenshots (≥ 3 pages)
- [ ] Web app screenshots (if built)
