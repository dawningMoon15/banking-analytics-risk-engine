"""Data loading and schema validation module for Banking Customer Analytics & Risk Engine."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from banking_analytics.utils.exceptions import DataIntegrityError, SchemaValidationError
from banking_analytics.utils.io_utils import compute_file_checksum, read_csv_safe
from banking_analytics.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_REQUIRED_COLUMNS = [
    "Application_ID",
    "Age",
    "Gender",
    "Marital_Status",
    "Education_Level",
    "Employment_Status",
    "Job_Experience_Years",
    "Annual_Income",
    "Monthly_Income",
    "Credit_Score",
    "Credit_History_Years",
    "Existing_Loans",
    "Late_Payments_Last_2_Years",
    "Loan_Amount",
    "Loan_Term_Months",
    "Loan_Purpose",
    "Interest_Rate",
    "Debt_To_Income_Ratio",
    "Savings_Balance",
    "Checking_Balance",
    "Total_Assets",
    "Total_Liabilities",
    "Monthly_Debt_Payment",
    "Property_Ownership",
    "Residential_Status",
    "Dependents",
    "Co_Applicant",
    "Collateral",
    "Application_Channel",
    "Region",
    "Bank_Account_Age_Years",
    "Previous_Loan_Status",
    "Risk_Score",
    "Default_Risk",
    "Approved_Amount",
    "Loan_Approved",
]


def validate_schema(
    df: pd.DataFrame,
    required_cols: Optional[List[str]] = None,
    target_column: str = "Loan_Approved",
) -> None:
    """Validates that a DataFrame contains all required columns and valid target integrity.

    Args:
        df: DataFrame to validate.
        required_cols: List of required column names. Defaults to standard 36 columns.
        target_column: Name of the target variable column.

    Raises:
        SchemaValidationError: If any required column is missing.
        DataIntegrityError: If the target column has missing/null values or df is empty.
    """
    if df.empty:
        raise DataIntegrityError(
            "Dataset is empty (0 rows).",
            module="data_loader.validate_schema",
            action="Provide a CSV file with valid records.",
        )

    cols_to_check = required_cols if required_cols is not None else DEFAULT_REQUIRED_COLUMNS
    missing = set(cols_to_check) - set(df.columns)
    if missing:
        raise SchemaValidationError(
            f"Missing required columns ({len(missing)}): {sorted(list(missing))}",
            module="data_loader.validate_schema",
            action="Verify dataset matches expected schema. Check data/raw/loan_approval_dataset.csv.",
        )

    if target_column in df.columns:
        null_target_count = df[target_column].isna().sum()
        if null_target_count > 0:
            raise DataIntegrityError(
                f"Target column '{target_column}' contains {null_target_count} null/missing values.",
                module="data_loader.validate_schema",
                action="Target column must have complete labels; remove or inspect unlabelled records.",
            )

    logger.info("Schema validation passed: %d rows, %d columns.", len(df), len(df.columns))


def log_metadata(df: pd.DataFrame, filepath: str) -> Dict[str, Any]:
    """Computes and logs metadata about the loaded dataset.

    Args:
        df: Loaded pandas DataFrame.
        filepath: Path to dataset source file.

    Returns:
        Dict[str, Any]: Summary metadata dictionary.
    """
    checksum = compute_file_checksum(filepath)
    metadata = {
        "filepath": filepath,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "checksum_md5": checksum,
        "columns": list(df.columns),
    }
    logger.info(
        "Loaded dataset from '%s': %d rows, %d columns, MD5: %s",
        filepath,
        metadata["row_count"],
        metadata["column_count"],
        checksum or "N/A",
    )
    return metadata


def load_dataset(
    filepath: str,
    required_cols: Optional[List[str]] = None,
    target_column: str = "Loan_Approved",
) -> pd.DataFrame:
    """Loads a raw CSV dataset, performs schema and target integrity validation, and logs metadata.

    Args:
        filepath: Path to the CSV file.
        required_cols: List of required columns. Defaults to standard 36 columns.
        target_column: Target column name to validate.

    Returns:
        pd.DataFrame: Validated DataFrame.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        SchemaValidationError: If required columns are missing.
        DataIntegrityError: If target column contains null values.
    """
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"Dataset file not found at: {filepath}")

    logger.info("Loading dataset from: %s", filepath)
    df = read_csv_safe(filepath)
    validate_schema(df, required_cols=required_cols, target_column=target_column)
    log_metadata(df, filepath)
    return df
