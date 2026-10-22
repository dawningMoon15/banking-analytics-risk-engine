"""Unit tests for data_cleaner module."""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from banking_analytics.data_cleaner import (
    clean_dataset,
    generate_quality_report,
    save_processed_dataset,
)
from banking_analytics.utils.exceptions import DataIntegrityError, DataSufficiencyError


def test_duplicates_are_removed(sample_df: pd.DataFrame):
    """Test that exact duplicates and duplicate Application_IDs are removed."""
    df_with_dups = pd.concat([sample_df, sample_df.iloc[:5]], ignore_index=True)
    assert len(df_with_dups) == 205

    cleaned, report = clean_dataset(df_with_dups, min_row_threshold=50)
    assert len(cleaned) == 200
    assert report["duplicates_removed"] == 5


def test_credit_score_out_of_range_is_flagged(sample_df: pd.DataFrame):
    """Test that out-of-range credit scores are flagged in quality report."""
    sample_df.loc[0, "Credit_Score"] = 950
    report = generate_quality_report(sample_df)
    assert report["columns"]["Credit_Score"]["range_violations"] > 0
    assert any("Credit_Score" in w for w in report["warnings"])


def test_loan_approved_encoded_as_binary(sample_df: pd.DataFrame):
    """Test that Yes/No and Approved/Rejected strings in Loan_Approved get mapped to integer 0/1."""
    # Test Yes/No
    df_yes_no = sample_df.copy()
    df_yes_no["Loan_Approved"] = df_yes_no["Loan_Approved"].map({1: "Yes", 0: "No"})
    cleaned, _ = clean_dataset(df_yes_no, min_row_threshold=50)
    assert set(cleaned["Loan_Approved"].unique()).issubset({0, 1})
    assert cleaned["Loan_Approved"].dtype == int

    # Test Approved/Rejected (actual Kaggle dataset format)
    df_app_rej = sample_df.copy()
    df_app_rej["Loan_Approved"] = df_app_rej["Loan_Approved"].map({1: "Approved", 0: "Rejected"})
    cleaned_app, _ = clean_dataset(df_app_rej, min_row_threshold=50)
    assert set(cleaned_app["Loan_Approved"].unique()).issubset({0, 1})
    assert cleaned_app["Loan_Approved"].dtype == int


def test_missing_values_imputed(sample_df: pd.DataFrame):
    """Test that missing numeric and categorical columns are appropriately imputed."""
    sample_df.loc[0, "Annual_Income"] = np.nan
    sample_df.loc[1, "Employment_Status"] = np.nan

    cleaned, report = clean_dataset(sample_df, min_row_threshold=50)
    assert not cleaned["Annual_Income"].isna().any()
    assert not cleaned["Employment_Status"].isna().any()


def test_unemployed_job_experience_imputed_zero(sample_df: pd.DataFrame):
    """Test that unemployed applicants with missing job experience receive 0.0."""
    sample_df.loc[0, "Employment_Status"] = "Unemployed"
    sample_df.loc[0, "Job_Experience_Years"] = np.nan

    cleaned, _ = clean_dataset(sample_df, min_row_threshold=50)
    assert cleaned.loc[0, "Job_Experience_Years"] == 0.0


def test_data_sufficiency_error_raised():
    """Test that cleaning a dataset below minimum threshold raises DataSufficiencyError."""
    small_df = pd.DataFrame({
        "Application_ID": ["APP01", "APP02"],
        "Loan_Approved": [1, 0],
    })
    with pytest.raises(DataSufficiencyError):
        clean_dataset(small_df, min_row_threshold=100)


def test_save_processed_dataset(tmp_path: Path, sample_df: pd.DataFrame):
    """Test saving processed dataset and data quality report to disk."""
    csv_dest = tmp_path / "cleaned.csv"
    json_dest = tmp_path / "report.json"
    report = {"test": True}

    saved_csv, saved_json = save_processed_dataset(sample_df, str(csv_dest), report, str(json_dest))
    assert saved_csv.is_file()
    assert saved_json.is_file()
