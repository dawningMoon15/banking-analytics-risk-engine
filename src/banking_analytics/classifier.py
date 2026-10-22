"""Classification modeling, threshold optimization, evaluation, and interpretability module."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.pipeline import Pipeline

from banking_analytics.feature_engineer import build_preprocessor, select_features, split_data
from banking_analytics.utils.io_utils import write_json_safe
from banking_analytics.utils.logger import get_logger
from banking_analytics.visualizer import (
    plot_confusion_matrix,
    plot_feature_coefficients,
    plot_pr_curve,
    plot_roc_curve,
)

logger = get_logger(__name__)


def build_classification_pipeline(
    preprocessor: Any,
    class_weight: str = "balanced",
    max_iter: int = 1000,
    solver: str = "lbfgs",
    C: float = 1.0,
    random_seed: int = 42,
) -> Pipeline:
    """Builds an end-to-end classification pipeline combining preprocessor and Logistic Regression."""
    model = LogisticRegression(
        class_weight=class_weight,
        max_iter=max_iter,
        solver=solver,
        C=C,
        random_state=random_seed,
    )
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", model),
        ]
    )
    return pipeline


def find_optimal_threshold(
    pipeline: Pipeline,
    X_val: pd.DataFrame,
    y_val: pd.Series,
) -> Tuple[float, float]:
    """Finds decision threshold maximizing F1 score on validation set."""
    y_probs = pipeline.predict_proba(X_val)[:, 1]
    thresholds = np.linspace(0.1, 0.9, 81)
    best_thresh = 0.5
    best_f1 = 0.0

    for thresh in thresholds:
        preds = (y_probs >= thresh).astype(int)
        score = f1_score(y_val, preds, zero_division=0)
        if score > best_f1:
            best_f1 = score
            best_thresh = thresh

    logger.info("Optimal validation threshold: %.2f (Validation F1: %.4f)", best_thresh, best_f1)
    return float(best_thresh), float(best_f1)


def evaluate_classifier(
    pipeline: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    threshold: float = 0.5,
) -> Dict[str, Any]:
    """Computes comprehensive evaluation metrics on held-out test data."""
    y_probs = pipeline.predict_proba(X_test)[:, 1]
    y_preds_default = (y_probs >= 0.5).astype(int)
    y_preds_opt = (y_probs >= threshold).astype(int)

    roc_auc = float(roc_auc_score(y_test, y_probs))
    pr_auc = float(average_precision_score(y_test, y_probs))
    brier = float(brier_score_loss(y_test, y_probs))

    cm = confusion_matrix(y_test, y_preds_opt)

    fpr, tpr, _ = roc_curve(y_test, y_probs)
    precisions, recalls, _ = precision_recall_curve(y_test, y_probs)

    metrics = {
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "brier_score": round(brier, 4),
        "default_threshold_0.5": {
            "accuracy": round(float(accuracy_score(y_test, y_preds_default)), 4),
            "precision": round(float(precision_score(y_test, y_preds_default, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_preds_default, zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, y_preds_default, zero_division=0)), 4),
        },
        "optimal_threshold": {
            "threshold": round(threshold, 2),
            "accuracy": round(float(accuracy_score(y_test, y_preds_opt)), 4),
            "precision": round(float(precision_score(y_test, y_preds_opt, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_preds_opt, zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, y_preds_opt, zero_division=0)), 4),
        },
        "confusion_matrix": cm.tolist(),
        "fpr": fpr.tolist(),
        "tpr": tpr.tolist(),
        "precisions": precisions.tolist(),
        "recalls": recalls.tolist(),
    }
    return metrics


def extract_coefficients(pipeline: Pipeline) -> pd.DataFrame:
    """Extracts transformed feature names, log-odds coefficients, and odds ratios."""
    preprocessor = pipeline.named_steps["preprocessor"]
    classifier = pipeline.named_steps["classifier"]

    raw_names = preprocessor.get_feature_names_out()
    # Clean feature prefixes (e.g. 'num__', 'cat__', 'bin__')
    clean_names = [name.split("__", 1)[-1] for name in raw_names]
    coefs = classifier.coef_[0]

    coef_df = pd.DataFrame({
        "feature": clean_names,
        "coefficient": coefs.round(4),
        "odds_ratio": np.exp(coefs).round(4),
    })
    return coef_df.sort_values(by="coefficient", ascending=False).reset_index(drop=True)


def train_and_evaluate_classification(
    df: pd.DataFrame,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """Orchestrates feature selection, model training, threshold tuning, and artifact generation."""
    logger.info("=== Starting Classification Pipeline (Milestone 3) ===")

    ml_conf = config.get("ml", {})
    cls_conf = ml_conf.get("classification", {})
    random_seed = ml_conf.get("random_seed", 42)
    figures_dir = config.get("visualization", {}).get("output_dir", "reports/figures")

    # 1. Feature selection & leakage exclusion
    X, y, num_cols, cat_cols, bin_cols = select_features(
        df,
        target_column=cls_conf.get("target_column", "Loan_Approved"),
        excluded_features=config.get("data", {}).get("excluded_features", []),
    )

    # 2. Stratified split
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(
        X,
        y,
        train_size=ml_conf.get("train_size", 0.70),
        val_size=ml_conf.get("val_size", 0.15),
        test_size=ml_conf.get("test_size", 0.15),
        random_seed=random_seed,
    )

    # 3. Train Baseline Dummy Classifier
    dummy = DummyClassifier(strategy="most_frequent")
    dummy.fit(X_train, y_train)
    dummy_preds = dummy.predict(X_test)
    dummy_acc = accuracy_score(y_test, dummy_preds)
    dummy_f1 = f1_score(y_test, dummy_preds, zero_division=0)

    # 4. Build and fit pipeline on Train set only (strict leakage prevention)
    preprocessor = build_preprocessor(num_cols, cat_cols, bin_cols)
    pipeline = build_classification_pipeline(
        preprocessor=preprocessor,
        class_weight=cls_conf.get("class_weight", "balanced"),
        max_iter=cls_conf.get("max_iter", 1000),
        solver=cls_conf.get("solver", "lbfgs"),
        C=cls_conf.get("C", 1.0),
        random_seed=random_seed,
    )
    pipeline.fit(X_train, y_train)
    logger.info("Logistic Regression pipeline successfully fitted on training data.")

    # 5. Threshold selection on validation set
    optimal_thresh, val_f1 = find_optimal_threshold(pipeline, X_val, y_val)

    # 6. Evaluation on held-out test set
    eval_metrics = evaluate_classifier(pipeline, X_test, y_test, threshold=optimal_thresh)
    eval_metrics["baseline_dummy"] = {
        "accuracy": round(float(dummy_acc), 4),
        "f1": round(float(dummy_f1), 4),
    }

    # 7. Extract coefficients and odds ratios
    coef_df = extract_coefficients(pipeline)

    # 8. Save figures
    plot_roc_curve(
        np.array(eval_metrics["fpr"]),
        np.array(eval_metrics["tpr"]),
        eval_metrics["roc_auc"],
        output_path=f"{figures_dir}/roc_curve.png",
    )
    plot_pr_curve(
        np.array(eval_metrics["precisions"]),
        np.array(eval_metrics["recalls"]),
        eval_metrics["pr_auc"],
        output_path=f"{figures_dir}/pr_curve.png",
    )
    plot_confusion_matrix(
        np.array(eval_metrics["confusion_matrix"]),
        output_path=f"{figures_dir}/confusion_matrix.png",
    )
    plot_feature_coefficients(
        coef_df,
        output_path=f"{figures_dir}/coefficient_plot.png",
    )

    # 9. Save model artifacts and metadata
    models_dir = Path("models")
    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / "logistic_model.joblib"
    joblib.dump(pipeline, model_path)
    logger.info("Saved trained pipeline model to: %s", model_path)

    metadata = {
        "timestamp": datetime.now().isoformat(),
        "model_type": "LogisticRegression",
        "random_seed": random_seed,
        "hyperparameters": {
            "C": cls_conf.get("C", 1.0),
            "class_weight": cls_conf.get("class_weight", "balanced"),
            "solver": cls_conf.get("solver", "lbfgs"),
            "max_iter": cls_conf.get("max_iter", 1000),
        },
        "optimal_threshold": optimal_thresh,
        "metrics_test": {
            "roc_auc": eval_metrics["roc_auc"],
            "pr_auc": eval_metrics["pr_auc"],
            "brier_score": eval_metrics["brier_score"],
            "accuracy": eval_metrics["optimal_threshold"]["accuracy"],
            "precision": eval_metrics["optimal_threshold"]["precision"],
            "recall": eval_metrics["optimal_threshold"]["recall"],
            "f1": eval_metrics["optimal_threshold"]["f1"],
        },
        "baseline_comparison": eval_metrics["baseline_dummy"],
    }
    metadata_path = models_dir / "metadata" / "lr_metadata.json"
    write_json_safe(metadata, str(metadata_path), indent=2)

    # 10. Write classification Markdown report
    report_path = Path("reports/model_evaluation/classification_report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    opt = eval_metrics["optimal_threshold"]
    def_th = eval_metrics["default_threshold_0.5"]
    base = eval_metrics["baseline_dummy"]

    top_pos = coef_df.head(5).to_markdown(index=False)
    top_neg = coef_df.tail(5).sort_values(by="coefficient", ascending=True).to_markdown(index=False)

    report_content = f"""# Default Risk Classification Model Evaluation Report

**Model:** Regularized Logistic Regression (`sklearn.linear_model.LogisticRegression`)
**Evaluation Dataset:** Held-out Test Set ({len(y_test):,} records)

---

## 1. Executive Performance Summary

| Metric | Dummy Baseline | Logistic Regression (Threshold 0.50) | Logistic Regression (Optimal Threshold {opt['threshold']}) |
|:-------|:---------------|:-------------------------------------|:-----------------------------------------------------------|
| **Accuracy** | {base['accuracy']:.4f} | {def_th['accuracy']:.4f} | **{opt['accuracy']:.4f}** |
| **Precision** | 0.0000 | {def_th['precision']:.4f} | **{opt['precision']:.4f}** |
| **Recall** | 0.0000 | {def_th['recall']:.4f} | **{opt['recall']:.4f}** |
| **F1-Score** | {base['f1']:.4f} | {def_th['f1']:.4f} | **{opt['f1']:.4f}** |
| **ROC-AUC** | 0.5000 | {eval_metrics['roc_auc']:.4f} | **{eval_metrics['roc_auc']:.4f}** |
| **PR-AUC** | {len(y_test[y_test==1])/len(y_test):.4f} | {eval_metrics['pr_auc']:.4f} | **{eval_metrics['pr_auc']:.4f}** |
| **Brier Score** | — | {eval_metrics['brier_score']:.4f} | **{eval_metrics['brier_score']:.4f}** |

---

## 2. Model Interpretability & Feature Odds Ratios

### Top 5 Positive Drivers (Increases Approval Odds)
{top_pos}

### Top 5 Risk Drivers (Increases Rejection Odds)
{top_neg}

---

## 3. Visual Artifacts
- ROC Curve: `reports/figures/roc_curve.png`
- PR Curve: `reports/figures/pr_curve.png`
- Confusion Matrix: `reports/figures/confusion_matrix.png`
- Coefficient Plot: `reports/figures/coefficient_plot.png`
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    logger.info("Classification evaluation report saved to: %s", report_path)

    return {
        "pipeline": pipeline,
        "metrics": eval_metrics,
        "metadata": metadata,
        "coef_df": coef_df,
    }
