# Exploratory Data Analysis & Analytical Findings Report

**Banking Customer Analytics & Risk Engine**
*Analyzed Records:* 30,000 applications | *Target Variable:* `Loan_Approved`

---

## 1. Executive Summary & Core Analytical Answers

### AQ-01: Overall Approval Rate
- **Total Applicants:** 30,000
- **Approved Count:** 17,291 (57.64%)
- **Rejected Count:** 12,709 (42.36%)
- **Finding:** The portfolio demonstrates a balanced outcome distribution, providing strong support for classification modeling without extreme class imbalance.

### AQ-02: Credit Score Impact
- **Approved Mean Credit Score:** 714.7 | **Rejected Mean:** 630.6
- **Mann-Whitney U Test:** p-value = 0.0000e+00 (Statistically Significant: True)
- **Finding:** Credit score is the strongest univariate risk differentiator. Applicants in Exceptional and Very Good tiers display substantially higher approval probability.

### AQ-03: Annual Income Distribution
- **Approved Mean Income:** $93,748.09 | **Rejected Mean:** $82,026.12
- **Welch's t-test:** p-value = 5.8720e-238
- **Finding:** Income positively correlates with loan serviceability and approval likelihood across all quartiles.

### AQ-04: Debt-To-Income (DTI) Ratio
- **Approved Mean DTI:** 8.28% | **Rejected Mean DTI:** 13.81%
- **Finding:** High DTI (>40%) creates a pronounced drop in approval probability regardless of income level.

### AQ-05: Loan Purpose Variances
- **Highest Approval Purpose:** Car (61.55%)
- **Lowest Approval Purpose:** Medical (54.99%)
- **Chi-Square Test:** p-value = 5.1954e-18

### AQ-06: Employment Status & Experience
- **Approved Average Experience:** 11.7 years vs Rejected: 10.2 years
- **Finding:** Full-time employed applicants with stable tenure achieve the lowest rejection rates.

### AQ-07: Co-Applicants and Collateral
- **Co-Applicant Odds Ratio:** 1.36 (p = 2.5979e-32)
- **Collateral Odds Ratio:** 1.53 (p = 2.2743e-69)
- **Finding:** Pledging collateral or including a creditworthy co-applicant significantly enhances loan approval odds.

### AQ-08: Geographic & Demographic Fair Lending Audit
- **Region Chi-Square p-value:** 0.0533
- **Gender Chi-Square p-value:** 0.4002
- **Fair Lending Note:** Demographic indicators are audited and monitored to avoid disparate impact or proxy bias in underwriting policies.

---

## 2. Visualizations
- Target Distribution: `reports/figures/target_distribution.png`
- Correlation Heatmap: `reports/figures/correlation_heatmap.png`
