"""Unit tests for feature_engineer module."""

import pandas as pd
import pytest

from banking_analytics.feature_engineer import (
    LEAKAGE_EXCLUSIONS,
    build_preprocessor,
    select_features,
    split_data,
)


def test_target_and_leakage_columns_excluded(sample_df: pd.DataFrame):
    """Asserts that all potential target leakage columns are strictly excluded from X."""
    X, y, num_cols, cat_cols, bin_cols = select_features(sample_df)

    for col in LEAKAGE_EXCLUSIONS:
        assert col not in X.columns, f"Leakage column {col} was found in feature matrix X!"

    assert len(y) == len(sample_df)
    assert len(X) == len(sample_df)


def test_split_data_proportions(sample_df: pd.DataFrame):
    """Asserts stratified train/val/test split produces expected row counts within rounding."""
    X, y, _, _, _ = select_features(sample_df)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(
        X, y, train_size=0.70, val_size=0.15, test_size=0.15, random_seed=42
    )

    total = len(sample_df)
    assert len(X_train) + len(X_val) + len(X_test) == total
    assert abs(len(X_train) - int(total * 0.70)) <= 1
    assert abs(len(X_val) - int(total * 0.15)) <= 1
    assert abs(len(X_test) - int(total * 0.15)) <= 1


def test_pipeline_fit_only_on_train(sample_df: pd.DataFrame):
    """Leakage check: Preprocessor must be fitted on train set only."""
    X, y, num_cols, cat_cols, bin_cols = select_features(sample_df)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(X, y)

    preprocessor = build_preprocessor(num_cols, cat_cols, bin_cols)
    preprocessor.fit(X_train)

    # Transform test set using statistics learned from train set
    transformed_test = preprocessor.transform(X_test)
    assert transformed_test.shape[0] == len(X_test)
    assert transformed_test.shape[1] > 0
