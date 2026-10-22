# Banking Customer Analytics & Risk Engine

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An end-to-end banking analytics and machine-learning portfolio project demonstrating practical skills across data engineering, SQL analytics, statistical analysis, default risk classification, customer segmentation, and automated reporting.

---

## 1. Project Overview

- **Dataset**: 30,000 retail banking loan records ([Kaggle: Loan Approval Dataset 2026](https://www.kaggle.com/datasets/mmumairkhattak/loan-approval-dataset-2026-credit-risk-and-bank-a))
- **Classification Engine**: Scikit-Learn Logistic Regression pipeline with strict leakage prevention to predict default approval risk (`Loan_Approved`)
- **Customer Segmentation**: Unsupervised K-Means clustering with silhouette and inertia analysis to identify distinct borrower risk personas
- **Relational Analytics**: Analytical SQL queries, CTEs, and views executing on DuckDB (zero-friction default) and PostgreSQL
- **Architecture**: Modular Python package with automated pipeline orchestration and full `pytest` suite

---

## 2. Repository Structure

```
banking-analytics/
├── config/
│   └── config.yaml                   # Central pipeline and modeling configuration
├── data/
│   ├── raw/                          # Raw dataset (gitignored)
│   ├── processed/                    # Versioned, cleaned dataset
│   └── reports/                      # Data quality validation report (JSON)
├── notebooks/                        # Exploratory Data Analysis & experiments
├── src/
│   └── banking_analytics/            # Core package
│       ├── data_loader.py            # CSV ingestion & schema validation
│       ├── data_cleaner.py           # Cleaning, imputation, outlier handling
│       ├── db_loader.py              # DuckDB / PostgreSQL interface
│       ├── eda.py                    # Statistical tests & bivariate analysis
│       ├── feature_engineer.py       # Scikit-learn feature pipeline
│       ├── classifier.py             # Logistic Regression & evaluation
│       ├── segmentor.py              # K-Means clustering & profiling
│       ├── visualizer.py             # Publication-quality charting
│       ├── reporter.py               # Automated Markdown insight generator
│       └── utils/                    # Config, logging, exceptions, file I/O
├── sql/
│   ├── schema/create_tables.sql      # Database DDL & indexes
│   └── queries/                      # Analytical SQL queries (q01-q06) & views
├── models/                           # Model artifacts & metadata
├── reports/
│   ├── figures/                      # High-resolution saved plots
│   └── model_evaluation/            # Classification & segmentation reports
├── scripts/
│   └── run_pipeline.py               # Orchestrator CLI entry point
└── tests/                            # Unit and integration pytest suite
```

---

## 3. Quickstart & Installation

### Prerequisites
- Python 3.11+
- Virtual environment (venv or conda)

### Setup
```bash
# Clone and navigate to repository
cd /Users/navya/Banking_Analytics

# Install package in editable mode with development dependencies
pip install -e .
pip install -r requirements-dev.txt
```

### Acquiring the Dataset
1. Download `loan_approval_dataset.csv` from [Kaggle](https://www.kaggle.com/datasets/mmumairkhattak/loan-approval-dataset-2026-credit-risk-and-bank-a).
2. Place the file at:
   ```
   data/raw/loan_approval_dataset.csv
   ```

*(Note: To verify or test the entire pipeline end-to-end without waiting for a manual Kaggle download, run with `--dry-run` to use synthetic validation data).*

---

## 4. Running the Pipeline

### Dry Run (Validates pipeline without full dataset):
```bash
python scripts/run_pipeline.py --dry-run
```

### Full End-to-End Execution:
```bash
python scripts/run_pipeline.py
```

### Running the Test Suite:
```bash
pytest tests/ -v
```
