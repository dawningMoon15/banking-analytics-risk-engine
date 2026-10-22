"""Integration test verifying end-to-end pipeline execution and output artifact generation."""

from pathlib import Path
import pandas as pd
import pytest
import yaml

from scripts.run_pipeline import run_pipeline


def test_pipeline_end_to_end(tmp_path: Path, sample_df: pd.DataFrame):
    """Executes all pipeline phases from ingestion to final reporting."""
    # Setup test workspace
    raw_path = tmp_path / "raw.csv"
    processed_path = tmp_path / "cleaned.csv"
    reports_path = tmp_path / "quality_report.json"
    figures_dir = tmp_path / "figures"
    duckdb_path = tmp_path / "test.duckdb"
    config_path = tmp_path / "test_config.yaml"

    sample_df.to_csv(raw_path, index=False)

    test_config = {
        "project": {"name": "test-banking", "version": "0.1.0"},
        "data": {
            "raw_path": str(raw_path),
            "processed_path": str(processed_path),
            "reports_path": str(reports_path),
            "version": "test_v1",
            "excluded_features": [
                "Application_ID",
                "Loan_Approved",
                "Default_Risk",
                "Approved_Amount",
                "Risk_Score",
                "Interest_Rate",
            ],
            "target_column": "Loan_Approved",
        },
        "database": {
            "backend": "duckdb",
            "duckdb": {"path": str(duckdb_path)},
        },
        "ml": {
            "random_seed": 42,
            "train_size": 0.70,
            "val_size": 0.15,
            "test_size": 0.15,
            "classification": {
                "target_column": "Loan_Approved",
                "class_weight": "balanced",
                "max_iter": 500,
                "solver": "lbfgs",
                "C": 1.0,
            },
            "clustering": {
                "k_range_min": 2,
                "k_range_max": 4,
                "selected_k": 3,
                "stability_seeds": [0, 42],
                "n_init": 5,
            },
        },
        "visualization": {
            "color_palette": "viridis",
            "figure_dpi": 100,
            "output_dir": str(figures_dir),
        },
        "logging": {
            "level": "INFO",
            "log_file": str(tmp_path / "pipeline.log"),
        },
    }

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(test_config, f)

    # Run end-to-end
    run_pipeline(config_path=str(config_path), dry_run=False, stage="all")

    # Assert all artifacts exist
    assert processed_path.is_file()
    assert reports_path.is_file()
    assert Path("models/logistic_model.joblib").is_file()
    assert Path("models/kmeans_model.joblib").is_file()
    assert Path("models/metadata/lr_metadata.json").is_file()
    assert Path("models/metadata/kmeans_metadata.json").is_file()
    assert Path("reports/eda_summary.md").is_file()
    assert Path("reports/model_evaluation/classification_report.md").is_file()
    assert Path("reports/model_evaluation/cluster_profiles.md").is_file()
    assert Path("reports/final_report.md").is_file()
    assert (figures_dir / "target_distribution.png").is_file()
    assert (figures_dir / "correlation_heatmap.png").is_file()
    assert (figures_dir / "roc_curve.png").is_file()
    assert (figures_dir / "pr_curve.png").is_file()
    assert (figures_dir / "confusion_matrix.png").is_file()
    assert (figures_dir / "elbow_plot.png").is_file()
    assert (figures_dir / "silhouette_plot.png").is_file()
    assert (figures_dir / "cluster_pca.png").is_file()
    assert (figures_dir / "coefficient_plot.png").is_file()
    assert (figures_dir / "calibration_curve.png").is_file()
    assert (figures_dir / "credit_score_vs_approval.png").is_file()
    assert (figures_dir / "dti_vs_approval.png").is_file()
    assert (figures_dir / "income_vs_approval.png").is_file()
    assert (figures_dir / "loan_purpose_vs_approval.png").is_file()
