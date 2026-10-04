# design-references/

> **The UI is built ONLY from what is in this folder** (AGENTS.md §11). Nothing will be designed or
> invented. Frontend tasks P7-05 … P7-09 stay blocked until this folder contains the designs.

## What to put here
| Item | Format | Notes |
|---|---|---|
| Screen designs | PNG/JPG (≥ 1440 px wide for desktop), PDF, or a Figma link in `figma-links.md` | One file per screen, named `NN_<screen-name>[_<state>].png` |
| Mobile/tablet versions | same | Suffix `_mobile`, `_tablet`. If missing, tell us whether the app must be responsive |
| States | same | Loading, empty, error, form-validation, success. **If not supplied, the agent will ask before guessing** |
| Design tokens | `tokens.md` or a Figma styles screenshot | Colours (hex), fonts (family, weights, sizes), spacing scale, border radius, shadows |
| Fonts | font files or Google Fonts names | |
| Icons / logo / images | SVG/PNG | Icon set name if a library is used (e.g. Lucide, Heroicons) |
| Copy | in the designs or `copy.md` | Exact text to use |
| Inspiration links | `inspiration.md` | Only if you want something *like* a site. Say what to take from it |
| Power BI design (optional) | PNG/PDF | Dashboard look → `powerbi/theme.json` |

## Expected screens (functional list — your designs decide the look and the final set)
1. **Risk assessment form** — enter patient details at discharge (fields: see `docs/api_contract.md` → `PatientInput`)
2. **Risk result** — probability, risk tier, top contributing factors, disclaimer
3. **High-risk patient list** — table with filters and pagination (`/patients/high-risk`)
4. **Overview / dashboard** — KPIs (`/stats/overview`) and model info (`/model/info`, `/model/metrics`)
5. *(optional)* **Batch upload** — CSV upload and results (`/predict/batch`)
6. *(optional)* **About / methodology** — model card summary

## Naming example
```
01_landing.png
02_assessment-form.png
02_assessment-form_error.png
03_result_high-risk.png
03_result_low-risk.png
04_high-risk-list.png
04_high-risk-list_empty.png
05_overview.png
tokens.md
figma-links.md
```
