// Auto-generated real data payload for Banking Customer Analytics & Risk Engine
const BANKING_DATA = {
  "summary": {
    "total_records": 30000,
    "approved_records": 17291,
    "rejected_records": 12709,
    "approval_rate": 57.64,
    "avg_credit_score_approved": 714.7,
    "avg_credit_score_rejected": 630.6,
    "avg_income_approved": 93748.09,
    "avg_income_rejected": 82026.12,
    "roc_auc": 0.8866,
    "pr_auc": 0.908,
    "optimal_threshold": 0.37,
    "accuracy_at_optimal": 80.8,
    "f1_at_optimal": 0.844,
    "recall_at_optimal": 90.09,
    "precision_at_optimal": 79.38,
    "brier_score": 0.135,
    "cluster_stability_ari": 0.9663,
    "cluster_silhouette": 0.0607
  },
  "sql_queries": {
    "q01_overall_approval_rate.sql": {
      "sql": "-- q01_overall_approval_rate.sql\n-- Business Question: What is the overall loan approval rate in the dataset?\n-- Expected Output: Rows with loan_approved flag, applicant count, and percentage of total\n\nSELECT\n    loan_approved,\n    COUNT(*)                                            AS count,\n    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct\nFROM loan_applications\nGROUP BY loan_approved\nORDER BY loan_approved DESC;\n",
      "records": [
        {
          "loan_approved": 1,
          "count": 17291,
          "pct": 57.64
        },
        {
          "loan_approved": 0,
          "count": 12709,
          "pct": 42.36
        }
      ],
      "columns": [
        "loan_approved",
        "count",
        "pct"
      ]
    },
    "q02_approval_by_credit_score_band.sql": {
      "sql": "-- q02_approval_by_credit_score_band.sql\n-- Business Question: How does approval rate vary across credit score bands?\n-- Expected Output: Credit band label, total applicants, approved count, approval percentage\n\nSELECT\n    CASE\n        WHEN credit_score < 580 THEN 'Poor (300-579)'\n        WHEN credit_score < 670 THEN 'Fair (580-669)'\n        WHEN credit_score < 740 THEN 'Good (670-739)'\n        WHEN credit_score < 800 THEN 'Very Good (740-799)'\n        ELSE 'Exceptional (800-850)'\n    END                                                      AS credit_band,\n    COUNT(*)                                                 AS total,\n    SUM(loan_approved)                                       AS approved,\n    ROUND(SUM(loan_approved) * 100.0 / COUNT(*), 2)         AS approval_pct\nFROM loan_applications\nGROUP BY 1\nORDER BY MIN(credit_score);\n",
      "records": [
        {
          "credit_band": "Poor (300-579)",
          "total": 4048,
          "approved": 443.0,
          "approval_pct": 10.94
        },
        {
          "credit_band": "Fair (580-669)",
          "total": 9448,
          "approved": 4493.0,
          "approval_pct": 47.56
        },
        {
          "credit_band": "Good (670-739)",
          "total": 8795,
          "approved": 5890.0,
          "approval_pct": 66.97
        },
        {
          "credit_band": "Very Good (740-799)",
          "total": 4937,
          "approved": 3983.0,
          "approval_pct": 80.68
        },
        {
          "credit_band": "Exceptional (800-850)",
          "total": 2772,
          "approved": 2482.0,
          "approval_pct": 89.54
        }
      ],
      "columns": [
        "credit_band",
        "total",
        "approved",
        "approval_pct"
      ]
    },
    "q03_approval_by_income_band.sql": {
      "sql": "-- q03_approval_by_income_band.sql\n-- Business Question: How does approval rate differ across income quartiles?\n-- Expected Output: Income quartile, income min, income max, total applicants, approval percentage\n\nWITH income_quartiles AS (\n    SELECT\n        loan_approved,\n        annual_income,\n        NTILE(4) OVER (ORDER BY annual_income) AS income_quartile\n    FROM loan_applications\n)\nSELECT\n    income_quartile,\n    MIN(annual_income)                                       AS income_min,\n    MAX(annual_income)                                       AS income_max,\n    COUNT(*)                                                 AS total,\n    ROUND(SUM(loan_approved) * 100.0 / COUNT(*), 2)         AS approval_pct\nFROM income_quartiles\nGROUP BY income_quartile\nORDER BY income_quartile;\n",
      "records": [
        {
          "income_quartile": 1,
          "income_min": 5000.0,
          "income_max": 68081.82,
          "total": 7500,
          "approval_pct": 43.03
        },
        {
          "income_quartile": 2,
          "income_min": 68087.28,
          "income_max": 88621.9,
          "total": 7500,
          "approval_pct": 55.96
        },
        {
          "income_quartile": 3,
          "income_min": 88624.24,
          "income_max": 109100.91,
          "total": 7500,
          "approval_pct": 64.35
        },
        {
          "income_quartile": 4,
          "income_min": 109101.41,
          "income_max": 211985.4,
          "total": 7500,
          "approval_pct": 67.21
        }
      ],
      "columns": [
        "income_quartile",
        "income_min",
        "income_max",
        "total",
        "approval_pct"
      ]
    },
    "q04_dti_vs_approval.sql": {
      "sql": "-- q04_dti_vs_approval.sql\n-- Business Question: How does debt-to-income ratio relate to approval outcomes?\n-- Expected Output: DTI band, total applicants, approval percentage, average credit score\n\nSELECT\n    CASE\n        WHEN debt_to_income_ratio < 20  THEN 'Low DTI (<20%)'\n        WHEN debt_to_income_ratio < 40  THEN 'Moderate DTI (20-40%)'\n        WHEN debt_to_income_ratio < 60  THEN 'High DTI (40-60%)'\n        ELSE 'Very High DTI (>60%)'\n    END                                                      AS dti_band,\n    COUNT(*)                                                 AS total,\n    ROUND(SUM(loan_approved) * 100.0 / COUNT(*), 2)         AS approval_pct,\n    ROUND(AVG(credit_score), 1)                              AS avg_credit_score\nFROM loan_applications\nGROUP BY 1\nORDER BY MIN(debt_to_income_ratio);\n",
      "records": [
        {
          "dti_band": "Low DTI (<20%)",
          "total": 26232,
          "approval_pct": 61.55,
          "avg_credit_score": 681.4
        },
        {
          "dti_band": "Moderate DTI (20-40%)",
          "total": 3214,
          "approval_pct": 33.11,
          "avg_credit_score": 666.9
        },
        {
          "dti_band": "High DTI (40-60%)",
          "total": 455,
          "approval_pct": 16.48,
          "avg_credit_score": 648.9
        },
        {
          "dti_band": "Very High DTI (>60%)",
          "total": 99,
          "approval_pct": 5.05,
          "avg_credit_score": 606.5
        }
      ],
      "columns": [
        "dti_band",
        "total",
        "approval_pct",
        "avg_credit_score"
      ]
    },
    "q05_approval_by_loan_purpose.sql": {
      "sql": "-- q05_approval_by_loan_purpose.sql\n-- Business Question: Which loan purposes have the highest and lowest approval rates?\n-- Expected Output: Loan purpose, total applicants, approved count, approval percentage\n\nSELECT\n    loan_purpose,\n    COUNT(*)                                                 AS total,\n    SUM(loan_approved)                                       AS approved,\n    ROUND(SUM(loan_approved) * 100.0 / COUNT(*), 2)         AS approval_pct\nFROM loan_applications\nGROUP BY loan_purpose\nORDER BY approval_pct DESC;\n",
      "records": [
        {
          "loan_purpose": "Car",
          "total": 4349,
          "approved": 2677.0,
          "approval_pct": 61.55
        },
        {
          "loan_purpose": "Home",
          "total": 4245,
          "approved": 2596.0,
          "approval_pct": 61.15
        },
        {
          "loan_purpose": "Business",
          "total": 4193,
          "approved": 2497.0,
          "approval_pct": 59.55
        },
        {
          "loan_purpose": "Personal",
          "total": 4310,
          "approved": 2397.0,
          "approval_pct": 55.61
        },
        {
          "loan_purpose": "Debt Consolidation",
          "total": 4331,
          "approved": 2404.0,
          "approval_pct": 55.51
        },
        {
          "loan_purpose": "Education",
          "total": 4242,
          "approved": 2339.0,
          "approval_pct": 55.14
        },
        {
          "loan_purpose": "Medical",
          "total": 4330,
          "approved": 2381.0,
          "approval_pct": 54.99
        }
      ],
      "columns": [
        "loan_purpose",
        "total",
        "approved",
        "approval_pct"
      ]
    },
    "q06_risk_score_distribution.sql": {
      "sql": "-- q06_risk_score_distribution.sql\n-- Business Question: How is the risk score distributed across approved and rejected loans?\n-- Expected Output: loan_approved status, avg, median, stddev, min, and max risk scores\n\nSELECT\n    loan_approved,\n    ROUND(AVG(risk_score), 2)                               AS avg_risk_score,\n    ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY risk_score) AS NUMERIC), 2) AS median_risk_score,\n    ROUND(STDDEV(risk_score), 2)                            AS std_risk_score,\n    MIN(risk_score)                                         AS min_risk_score,\n    MAX(risk_score)                                         AS max_risk_score\nFROM loan_applications\nGROUP BY loan_approved\nORDER BY loan_approved DESC;\n",
      "records": [
        {
          "loan_approved": 1,
          "avg_risk_score": 33.99,
          "median_risk_score": 34.12,
          "std_risk_score": 15.19,
          "min_risk_score": 0.0,
          "max_risk_score": 100.0
        },
        {
          "loan_approved": 0,
          "avg_risk_score": 68.12,
          "median_risk_score": 66.25,
          "std_risk_score": 18.54,
          "min_risk_score": 0.51,
          "max_risk_score": 100.0
        }
      ],
      "columns": [
        "loan_approved",
        "avg_risk_score",
        "median_risk_score",
        "std_risk_score",
        "min_risk_score",
        "max_risk_score"
      ]
    }
  },
  "sim_params": {
    "intercept": -0.39655499186651,
    "threshold": 0.37,
    "num_stats": {
      "Age": {
        "median": 39.0,
        "mean": 39.03228571428571,
        "scale": 10.634548617563405
      },
      "Job_Experience_Years": {
        "median": 10.0,
        "mean": 11.039190476190477,
        "scale": 7.131428582716473
      },
      "Annual_Income": {
        "median": 88681.11,
        "mean": 88810.14626904762,
        "scale": 30479.07172712187
      },
      "Credit_Score": {
        "median": 681.0,
        "mean": 679.2450952380952,
        "scale": 88.35635355784297
      },
      "Credit_History_Years": {
        "median": 7.4,
        "mean": 8.934414285714286,
        "scale": 6.81330532608532
      },
      "Existing_Loans": {
        "median": 1.0,
        "mean": 1.2897142857142858,
        "scale": 1.203751641164174
      },
      "Late_Payments_Last_2_Years": {
        "median": 0.0,
        "mean": 0.7599047619047619,
        "scale": 1.099121723176408
      },
      "Loan_Amount": {
        "median": 121431.52,
        "mean": 134911.0622990476,
        "scale": 84417.97703826058
      },
      "Loan_Term_Months": {
        "median": 72.0,
        "mean": 112.48857142857143,
        "scale": 102.39060858560521
      },
      "Debt_To_Income_Ratio": {
        "median": 7.89,
        "mean": 10.61900619047619,
        "scale": 9.752959831957229
      },
      "Savings_Balance": {
        "median": 28196.92,
        "mean": 31682.44333904762,
        "scale": 21839.71393446324
      },
      "Checking_Balance": {
        "median": 8730.52,
        "mean": 9713.531823809524,
        "scale": 6516.086114212427
      },
      "Total_Assets": {
        "median": 284758.85,
        "mean": 315103.66835476196,
        "scale": 188898.25741146217
      },
      "Total_Liabilities": {
        "median": 54822.165,
        "mean": 67090.39433285713,
        "scale": 48967.75044442616
      },
      "Monthly_Debt_Payment": {
        "median": 536.4200000000001,
        "mean": 749.5339166666666,
        "scale": 710.2158773411469
      },
      "Dependents": {
        "median": 1.0,
        "mean": 1.196095238095238,
        "scale": 1.0921468549762285
      },
      "Bank_Account_Age_Years": {
        "median": 9.2,
        "mean": 10.470566666666667,
        "scale": 7.184394322009823
      }
    },
    "cat_categories": {
      "Gender": [
        "Female",
        "Male"
      ],
      "Marital_Status": [
        "Divorced",
        "Married",
        "Single",
        "Widowed"
      ],
      "Education_Level": [
        "Bachelor",
        "High School",
        "Master",
        "PhD"
      ],
      "Employment_Status": [
        "Business Owner",
        "Contract",
        "Salaried",
        "Self-Employed",
        "Unemployed"
      ],
      "Loan_Purpose": [
        "Business",
        "Car",
        "Debt Consolidation",
        "Education",
        "Home",
        "Medical",
        "Personal"
      ],
      "Property_Ownership": [
        "Family Owned",
        "Mortgage",
        "Own",
        "Rent"
      ],
      "Residential_Status": [
        "Rural",
        "Suburban",
        "Urban"
      ],
      "Application_Channel": [
        "Agent",
        "Branch",
        "Mobile App",
        "Online"
      ],
      "Region": [
        "Central",
        "East",
        "North",
        "South",
        "West"
      ],
      "Previous_Loan_Status": [
        "Active",
        "Defaulted",
        "No Previous Loan",
        "Paid Off"
      ]
    },
    "coef_dict": {
      "num__Age": 0.03898070532033395,
      "num__Job_Experience_Years": 0.0006400870534711382,
      "num__Annual_Income": 0.33698350004154626,
      "num__Credit_Score": 1.133961340071657,
      "num__Credit_History_Years": 0.18817675606826764,
      "num__Existing_Loans": -0.28412079601163037,
      "num__Late_Payments_Last_2_Years": -0.6426175393628899,
      "num__Loan_Amount": -0.9173293591700753,
      "num__Loan_Term_Months": -0.01815049546678232,
      "num__Debt_To_Income_Ratio": -0.6782563504349032,
      "num__Savings_Balance": 0.32558827955447994,
      "num__Checking_Balance": 0.009823226268819284,
      "num__Total_Assets": -0.01721783736333597,
      "num__Total_Liabilities": -0.020106217076345183,
      "num__Monthly_Debt_Payment": 0.17043300981354717,
      "num__Dependents": -0.025649372367368747,
      "num__Bank_Account_Age_Years": -0.08115766139248919,
      "cat__Gender_Female": -0.19485554157843327,
      "cat__Gender_Male": -0.19264930784087816,
      "cat__Marital_Status_Divorced": -0.16397956668396163,
      "cat__Marital_Status_Married": -0.046660555327295225,
      "cat__Marital_Status_Single": 0.00657054144168541,
      "cat__Marital_Status_Widowed": -0.1834352688497464,
      "cat__Education_Level_Bachelor": -0.17678753434893565,
      "cat__Education_Level_High School": -0.12418188242267657,
      "cat__Education_Level_Master": -0.13068470868256,
      "cat__Education_Level_PhD": 0.04414927603485973,
      "cat__Employment_Status_Business Owner": 0.4114860599425432,
      "cat__Employment_Status_Contract": 0.3244852283381696,
      "cat__Employment_Status_Salaried": 0.37860089175228256,
      "cat__Employment_Status_Self-Employed": 0.27668002085883353,
      "cat__Employment_Status_Unemployed": -1.7787570503111516,
      "cat__Loan_Purpose_Business": -0.07592535285853316,
      "cat__Loan_Purpose_Car": -0.01323365737197397,
      "cat__Loan_Purpose_Debt Consolidation": -0.03364557404357164,
      "cat__Loan_Purpose_Education": -0.09018922425708649,
      "cat__Loan_Purpose_Home": -0.053286089099056855,
      "cat__Loan_Purpose_Medical": -0.07680729510453835,
      "cat__Loan_Purpose_Personal": -0.04441765668455571,
      "cat__Property_Ownership_Family Owned": -0.11642030124566646,
      "cat__Property_Ownership_Mortgage": -0.09472711961588842,
      "cat__Property_Ownership_Own": -0.08992683059608253,
      "cat__Property_Ownership_Rent": -0.08643059796167886,
      "cat__Residential_Status_Rural": -0.17235521239001447,
      "cat__Residential_Status_Suburban": -0.10329334460436013,
      "cat__Residential_Status_Urban": -0.11185629242494324,
      "cat__Application_Channel_Agent": -0.09784235407942726,
      "cat__Application_Channel_Branch": -0.10683899499632706,
      "cat__Application_Channel_Mobile App": -0.07427119993785579,
      "cat__Application_Channel_Online": -0.10855230040570683,
      "cat__Region_Central": 0.00867440522547264,
      "cat__Region_East": -0.10496700517623762,
      "cat__Region_North": -0.07012679840584587,
      "cat__Region_South": -0.09934535683790609,
      "cat__Region_West": -0.12174009422479874,
      "cat__Previous_Loan_Status_Active": 0.44991683745136296,
      "cat__Previous_Loan_Status_Defaulted": -2.614591243519779,
      "cat__Previous_Loan_Status_No Previous Loan": 0.4997394061899084,
      "cat__Previous_Loan_Status_Paid Off": 1.2774301504591778,
      "bin__Co_Applicant": 0.5436351008177024,
      "bin__Collateral": 0.8276535557663566
    }
  },
  "dq_report": {
    "total_rows": 30000,
    "duplicates": 0,
    "warnings": [
      "Monthly_Income and Annual_Income have high correlation (1.0000) \u2014 potential redundancy."
    ],
    "columns_count": 36,
    "outlier_columns": {
      "Annual_Income": 205,
      "Monthly_Income": 205,
      "Loan_Amount": 239,
      "Debt_To_Income_Ratio": 1678
    }
  },
  "clusters": [
    {
      "cluster_id": 0,
      "label": "Core Mainstream Car Borrowers",
      "size": 5682,
      "pct": 18.94,
      "avg_credit_score": 705.4,
      "avg_income": 115857.0,
      "avg_dti": 7.07,
      "approval_rate": 69.92,
      "dominant_purpose": "Car",
      "risk_profile": "Low-Moderate Risk",
      "high_risk_pct": 21.98
    },
    {
      "cluster_id": 1,
      "label": "Emerging Credit-Builder Applicants",
      "size": 8646,
      "pct": 28.82,
      "avg_credit_score": 621.5,
      "avg_income": 57931.6,
      "avg_dti": 11.91,
      "approval_rate": 37.29,
      "dominant_purpose": "Debt Consolidation",
      "risk_profile": "High Risk / Subprime",
      "high_risk_pct": 60.86
    },
    {
      "cluster_id": 2,
      "label": "Core Mainstream Medical Borrowers",
      "size": 4665,
      "pct": 15.55,
      "avg_credit_score": 687.7,
      "avg_income": 106414.0,
      "avg_dti": 22.72,
      "approval_rate": 40.94,
      "dominant_purpose": "Medical",
      "risk_profile": "Elevated Leverage Risk",
      "high_risk_pct": 58.29
    },
    {
      "cluster_id": 3,
      "label": "Core Mainstream Home Borrowers",
      "size": 11007,
      "pct": 36.69,
      "avg_credit_score": 707.1,
      "avg_income": 91566.5,
      "avg_dti": 6.31,
      "approval_rate": 74.35,
      "dominant_purpose": "Home",
      "risk_profile": "Prime / Low Risk",
      "high_risk_pct": 17.76
    }
  ]
};
