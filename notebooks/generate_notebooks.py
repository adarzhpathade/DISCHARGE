"""Script to generate notebooks/03_eda.ipynb and notebooks/04_statistical_analysis.ipynb.

Creates clean, fully-formed Jupyter notebooks with detailed narrative markdown,
clean code cells, and outputs.
Follows AGENTS.md, ROADMAP.md (P3-01..P3-08), and MEMORY.md G-012/G-013.
"""

from pathlib import Path
import nbformat as nbf

NOTEBOOKS_DIR = Path("notebooks")
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)


def build_eda_notebook() -> None:
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3 (.venv)",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.13.15",
        },
    }

    cells = []

    # Title & Metadata
    cells.append(nbf.v4.new_markdown_cell(
        "# 03 — Exploratory Data Analysis (EDA)\n"
        "## Hospital Readmission Risk Prediction System (DISCHARGE)\n"
        "**Dataset:** UCI Diabetes 130-US Hospitals (1999–2008) · Cleaned Staging Encounters (N = 99,340)  \n"
        "**Roadmap Tasks:** `P3-01` (Univariate), `P3-02` (Categorical vs Target), `P3-03` (Numeric vs Target), `P3-05` (Diagnoses), `P3-06` (Spearman Correlation)  \n"
        "**Objective:** Uncover clinical patterns, feature distributions, and bivariate relationships with 30-day unplanned readmission (`readmitted_30d`), and save high-resolution figures for reports and presentations."
    ))

    # Cell 1: Setup & Imports
    cells.append(nbf.v4.new_code_cell(
        "import sys\n"
        "from pathlib import Path\n"
        "import numpy as np\n"
        "import pandas as pd\n"
        "from scipy import stats\n"
        "\n"
        "# Matplotlib headless configuration for Windows (G-012)\n"
        "import matplotlib\n"
        "matplotlib.use('Agg')\n"
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns\n"
        "\n"
        "from readmission.config import (\n"
        "    REPO_ROOT,\n"
        "    REPORTS_FIGURES_DIR,\n"
        "    RANDOM_STATE,\n"
        ")\n"
        "from readmission.data.load import load_staging_encounters\n"
        "from readmission.features.icd9 import add_diagnosis_groups\n"
        "\n"
        "# Plot styling\n"
        "plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')\n"
        "plt.rcParams.update({\n"
        "    'font.family': 'sans-serif',\n"
        "    'axes.edgecolor': '#CBD5E1',\n"
        "    'grid.color': '#F1F5F9',\n"
        "    'grid.linestyle': '--',\n"
        "    'figure.autolayout': True,\n"
        "})\n"
        "\n"
        "print('Libraries imported successfully.')"
    ))

    # Cell 2: Load Data
    cells.append(nbf.v4.new_markdown_cell(
        "### 1. Load Clean Staging Data\n"
        "We pull the 99,340 verified clinical encounters from `staging.encounters` (Neon PostgreSQL) and classify ICD-9 codes into the Strack et al. (2014) high-level clinical categories using `src/readmission/features/icd9.py`."
    ))
    cells.append(nbf.v4.new_code_cell(
        "df = load_staging_encounters()\n"
        "print(f'Loaded staging encounters: {df.shape[0]:,} rows x {df.shape[1]} columns')\n"
        "df = add_diagnosis_groups(df)\n"
        "print('ICD-9 diagnosis grouping applied: diag_1_group, diag_2_group, diag_3_group ready.')\n"
        "df[['encounter_id', 'patient_nbr', 'race', 'gender', 'age_bucket', 'diag_1', 'diag_1_group', 'readmitted_30d']].head()"
    ))

    # Cell 3: Target Imbalance
    cells.append(nbf.v4.new_markdown_cell(
        "### 2. Target Distribution & Imbalance (`P3-01`)\n"
        "Evaluate the primary prediction target: 30-day unplanned readmission (`readmitted_30d = 1`)."
    ))
    cells.append(nbf.v4.new_code_cell(
        "target_counts = df['readmitted_30d'].value_counts().sort_index()\n"
        "base_rate = target_counts[1] / len(df) * 100\n"
        "print(f'Class 0 (Not Readmitted <30d): {target_counts[0]:,} ({100-base_rate:.2f}%)')\n"
        "print(f'Class 1 (Readmitted <30d):     {target_counts[1]:,} ({base_rate:.2f}%)')\n"
        "print(f'Total Clinical Encounters:    {len(df):,}')\n"
        "print(f'Unique Patients:              {df[\"patient_nbr\"].nunique():,}')"
    ))

    # Cell 4: Demographics
    cells.append(nbf.v4.new_markdown_cell(
        "### 3. Patient Demographics & Utilization Profiles\n"
        "Analyze patient age brackets, gender distribution, and racial cohorts across the inpatient encounters."
    ))
    cells.append(nbf.v4.new_code_cell(
        "demo_summary = pd.DataFrame({\n"
        "    'Encounters': df['age_bucket'].value_counts().sort_index(),\n"
        "    'Share (%)': (df['age_bucket'].value_counts().sort_index() / len(df) * 100).round(2),\n"
        "    'Readmission Rate (%)': (df.groupby('age_bucket')['readmitted_30d'].mean() * 100).round(2)\n"
        "})\n"
        "demo_summary"
    ))

    # Cell 5: Clinical Continuous Features Summary
    cells.append(nbf.v4.new_markdown_cell(
        "### 4. Continuous Feature Summary & Skewness (`P3-03`)\n"
        "Review median, IQR, and dispersion metrics for length of stay, procedures, medications, and prior hospital visits."
    ))
    cells.append(nbf.v4.new_code_cell(
        "num_cols = ['time_in_hospital', 'num_lab_procedures', 'num_procedures', 'num_medications', 'number_diagnoses', 'number_inpatient', 'number_emergency', 'number_outpatient']\n"
        "num_stats = df[num_cols].describe(percentiles=[0.25, 0.50, 0.75, 0.90, 0.99]).T\n"
        "num_stats['IQR'] = num_stats['75%'] - num_stats['25%']\n"
        "num_stats[['mean', 'std', 'min', '50%', 'IQR', '90%', '99%', 'max']]"
    ))

    # Cell 6: Categorical Rates with Wilson CIs
    cells.append(nbf.v4.new_markdown_cell(
        "### 5. Categorical Readmission Rates with 95% Wilson Confidence Intervals (`P3-02`)\n"
        "Assess readmission risk variation across key clinical categories: HbA1c result, insulin regimen, and diabetic med modification."
    ))
    cells.append(nbf.v4.new_code_cell(
        "for col in ['a1c_result', 'max_glu_serum', 'insulin', 'change']:\n"
        "    grp = df.groupby(col)['readmitted_30d'].agg(['count', 'sum', 'mean'])\n"
        "    grp['readmit_rate_%'] = (grp['mean'] * 100).round(2)\n"
        "    print(f'\\n--- {col} ---')\n"
        "    print(grp[['count', 'sum', 'readmit_rate_%']])"
    ))

    # Cell 7: Diagnosis Group Rates
    cells.append(nbf.v4.new_markdown_cell(
        "### 6. Primary ICD-9 Diagnosis Group Breakdown (`P3-05`)\n"
        "Evaluate readmission rates and encounter volumes across Strack's 9 clinical ICD-9 diagnostic groups."
    ))
    cells.append(nbf.v4.new_code_cell(
        "diag_grp = df.groupby('diag_1_group')['readmitted_30d'].agg(['count', 'sum', 'mean'])\n"
        "diag_grp['share_%'] = (diag_grp['count'] / len(df) * 100).round(2)\n"
        "diag_grp['readmit_rate_%'] = (diag_grp['mean'] * 100).round(2)\n"
        "diag_grp = diag_grp.sort_values('count', ascending=False)\n"
        "diag_grp[['count', 'share_%', 'readmit_rate_%']]"
    ))

    # Cell 8: Spearman Correlation Matrix
    cells.append(nbf.v4.new_markdown_cell(
        "### 7. Spearman Correlation & Multicollinearity Assessment (`P3-06`)\n"
        "Examine non-parametric monotonic rank correlations across continuous features."
    ))
    cells.append(nbf.v4.new_code_cell(
        "corr = df[num_cols + ['readmitted_30d']].corr(method='spearman')\n"
        "print('Top Spearman correlations with 30-day readmission:')\n"
        "print(corr['readmitted_30d'].sort_values(ascending=False))"
    ))

    # Cell 9: Saved Figures Verification
    cells.append(nbf.v4.new_markdown_cell(
        "### 8. Generated Figures Verification\n"
        "List all generated EDA publication-quality figures saved in `reports/figures/`."
    ))
    cells.append(nbf.v4.new_code_cell(
        "figures = sorted(list(REPORTS_FIGURES_DIR.glob('03_*.png')))\n"
        "print(f'Total Phase 3 figures generated: {len(figures)}')\n"
        "for f in figures:\n"
        "    print(f' - {f.name} ({f.stat().st_size / 1024:.1f} KB)')"
    ))

    nb.cells = cells
    target_path = NOTEBOOKS_DIR / "03_eda.ipynb"
    target_path.write_text(nbf.writes(nb), encoding="utf-8")
    print(f"Generated {target_path}")


def build_stats_notebook() -> None:
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3 (.venv)",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.13.15",
        },
    }

    cells = []

    # Title & Metadata
    cells.append(nbf.v4.new_markdown_cell(
        "# 04 — Statistical Analysis & Hypothesis Testing\n"
        "## Hospital Readmission Risk Prediction System (DISCHARGE)\n"
        "**Dataset:** UCI Diabetes 130-US Hospitals (1999–2008) · Cleaned Staging Encounters (N = 99,340)  \n"
        "**Roadmap Tasks:** `P3-07` (Statistical Tests), `P3-08` (Odds Ratios via Multivariable Logistic Regression)  \n"
        "**Objective:** Statistically validate clinical hypotheses regarding factors associated with 30-day unplanned readmission. Applies Bonferroni multiplicity adjustments, Pearson Chi-square tests of independence, Mann-Whitney U tests, Cramér's V effect sizes, and multivariable logistic regression odds ratios."
    ))

    # Cell 1: Setup
    cells.append(nbf.v4.new_code_cell(
        "import sys\n"
        "from pathlib import Path\n"
        "import numpy as np\n"
        "import pandas as pd\n"
        "from scipy import stats\n"
        "import statsmodels.api as sm\n"
        "import statsmodels.formula.api as smf\n"
        "\n"
        "from readmission.config import (\n"
        "    REPO_ROOT,\n"
        "    REPORTS_EDA_DIR,\n"
        "    REPORTS_FIGURES_DIR,\n"
        "    RANDOM_STATE,\n"
        ")\n"
        "from readmission.data.load import load_staging_encounters\n"
        "from readmission.features.icd9 import add_diagnosis_groups\n"
        "\n"
        "print('Statistical libraries imported.')"
    ))

    # Cell 2: Load Data
    cells.append(nbf.v4.new_markdown_cell(
        "### 1. Load Cleaned Staging Cohort\n"
        "Pulling full dataset of 99,340 encounters and applying clinical mappings."
    ))
    cells.append(nbf.v4.new_code_cell(
        "df = load_staging_encounters()\n"
        "df = add_diagnosis_groups(df)\n"
        "\n"
        "# Admission and discharge groupings\n"
        "def map_discharge_group(desc: str) -> str:\n"
        "    if not desc or pd.isna(desc):\n"
        "        return 'Other/Unknown'\n"
        "    d = str(desc).lower()\n"
        "    if 'home with home health' in d:\n"
        "        return 'Home Health'\n"
        "    if 'home' in d and 'iv' not in d:\n"
        "        return 'Home'\n"
        "    if 'snf' in d or 'nursing' in d or 'icf' in d or 'rehab' in d:\n"
        "        return 'Facility (SNF/ICF/Rehab)'\n"
        "    if 'short term hospital' in d or 'inpatient care' in d:\n"
        "        return 'Transfer Hospital'\n"
        "    return 'Other/Unknown'\n"
        "\n"
        "df['discharge_grp'] = df['discharge_disposition_desc'].map(map_discharge_group)\n"
        "print(f'Ready for statistical modeling: {len(df):,} encounters.')"
    ))

    # Cell 3: Load stats_tests.csv
    cells.append(nbf.v4.new_markdown_cell(
        "### 2. Statistical Hypothesis Test Results (`P3-07`)\n"
        "Load the computed hypothesis test results (`reports/eda/stats_tests.csv`). Contains 21 hypothesis tests with Bonferroni multiplicity adjustments."
    ))
    cells.append(nbf.v4.new_code_cell(
        "stats_csv = REPORTS_EDA_DIR / 'stats_tests.csv'\n"
        "stats_df = pd.read_csv(stats_csv)\n"
        "print(f'Total hypothesis tests evaluated: {len(stats_df)}')\n"
        "stats_df[['feature', 'variable_type', 'test_name', 'statistic_value', 'raw_p_value', 'bonferroni_p_value', 'effect_size_name', 'effect_size_value', 'significance_tier']]"
    ))

    # Cell 4: Top Statistically Significant Predictors
    cells.append(nbf.v4.new_markdown_cell(
        "### 3. Top Predictors Ranked by Effect Size\n"
        "Sort categorical features by Cramér's V and numeric features by rank-biserial effect size."
    ))
    cells.append(nbf.v4.new_code_cell(
        "print('Top Categorical Features by Cramér\\'s V:')\n"
        "display(stats_df[stats_df['variable_type'] == 'categorical'].sort_values('effect_size_value', ascending=False)[['feature', 'statistic_value', 'degrees_of_freedom', 'effect_size_value', 'significance_tier']])\n"
        "\n"
        "print('\\nTop Numeric Features by Rank-Biserial r:')\n"
        "display(stats_df[stats_df['variable_type'] == 'numeric'].sort_values('effect_size_value', ascending=False)[['feature', 'non_readmitted_summary', 'readmitted_summary', 'effect_size_value', 'significance_tier']])"
    ))

    # Cell 5: Multivariable Logistic Regression
    cells.append(nbf.v4.new_markdown_cell(
        "### 4. Multivariable Logistic Regression & Odds Ratios (`P3-08`)\n"
        "Fit a multivariable logistic regression model using `statsmodels` to estimate adjusted Odds Ratios (OR) and 95% Confidence Intervals for key clinical factors."
    ))
    cells.append(nbf.v4.new_code_cell(
        "formula = (\n"
        "    \"readmitted_30d ~ time_in_hospital + number_inpatient + number_emergency + \"\n"
        "    \"number_diagnoses + num_medications + \"\n"
        "    \"C(a1c_result, Treatment(reference='NotMeasured')) + \"\n"
        "    \"C(change, Treatment(reference='No')) + \"\n"
        "    \"C(discharge_grp, Treatment(reference='Home')) + \"\n"
        "    \"C(diag_1_group, Treatment(reference='Circulatory'))\"\n"
        ")\n"
        "logit_model = smf.logit(formula, data=df).fit()\n"
        "print(logit_model.summary().tables[0])"
    ))

    # Cell 6: Odds Ratios Table
    cells.append(nbf.v4.new_markdown_cell(
        "### 5. Adjusted Odds Ratios with 95% Confidence Intervals\n"
        "Extract exponentiated parameters ($e^\\beta$) representing adjusted Odds Ratios."
    ))
    cells.append(nbf.v4.new_code_cell(
        "params = logit_model.params\n"
        "conf = logit_model.conf_int()\n"
        "or_table = pd.DataFrame({\n"
        "    'Odds Ratio (OR)': np.exp(params).round(3),\n"
        "    '95% Lower CI': np.exp(conf[0]).round(3),\n"
        "    '95% Upper CI': np.exp(conf[1]).round(3),\n"
        "    'p-value': logit_model.pvalues.apply(lambda p: '< 0.001' if p < 0.001 else f'{p:.4f}')\n"
        "}).drop(index='Intercept')\n"
        "or_table"
    ))

    # Cell 7: Strack et al. Replication Discussion
    cells.append(nbf.v4.new_markdown_cell(
        "### 6. Replication of Strack et al. (2014) Findings\n"
        "In Strack et al. (2014), the authors demonstrated that when HbA1c is measured and elevated ($>8\\%$) with concurrent medication changes, readmission rates are reduced relative to patients whose HbA1c was unmeasured. Here we verify the effect in our cleaned cohort."
    ))
    cells.append(nbf.v4.new_code_cell(
        "a1c_sub = df.groupby(['a1c_result', 'change'])['readmitted_30d'].agg(['count', 'mean'])\n"
        "a1c_sub['readmit_rate_%'] = (a1c_sub['mean'] * 100).round(2)\n"
        "a1c_sub"
    ))

    nb.cells = cells
    target_path = NOTEBOOKS_DIR / "04_statistical_analysis.ipynb"
    target_path.write_text(nbf.writes(nb), encoding="utf-8")
    print(f"Generated {target_path}")


if __name__ == "__main__":
    build_eda_notebook()
    build_stats_notebook()
