# Banking Customer Analytics & Risk Engine — Final Executive Report

**Project:** Banking Customer Analytics & Risk Engine
**Date Generated:** 2026-10-23 02:25:22
**Pipeline Status:** End-to-End Execution Complete (100% Tests Passing)

---

## 1. Executive Summary

This report presents findings from an end-to-end analytical and machine-learning risk evaluation of loan application records. The system applies rigorous data engineering, exploratory statistical inference, relational SQL analytics on DuckDB/PostgreSQL, regularized Logistic Regression default classification with strict leakage prevention, and unsupervised K-Means customer segmentation.

### Key Highlights:
1. **Portfolio Baseline:** Overall approval rate is **57.64%** across 30,000 evaluated applicants.
2. **Predictive Performance:** The default risk classifier achieved **ROC-AUC of 0.8866** and **PR-AUC of 0.9080**, significantly outperforming the zero-skill majority baseline (0.5764 accuracy).
3. **Primary Credit Drivers:** Credit Score and Debt-to-Income (DTI) ratio represent the most decisive quantitative underwriting factors. Co-applicant endorsement increases approval odds by **1.36x**.
4. **Actionable Segmentation:** Borrowers cluster into **4 distinct personas** displaying stark approval differences (ranging from low-risk prime applicants to high-leverage subprime applicants).

---

## 2. Exploratory Data Analysis & Statistical Findings

- **Credit Score Impact (AQ-02):** Approved applicants exhibit an average credit score of **714.7** compared to **630.6** for rejected applicants (Mann-Whitney U p-value = `0.0000e+00`).
- **Income Serviceability (AQ-03):** Mean annual income of approved borrowers is **$93,748.09** vs **$82,026.12** for rejected borrowers.
- **Leverage Ceiling (AQ-04):** DTI ratios exceeding 40% correlate with steep approval drop-offs regardless of borrower income quartile.
- **Loan Purpose (AQ-05):** Applications for **Car** experience the highest approval rates (61.55%), whereas **Medical** experiences the lowest (54.99%).

---

## 3. Relational Analytics & SQL Insights

Analytical queries executed across relational schemas verify key portfolio dynamics:
- `q01_overall_approval_rate.sql`: Quantifies overall volume and approval splits.
- `q02_approval_by_credit_score_band.sql`: Establishes FICO tier approval gradients.
- `q03_approval_by_income_band.sql`: Benchmarks income quartile approval distributions.
- `q04_dti_vs_approval.sql`: Compares leverage bands against mean credit quality.
- `q05_approval_by_loan_purpose.sql`: Ranks loan purpose demand and conversion.
- `q06_risk_score_distribution.sql`: Computes summary statistics across outcome groups.

---

## 4. Default Risk Predictive Modeling (Logistic Regression)

Strict leakage auditing was enforced prior to training:
- **Excluded Features:** `Loan_Approved`, `Default_Risk`, `Approved_Amount`, `Risk_Score`, `Interest_Rate`, and `Application_ID`.
- **Pipeline Architecture:** Scikit-Learn `ColumnTransformer` (median imputation + `StandardScaler` for numeric, most frequent imputation + `OneHotEncoder` for categorical) coupled to `LogisticRegression(class_weight='balanced')`.

### Held-out Test Set Performance:
- **ROC-AUC:** 0.8866
- **PR-AUC:** 0.9080
- **Optimal Decision Threshold:** 0.37
- **Accuracy at Optimal Threshold:** 0.8080
- **F1-Score at Optimal Threshold:** 0.8440
- **Brier Score (Calibration):** 0.1350

---

## 5. Customer Segmentation & Persona Profiles

Borrowers were clustered unsupervised using K-Means ($k=4$) based on financial attributes, balance sheets, and request features:

|   cluster_id | persona_label                      |   size |   pct_of_portfolio |   avg_credit_score |   avg_income |   avg_dti |   approval_rate | dominant_loan_purpose   |
|-------------:|:-----------------------------------|-------:|-------------------:|-------------------:|-------------:|----------:|----------------:|:------------------------|
|            0 | Core Mainstream Borrowers          |   5682 |              18.94 |              705.4 |     115857   |      7.07 |           69.92 | Car                     |
|            1 | Emerging Credit-Builder Applicants |   8646 |              28.82 |              621.5 |      57931.6 |     11.91 |           37.29 | Debt Consolidation      |
|            2 | Core Mainstream Borrowers (Tier 2) |   4665 |              15.55 |              687.7 |     106414   |     22.72 |           40.94 | Medical                 |
|            3 | Core Mainstream Borrowers (Tier 3) |  11007 |              36.69 |              707.1 |      91566.5 |      6.31 |           74.35 | Home                    |

- **Silhouette Score:** 0.0607
- **Cluster Stability Across 5 Seeds:** Mean ARI = 0.9663

---

## 6. Cross-Referenced Segment Risk Analysis

By projecting the supervised classification model's predicted approval probabilities onto unsupervised customer segments, we evaluate intra-segment credit risk:

|   cluster |   applicant_count |   actual_approval_rate |   mean_predicted_prob |   median_predicted_prob |   high_risk_pct |
|----------:|------------------:|-----------------------:|----------------------:|------------------------:|----------------:|
|         0 |              5682 |                  69.92 |                0.6757 |                  0.7956 |           21.98 |
|         1 |              8646 |                  37.29 |                0.3381 |                  0.257  |           60.86 |
|         2 |              4665 |                  40.94 |                0.3602 |                  0.3028 |           58.29 |
|         3 |             11007 |                  74.35 |                0.6964 |                  0.7958 |           17.76 |

---

## 7. Policy Recommendations & Next Steps

1. **Automated Tiered Underwriting:**
   - Fast-track applicants fitting the **Prime Low-Risk** profile (Credit Score > 720, DTI < 30%) with automated approval rules.
   - Route near-prime or high-DTI applicants to manual underwriting, requiring collateral or co-applicant backing.
2. **Dynamic Risk-Based Pricing:**
   - Introduce calibrated interest rate surcharges for applicant segments exhibiting elevated default probabilities rather than issuing flat rejections.
3. **Fair Lending & Governance:**
   - Continuously monitor model predictions across demographic slices (AQ-08) to maintain compliance with fair lending statutes (ECOA / FCRA) and prevent proxy discrimination.

---
*Report artifact generated by Banking Customer Analytics & Risk Engine.*
