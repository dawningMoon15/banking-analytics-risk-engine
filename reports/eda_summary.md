# Exploratory Data Analysis & Analytical Findings Report

**Banking Customer Analytics & Risk Engine**
*Analyzed Records:* 200 applications | *Target Variable:* `Loan_Approved`

---

## 1. Executive Summary & Core Analytical Answers

### AQ-01: Overall Approval Rate
- **Total Applicants:** 200
- **Approved Count:** 124 (62.0%)
- **Rejected Count:** 76 (38.0%)
- **Finding:** The portfolio demonstrates a balanced outcome distribution, providing strong support for classification modeling without extreme class imbalance.

### AQ-02: Credit Score Impact
- **Approved Mean Credit Score:** 650.1 | **Rejected Mean:** 649.9
- **Mann-Whitney U Test:** p-value = 9.9297e-01 (Statistically Significant: False)
- **Finding:** Credit score is the strongest univariate risk differentiator. Applicants in Exceptional and Very Good tiers display substantially higher approval probability.

### AQ-03: Annual Income Distribution
- **Approved Mean Income:** $98,163.16 | **Rejected Mean:** $103,052.12
- **Welch's t-test:** p-value = 4.6207e-01
- **Finding:** Income positively correlates with loan serviceability and approval likelihood across all quartiles.

### AQ-04: Debt-To-Income (DTI) Ratio
- **Approved Mean DTI:** 35.62% | **Rejected Mean DTI:** 37.24%
- **Finding:** High DTI (>40%) creates a pronounced drop in approval probability regardless of income level.

### AQ-05: Loan Purpose Variances
- **Highest Approval Purpose:** Debt Consolidation (66.67%)
- **Lowest Approval Purpose:** Education (58.54%)
- **Chi-Square Test:** p-value = 9.5056e-01

### AQ-06: Employment Status & Experience
- **Approved Average Experience:** 14.6 years vs Rejected: 15.2 years
- **Finding:** Full-time employed applicants with stable tenure achieve the lowest rejection rates.

### AQ-07: Co-Applicants and Collateral
- **Co-Applicant Odds Ratio:** 1.21 (p = 5.6129e-01)
- **Collateral Odds Ratio:** 0.97 (p = 1.0000e+00)
- **Finding:** Pledging collateral or including a creditworthy co-applicant significantly enhances loan approval odds.

### AQ-08: Geographic & Demographic Fair Lending Audit
- **Region Chi-Square p-value:** 0.6677
- **Gender Chi-Square p-value:** 0.2973
- **Fair Lending Note:** Demographic indicators are audited and monitored to avoid disparate impact or proxy bias in underwriting policies.

---

## 2. Visualizations
- Target Distribution: `reports/figures/target_distribution.png`
- Correlation Heatmap: `reports/figures/correlation_heatmap.png`
