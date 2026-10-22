-- q04_dti_vs_approval.sql
-- Business Question: How does debt-to-income ratio relate to approval outcomes?
-- Expected Output: DTI band, total applicants, approval percentage, average credit score

SELECT
    CASE
        WHEN debt_to_income_ratio < 20  THEN 'Low DTI (<20%)'
        WHEN debt_to_income_ratio < 40  THEN 'Moderate DTI (20-40%)'
        WHEN debt_to_income_ratio < 60  THEN 'High DTI (40-60%)'
        ELSE 'Very High DTI (>60%)'
    END                                                      AS dti_band,
    COUNT(*)                                                 AS total,
    ROUND(SUM(loan_approved) * 100.0 / COUNT(*), 2)         AS approval_pct,
    ROUND(AVG(credit_score), 1)                              AS avg_credit_score
FROM loan_applications
GROUP BY 1
ORDER BY MIN(debt_to_income_ratio);
