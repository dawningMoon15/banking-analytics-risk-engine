#!/usr/bin/env python3
"""CLI script to execute EDA, SQL queries, and generate visual artifacts."""

import argparse
import sys
from pathlib import Path

from banking_analytics.data_cleaner import clean_dataset
from banking_analytics.data_loader import load_dataset
from banking_analytics.db_loader import DatabaseManager
from banking_analytics.eda import run_full_eda
from banking_analytics.utils.config_loader import load_config
from banking_analytics.utils.io_utils import read_csv_safe
from banking_analytics.utils.logger import get_logger

logger = get_logger("banking_analytics.run_eda")


def main():
    parser = argparse.ArgumentParser(description="Run EDA and SQL Analytics")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    processed_path = config["data"]["processed_path"]
    figures_dir = config["visualization"]["output_dir"]

    if not Path(processed_path).is_file():
        logger.info("Processed data not found at %s. Loading raw data...", processed_path)
        raw_path = config["data"]["raw_path"]
        df_raw = load_dataset(raw_path)
        df, _ = clean_dataset(df_raw)
    else:
        logger.info("Loading processed data from: %s", processed_path)
        df = read_csv_safe(processed_path)

    # 1. Database and SQL analytics
    logger.info("=== Executing Database Loading & SQL Analytics ===")
    db = DatabaseManager(config)
    db.init_schema("sql/schema/create_tables.sql")
    db.load_data(df)
    db.create_views("sql/queries/views")
    query_results = db.execute_all_queries("sql/queries")

    for q_name, q_df in query_results.items():
        logger.info("Query '%s' returned %d rows.", q_name, len(q_df))

    # 2. EDA and Statistical Analysis
    logger.info("=== Executing Statistical Tests & EDA Visualizations ===")
    run_full_eda(df, figures_dir=figures_dir, report_output_path="reports/eda_summary.md")

    db.close()
    logger.info("EDA and SQL analytics completed successfully.")


if __name__ == "__main__":
    main()
