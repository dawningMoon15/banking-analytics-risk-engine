-- sql/queries/views/v_credit_risk_summary.sql
-- Reusable view: aggregates loan performance, average income, and DTI metrics by credit band

CREATE OR REPLACE VIEW v_credit_risk_summary AS
SELECT
    credit_band,
    COUNT(*)                                         AS total_applicants,
    SUM(loan_approved)                               AS approved_count,
    ROUND(SUM(loan_approved) * 100.0 / COUNT(*), 2)  AS approval_pct,
    ROUND(AVG(annual_income), 2)                     AS avg_annual_income,
    ROUND(AVG(debt_to_income_ratio), 2)             AS avg_dti,
    ROUND(AVG(credit_score), 1)                      AS avg_credit_score
FROM v_applicant_segments
GROUP BY credit_band;
