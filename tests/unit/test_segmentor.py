"""Unit tests for segmentor module."""

import numpy as np
import pandas as pd
import pytest

from banking_analytics.segmentor import (
    build_cluster_profiles,
    build_clustering_features,
    check_clustering_stability,
    evaluate_k_range,
)


def test_build_clustering_features_excludes_target(sample_df: pd.DataFrame):
    """Test that target variable and leakage columns are excluded from clustering features."""
    X_scaled, feature_names, scaler = build_clustering_features(sample_df)

    assert "Loan_Approved" not in feature_names
    assert "Default_Risk" not in feature_names
    assert "Approved_Amount" not in feature_names
    assert X_scaled.shape[0] == len(sample_df)
    assert X_scaled.shape[1] == len(feature_names)


def test_evaluate_k_range(sample_df: pd.DataFrame):
    """Test k-range evaluation computes inertias and silhouettes for each k."""
    X_scaled, _, _ = build_clustering_features(sample_df)
    k_range, inertias, silhouettes = evaluate_k_range(X_scaled, k_min=2, k_max=4)

    assert k_range == [2, 3, 4]
    assert len(inertias) == 3
    assert len(silhouettes) == 3
    assert all(i > 0 for i in inertias)
    assert all(-1.0 <= s <= 1.0 for s in silhouettes)


def test_check_clustering_stability(sample_df: pd.DataFrame):
    """Test clustering stability assessment across seeds."""
    X_scaled, _, _ = build_clustering_features(sample_df)
    report = check_clustering_stability(X_scaled, k=3, seeds=[1, 2, 3])

    assert "mean_ari" in report
    assert "is_stable" in report
    assert len(report["pairwise_ari_scores"]) == 3


def test_build_cluster_profiles(sample_df: pd.DataFrame):
    """Test cluster profiling computes size, averages, and approval rate per cluster."""
    labels = np.random.choice([0, 1, 2], size=len(sample_df))
    profiles = build_cluster_profiles(sample_df, labels)

    assert len(profiles) == 3
    assert "cluster_id" in profiles.columns
    assert "approval_rate" in profiles.columns
    assert "persona_label" in profiles.columns
    assert "avg_credit_score" in profiles.columns
    assert sum(profiles["size"]) == len(sample_df)
