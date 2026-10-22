-- q05_approval_by_loan_purpose.sql
-- Business Question: Which loan purposes have the highest and lowest approval rates?
-- Expected Output: Loan purpose, total applicants, approved count, approval percentage

SELECT
    loan_purpose,
    COUNT(*)                                                 AS total,
    SUM(loan_approved)                                       AS approved,
    ROUND(SUM(loan_approved) * 100.0 / COUNT(*), 2)         AS approval_pct
FROM loan_applications
GROUP BY loan_purpose
ORDER BY approval_pct DESC;
