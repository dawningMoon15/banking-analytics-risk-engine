#!/usr/bin/env python3
"""End-to-end pipeline orchestrator for Banking Customer Analytics & Risk Engine."""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd

from banking_analytics.classifier import train_and_evaluate_classification
from banking_analytics.data_cleaner import clean_dataset, save_processed_dataset
from banking_analytics.data_loader import DEFAULT_REQUIRED_COLUMNS, load_dataset
from banking_analytics.db_loader import DatabaseManager
from banking_analytics.eda import run_full_eda
from banking_analytics.evaluator import cross_reference_clusters
from banking_analytics.reporter import generate_final_report
from banking_analytics.segmentor import train_and_evaluate_segmentation
from banking_analytics.utils.config_loader import load_config
from banking_analytics.utils.io_utils import read_json_safe, write_csv_safe
from banking_analytics.utils.logger import get_logger

logger = get_logger("banking_analytics.pipeline")


def generate_synthetic_raw_dataset(dest_path: str, n_rows: int = 500, random_seed: int = 42) -> Path:
    """Generates a realistic synthetic raw dataset for dry-run validation."""
    np.random.seed(random_seed)
    n = n_rows

    annual_income = np.random.uniform(25000, 200000, n).round(2)
    monthly_income = (annual_income / 12.0).round(2)
    loan_amount = np.random.uniform(5000, 80000, n).round(2)
    credit_score = np.random.randint(400, 850, n)
    dti = np.random.uniform(10.0, 70.0, n).round(2)

    logit = -3.0 + (credit_score - 600) * 0.015 - (dti - 35) * 0.03
    prob = 1.0 / (1.0 + np.exp(-logit))
    loan_approved = (np.random.uniform(0, 1, n) < prob).astype(int)
    approved_amount = np.where(loan_approved == 1, loan_amount, 0.0)

    data = {
        "Application_ID": [f"SYNTH_{i:06d}" for i in range(n)],
        "Age": np.random.randint(21, 68, n),
        "Gender": np.random.choice(["Male", "Female", "Non-Binary"], n, p=[0.49, 0.49, 0.02]),
        "Marital_Status": np.random.choice(["Single", "Married", "Divorced"], n),
        "Education_Level": np.random.choice(["High School", "Bachelor", "Master", "PhD"], n, p=[0.3, 0.45, 0.2, 0.05]),
        "Employment_Status": np.random.choice(["Employed", "Self-Employed", "Unemployed"], n, p=[0.75, 0.18, 0.07]),
        "Job_Experience_Years": np.random.uniform(0.5, 30.0, n).round(1),
        "Annual_Income": annual_income,
        "Monthly_Income": monthly_income,
        "Credit_Score": credit_score,
        "Credit_History_Years": np.random.uniform(1.0, 25.0, n).round(1),
        "Existing_Loans": np.random.randint(0, 5, n),
        "Late_Payments_Last_2_Years": np.random.choice([0, 1, 2, 3, 4], n, p=[0.65, 0.2, 0.1, 0.03, 0.02]),
        "Loan_Amount": loan_amount,
        "Loan_Term_Months": np.random.choice([12, 24, 36, 48, 60], n),
        "Loan_Purpose": np.random.choice(["Home", "Auto", "Personal", "Education", "Debt Consolidation"], n),
        "Interest_Rate": np.random.uniform(5.5, 24.0, n).round(2),
        "Debt_To_Income_Ratio": dti,
        "Savings_Balance": np.random.uniform(500, 45000, n).round(2),
        "Checking_Balance": np.random.uniform(200, 15000, n).round(2),
        "Total_Assets": np.random.uniform(10000, 400000, n).round(2),
        "Total_Liabilities": np.random.uniform(2000, 180000, n).round(2),
        "Monthly_Debt_Payment": np.random.uniform(100, 3500, n).round(2),
        "Property_Ownership": np.random.choice(["Own", "Rent", "Mortgage"], n),
        "Residential_Status": np.random.choice(["Permanent", "Temporary", "Living with Parents"], n),
        "Dependents": np.random.randint(0, 5, n),
        "Co_Applicant": np.random.choice([0, 1], n, p=[0.7, 0.3]),
        "Collateral": np.random.choice([0, 1], n, p=[0.65, 0.35]),
        "Application_Channel": np.random.choice(["Online", "In-Person", "Mobile App"], n),
        "Region": np.random.choice(["North", "South", "East", "West", "Central"], n),
        "Bank_Account_Age_Years": np.random.uniform(1.0, 22.0, n).round(1),
        "Previous_Loan_Status": np.random.choice(["Fully Paid", "Current", "Defaulted", "No Previous Loan"], n),
        "Risk_Score": (100 - (credit_score - 300) / 5.5 + np.random.normal(0, 5, n)).clip(5, 95).round(2),
        "Default_Risk": np.where(credit_score < 580, "High", np.where(credit_score < 720, "Medium", "Low")),
        "Approved_Amount": approved_amount,
        "Loan_Approved": loan_approved,
    }
    df = pd.DataFrame(data)
    out_path = write_csv_safe(df, dest_path, index=False)
    logger.info("Generated %d synthetic raw records at: %s", n, out_path)
    return out_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Banking Customer Analytics & Risk Engine Pipeline Runner"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to YAML configuration file (default: config/config.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline in dry-run verification mode (uses synthetic data if raw dataset is absent)",
    )
    parser.add_argument(
        "--stage",
        type=str,
        default="all",
        choices=["data", "db", "eda", "classification", "segmentation", "report", "all"],
        help="Pipeline stage to execute (default: all)",
    )
    return parser.parse_args()


def run_pipeline(config_path: str = "config/config.yaml", dry_run: bool = False, stage: str = "all") -> None:
    config = load_config(config_path)
    logger.info("Starting pipeline execution for project: %s (v%s)", config["project"]["name"], config["project"]["version"])

    raw_path = config["data"]["raw_path"]
    processed_path = config["data"]["processed_path"]
    reports_path = config["data"]["reports_path"]
    figures_dir = config["visualization"]["output_dir"]

    # Check raw data existence
    if not Path(raw_path).is_file():
        if dry_run:
            logger.info("Raw dataset '%s' not found. Dry-run mode enabled: generating synthetic dataset.", raw_path)
            generate_synthetic_raw_dataset(raw_path, n_rows=500, random_seed=config["ml"]["random_seed"])
        else:
            logger.error("Raw dataset not found at '%s'. Download dataset or use --dry-run.", raw_path)
            sys.exit(1)

    # 1. Data Stage
    logger.info("=== Phase 1: Data Validation & Cleaning ===")
    raw_df = load_dataset(raw_path)
    clean_df, quality_report = clean_dataset(raw_df, min_row_threshold=50 if dry_run else 100)
    save_processed_dataset(clean_df, processed_path, quality_report, reports_path)

    if stage == "data":
        logger.info("Completed requested stage 'data'. Exiting.")
        return

    # 2. Database & SQL Stage
    logger.info("=== Phase 2: Relational Schema & Analytical Queries ===")
    db = DatabaseManager(config)
    db.init_schema("sql/schema/create_tables.sql")
    db.load_data(clean_df)
    db.create_views("sql/queries/views")
    query_results = db.execute_all_queries("sql/queries")
    db.close()

    if stage == "db":
        logger.info("Completed requested stage 'db'. Exiting.")
        return

    # 3. EDA & Statistical Testing
    logger.info("=== Phase 3: Exploratory Data Analysis & Statistical Tests ===")
    eda_answers = run_full_eda(clean_df, figures_dir=figures_dir, report_output_path="reports/eda_summary.md")

    if stage == "eda":
        logger.info("Completed requested stage 'eda'. Exiting.")
        return

    # 4. Classification Pipeline
    logger.info("=== Phase 4: Default Risk Classification Modeling ===")
    clf_results = train_and_evaluate_classification(clean_df, config)

    if stage == "classification":
        logger.info("Completed requested stage 'classification'. Exiting.")
        return

    # 5. Customer Segmentation Pipeline
    logger.info("=== Phase 5: Customer Segmentation & Profiling ===")
    seg_results = train_and_evaluate_segmentation(clean_df, config)

    if stage == "segmentation":
        logger.info("Completed requested stage 'segmentation'. Exiting.")
        return

    # 6. Cross-Referenced Evaluation & Reporting
    logger.info("=== Phase 6: Cross-Referenced Evaluation & Final Report Synthesis ===")
    cross_tab = cross_reference_clusters(
        clean_df,
        clf_results["pipeline"],
        seg_results["labels"],
        target_column=config["data"].get("target_column", "Loan_Approved"),
    )

    generate_final_report(
        eda_results=eda_answers,
        lr_metadata=clf_results["metadata"],
        kmeans_metadata=seg_results["metadata"],
        cross_tab_df=cross_tab,
        output_path="reports/final_report.md",
    )

    logger.info("================================================================")
    logger.info("ALL PIPELINE PHASES COMPLETED SUCCESSFULLY!")
    logger.info("Processed Dataset: %s", processed_path)
    logger.info("Quality Report:    %s", reports_path)
    logger.info("EDA Summary:       reports/eda_summary.md")
    logger.info("Classif. Report:   reports/model_evaluation/classification_report.md")
    logger.info("Segment. Report:   reports/model_evaluation/cluster_profiles.md")
    logger.info("Final Report:      reports/final_report.md")
    logger.info("Saved Figures:     %s/", figures_dir)
    logger.info("Saved Models:      models/")
    logger.info("================================================================")


def main():
    args = parse_args()
    try:
        run_pipeline(config_path=args.config, dry_run=args.dry_run, stage=args.stage)
    except Exception as exc:
        logger.exception("Pipeline failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
