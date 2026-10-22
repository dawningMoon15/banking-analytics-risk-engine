-- q03_approval_by_income_band.sql
-- Business Question: How does approval rate differ across income quartiles?
-- Expected Output: Income quartile, income min, income max, total applicants, approval percentage

WITH income_quartiles AS (
    SELECT
        loan_approved,
        annual_income,
        NTILE(4) OVER (ORDER BY annual_income) AS income_quartile
    FROM loan_applications
)
SELECT
    income_quartile,
    MIN(annual_income)                                       AS income_min,
    MAX(annual_income)                                       AS income_max,
    COUNT(*)                                                 AS total,
    ROUND(SUM(loan_approved) * 100.0 / COUNT(*), 2)         AS approval_pct
FROM income_quartiles
GROUP BY income_quartile
ORDER BY income_quartile;
