"""Pytest fixtures for unit and integration testing."""

import numpy as np
import pandas as pd
import pytest

ALL_36_COLUMNS = [
    "Application_ID",
    "Age",
    "Gender",
    "Marital_Status",
    "Education_Level",
    "Employment_Status",
    "Job_Experience_Years",
    "Annual_Income",
    "Monthly_Income",
    "Credit_Score",
    "Credit_History_Years",
    "Existing_Loans",
    "Late_Payments_Last_2_Years",
    "Loan_Amount",
    "Loan_Term_Months",
    "Loan_Purpose",
    "Interest_Rate",
    "Debt_To_Income_Ratio",
    "Savings_Balance",
    "Checking_Balance",
    "Total_Assets",
    "Total_Liabilities",
    "Monthly_Debt_Payment",
    "Property_Ownership",
    "Residential_Status",
    "Dependents",
    "Co_Applicant",
    "Collateral",
    "Application_Channel",
    "Region",
    "Bank_Account_Age_Years",
    "Previous_Loan_Status",
    "Risk_Score",
    "Default_Risk",
    "Approved_Amount",
    "Loan_Approved",
]


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Generate a clean, valid DataFrame with 200 rows and all 36 columns for unit tests."""
    np.random.seed(42)
    n = 200

    annual_income = np.random.uniform(25000, 180000, n).round(2)
    monthly_income = (annual_income / 12.0).round(2)
    loan_amount = np.random.uniform(5000, 75000, n).round(2)
    loan_approved = np.random.choice([0, 1], size=n, p=[0.4, 0.6])
    approved_amount = np.where(loan_approved == 1, loan_amount, 0.0)

    data = {
        "Application_ID": [f"APP{i:05d}" for i in range(n)],
        "Age": np.random.randint(22, 65, n),
        "Gender": np.random.choice(["Male", "Female", "Non-Binary"], n),
        "Marital_Status": np.random.choice(["Single", "Married", "Divorced"], n),
        "Education_Level": np.random.choice(["High School", "Bachelor", "Master", "PhD"], n),
        "Employment_Status": np.random.choice(["Employed", "Self-Employed", "Unemployed"], n),
        "Job_Experience_Years": np.random.uniform(0.5, 30.0, n).round(1),
        "Annual_Income": annual_income,
        "Monthly_Income": monthly_income,
        "Credit_Score": np.random.randint(450, 850, n),
        "Credit_History_Years": np.random.uniform(1.0, 25.0, n).round(1),
        "Existing_Loans": np.random.randint(0, 5, n),
        "Late_Payments_Last_2_Years": np.random.randint(0, 4, n),
        "Loan_Amount": loan_amount,
        "Loan_Term_Months": np.random.choice([12, 24, 36, 48, 60], n),
        "Loan_Purpose": np.random.choice(["Home", "Auto", "Personal", "Education", "Debt Consolidation"], n),
        "Interest_Rate": np.random.uniform(5.5, 22.0, n).round(2),
        "Debt_To_Income_Ratio": np.random.uniform(10.0, 65.0, n).round(2),
        "Savings_Balance": np.random.uniform(500, 40000, n).round(2),
        "Checking_Balance": np.random.uniform(200, 15000, n).round(2),
        "Total_Assets": np.random.uniform(10000, 350000, n).round(2),
        "Total_Liabilities": np.random.uniform(2000, 150000, n).round(2),
        "Monthly_Debt_Payment": np.random.uniform(100, 3000, n).round(2),
        "Property_Ownership": np.random.choice(["Own", "Rent", "Mortgage"], n),
        "Residential_Status": np.random.choice(["Permanent", "Temporary", "Living with Parents"], n),
        "Dependents": np.random.randint(0, 5, n),
        "Co_Applicant": np.random.choice([0, 1], n),
        "Collateral": np.random.choice([0, 1], n),
        "Application_Channel": np.random.choice(["Online", "In-Person", "Mobile App"], n),
        "Region": np.random.choice(["North", "South", "East", "West", "Central"], n),
        "Bank_Account_Age_Years": np.random.uniform(1.0, 20.0, n).round(1),
        "Previous_Loan_Status": np.random.choice(["Fully Paid", "Current", "Defaulted", "No Previous Loan"], n),
        "Risk_Score": np.random.uniform(15.0, 90.0, n).round(2),
        "Default_Risk": np.random.choice(["Low", "Medium", "High"], n),
        "Approved_Amount": approved_amount,
        "Loan_Approved": loan_approved,
    }
    return pd.DataFrame(data)
