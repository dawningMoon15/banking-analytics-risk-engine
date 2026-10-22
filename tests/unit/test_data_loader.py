"""Unit tests for data_loader module."""

from pathlib import Path
import pandas as pd
import pytest

from banking_analytics.data_loader import load_dataset, validate_schema
from banking_analytics.utils.exceptions import DataIntegrityError, SchemaValidationError


def test_load_dataset_returns_dataframe(tmp_path: Path, sample_df: pd.DataFrame):
    """Test loading a valid CSV dataset returns DataFrame with expected rows."""
    csv_path = tmp_path / "valid.csv"
    sample_df.to_csv(csv_path, index=False)

    df = load_dataset(str(csv_path))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 200
    assert len(df.columns) == 36


def test_load_dataset_raises_on_missing_column(tmp_path: Path, sample_df: pd.DataFrame):
    """Test loading a CSV missing a required column raises SchemaValidationError."""
    bad_df = sample_df.drop(columns=["Credit_Score"])
    csv_path = tmp_path / "missing_col.csv"
    bad_df.to_csv(csv_path, index=False)

    with pytest.raises(SchemaValidationError) as exc_info:
        load_dataset(str(csv_path))
    assert "Credit_Score" in str(exc_info.value)


def test_load_dataset_raises_on_null_target(tmp_path: Path, sample_df: pd.DataFrame):
    """Test loading a CSV with missing target values raises DataIntegrityError."""
    sample_df.loc[0, "Loan_Approved"] = None
    csv_path = tmp_path / "null_target.csv"
    sample_df.to_csv(csv_path, index=False)

    with pytest.raises(DataIntegrityError) as exc_info:
        load_dataset(str(csv_path))
    assert "Loan_Approved" in str(exc_info.value)


def test_load_dataset_raises_on_missing_file():
    """Test loading a non-existent path raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_dataset("data/non_existent_file.csv")


def test_validate_schema_on_empty_df():
    """Test that validating an empty DataFrame raises DataIntegrityError."""
    empty_df = pd.DataFrame()
    with pytest.raises(DataIntegrityError):
        validate_schema(empty_df)
