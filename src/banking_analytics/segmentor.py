"""Customer segmentation pipeline using K-Means clustering, silhouette analysis, and profiling."""

from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from banking_analytics.feature_engineer import LEAKAGE_EXCLUSIONS
from banking_analytics.utils.io_utils import write_json_safe
from banking_analytics.utils.logger import get_logger
from banking_analytics.visualizer import plot_cluster_pca, plot_elbow_and_silhouette

logger = get_logger(__name__)


def build_clustering_features(
    df: pd.DataFrame,
    excluded_features: List[str] = LEAKAGE_EXCLUSIONS,
) -> Tuple[np.ndarray, List[str], StandardScaler]:
    """Prepares and scales feature matrix strictly for unsupervised borrower segmentation.

    Args:
        df: Cleaned dataset.
        excluded_features: Columns to exclude (identifiers, target, and leakage).

    Returns:
        Tuple: (X_scaled, feature_names, fitted_scaler)
    """
    logger.info("Building feature matrix for unsupervised K-Means segmentation.")

    cols_to_drop = [c for c in excluded_features if c in df.columns]
    feature_df = df.drop(columns=cols_to_drop).copy()

    # Drop redundant Monthly_Income if present
    if "Monthly_Income" in feature_df.columns:
        feature_df = feature_df.drop(columns=["Monthly_Income"])

    # Separate numeric and categorical
    numeric_df = feature_df.select_dtypes(include=[np.number])
    cat_df = feature_df.select_dtypes(include=["object", "category", "string"])

    scaler = StandardScaler()
    scaled_numeric = scaler.fit_transform(numeric_df.fillna(numeric_df.median()))
    feature_names = list(numeric_df.columns)

    if not cat_df.empty:
        ohe = OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore")
        encoded_cat = ohe.fit_transform(cat_df.fillna("Unknown"))
        cat_feature_names = list(ohe.get_feature_names_out(cat_df.columns))
        X_all = np.hstack([scaled_numeric, encoded_cat])
        feature_names.extend(cat_feature_names)
    else:
        X_all = scaled_numeric

    logger.info("Clustering feature matrix shape: (%d, %d)", X_all.shape[0], X_all.shape[1])
    return X_all, feature_names, scaler


def evaluate_k_range(
    X: np.ndarray,
    k_min: int = 2,
    k_max: int = 10,
    random_seed: int = 42,
) -> Tuple[List[int], List[float], List[float]]:
    """Evaluates inertias and silhouette coefficients across a range of k."""
    k_range = list(range(k_min, k_max + 1))
    inertias = []
    silhouettes = []

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=random_seed, n_init=10)
        labels = kmeans.fit_predict(X)
        inertias.append(float(kmeans.inertia_))
        sil_score = float(silhouette_score(X, labels))
        silhouettes.append(sil_score)
        logger.info("k=%d | Inertia: %.2f | Silhouette: %.4f", k, kmeans.inertia_, sil_score)

    return k_range, inertias, silhouettes


def check_clustering_stability(
    X: np.ndarray,
    k: int,
    seeds: List[int] = [0, 42, 123, 456, 789],
) -> Dict[str, Any]:
    """Tests clustering stability by computing Adjusted Rand Index (ARI) across different random seeds."""
    label_runs = []
    for s in seeds:
        km = KMeans(n_clusters=k, random_state=s, n_init=10)
        label_runs.append(km.fit_predict(X))

    ari_scores = []
    for l1, l2 in combinations(label_runs, 2):
        ari_scores.append(float(adjusted_rand_score(l1, l2)))

    mean_ari = float(np.mean(ari_scores)) if ari_scores else 1.0
    logger.info("Clustering stability across %d seeds (k=%d): Mean ARI = %.4f", len(seeds), k, mean_ari)
    return {
        "seeds": seeds,
        "pairwise_ari_scores": [round(x, 4) for x in ari_scores],
        "mean_ari": round(mean_ari, 4),
        "is_stable": bool(mean_ari > 0.65),
    }


def assign_persona_labels(profiles_df: pd.DataFrame) -> List[str]:
    """Assigns descriptive business persona labels to clusters based on financial traits."""
    personas = []
    for _, row in profiles_df.iterrows():
        credit = row["avg_credit_score"]
        dti = row["avg_dti"]
        income = row["avg_income"]

        if credit >= 720 and dti <= 35:
            persona = "Prime Low-Risk Borrowers"
        elif credit < 600 and dti > 45:
            persona = "Subprime High-DTI Borrowers"
        elif income > profiles_df["avg_income"].median() and dti > 40:
            persona = "Overleveraged Affluent Applicants"
        elif credit >= 650:
            persona = "Core Mainstream Borrowers"
        else:
            persona = "Emerging Credit-Builder Applicants"
        personas.append(persona)

    # Ensure unique persona names by appending cluster index if duplicates occur
    seen = {}
    unique_personas = []
    for i, p in enumerate(personas):
        if p in seen:
            seen[p] += 1
            unique_personas.append(f"{p} (Tier {seen[p]})")
        else:
            seen[p] = 1
            unique_personas.append(p)

    return unique_personas


def build_cluster_profiles(
    df: pd.DataFrame,
    labels: np.ndarray,
) -> pd.DataFrame:
    """Profiles each customer segment on core credit, income, and approval metrics."""
    df_profile = df.copy()
    df_profile["cluster"] = labels

    total = len(df_profile)
    summary_list = []

    for cluster_id in sorted(np.unique(labels)):
        cluster_data = df_profile[df_profile["cluster"] == cluster_id]
        size = len(cluster_data)
        pct = round(size / total * 100.0, 2)

        # Dominant loan purpose
        top_purpose = cluster_data["Loan_Purpose"].mode().iloc[0] if "Loan_Purpose" in cluster_data.columns else "N/A"

        summary_list.append({
            "cluster_id": int(cluster_id),
            "size": size,
            "pct_of_portfolio": pct,
            "avg_credit_score": round(float(cluster_data["Credit_Score"].mean()), 1),
            "avg_income": round(float(cluster_data["Annual_Income"].mean()), 2),
            "avg_dti": round(float(cluster_data["Debt_To_Income_Ratio"].mean()), 2),
            "avg_loan_amount": round(float(cluster_data["Loan_Amount"].mean()), 2),
            "approval_rate": round(float(cluster_data["Loan_Approved"].mean() * 100.0), 2),
            "dominant_loan_purpose": top_purpose,
        })

    profiles_df = pd.DataFrame(summary_list)
    profiles_df["persona_label"] = assign_persona_labels(profiles_df)
    return profiles_df


def train_and_evaluate_segmentation(
    df: pd.DataFrame,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """Runs complete segmentation pipeline: elbow/silhouette evaluation, K-Means fitting, stability checks, and profiling."""
    logger.info("=== Starting Customer Segmentation Pipeline (Milestone 4) ===")

    ml_conf = config.get("ml", {})
    seg_conf = ml_conf.get("clustering", {})
    k_min = seg_conf.get("k_range_min", 2)
    k_max = seg_conf.get("k_range_max", 10)
    selected_k = seg_conf.get("selected_k", 4)
    stability_seeds = seg_conf.get("stability_seeds", [0, 42, 123, 456, 789])
    figures_dir = config.get("visualization", {}).get("output_dir", "reports/figures")

    # 1. Feature scaling
    X_scaled, feature_names, scaler = build_clustering_features(df)

    # 2. Evaluate k range
    k_range, inertias, silhouettes = evaluate_k_range(X_scaled, k_min=k_min, k_max=k_max)

    # 3. Save Elbow and Silhouette plots
    plot_elbow_and_silhouette(
        k_range,
        inertias,
        silhouettes,
        elbow_path=f"{figures_dir}/elbow_plot.png",
        silhouette_path=f"{figures_dir}/silhouette_plot.png",
    )

    # 4. Fit final K-Means model with selected k
    logger.info("Fitting final K-Means model with k=%d", selected_k)
    final_kmeans = KMeans(n_clusters=selected_k, random_state=ml_conf.get("random_seed", 42), n_init=seg_conf.get("n_init", 10))
    cluster_labels = final_kmeans.fit_predict(X_scaled)

    # 5. Stability check across seeds
    stability_report = check_clustering_stability(X_scaled, selected_k, seeds=stability_seeds)

    # 6. Cluster Profiling
    profiles_df = build_cluster_profiles(df, cluster_labels)

    # 7. 2D PCA Visualization
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    plot_cluster_pca(X_pca, cluster_labels, output_path=f"{figures_dir}/cluster_pca.png")

    # 8. Save models & metadata
    models_dir = Path("models")
    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_kmeans, models_dir / "kmeans_model.joblib")
    joblib.dump(scaler, models_dir / "scaler.joblib")

    metadata = {
        "timestamp": datetime.now().isoformat(),
        "algorithm": "KMeans",
        "selected_k": selected_k,
        "inertia": float(final_kmeans.inertia_),
        "silhouette_score": float(silhouette_score(X_scaled, cluster_labels)),
        "stability_report": stability_report,
        "pca_variance_explained": [round(float(v), 4) for v in pca.explained_variance_ratio_],
        "cluster_profiles": profiles_df.to_dict(orient="records"),
    }
    write_json_safe(metadata, str(models_dir / "metadata" / "kmeans_metadata.json"), indent=2)

    # 9. Save cluster profiles report
    report_path = Path("reports/model_evaluation/cluster_profiles.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    table_md = profiles_df[[
        "cluster_id",
        "persona_label",
        "size",
        "pct_of_portfolio",
        "avg_credit_score",
        "avg_income",
        "avg_dti",
        "approval_rate",
        "dominant_loan_purpose",
    ]].to_markdown(index=False)

    report_content = f"""# Customer Segmentation & Risk Persona Report

**Clustering Algorithm:** K-Means ($k={selected_k}$)
**Evaluation Metrics:** Silhouette Score = {metadata['silhouette_score']:.4f} | Stability Mean ARI = {stability_report['mean_ari']:.4f}

---

## 1. Segment Profiles & Risk Distribution

{table_md}

---

## 2. Cluster Stability Audit
- **Seeds Evaluated:** {stability_seeds}
- **Pairwise Adjusted Rand Index (ARI):** {stability_report['pairwise_ari_scores']}
- **Mean ARI:** {stability_report['mean_ari']:.4f} ({'Stable' if stability_report['is_stable'] else 'Moderate Variability'})

---

## 3. Visual Artifacts
- Elbow Plot: `reports/figures/elbow_plot.png`
- Silhouette Plot: `reports/figures/silhouette_plot.png`
- 2D PCA Cluster Map: `reports/figures/cluster_pca.png`
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    logger.info("Saved cluster profiles report to: %s", report_path)
    return {
        "kmeans": final_kmeans,
        "labels": cluster_labels,
        "profiles": profiles_df,
        "metadata": metadata,
    }
