"""Integration tests for DatabaseManager and SQL queries."""

from pathlib import Path
import pandas as pd
import pytest

from banking_analytics.db_loader import DatabaseManager


@pytest.fixture
def test_db_config(tmp_path: Path) -> dict:
    """Provides a test configuration using a temporary DuckDB database."""
    duckdb_file = tmp_path / "test_banking.duckdb"
    return {
        "database": {
            "backend": "duckdb",
            "duckdb": {
                "path": str(duckdb_file),
            },
        }
    }


def test_db_loader_full_flow(test_db_config: dict, sample_df: pd.DataFrame):
    """Tests end-to-end database initialization, loading, views, and query execution."""
    db = DatabaseManager(test_db_config)

    # 1. Initialize schema
    db.init_schema("sql/schema/create_tables.sql")

    # 2. Load cleaned data
    db.load_data(sample_df)

    # 3. Create views
    db.create_views("sql/queries/views")

    # 4. Execute analytical queries
    query_results = db.execute_all_queries("sql/queries")

    assert "q01_overall_approval_rate" in query_results
    assert "q02_approval_by_credit_score_band" in query_results
    assert "q03_approval_by_income_band" in query_results
    assert "q04_dti_vs_approval" in query_results
    assert "q05_approval_by_loan_purpose" in query_results
    assert "q06_risk_score_distribution" in query_results

    # Check query 1 output
    df_q1 = query_results["q01_overall_approval_rate"]
    assert not df_q1.empty
    assert "loan_approved" in df_q1.columns
    assert "pct" in df_q1.columns

    # Check view query
    df_view = db.run_query("SELECT * FROM v_credit_risk_summary")
    assert not df_view.empty
    assert "credit_band" in df_view.columns
    assert "approval_pct" in df_view.columns

    db.close()
