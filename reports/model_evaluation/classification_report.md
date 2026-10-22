# Default Risk Classification Model Evaluation Report

**Model:** Regularized Logistic Regression (`sklearn.linear_model.LogisticRegression`)
**Evaluation Dataset:** Held-out Test Set (30 records)

---

## 1. Executive Performance Summary

| Metric | Dummy Baseline | Logistic Regression (Threshold 0.50) | Logistic Regression (Optimal Threshold 0.1) |
|:-------|:---------------|:-------------------------------------|:-----------------------------------------------------------|
| **Accuracy** | 0.6333 | 0.3000 | **0.5333** |
| **Precision** | 0.0000 | 0.4286 | **0.5926** |
| **Recall** | 0.0000 | 0.3158 | **0.8421** |
| **F1-Score** | 0.7755 | 0.3636 | **0.6957** |
| **ROC-AUC** | 0.5000 | 0.2632 | **0.2632** |
| **PR-AUC** | 0.6333 | 0.5602 | **0.5602** |
| **Brier Score** | — | 0.4508 | **0.4508** |

---

## 2. Model Interpretability & Feature Odds Ratios

### Top 5 Positive Drivers (Increases Approval Odds)
| feature                         |   coefficient |   odds_ratio |
|:--------------------------------|--------------:|-------------:|
| Loan_Purpose_Debt Consolidation |        0.5849 |       1.7947 |
| Application_Channel_Online      |        0.4081 |       1.5039 |
| Employment_Status_Unemployed    |        0.3971 |       1.4875 |
| Savings_Balance                 |        0.378  |       1.4593 |
| Co_Applicant                    |        0.3758 |       1.4562 |

### Top 5 Risk Drivers (Increases Rejection Odds)
| feature           |   coefficient |   odds_ratio |
|:------------------|--------------:|-------------:|
| Region_Central    |       -0.4849 |       0.6158 |
| Loan_Amount       |       -0.4748 |       0.622  |
| Existing_Loans    |       -0.4669 |       0.6269 |
| Gender_Non-Binary |       -0.4343 |       0.6477 |
| Loan_Purpose_Home |       -0.4169 |       0.6591 |

---

## 3. Visual Artifacts
- ROC Curve: `reports/figures/roc_curve.png`
- PR Curve: `reports/figures/pr_curve.png`
- Confusion Matrix: `reports/figures/confusion_matrix.png`
- Coefficient Plot: `reports/figures/coefficient_plot.png`
