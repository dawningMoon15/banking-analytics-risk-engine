"""Publication-quality visualization utilities for banking analytics and risk engine."""

from pathlib import Path
from typing import List, Optional
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from banking_analytics.utils.logger import get_logger

logger = get_logger(__name__)

# Set publication-standard aesthetics
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Helvetica", "Arial"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def _ensure_output_dir(output_path: str) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def plot_target_distribution(
    df: pd.DataFrame,
    target_col: str = "Loan_Approved",
    output_path: str = "reports/figures/target_distribution.png",
    dpi: int = 150,
) -> Path:
    """Plots and saves the target class distribution."""
    dest = _ensure_output_dir(output_path)
    fig, ax = plt.subplots(figsize=(7, 5))

    counts = df[target_col].value_counts().sort_index()
    labels = ["Rejected (0)", "Approved (1)"] if list(counts.index) == [0, 1] else [str(x) for x in counts.index]
    colors = ["#e74c3c", "#2ecc71"]

    bars = ax.bar(labels, counts.values, color=colors, width=0.5, edgecolor="none", alpha=0.9)
    total = len(df)
    for bar in bars:
        height = bar.get_height()
        pct = (height / total) * 100
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + total * 0.01,
            f"{int(height):,} ({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=10,
        )

    ax.set_title("Target Distribution: Loan Approval Status", fontsize=13, fontweight="bold", pad=15)
    ax.set_ylabel("Applicant Count", fontsize=11)
    ax.set_ylim(0, max(counts.values) * 1.15)
    plt.tight_layout()
    fig.savefig(dest, dpi=dpi)
    plt.close(fig)
    logger.info("Saved target distribution plot to: %s", dest)
    return dest


def plot_correlation_heatmap(
    df: pd.DataFrame,
    features: Optional[List[str]] = None,
    output_path: str = "reports/figures/correlation_heatmap.png",
    dpi: int = 150,
) -> Path:
    """Plots correlation heatmap across continuous features."""
    dest = _ensure_output_dir(output_path)
    if features is None:
        numeric_df = df.select_dtypes(include=[np.number])
    else:
        valid_cols = [c for c in features if c in df.columns]
        numeric_df = df[valid_cols]

    corr = numeric_df.corr()
    fig, ax = plt.subplots(figsize=(11, 9))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(
        corr,
        mask=mask,
        cmap="coolwarm",
        vmax=1.0,
        vmin=-1.0,
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        ax=ax,
        fmt=".2f",
    )
    ax.set_title("Correlation Heatmap: Financial & Credit Features", fontsize=13, fontweight="bold", pad=15)
    plt.tight_layout()
    fig.savefig(dest, dpi=dpi)
    plt.close(fig)
    logger.info("Saved correlation heatmap to: %s", dest)
    return dest


def plot_roc_curve(
    fpr: np.ndarray,
    tpr: np.ndarray,
    roc_auc: float,
    output_path: str = "reports/figures/roc_curve.png",
    dpi: int = 150,
) -> Path:
    """Plots and saves the Receiver Operating Characteristic (ROC) curve."""
    dest = _ensure_output_dir(output_path)
    fig, ax = plt.subplots(figsize=(7, 6))

    ax.plot(fpr, tpr, color="#2980b9", lw=2.5, label=f"Logistic Regression (AUC = {roc_auc:.3f})")
    ax.plot([0, 1], [0, 1], color="#7f8c8d", lw=1.5, linestyle="--", label="Random Classifier (AUC = 0.500)")

    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate (1 - Specificity)", fontsize=11)
    ax.set_ylabel("True Positive Rate (Recall)", fontsize=11)
    ax.set_title("ROC Curve: Default Risk Classification", fontsize=13, fontweight="bold", pad=15)
    ax.legend(loc="lower right", frameon=True)
    plt.tight_layout()
    fig.savefig(dest, dpi=dpi)
    plt.close(fig)
    logger.info("Saved ROC curve to: %s", dest)
    return dest


def plot_pr_curve(
    precision: np.ndarray,
    recall: np.ndarray,
    pr_auc: float,
    output_path: str = "reports/figures/pr_curve.png",
    dpi: int = 150,
) -> Path:
    """Plots and saves the Precision-Recall (PR) curve."""
    dest = _ensure_output_dir(output_path)
    fig, ax = plt.subplots(figsize=(7, 6))

    ax.plot(recall, precision, color="#8e44ad", lw=2.5, label=f"Logistic Regression (PR-AUC = {pr_auc:.3f})")
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("Recall", fontsize=11)
    ax.set_ylabel("Precision", fontsize=11)
    ax.set_title("Precision-Recall Curve", fontsize=13, fontweight="bold", pad=15)
    ax.legend(loc="lower left", frameon=True)
    plt.tight_layout()
    fig.savefig(dest, dpi=dpi)
    plt.close(fig)
    logger.info("Saved PR curve to: %s", dest)
    return dest


def plot_confusion_matrix(
    cm: np.ndarray,
    labels: Optional[List[str]] = None,
    output_path: str = "reports/figures/confusion_matrix.png",
    dpi: int = 150,
) -> Path:
    """Plots and saves the confusion matrix heatmap."""
    dest = _ensure_output_dir(output_path)
    class_labels = labels if labels else ["Rejected", "Approved"]

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_labels,
        yticklabels=class_labels,
        ax=ax,
        cbar=False,
    )
    ax.set_title("Confusion Matrix (Held-out Test Set)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Predicted Label", fontsize=11)
    ax.set_ylabel("True Label", fontsize=11)
    plt.tight_layout()
    fig.savefig(dest, dpi=dpi)
    plt.close(fig)
    logger.info("Saved confusion matrix to: %s", dest)
    return dest


def plot_elbow_and_silhouette(
    k_range: List[int],
    inertias: List[float],
    silhouettes: List[float],
    elbow_path: str = "reports/figures/elbow_plot.png",
    silhouette_path: str = "reports/figures/silhouette_plot.png",
    dpi: int = 150,
) -> Tuple[Path, Path]:
    """Plots and saves K-Means elbow plot (inertia) and silhouette score plots."""
    dest_elbow = _ensure_output_dir(elbow_path)
    dest_sil = _ensure_output_dir(silhouette_path)

    # Elbow plot
    fig1, ax1 = plt.subplots(figsize=(7, 5))
    ax1.plot(k_range, inertias, "bo-", lw=2, markersize=8)
    ax1.set_title("K-Means Elbow Plot: Inertia vs Number of Clusters", fontsize=13, fontweight="bold", pad=15)
    ax1.set_xlabel("Number of Clusters (k)", fontsize=11)
    ax1.set_ylabel("Inertia (Sum of Squared Distances)", fontsize=11)
    ax1.set_xticks(k_range)
    plt.tight_layout()
    fig1.savefig(dest_elbow, dpi=dpi)
    plt.close(fig1)

    # Silhouette plot
    fig2, ax2 = plt.subplots(figsize=(7, 5))
    ax2.plot(k_range, silhouettes, "rs-", lw=2, markersize=8)
    ax2.set_title("Silhouette Score vs Number of Clusters", fontsize=13, fontweight="bold", pad=15)
    ax2.set_xlabel("Number of Clusters (k)", fontsize=11)
    ax2.set_ylabel("Mean Silhouette Coefficient", fontsize=11)
    ax2.set_xticks(k_range)
    plt.tight_layout()
    fig2.savefig(dest_sil, dpi=dpi)
    plt.close(fig2)

    logger.info("Saved elbow plot to: %s", dest_elbow)
    logger.info("Saved silhouette plot to: %s", dest_sil)
    return dest_elbow, dest_sil


def plot_cluster_pca(
    X_pca: np.ndarray,
    cluster_labels: np.ndarray,
    output_path: str = "reports/figures/cluster_pca.png",
    dpi: int = 150,
) -> Path:
    """Visualizes borrower segments on the first two Principal Components."""
    dest = _ensure_output_dir(output_path)
    fig, ax = plt.subplots(figsize=(8, 6))

    unique_clusters = np.unique(cluster_labels)
    palette = sns.color_palette("Set2", len(unique_clusters))

    for idx, cluster in enumerate(unique_clusters):
        mask = cluster_labels == cluster
        ax.scatter(
            X_pca[mask, 0],
            X_pca[mask, 1],
            label=f"Cluster {cluster}",
            alpha=0.6,
            edgecolors="none",
            s=40,
            color=palette[idx],
        )

    ax.set_title("Borrower Segments: 2D PCA Projection", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Principal Component 1", fontsize=11)
    ax.set_ylabel("Principal Component 2", fontsize=11)
    ax.legend(title="Segment", frameon=True)
    plt.tight_layout()
    fig.savefig(dest, dpi=dpi)
    plt.close(fig)
    logger.info("Saved cluster PCA plot to: %s", dest)
    return dest


def plot_feature_coefficients(
    coef_df: pd.DataFrame,
    output_path: str = "reports/figures/coefficient_plot.png",
    dpi: int = 150,
    top_n: int = 15,
) -> Path:
    """Plots top positive and negative Logistic Regression feature coefficients."""
    dest = _ensure_output_dir(output_path)
    # Sort by absolute coefficient value
    sorted_df = coef_df.reindex(coef_df["coefficient"].abs().sort_values(ascending=False).index).head(top_n)
    sorted_df = sorted_df.sort_values(by="coefficient", ascending=True)

    fig, ax = plt.subplots(figsize=(9, 7))
    colors = ["#2ecc71" if x > 0 else "#e74c3c" for x in sorted_df["coefficient"]]
    bars = ax.barh(sorted_df["feature"], sorted_df["coefficient"], color=colors, height=0.6)

    ax.axvline(0, color="#333333", linestyle="--", linewidth=0.8)
    ax.set_title(f"Top {top_n} Predictive Feature Coefficients (Logistic Regression)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Log-Odds Coefficient (Positive = Increases Approval Odds)", fontsize=11)
    plt.tight_layout()
    fig.savefig(dest, dpi=dpi)
    plt.close(fig)
    logger.info("Saved coefficient plot to: %s", dest)
    return dest


def plot_bivariate_boxplots(
    df: pd.DataFrame,
    feature: str,
    target_col: str = "Loan_Approved",
    output_path: Optional[str] = None,
    dpi: int = 150,
) -> Path:
    """Plots and saves bivariate boxplots of a continuous feature stratified by the target label."""
    if output_path is None:
        clean_feat = feature.lower().replace(" ", "_")
        output_path = f"reports/figures/{clean_feat}_vs_approval.png"
    dest = _ensure_output_dir(output_path)

    fig, ax = plt.subplots(figsize=(7, 5))
    plot_df = df[[feature, target_col]].dropna().copy()
    plot_df["Status"] = plot_df[target_col].map({1: "Approved", 0: "Rejected"}).fillna(plot_df[target_col].astype(str))

    palette = {"Approved": "#2ecc71", "Rejected": "#e74c3c"}
    sns.boxplot(data=plot_df, x="Status", y=feature, hue="Status", palette=palette, legend=False, ax=ax, width=0.45, showmeans=True,
                meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black", "markersize": "7"})

    ax.set_title(f"Bivariate Distribution: {feature} by Loan Status", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Loan Approval Status", fontsize=11)
    ax.set_ylabel(feature, fontsize=11)
    plt.tight_layout()
    fig.savefig(dest, dpi=dpi)
    plt.close(fig)
    logger.info("Saved bivariate boxplot for %s to: %s", feature, dest)
    return dest


def plot_bivariate_categorical(
    df: pd.DataFrame,
    feature: str,
    target_col: str = "Loan_Approved",
    output_path: Optional[str] = None,
    dpi: int = 150,
) -> Path:
    """Plots and saves approval rate percentages stratified by a categorical feature."""
    if output_path is None:
        clean_feat = feature.lower().replace(" ", "_")
        output_path = f"reports/figures/{clean_feat}_vs_approval.png"
    dest = _ensure_output_dir(output_path)

    rates = (
        df.groupby(feature)[target_col]
        .agg(["count", "mean"])
        .reset_index()
    )
    rates["approval_pct"] = rates["mean"] * 100.0
    rates = rates.sort_values(by="approval_pct", ascending=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(rates[feature].astype(str), rates["approval_pct"], color="#3498db", width=0.55)

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, h + 1.0, f"{h:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_title(f"Approval Rate by {feature}", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel(feature, fontsize=11)
    ax.set_ylabel("Approval Rate (%)", fontsize=11)
    ax.set_ylim(0, max(rates["approval_pct"]) * 1.15)
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    fig.savefig(dest, dpi=dpi)
    plt.close(fig)
    logger.info("Saved categorical bivariate plot for %s to: %s", feature, dest)
    return dest


def plot_calibration_curve(
    y_true: np.ndarray,
    y_probs: np.ndarray,
    output_path: str = "reports/figures/calibration_curve.png",
    dpi: int = 150,
    n_bins: int = 10,
) -> Path:
    """Plots and saves probability calibration curve (reliability diagram) with Brier score."""
    from sklearn.calibration import calibration_curve
    from sklearn.metrics import brier_score_loss

    dest = _ensure_output_dir(output_path)
    prob_true, prob_pred = calibration_curve(y_true, y_probs, n_bins=n_bins, strategy="uniform")
    brier = brier_score_loss(y_true, y_probs)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot([0, 1], [0, 1], linestyle="--", color="#7f8c8d", label="Perfect Calibration")
    ax.plot(prob_pred, prob_true, marker="o", lw=2, color="#2980b9", label=f"Logistic Regression (Brier: {brier:.4f})")

    ax.set_title("Probability Calibration Curve (Reliability Diagram)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Mean Predicted Probability", fontsize=11)
    ax.set_ylabel("Observed Fraction of Positives", fontsize=11)
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.legend(loc="lower right", frameon=True)
    plt.tight_layout()
    fig.savefig(dest, dpi=dpi)
    plt.close(fig)
    logger.info("Saved calibration curve to: %s", dest)
    return dest
