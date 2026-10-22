-- q06_risk_score_distribution.sql
-- Business Question: How is the risk score distributed across approved and rejected loans?
-- Expected Output: loan_approved status, avg, median, stddev, min, and max risk scores

SELECT
    loan_approved,
    ROUND(AVG(risk_score), 2)                               AS avg_risk_score,
    ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY risk_score) AS NUMERIC), 2) AS median_risk_score,
    ROUND(STDDEV(risk_score), 2)                            AS std_risk_score,
    MIN(risk_score)                                         AS min_risk_score,
    MAX(risk_score)                                         AS max_risk_score
FROM loan_applications
GROUP BY loan_approved
ORDER BY loan_approved DESC;
