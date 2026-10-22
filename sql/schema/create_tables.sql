-- sql/schema/create_tables.sql
-- Table definition and indexing for loan applications in Banking Analytics

CREATE TABLE IF NOT EXISTS loan_applications (
    application_id          VARCHAR(64) PRIMARY KEY,
    age                     INTEGER         CHECK (age BETWEEN 18 AND 100),
    gender                  VARCHAR(32),
    marital_status          VARCHAR(32),
    education_level         VARCHAR(64),
    employment_status       VARCHAR(64),
    job_experience_years    NUMERIC(5,2),
    annual_income           NUMERIC(15,2),
    monthly_income          NUMERIC(15,2),
    credit_score            INTEGER         CHECK (credit_score BETWEEN 300 AND 850),
    credit_history_years    NUMERIC(5,2),
    existing_loans          INTEGER         CHECK (existing_loans >= 0),
    late_payments_last_2_years INTEGER      CHECK (late_payments_last_2_years >= 0),
    loan_amount             NUMERIC(15,2),
    loan_term_months        INTEGER         CHECK (loan_term_months > 0),
    loan_purpose            VARCHAR(64),
    interest_rate           NUMERIC(6,4),
    debt_to_income_ratio    NUMERIC(8,4),
    savings_balance         NUMERIC(15,2),
    checking_balance        NUMERIC(15,2),
    total_assets            NUMERIC(15,2),
    total_liabilities       NUMERIC(15,2),
    monthly_debt_payment    NUMERIC(15,2),
    property_ownership      VARCHAR(32),
    residential_status      VARCHAR(64),
    dependents              INTEGER         CHECK (dependents >= 0),
    co_applicant            INTEGER         CHECK (co_applicant IN (0, 1)),
    collateral              INTEGER         CHECK (collateral IN (0, 1)),
    application_channel     VARCHAR(64),
    region                  VARCHAR(64),
    bank_account_age_years  NUMERIC(5,2),
    previous_loan_status    VARCHAR(64),
    risk_score              NUMERIC(6,2)    CHECK (risk_score BETWEEN 0 AND 100),
    default_risk            VARCHAR(32),
    approved_amount         NUMERIC(15,2),
    loan_approved           INTEGER         NOT NULL CHECK (loan_approved IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_credit_score ON loan_applications(credit_score);
CREATE INDEX IF NOT EXISTS idx_loan_approved ON loan_applications(loan_approved);
CREATE INDEX IF NOT EXISTS idx_loan_purpose ON loan_applications(loan_purpose);
CREATE INDEX IF NOT EXISTS idx_region ON loan_applications(region);
