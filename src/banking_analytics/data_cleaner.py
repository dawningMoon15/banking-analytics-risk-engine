"""Data cleaning, transformation, imputation, and data quality validation module."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from banking_analytics.utils.exceptions import (
    DataIntegrityError,
    DataSufficiencyError,
)
from banking_analytics.utils.io_utils import (
    compute_file_checksum,
    write_csv_safe,
    write_json_safe,
)
from banking_analytics.utils.logger import get_logger

logger = get_logger(__name__)

NUMERIC_COLUMNS = [
    "Age",
    "Job_Experience_Years",
    "Annual_Income",
    "Monthly_Income",
    "Credit_Score",
    "Credit_History_Years",
    "Existing_Loans",
    "Late_Payments_Last_2_Years",
    "Loan_Amount",
    "Loan_Term_Months",
    "Interest_Rate",
    "Debt_To_Income_Ratio",
    "Savings_Balance",
    "Checking_Balance",
    "Total_Assets",
    "Total_Liabilities",
    "Monthly_Debt_Payment",
    "Dependents",
    "Bank_Account_Age_Years",
    "Risk_Score",
    "Approved_Amount",
]

BINARY_COLUMNS = ["Loan_Approved", "Co_Applicant", "Collateral"]

CATEGORICAL_COLUMNS = [
    "Gender",
    "Marital_Status",
    "Education_Level",
    "Employment_Status",
    "Loan_Purpose",
    "Property_Ownership",
    "Residential_Status",
    "Application_Channel",
    "Region",
    "Previous_Loan_Status",
    "Default_Risk",
]


def _map_binary_value(val: Any) -> Optional[int]:
    """Normalizes binary values (0/1, True/False, 'Yes'/'No', '1'/'0') to 0 or 1."""
    if pd.isna(val):
        return None
    if isinstance(val, (int, np.integer)):
        return 1 if val != 0 else 0
    if isinstance(val, (float, np.floating)):
        return 1 if val != 0.0 else 0
    if isinstance(val, bool):
        return 1 if val else 0
    str_val = str(val).strip().lower()
    if str_val in ["1", "yes", "true", "y", "approved", "t"]:
        return 1
    elif str_val in ["0", "no", "false", "n", "rejected", "f"]:
        return 0
    return None


def generate_quality_report(
    df: pd.DataFrame,
    raw_path: Optional[str] = None,
    raw_row_count: Optional[int] = None,
    duplicates_removed: int = 0,
) -> Dict[str, Any]:
    """Generates a comprehensive data quality report per TRD Section 5.7.

    Args:
        df: DataFrame being assessed.
        raw_path: Optional path to raw dataset.
        raw_row_count: Total rows before deduplication.
        duplicates_removed: Number of duplicate rows removed.

    Returns:
        Dict[str, Any]: Structured data quality report dictionary.
    """
    total_rows = len(df)
    report: Dict[str, Any] = {
        "run_timestamp": datetime.now().isoformat(),
        "dataset_path": raw_path or "N/A",
        "checksum_md5": compute_file_checksum(raw_path) if raw_path and Path(raw_path).exists() else "N/A",
        "row_count_raw": raw_row_count if raw_row_count is not None else total_rows + duplicates_removed,
        "row_count_after_dedup": total_rows,
        "duplicates_removed": duplicates_removed,
        "columns": {},
        "critical_errors": [],
        "warnings": [],
    }

    # Inspect columns
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        null_pct = round(float(null_count / total_rows * 100.0), 2) if total_rows > 0 else 0.0

        col_info: Dict[str, Any] = {
            "dtype": str(df[col].dtype),
            "null_count": null_count,
            "null_pct": null_pct,
            "outliers_flagged": 0,
            "range_violations": 0,
            "outliers_action": "none",
        }

        # Check domain range violations
        if col == "Credit_Score" and pd.api.types.is_numeric_dtype(df[col]):
            violations = int(((df[col] < 300) | (df[col] > 850)).sum())
            col_info["range_violations"] = violations
            if violations > 0:
                report["warnings"].append(f"Credit_Score contains {violations} records outside 300-850 range.")

        elif col == "Age" and pd.api.types.is_numeric_dtype(df[col]):
            violations = int(((df[col] < 18) | (df[col] > 100)).sum())
            col_info["range_violations"] = violations
            if violations > 0:
                report["warnings"].append(f"Age contains {violations} records outside 18-100 range.")

        # Outlier count via IQR for continuous numerical features
        if col in ["Annual_Income", "Monthly_Income", "Loan_Amount", "Debt_To_Income_Ratio"] and pd.api.types.is_numeric_dtype(df[col]):
            valid_vals = df[col].dropna()
            if len(valid_vals) > 0:
                q25, q75 = np.percentile(valid_vals, 25), np.percentile(valid_vals, 75)
                iqr = q75 - q25
                outliers = int(((valid_vals < (q25 - 1.5 * iqr)) | (valid_vals > (q75 + 1.5 * iqr))).sum())
                col_info["outliers_flagged"] = outliers

        report["columns"][col] = col_info

    # Check correlation between Monthly_Income and Annual_Income for redundancy warning
    if "Monthly_Income" in df.columns and "Annual_Income" in df.columns:
        if pd.api.types.is_numeric_dtype(df["Monthly_Income"]) and pd.api.types.is_numeric_dtype(df["Annual_Income"]):
            corr = df[["Monthly_Income", "Annual_Income"]].dropna().corr().iloc[0, 1]
            if not np.isnan(corr) and corr > 0.95:
                report["warnings"].append(
                    f"Monthly_Income and Annual_Income have high correlation ({corr:.4f}) — potential redundancy."
                )

    return report


def clean_dataset(
    df: pd.DataFrame,
    min_row_threshold: int = 100,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Cleans raw dataset according to TRD Section 5.3 - 5.6 rules.

    Performs:
    1. Duplicate row removal & Application_ID duplicate resolution
    2. Target integrity verification (raises DataIntegrityError on missing targets)
    3. Type conversions and binary normalization (Loan_Approved, Co_Applicant, Collateral)
    4. Hard-range validation on Age (18-100) and Credit_Score (300-850)
    5. Domain-specific missing value imputation
    6. Minimum row count validation

    Args:
        df: Raw input DataFrame.
        min_row_threshold: Minimum acceptable rows post-cleaning (default 100).

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: Cleaned DataFrame and quality report dictionary.

    Raises:
        DataIntegrityError: If target column contains nulls or Application_ID is corrupted.
        DataSufficiencyError: If resulting rows < min_row_threshold.
    """
    raw_count = len(df)
    clean_df = df.copy()

    logger.info("Starting dataset cleaning. Input shape: (%d, %d)", len(clean_df), len(clean_df.columns))

    # 1. Deduplication
    exact_dups = int(clean_df.duplicated().sum())
    if exact_dups > 0:
        logger.info("Removing %d exact row duplicate(s).", exact_dups)
        clean_df = clean_df.drop_duplicates()

    if "Application_ID" in clean_df.columns:
        if clean_df["Application_ID"].isna().sum() > 0:
            raise DataIntegrityError(
                "Application_ID contains null values.",
                module="data_cleaner",
                action="Clean raw data to ensure Application_ID is populated.",
            )
        app_id_dups = int(clean_df.duplicated(subset=["Application_ID"]).sum())
        if app_id_dups > 0:
            logger.warning("Found %d duplicate Application_ID(s). Keeping first occurrence.", app_id_dups)
            clean_df = clean_df.drop_duplicates(subset=["Application_ID"], keep="first")

    total_dups_removed = raw_count - len(clean_df)

    # 2. Binary column normalization
    for col in BINARY_COLUMNS:
        if col in clean_df.columns:
            clean_df[col] = clean_df[col].apply(_map_binary_value)

    # Verify target variable integrity
    if "Loan_Approved" in clean_df.columns:
        if clean_df["Loan_Approved"].isna().sum() > 0:
            raise DataIntegrityError(
                "Target column 'Loan_Approved' contains missing or unmapped values.",
                module="data_cleaner",
                action="All rows must have a valid binary target label (0 or 1).",
            )
        clean_df["Loan_Approved"] = clean_df["Loan_Approved"].astype(int)

    # 3. Numeric type conversion
    for col in NUMERIC_COLUMNS:
        if col in clean_df.columns:
            clean_df[col] = pd.to_numeric(clean_df[col], errors="coerce")

    # 4. Domain boundary checks & filtering
    if "Age" in clean_df.columns:
        clean_df = clean_df[(clean_df["Age"].isna()) | ((clean_df["Age"] >= 18) & (clean_df["Age"] <= 100))]

    if "Credit_Score" in clean_df.columns:
        clean_df = clean_df[
            (clean_df["Credit_Score"].isna()) | ((clean_df["Credit_Score"] >= 300) & (clean_df["Credit_Score"] <= 850))
        ]

    # 5. Missing value imputation
    # Strategy: Job_Experience_Years: 0 if unemployed; median otherwise
    if "Job_Experience_Years" in clean_df.columns and "Employment_Status" in clean_df.columns:
        unemployed_mask = clean_df["Employment_Status"].astype(str).str.lower() == "unemployed"
        clean_df.loc[unemployed_mask & clean_df["Job_Experience_Years"].isna(), "Job_Experience_Years"] = 0.0

    # Numeric columns: Median imputation
    for col in NUMERIC_COLUMNS:
        if col in clean_df.columns and clean_df[col].isna().sum() > 0:
            median_val = clean_df[col].median()
            if pd.notna(median_val):
                clean_df[col] = clean_df[col].fillna(median_val)

    # Categorical columns: Mode imputation for low-null, 'Unknown' for higher
    for col in CATEGORICAL_COLUMNS:
        if col in clean_df.columns and clean_df[col].isna().sum() > 0:
            null_pct = clean_df[col].isna().mean()
            if null_pct < 0.05:
                mode_vals = clean_df[col].mode()
                fill_val = mode_vals.iloc[0] if len(mode_vals) > 0 else "Unknown"
                clean_df[col] = clean_df[col].fillna(fill_val)
            else:
                clean_df[col] = clean_df[col].fillna("Unknown")

    # Binary non-target columns: mode imputation if any nulls remain
    for col in ["Co_Applicant", "Collateral"]:
        if col in clean_df.columns and clean_df[col].isna().sum() > 0:
            clean_df[col] = clean_df[col].fillna(0).astype(int)

    # 6. Minimum sufficiency check
    if len(clean_df) < min_row_threshold:
        raise DataSufficiencyError(
            f"Cleaned dataset has {len(clean_df)} rows, which is below the minimum threshold of {min_row_threshold}.",
            module="data_cleaner",
            action="Check data filters and input dataset row counts.",
        )

    # Generate quality report
    report = generate_quality_report(
        clean_df,
        raw_row_count=raw_count,
        duplicates_removed=total_dups_removed,
    )

    logger.info("Dataset cleaning complete. Clean shape: (%d, %d)", len(clean_df), len(clean_df.columns))
    return clean_df, report


def save_processed_dataset(
    df: pd.DataFrame,
    processed_path: str,
    report: Dict[str, Any],
    reports_path: str,
) -> Tuple[Path, Path]:
    """Persists cleaned dataset CSV and data quality JSON report.

    Args:
        df: Cleaned pandas DataFrame.
        processed_path: Target CSV destination.
        report: Quality report dictionary.
        reports_path: Target JSON report destination.

    Returns:
        Tuple[Path, Path]: Paths to written CSV and JSON report.
    """
    csv_path = write_csv_safe(df, processed_path, index=False)
    json_path = write_json_safe(report, reports_path, indent=2)
    logger.info("Saved cleaned dataset to: %s", csv_path)
    logger.info("Saved data quality report to: %s", json_path)
    return csv_path, json_path
