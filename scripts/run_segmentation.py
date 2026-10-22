#!/usr/bin/env python3
"""CLI script to run customer segmentation pipeline."""

import argparse
from pathlib import Path

from banking_analytics.segmentor import train_and_evaluate_segmentation
from banking_analytics.utils.config_loader import load_config
from banking_analytics.utils.io_utils import read_csv_safe
from banking_analytics.utils.logger import get_logger

logger = get_logger("banking_analytics.run_segmentation")


def main():
    parser = argparse.ArgumentParser(description="Run Segmentation Pipeline")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    processed_path = config["data"]["processed_path"]

    if not Path(processed_path).is_file():
        logger.error("Processed data file '%s' not found. Run run_pipeline.py first.", processed_path)
        return

    df = read_csv_safe(processed_path)
    train_and_evaluate_segmentation(df, config)
    logger.info("Segmentation pipeline executed successfully.")


if __name__ == "__main__":
    main()
