/**
 * Real-time Underwriting Risk Scoring Engine
 * Powered by regularized Logistic Regression trained on 30,000 real banking records.
 */

class UnderwritingSimulator {
  constructor(simParams) {
    this.intercept = simParams.intercept;
    this.threshold = simParams.threshold || 0.37;
    this.numStats = simParams.num_stats;
    this.catCategories = simParams.cat_categories;
    this.coefDict = simParams.coef_dict;
  }

  /**
   * Evaluates an applicant's loan application
   * @param {Object} input - borrower features
   * @returns {Object} score, probability, decision, contributions
   */
  evaluate(input) {
    let logOdds = this.intercept;
    const contributions = [];

    // Contribution from intercept
    contributions.push({
      feature: 'Model Intercept (Base Bias)',
      label: 'Base Baseline',
      contribution: this.intercept,
      type: 'neutral'
    });

    // 1. Numeric features: standard-scale then multiply by coefficient
    for (const [col, stats] of Object.entries(this.numStats)) {
      const val = input[col] !== undefined ? Number(input[col]) : stats.median;
      const zScore = (val - stats.mean) / stats.scale;
      const featKey = `num__${col}`;
      const coef = this.coefDict[featKey] || 0;
      const contrib = coef * zScore;
      logOdds += contrib;

      contributions.push({
        feature: col,
        label: this.formatFeatureLabel(col),
        value: val,
        contribution: contrib,
        type: contrib >= 0 ? 'positive' : 'negative'
      });
    }

    // 2. Binary features: binary 0/1 multiply by coefficient
    const binaryCols = ['Collateral', 'Co_Applicant'];
    for (const col of binaryCols) {
      const val = input[col] ? 1 : 0;
      const featKey = `bin__${col}`;
      const coef = this.coefDict[featKey] || 0;
      const contrib = coef * val;
      logOdds += contrib;

      contributions.push({
        feature: col,
        label: col === 'Collateral' ? 'Pledged Collateral' : 'Co-Applicant Endorsement',
        value: val ? 'Yes' : 'No',
        contribution: contrib,
        type: contrib >= 0 ? 'positive' : 'negative'
      });
    }

    // 3. Categorical features: One-Hot encode then multiply by coefficient
    for (const [col, cats] of Object.entries(this.catCategories)) {
      const selectedVal = input[col] || cats[0];
      for (const cat of cats) {
        const featKey = `cat__${col}_${cat}`;
        const coef = this.coefDict[featKey] || 0;
        const isPresent = (String(selectedVal) === String(cat)) ? 1 : 0;
        if (isPresent) {
          const contrib = coef * 1;
          logOdds += contrib;
          contributions.push({
            feature: `${col}: ${cat}`,
            label: `${this.formatFeatureLabel(col)}: ${cat}`,
            value: cat,
            contribution: contrib,
            type: contrib >= 0 ? 'positive' : 'negative'
          });
        }
      }
    }

    // Sigmoid probability
    const probability = 1 / (1 + Math.exp(-logOdds));
    const riskScore = Math.round((1 - probability) * 100);

    // Decision based on calibrated threshold
    let decision = 'REJECTED';
    let statusClass = 'status-rejected';
    let recommendation = 'High probability of default. Decline application or require significant equity/collateral restructure.';

    if (probability >= 0.60) {
      decision = 'AUTOMATED APPROVAL';
      statusClass = 'status-approved';
      recommendation = 'Prime applicant meeting automated underwriting standards. Fast-track loan agreement dispatch.';
    } else if (probability >= this.threshold) {
      decision = 'CONDITIONAL APPROVAL';
      statusClass = 'status-conditional';
      recommendation = 'Meets threshold criteria above 0.37 cut-off. Route to desk underwriter for collateral or co-signer verification.';
    }

    // Sort contributions by absolute impact
    const topDrivers = [...contributions]
      .filter(c => c.feature !== 'Model Intercept (Base Bias)')
      .sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution));

    return {
      logOdds,
      probability,
      approvalPct: (probability * 100).toFixed(1),
      riskScore,
      decision,
      statusClass,
      threshold: this.threshold,
      recommendation,
      topPositive: topDrivers.filter(c => c.contribution > 0).slice(0, 5),
      topNegative: topDrivers.filter(c => c.contribution < 0).slice(0, 5),
      allDrivers: topDrivers
    };
  }

  formatFeatureLabel(feat) {
    return feat
      .replace(/_/g, ' ')
      .replace(/([a-z])([A-Z])/g, '$1 $2');
  }
}

// Preset applicant profiles for live demonstration
const PRESET_APPLICANTS = {
  prime: {
    name: 'Prime Homebuyer (Low Risk)',
    Age: 42,
    Job_Experience_Years: 12,
    Annual_Income: 145000,
    Credit_Score: 785,
    Credit_History_Years: 16,
    Existing_Loans: 1,
    Late_Payments_Last_2_Years: 0,
    Loan_Amount: 32000,
    Loan_Term_Months: 60,
    Debt_To_Income_Ratio: 8.5,
    Savings_Balance: 48000,
    Checking_Balance: 12000,
    Total_Assets: 380000,
    Total_Liabilities: 65000,
    Monthly_Debt_Payment: 1020,
    Dependents: 1,
    Bank_Account_Age_Years: 10,
    Employment_Status: 'Salaried',
    Previous_Loan_Status: 'Paid Off',
    Loan_Purpose: 'Home',
    Property_Ownership: 'Owned',
    Residential_Status: 'Own',
    Education_Level: 'Master',
    Marital_Status: 'Married',
    Gender: 'Female',
    Application_Channel: 'Online',
    Region: 'North',
    Collateral: 1,
    Co_Applicant: 1
  },
  nearPrime: {
    name: 'Near-Prime Working Professional',
    Age: 31,
    Job_Experience_Years: 5,
    Annual_Income: 78000,
    Credit_Score: 655,
    Credit_History_Years: 7,
    Existing_Loans: 2,
    Late_Payments_Last_2_Years: 1,
    Loan_Amount: 22000,
    Loan_Term_Months: 48,
    Debt_To_Income_Ratio: 18.4,
    Savings_Balance: 11000,
    Checking_Balance: 4200,
    Total_Assets: 95000,
    Total_Liabilities: 32000,
    Monthly_Debt_Payment: 1190,
    Dependents: 0,
    Bank_Account_Age_Years: 6,
    Employment_Status: 'Salaried',
    Previous_Loan_Status: 'Active',
    Loan_Purpose: 'Car',
    Property_Ownership: 'Rented',
    Residential_Status: 'Rent',
    Education_Level: 'Bachelor',
    Marital_Status: 'Single',
    Gender: 'Male',
    Application_Channel: 'Online',
    Region: 'West',
    Collateral: 1,
    Co_Applicant: 0
  },
  highDti: {
    name: 'Overleveraged High DTI Applicant',
    Age: 48,
    Job_Experience_Years: 8,
    Annual_Income: 62000,
    Credit_Score: 590,
    Credit_History_Years: 6,
    Existing_Loans: 4,
    Late_Payments_Last_2_Years: 2,
    Loan_Amount: 48000,
    Loan_Term_Months: 72,
    Debt_To_Income_Ratio: 46.2,
    Savings_Balance: 2500,
    Checking_Balance: 850,
    Total_Assets: 45000,
    Total_Liabilities: 88000,
    Monthly_Debt_Payment: 2380,
    Dependents: 3,
    Bank_Account_Age_Years: 4,
    Employment_Status: 'Self-Employed',
    Previous_Loan_Status: 'No Previous Loan',
    Loan_Purpose: 'Debt Consolidation',
    Property_Ownership: 'Rented',
    Residential_Status: 'Rent',
    Education_Level: 'High School',
    Marital_Status: 'Married',
    Gender: 'Male',
    Application_Channel: 'Branch',
    Region: 'South',
    Collateral: 0,
    Co_Applicant: 0
  },
  defaultRisk: {
    name: 'Distressed Prior-Default Borrower',
    Age: 35,
    Job_Experience_Years: 2,
    Annual_Income: 38000,
    Credit_Score: 510,
    Credit_History_Years: 4,
    Existing_Loans: 3,
    Late_Payments_Last_2_Years: 4,
    Loan_Amount: 35000,
    Loan_Term_Months: 36,
    Debt_To_Income_Ratio: 52.0,
    Savings_Balance: 600,
    Checking_Balance: 150,
    Total_Assets: 12000,
    Total_Liabilities: 62000,
    Monthly_Debt_Payment: 1650,
    Dependents: 2,
    Bank_Account_Age_Years: 2,
    Employment_Status: 'Unemployed',
    Previous_Loan_Status: 'Defaulted',
    Loan_Purpose: 'Personal',
    Property_Ownership: 'Rented',
    Residential_Status: 'Rent',
    Education_Level: 'High School',
    Marital_Status: 'Single',
    Gender: 'Female',
    Application_Channel: 'Mobile',
    Region: 'East',
    Collateral: 0,
    Co_Applicant: 0
  }
};
