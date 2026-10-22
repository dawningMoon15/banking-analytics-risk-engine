"""Unit tests for classifier module."""

import numpy as np
import pandas as pd
import pytest

from banking_analytics.classifier import (
    build_classification_pipeline,
    evaluate_classifier,
    extract_coefficients,
    find_optimal_threshold,
)
from banking_analytics.feature_engineer import build_preprocessor, select_features, split_data


def test_classifier_fit_and_predict(sample_df: pd.DataFrame):
    """Test training and predicting with the Logistic Regression pipeline."""
    X, y, num_cols, cat_cols, bin_cols = select_features(sample_df)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(X, y)

    preprocessor = build_preprocessor(num_cols, cat_cols, bin_cols)
    pipeline = build_classification_pipeline(preprocessor)
    pipeline.fit(X_train, y_train)

    probs = pipeline.predict_proba(X_test)
    assert probs.shape == (len(X_test), 2)
    assert np.all((probs >= 0.0) & (probs <= 1.0))


def test_find_optimal_threshold(sample_df: pd.DataFrame):
    """Test threshold selection on validation data returns valid float in [0.1, 0.9]."""
    X, y, num_cols, cat_cols, bin_cols = select_features(sample_df)
    X_train, X_val, _, y_train, y_val, _ = split_data(X, y)

    preprocessor = build_preprocessor(num_cols, cat_cols, bin_cols)
    pipeline = build_classification_pipeline(preprocessor)
    pipeline.fit(X_train, y_train)

    thresh, f1 = find_optimal_threshold(pipeline, X_val, y_val)
    assert 0.1 <= thresh <= 0.9
    assert 0.0 <= f1 <= 1.0


def test_evaluate_classifier(sample_df: pd.DataFrame):
    """Test computation of evaluation metrics on test data."""
    X, y, num_cols, cat_cols, bin_cols = select_features(sample_df)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(X, y)

    preprocessor = build_preprocessor(num_cols, cat_cols, bin_cols)
    pipeline = build_classification_pipeline(preprocessor)
    pipeline.fit(X_train, y_train)

    metrics = evaluate_classifier(pipeline, X_test, y_test, threshold=0.5)
    assert "roc_auc" in metrics
    assert "pr_auc" in metrics
    assert "brier_score" in metrics
    assert 0.0 <= metrics["roc_auc"] <= 1.0
    assert 0.0 <= metrics["brier_score"] <= 1.0


def test_extract_coefficients(sample_df: pd.DataFrame):
    """Test coefficient extraction produces a DataFrame with odds ratios."""
    X, y, num_cols, cat_cols, bin_cols = select_features(sample_df)
    X_train, _, _, y_train, _, _ = split_data(X, y)

    preprocessor = build_preprocessor(num_cols, cat_cols, bin_cols)
    pipeline = build_classification_pipeline(preprocessor)
    pipeline.fit(X_train, y_train)

    coef_df = extract_coefficients(pipeline)
    assert isinstance(coef_df, pd.DataFrame)
    assert "feature" in coef_df.columns
    assert "coefficient" in coef_df.columns
    assert "odds_ratio" in coef_df.columns
    assert len(coef_df) > 0
