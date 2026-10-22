-- sql/queries/views/v_applicant_segments.sql
-- Reusable view: enriches each application with credit band and DTI band labels

CREATE OR REPLACE VIEW v_applicant_segments AS
SELECT
    application_id,
    loan_approved,
    annual_income,
    credit_score,
    debt_to_income_ratio,
    loan_purpose,
    region,
    CASE
        WHEN credit_score < 580 THEN 'Poor'
        WHEN credit_score < 670 THEN 'Fair'
        WHEN credit_score < 740 THEN 'Good'
        WHEN credit_score < 800 THEN 'Very Good'
        ELSE 'Exceptional'
    END AS credit_band,
    CASE
        WHEN debt_to_income_ratio < 20 THEN 'Low'
        WHEN debt_to_income_ratio < 40 THEN 'Moderate'
        WHEN debt_to_income_ratio < 60 THEN 'High'
        ELSE 'Very High'
    END AS dti_band
FROM loan_applications;
