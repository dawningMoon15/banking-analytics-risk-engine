# Default Risk Classification Model Evaluation Report

**Model:** Regularized Logistic Regression (`sklearn.linear_model.LogisticRegression`)
**Evaluation Dataset:** Held-out Test Set (4,500 records)

---

## 1. Executive Performance Summary

| Metric | Dummy Baseline | Logistic Regression (Threshold 0.50) | Logistic Regression (Optimal Threshold 0.37) |
|:-------|:---------------|:-------------------------------------|:-----------------------------------------------------------|
| **Accuracy** | 0.5764 | 0.8009 | **0.8080** |
| **Precision** | 0.0000 | 0.8314 | **0.7938** |
| **Recall** | 0.0000 | 0.8211 | **0.9009** |
| **F1-Score** | 0.7313 | 0.8262 | **0.8440** |
| **ROC-AUC** | 0.5000 | 0.8866 | **0.8866** |
| **PR-AUC** | 0.5764 | 0.9080 | **0.9080** |
| **Brier Score** | — | 0.1350 | **0.1350** |

---

## 2. Model Interpretability & Feature Odds Ratios

### Top 5 Positive Drivers (Increases Approval Odds)
| feature                               |   coefficient |   odds_ratio |
|:--------------------------------------|--------------:|-------------:|
| Previous_Loan_Status_Paid Off         |        1.2774 |       3.5874 |
| Credit_Score                          |        1.134  |       3.1079 |
| Collateral                            |        0.8277 |       2.2879 |
| Co_Applicant                          |        0.5436 |       1.7223 |
| Previous_Loan_Status_No Previous Loan |        0.4997 |       1.6483 |

### Top 5 Risk Drivers (Increases Rejection Odds)
| feature                        |   coefficient |   odds_ratio |
|:-------------------------------|--------------:|-------------:|
| Previous_Loan_Status_Defaulted |       -2.6146 |       0.0732 |
| Employment_Status_Unemployed   |       -1.7788 |       0.1688 |
| Loan_Amount                    |       -0.9173 |       0.3996 |
| Debt_To_Income_Ratio           |       -0.6783 |       0.5075 |
| Late_Payments_Last_2_Years     |       -0.6426 |       0.5259 |

---

## 3. Visual Artifacts
- ROC Curve: `reports/figures/roc_curve.png`
- PR Curve: `reports/figures/pr_curve.png`
- Confusion Matrix: `reports/figures/confusion_matrix.png`
- Coefficient Plot: `reports/figures/coefficient_plot.png`
