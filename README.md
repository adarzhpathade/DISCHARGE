# Hospital Readmission Risk Prediction System

A decision-support system that estimates the **probability of unplanned readmission within 30 days of discharge**, using only information available at or before discharge. It is built on the UCI Diabetes 130-US Hospitals dataset with PostgreSQL, Python (Pandas/NumPy), scikit-learn, FastAPI, Next.js, and Power BI.

> ⚠ This system produces statistical risk estimates to support, not replace, clinical judgement.

## Status
🚧 Planning complete. Implementation starts Week 1 (2026-10-05). See [`PROGRESS.md`](PROGRESS.md).

## Start here
| If you want to… | Read |
|---|---|
| Understand the whole project (humans & AI agents) | [`AGENTS.md`](AGENTS.md) |
| See the plan | [`ROADMAP.md`](ROADMAP.md) |
| See progress | [`PROGRESS.md`](PROGRESS.md) |
| Know why decisions were made | [`MEMORY.md`](MEMORY.md) |
| Train the model step by step | [`docs/MODEL_TRAINING_GUIDE.md`](docs/MODEL_TRAINING_GUIDE.md) |
| Set up your machine | [`docs/environment_setup.md`](docs/environment_setup.md) |

## Quickstart (available once Phase 6 is done)
```bash
make setup && make db-up && make db-init
make pipeline          # ingest → clean → features → train → evaluate → score → views → export-bi
make api               # http://localhost:8000/docs
make web               # http://localhost:3000  (after the UI is built)
```

## Results
*To be filled after P5-07: test ROC-AUC, PR-AUC, recall, and risk-tier lift.*
