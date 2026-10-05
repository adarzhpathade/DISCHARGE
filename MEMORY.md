# MEMORY.md — Project Memory (decisions, gotchas, current state)

> Long-lived memory for humans and AI agents. `AGENTS.md` says **what** the rules are. This file
> records **why**, **what we learned**, and **where we are**. Append new entries at the top of each
> section, with dates (YYYY-MM-DD). Never delete history. Mark superseded entries ~~struck through~~.

---

## 1. Current state

| Field | Value |
|---|---|
| Last updated | 2026-10-06 |
| Project name | **DISCHARGE** (Diabetic Inpatient Stratification and Clinical Decision-Support System) |
| Repository | `https://github.com/adarzhpathade/DISCHARGE` (branch `main`) |
| Dev OS | **Windows** (pwsh). Native Power BI Desktop available directly |
| Current phase | Phase 3 — Exploratory Data Analysis & Statistical Analysis (ready to start) |
| Completed tasks | `P0-01` to `P0-06`, `P0-08`, `P0-10` (Phase 0); `P1-01` to `P1-07` (Phase 1); `P2-01` to `P2-07` (Phase 2 complete) |
| Next task | `P3-01` Univariate analysis (`reports/figures/03_*.png`) & `P3-04` ICD-9 diagnosis grouping |
| Active model | none (`models/CURRENT` does not exist yet) |
| Best val ROC-AUC so far | — |
| Blockers | UI design references not yet supplied (`P7-05`) |

---

## 2. Decisions log (ADR-lite)

| ID | Date | Decision | Why | Alternatives rejected |
|---|---|---|---|---|
| D-018 | 2026-10-06 | Explicit DDL + INSERT for `staging.encounters` with clinical check constraints | Strict data typing, primary key indexing on `encounter_id`, and validation constraints on numeric ranges and categories | Implicit types from CREATE TABLE AS SELECT |
| D-017 | 2026-10-05 | Ingestion via psycopg driver COPY and dynamic SQL parsing of stacked dim tables | Streaming COPY from STDIN loads 101,766 rows into PostgreSQL in ~15s without type distortion; SQL bounds separate the 3 stacked lookup tables reliably | pandas to_sql (slow, alters column types), manual psql CLI |
| D-016 | 2026-10-05 | Database hosted on Neon Postgres (project: `twilight-unit-85400243`) | Zero local daemon/Docker overhead on Windows, serverless sleep/instant-wake prevents inactivity locking, standard PostgreSQL driver connection | Local Docker, local Windows PostgreSQL service, Supabase |
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
- **G-010 — Dataset SHA-256 and verified row count.** Downloaded from UCI repository (id 296). `diabetic_data.csv`: 101,766 rows (101,767 lines with header), 19,159,383 bytes, SHA-256: `0689e7ec031237dc63031b938805c48377748761a3b26acab621567afa24df97`. `IDs_mapping.csv`: 68 lines, 2,547 bytes, SHA-256: `f1bb82b471cb34649352597572c9b1fb00bd27f77b9f5a22a03dc3eb1039749e`. Note: the zip file contained `IDS_mapping.csv` with capital 'S', extracted as canonical `IDs_mapping.csv`.
- **G-011 — Stacking lookup tables in `IDs_mapping.csv`.** Staging lookup dimensions (`staging.dim_admission_type`, `staging.dim_discharge_disposition`, `staging.dim_admission_source`) are populated dynamically from `raw.ids_mapping` by locating the line numbers where section header strings occur and filtering numerical IDs (`col1 ~ '^[0-9]+$'`).
- **G-012 — Matplotlib headless backend on Windows.** Matplotlib defaults to `tkagg` on Windows, which attempts to spawn a GUI Tkinter root window that blocks headless background subprocesses. Always specify `matplotlib.use('Agg')` in scripts and headless notebook runners.
- **G-013 — Tornado / ZMQ Proactor loop deadlock on Windows (Python 3.13).** When running IPython `NotebookClient` over ZMQ on Windows Python 3.13, the default `ProactorEventLoop` can deadlock on IPC socket polling. Use in-process `InteractiveShell` execution or `WindowsSelectorEventLoopPolicy` for deterministic cell execution.
- **G-014 — Staging cleaning row impact verification.** Exactly 2,426 rows were excluded from raw (101,766 encounters) to staging (99,340 encounters): 3 rows with `gender = 'Unknown/Invalid'` (Rule C3) and 2,423 rows with hospice/expired discharge dispositions (Rule C4). Staging readmission prevalence is 11.39% (11,314 positive `<30` cases across 69,987 unique patients).

*(Add new gotchas here as they are discovered: G-015, …)*

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
