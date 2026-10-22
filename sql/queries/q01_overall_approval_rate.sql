-- q01_overall_approval_rate.sql
-- Business Question: What is the overall loan approval rate in the dataset?
-- Expected Output: Rows with loan_approved flag, applicant count, and percentage of total

SELECT
    loan_approved,
    COUNT(*)                                            AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct
FROM loan_applications
GROUP BY loan_approved
ORDER BY loan_approved DESC;
