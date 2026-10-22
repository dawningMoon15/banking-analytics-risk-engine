"""Unit tests for evaluator module."""

import numpy as np
import pandas as pd
import pytest

from banking_analytics.classifier import build_classification_pipeline
from banking_analytics.evaluator import compare_models, cross_reference_clusters
from banking_analytics.feature_engineer import build_preprocessor, select_features, split_data


def test_compare_models():
    """Test generating model comparison table."""
    baseline = {"accuracy": 0.55, "f1": 0.60}
    lr_metrics = {
        "roc_auc": 0.85,
        "brier_score": 0.15,
        "default_threshold_0.5": {
            "accuracy": 0.80,
            "precision": 0.82,
            "recall": 0.78,
            "f1": 0.80,
        },
        "optimal_threshold": {
            "accuracy": 0.82,
            "precision": 0.81,
            "recall": 0.86,
            "f1": 0.83,
        },
    }

    df_cmp = compare_models(baseline, lr_metrics)
    assert isinstance(df_cmp, pd.DataFrame)
    assert "Metric" in df_cmp.columns
    assert "Dummy Baseline" in df_cmp.columns
    assert "Logistic Regression (Optimal Thresh)" in df_cmp.columns
    assert len(df_cmp) >= 6


def test_cross_reference_clusters(sample_df: pd.DataFrame):
    """Test cross-referencing predicted approval probabilities with cluster labels."""
    X, y, num_cols, cat_cols, bin_cols = select_features(sample_df)
    preprocessor = build_preprocessor(num_cols, cat_cols, bin_cols)
    pipeline = build_classification_pipeline(preprocessor)
    pipeline.fit(X, y)

    cluster_labels = pd.Series(np.random.choice([0, 1, 2], size=len(sample_df)))
    cross_tab = cross_reference_clusters(sample_df, pipeline, cluster_labels)

    assert isinstance(cross_tab, pd.DataFrame)
    assert len(cross_tab) == 3
    assert "cluster" in cross_tab.columns
    assert "applicant_count" in cross_tab.columns
    assert "actual_approval_rate" in cross_tab.columns
    assert "mean_predicted_prob" in cross_tab.columns
    assert sum(cross_tab["applicant_count"]) == len(sample_df)
