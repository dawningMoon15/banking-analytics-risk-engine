"""Feature engineering, leakage elimination, and Scikit-Learn preprocessing pipeline builder."""

from typing import List, Tuple
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from banking_analytics.utils.logger import get_logger

logger = get_logger(__name__)

# Mandatory exclusions for classification to prevent data leakage (TRD Decision 5)
LEAKAGE_EXCLUSIONS = [
    "Application_ID",
    "Loan_Approved",
    "Default_Risk",
    "Approved_Amount",
    "Risk_Score",
    "Interest_Rate",
]


def select_features(
    df: pd.DataFrame,
    target_column: str = "Loan_Approved",
    excluded_features: List[str] = LEAKAGE_EXCLUSIONS,
    corr_threshold: float = 0.98,
) -> Tuple[pd.DataFrame, pd.Series, List[str], List[str], List[str]]:
    """Separates features X and target y, enforcing leakage exclusions and redundancy checks.

    Args:
        df: Cleaned dataset.
        target_column: Target label column name.
        excluded_features: List of column names to strictly exclude.
        corr_threshold: Correlation cutoff above which Monthly_Income is dropped if redundant.

    Returns:
        Tuple: (X, y, numeric_cols, categorical_cols, binary_cols)
    """
    logger.info("Separating features and target with strict leakage prevention audit.")

    # Target series
    y = df[target_column].copy()

    # Drop target and all leakage columns
    cols_to_drop = [c for c in excluded_features if c in df.columns]
    if target_column not in cols_to_drop:
        cols_to_drop.append(target_column)

    X = df.drop(columns=cols_to_drop).copy()
    logger.info("Excluded %d columns from classification features: %s", len(cols_to_drop), cols_to_drop)

    # Check redundancy: if Annual_Income and Monthly_Income both exist and corr > threshold
    if "Annual_Income" in X.columns and "Monthly_Income" in X.columns:
        corr = X[["Annual_Income", "Monthly_Income"]].corr().iloc[0, 1]
        if not np.isnan(corr) and corr >= corr_threshold:
            logger.info("Dropping redundant 'Monthly_Income' (corr with Annual_Income = %.4f >= %.2f)", corr, corr_threshold)
            X = X.drop(columns=["Monthly_Income"])

    # Identify column types
    binary_cols = [c for c in ["Co_Applicant", "Collateral"] if c in X.columns]
    categorical_cols = [
        c
        for c in [
            "Gender",
            "Marital_Status",
            "Education_Level",
            "Employment_Status",
            "Loan_Purpose",
            "Property_Ownership",
            "Residential_Status",
            "Application_Channel",
            "Region",
            "Previous_Loan_Status",
        ]
        if c in X.columns
    ]
    numeric_cols = [
        c for c in X.select_dtypes(include=[np.number]).columns if c not in binary_cols
    ]

    logger.info(
        "Feature matrix prepared: %d total features (%d numeric, %d categorical, %d binary).",
        len(X.columns),
        len(numeric_cols),
        len(categorical_cols),
        len(binary_cols),
    )
    return X, y, numeric_cols, categorical_cols, binary_cols


def build_preprocessor(
    numeric_cols: List[str],
    categorical_cols: List[str],
    binary_cols: List[str],
) -> ColumnTransformer:
    """Constructs a Scikit-Learn ColumnTransformer for preprocessing.

    - Numeric: Median imputation followed by StandardScaler.
    - Categorical: Most frequent imputation followed by OneHotEncoder (unknowns ignored).
    - Binary: Passthrough.
    """
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    binary_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("passthrough", "passthrough"),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
            ("bin", binary_transformer, binary_cols),
        ],
        remainder="drop",
    )
    return preprocessor


def split_data(
    X: pd.DataFrame,
    y: pd.Series,
    train_size: float = 0.70,
    val_size: float = 0.15,
    test_size: float = 0.15,
    random_seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """Splits data into stratified train, validation, and test subsets.

    Args:
        X: Feature matrix.
        y: Target series.
        train_size: Proportion for training (default 0.70).
        val_size: Proportion for validation (default 0.15).
        test_size: Proportion for testing (default 0.15).
        random_seed: Seed for reproducibility.

    Returns:
        Tuple: (X_train, X_val, X_test, y_train, y_val, y_test)
    """
    # First split off test set
    test_ratio = test_size / (train_size + val_size + test_size)
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=test_ratio, random_state=random_seed, stratify=y
    )

    # Then split temp into train and validation
    val_ratio = val_size / (train_size + val_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_ratio, random_state=random_seed, stratify=y_temp
    )

    logger.info(
        "Stratified split completed: Train=%d, Val=%d, Test=%d (Total=%d)",
        len(X_train),
        len(X_val),
        len(X_test),
        len(X),
    )
    return X_train, X_val, X_test, y_train, y_val, y_test
