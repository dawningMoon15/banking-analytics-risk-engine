"""Unified evaluation and cross-referencing module between classification and segmentation."""

from typing import Any, Dict
import pandas as pd
from sklearn.pipeline import Pipeline

from banking_analytics.feature_engineer import select_features
from banking_analytics.utils.logger import get_logger

logger = get_logger(__name__)


def cross_reference_clusters(
    df: pd.DataFrame,
    clf_pipeline: Pipeline,
    cluster_labels: pd.Series,
    target_column: str = "Loan_Approved",
) -> pd.DataFrame:
    """Attaches model-predicted approval probabilities to borrower clusters to audit segment-level default risk."""
    logger.info("Cross-referencing classification model predictions with borrower clusters.")

    # Prepare feature matrix for prediction
    X, y, _, _, _ = select_features(df, target_column=target_column)
    predicted_probs = clf_pipeline.predict_proba(X)[:, 1]

    analysis_df = pd.DataFrame({
        "cluster": cluster_labels,
        "actual_approved": y,
        "predicted_approval_prob": predicted_probs.round(4),
    })

    cross_tab = (
        analysis_df.groupby("cluster")
        .agg(
            applicant_count=("actual_approved", "count"),
            actual_approval_rate=("actual_approved", lambda s: round(s.mean() * 100.0, 2)),
            mean_predicted_prob=("predicted_approval_prob", lambda s: round(s.mean(), 4)),
            median_predicted_prob=("predicted_approval_prob", lambda s: round(s.median(), 4)),
            high_risk_pct=("predicted_approval_prob", lambda s: round((s < 0.40).mean() * 100.0, 2)),
        )
        .reset_index()
    )

    logger.info("Segment risk cross-reference completed across %d clusters.", len(cross_tab))
    return cross_tab


def compare_models(
    baseline_metrics: Dict[str, float],
    lr_metrics: Dict[str, Any],
) -> pd.DataFrame:
    """Constructs a side-by-side comparison table between baseline and regularized Logistic Regression."""
    opt = lr_metrics.get("optimal_threshold", {})
    def_th = lr_metrics.get("default_threshold_0.5", {})

    data = [
        {
            "Metric": "Accuracy",
            "Dummy Baseline": baseline_metrics.get("accuracy", 0.0),
            "Logistic Regression (0.50)": def_th.get("accuracy", 0.0),
            "Logistic Regression (Optimal Thresh)": opt.get("accuracy", 0.0),
        },
        {
            "Metric": "Precision",
            "Dummy Baseline": 0.0,
            "Logistic Regression (0.50)": def_th.get("precision", 0.0),
            "Logistic Regression (Optimal Thresh)": opt.get("precision", 0.0),
        },
        {
            "Metric": "Recall",
            "Dummy Baseline": 0.0,
            "Logistic Regression (0.50)": def_th.get("recall", 0.0),
            "Logistic Regression (Optimal Thresh)": opt.get("recall", 0.0),
        },
        {
            "Metric": "F1-Score",
            "Dummy Baseline": baseline_metrics.get("f1", 0.0),
            "Logistic Regression (0.50)": def_th.get("f1", 0.0),
            "Logistic Regression (Optimal Thresh)": opt.get("f1", 0.0),
        },
        {
            "Metric": "ROC-AUC",
            "Dummy Baseline": 0.5000,
            "Logistic Regression (0.50)": lr_metrics.get("roc_auc", 0.0),
            "Logistic Regression (Optimal Thresh)": lr_metrics.get("roc_auc", 0.0),
        },
        {
            "Metric": "Brier Score",
            "Dummy Baseline": "N/A",
            "Logistic Regression (0.50)": lr_metrics.get("brier_score", 0.0),
            "Logistic Regression (Optimal Thresh)": lr_metrics.get("brier_score", 0.0),
        },
    ]
    return pd.DataFrame(data)
