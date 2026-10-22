-- q02_approval_by_credit_score_band.sql
-- Business Question: How does approval rate vary across credit score bands?
-- Expected Output: Credit band label, total applicants, approved count, approval percentage

SELECT
    CASE
        WHEN credit_score < 580 THEN 'Poor (300-579)'
        WHEN credit_score < 670 THEN 'Fair (580-669)'
        WHEN credit_score < 740 THEN 'Good (670-739)'
        WHEN credit_score < 800 THEN 'Very Good (740-799)'
        ELSE 'Exceptional (800-850)'
    END                                                      AS credit_band,
    COUNT(*)                                                 AS total,
    SUM(loan_approved)                                       AS approved,
    ROUND(SUM(loan_approved) * 100.0 / COUNT(*), 2)         AS approval_pct
FROM loan_applications
GROUP BY 1
ORDER BY MIN(credit_score);
