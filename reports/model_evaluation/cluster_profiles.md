# Customer Segmentation & Risk Persona Report

**Clustering Algorithm:** K-Means ($k=4$)
**Evaluation Metrics:** Silhouette Score = 0.0607 | Stability Mean ARI = 0.9663

---

## 1. Segment Profiles & Risk Distribution

|   cluster_id | persona_label                      |   size |   pct_of_portfolio |   avg_credit_score |   avg_income |   avg_dti |   approval_rate | dominant_loan_purpose   |
|-------------:|:-----------------------------------|-------:|-------------------:|-------------------:|-------------:|----------:|----------------:|:------------------------|
|            0 | Core Mainstream Borrowers          |   5682 |              18.94 |              705.4 |     115857   |      7.07 |           69.92 | Car                     |
|            1 | Emerging Credit-Builder Applicants |   8646 |              28.82 |              621.5 |      57931.6 |     11.91 |           37.29 | Debt Consolidation      |
|            2 | Core Mainstream Borrowers (Tier 2) |   4665 |              15.55 |              687.7 |     106414   |     22.72 |           40.94 | Medical                 |
|            3 | Core Mainstream Borrowers (Tier 3) |  11007 |              36.69 |              707.1 |      91566.5 |      6.31 |           74.35 | Home                    |

---

## 2. Cluster Stability Audit
- **Seeds Evaluated:** [0, 42, 123, 456, 789]
- **Pairwise Adjusted Rand Index (ARI):** [0.9741, 0.9885, 0.9678, 0.9609, 0.9635, 0.9935, 0.9504, 0.9573, 0.9613, 0.9461]
- **Mean ARI:** 0.9663 (Stable)

---

## 3. Visual Artifacts
- Elbow Plot: `reports/figures/elbow_plot.png`
- Silhouette Plot: `reports/figures/silhouette_plot.png`
- 2D PCA Cluster Map: `reports/figures/cluster_pca.png`
