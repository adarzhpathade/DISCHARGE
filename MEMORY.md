# MEMORY.md — Project Memory (decisions, gotchas, current state)

> Long-lived memory for humans and AI agents. `AGENTS.md` says **what** the rules are. This file
> records **why**, **what we learned**, and **where we are**. Append new entries at the top of each
> section, with dates (YYYY-MM-DD). Never delete history. Mark superseded entries ~~struck through~~.

---

## 1. Current state

| Field | Value |
|---|---|
| Last updated | 2026-10-04 |
| Project name | **DISCHARGE** (Diabetic Inpatient Stratification and Clinical Decision-Support System) |
| Repository | `https://github.com/adarzhpathade/DISCHARGE` (branch `main`) |
| Dev OS | **Windows** (pwsh). Native Power BI Desktop available directly |
| Current phase | Phase 0 — Setup & Planning (in progress) |
| Completed tasks | `P0-01` Initialise repository & folder structure (commit `30847d2`, pushed to GitHub) |
| Next task | `P0-02` Python environment |
| Active model | none (`models/CURRENT` does not exist yet) |
| Best val ROC-AUC so far | — |
| Blockers | UI design references not yet supplied (`P7-05`) |

---

## 2. Decisions log (ADR-lite)

| ID | Date | Decision | Why | Alternatives rejected |
|---|---|---|---|---|
| D-015 | 2026-10-04 | Host OS confirmed as Windows (pwsh) | Host environment is Windows with Python 3.13, Node 24, Git 2.53. Allows native Power BI Desktop execution | macOS assumptions in earlier draft |
| D-014 | 2026-10-04 | Local study/presentation guides kept uncommitted in `.gitignore` | `docs/TEACHER_EXPLANATION_GUIDE.md` and `docs/OPERATIONAL_FLOW.md` are for student viva and team explanations; user requested they not be pushed | Committing presentation guides to public git |
| D-013 | 2026-10-04 | Project named **DISCHARGE** (repo: `adarzhpathade/DISCHARGE`) | Acronym matches clinical domain: Diabetic Inpatient Stratification and Clinical Decision-Support System | CareCast, ReAdmitIQ, generic Hospital Readmission |
| D-001 | 2026-10-04 | Dataset = UCI Diabetes 130-US (1999–2008) | Public, ≈100k rows, ready `<30` label, realistically messy, well cited (Strack 2014) | MIMIC (credentialing delay), Synthea (unrealistic patterns) |
| D-002 | 2026-10-04 | Database = PostgreSQL 16 | User choice. Real SQL engine for the cleaning stage, native Power BI connector on Windows | SQLite, MySQL |
| D-003 | 2026-10-04 | Backend = FastAPI, Frontend = Next.js (App Router, TS, Tailwind) | User choice. Python backend can load the sklearn model directly | Flask, Streamlit, Vite React |
| D-004 | 2026-10-04 | Agent context file = `AGENTS.md` only (no CLAUDE.md) | User choice, cross-tool standard | — |
| D-005 | 2026-10-04 | Target = `readmitted == '<30'` → 1, else 0 (`>30` counts as 0) | Problem statement defines 30-day unplanned readmission | 3-class target |
| D-006 | 2026-10-04 | Remove discharge dispositions 11, 13, 14, 19, 20, 21 | Expired/hospice patients cannot be readmitted | Keep and flag |
| D-007 | 2026-10-04 | Split by `patient_nbr` groups (70/15/15) | Same patient in train and test inflates metrics (leakage) | Random row split; first-encounter-only (noted as a sensitivity check) |
| D-008 | 2026-10-04 | Imbalance handled with class_weight + threshold tuning (F2 on val) | Simple, no synthetic data, clinically favours recall | SMOTE (kept as an optional comparison) |
| D-009 | 2026-10-04 | Risk tiers by percentile: High top 10%, Medium next 20%, Low rest | Matches limited follow-up capacity, which is easy to explain to hospital management | Fixed probability cut-offs |
| D-010 | 2026-10-04 | Power BI fed by CSV exports of `analytics.vw_*` | Power BI Desktop can connect to CSVs or directly to PostgreSQL on Windows | Direct DB only |
| D-011 | 2026-10-04 | UI is built only from user-supplied design references | User instruction: "user will give design references, replicate exactly" | Agent-designed UI |
| D-012 | 2026-10-04 | Drop `weight`, `payer_code`, `examide`, `citoglipton` | ≈97% missing, ≈40% missing & administrative, constant, constant | Imputation |

---

## 3. Gotchas & learnings

- **G-001 — pandas `"None"` trap.** pandas ≥ 2.0 includes `"None"` in its default NA strings. In this dataset, `A1Cresult = "None"` means "test not performed" (a real category). Always use `pd.read_csv(..., keep_default_na=False, na_values=["?"])`. Load into Postgres as TEXT.
- **G-002 — `IDs_mapping.csv` is three tables in one file**, separated by blank lines, each with its own header (`admission_type_id,description` / `discharge_disposition_id,description` / `admission_source_id,description`). Parse it by splitting on blank lines.
- **G-003 — Quoted identifiers.** Raw columns like `glyburide-metformin`, `A1Cresult`, `diabetesMed` need double quotes in PostgreSQL. Staging renames them to snake_case.
- **G-004 — Expected performance ceiling.** Published work on this dataset reports ROC-AUC of about 0.64–0.70 for 30-day readmission. Higher than ≈0.75 almost certainly means leakage.
- **G-005 — ~~Power BI on Mac.~~** ~~No native macOS build.~~ Superseded by D-015: Host OS is Windows, so Power BI Desktop runs natively.
- **G-006 — `encounter_id` ordering** is not guaranteed to be chronological, so don't build "previous encounter" features from it without caveats.
- **G-007 — ~~Broken system Python on this Mac.~~** Superseded by D-015: Host is Windows with Python 3.13.15 installed.
- **G-008 — Git ignore directory traversal trap.** Simple `data/**` excludes directory paths before evaluating un-ignore patterns `!data/**/.gitkeep`. The pattern must allow subdirectories `!data/*/` and `!data/**/` while ignoring nested content files.
- **G-009 — Windows PowerShell execution.** Shell commands must use PowerShell syntax (`New-Item`, `;` delimiter instead of `&&`, Windows paths).

*(Add new gotchas here as they are discovered: G-010, …)*

---

## 4. Experiment log

| Date | model_version | Features / change | CV ROC-AUC | Val ROC-AUC | Val PR-AUC | Val Recall@thr | Notes |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — |

---

## 5. Open questions for the user

- [x] ~~Which Power BI option: lab PC / Windows VM / Power BI Service web? (`P0-08`)~~ -> Resolved: Native Power BI Desktop on Windows (D-015).
- [ ] When will UI design references arrive in `design-references/`? Which screens? (`P7-05`)
- [ ] College report/synopsis format: does the university have a template (font, margins, chapter names)? (`P0-09`)
- [ ] Submission and viva dates, to confirm the 8-week calendar
- [ ] Does the guide/supervisor require a specific citation style (IEEE / APA)? Default is **IEEE**.

---

## 6. Glossary

- **Encounter** — one hospital admission (one row).
- **30-day readmission** — an unplanned inpatient readmission within 30 days of discharge (`readmitted = '<30'`).
- **Base rate / prevalence** — share of encounters with label 1 (≈11%).
- **PR-AUC** — area under the precision-recall curve. More informative than ROC-AUC when positives are rare.
- **F2** — F-score that weights recall twice as much as precision.
- **Calibration** — whether a predicted 20% risk really corresponds to ≈20% observed readmissions.
- **Risk tier** — Low / Medium / High bucket used for follow-up prioritisation.
