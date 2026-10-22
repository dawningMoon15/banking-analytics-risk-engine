# Customer Segmentation & Risk Persona Report

**Clustering Algorithm:** K-Means ($k=3$)
**Evaluation Metrics:** Silhouette Score = 0.0370 | Stability Mean ARI = 0.1540

---

## 1. Segment Profiles & Risk Distribution

|   cluster_id | persona_label                               |   size |   pct_of_portfolio |   avg_credit_score |   avg_income |   avg_dti |   approval_rate | dominant_loan_purpose   |
|-------------:|:--------------------------------------------|-------:|-------------------:|-------------------:|-------------:|----------:|----------------:|:------------------------|
|            0 | Emerging Credit-Builder Applicants          |     63 |               31.5 |              581.7 |      78457.4 |     42.11 |           66.67 | Home                    |
|            1 | Emerging Credit-Builder Applicants (Tier 2) |     69 |               34.5 |              645   |      96268.9 |     30.68 |           62.32 | Home                    |
|            2 | Core Mainstream Borrowers                   |     68 |               34   |              718.5 |     123806   |     36.42 |           57.35 | Debt Consolidation      |

---

## 2. Cluster Stability Audit
- **Seeds Evaluated:** [0, 42]
- **Pairwise Adjusted Rand Index (ARI):** [0.154]
- **Mean ARI:** 0.1540 (Moderate Variability)

---

## 3. Visual Artifacts
- Elbow Plot: `reports/figures/elbow_plot.png`
- Silhouette Plot: `reports/figures/silhouette_plot.png`
- 2D PCA Cluster Map: `reports/figures/cluster_pca.png`
