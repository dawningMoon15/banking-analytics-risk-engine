/**
 * Simplified Banking Analytics & Risk Dashboard Controller
 */

let driverChartsRendered = false;

function showTab(tabId) {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  tabBtns.forEach(b => {
    if (b.dataset.tab === tabId) {
      b.classList.add('active');
    } else {
      b.classList.remove('active');
    }
  });

  tabPanes.forEach(p => {
    if (p.id === tabId) {
      p.classList.add('active');
    } else {
      p.classList.remove('active');
    }
  });

  // Render Risk Drivers charts on first view so Chart.js has proper container dimensions
  if (tabId === 'tab-drivers' && !driverChartsRendered) {
    setTimeout(renderDriverCharts, 50);
    driverChartsRendered = true;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const simulator = new UnderwritingSimulator(BANKING_DATA.sim_params);

  // Tab listeners
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      showTab(btn.dataset.tab);
    });
  });

  // Render initial overview charts
  renderOverviewCharts();

  // Initialize simulator
  initSimulator(simulator);
});

/* ==========================================================================
   Overview Tab Charts
   ========================================================================== */
function renderOverviewCharts() {
  // Chart 1: Credit Score Band
  const ctxCredit = document.getElementById('chartCreditBand');
  if (ctxCredit) {
    const q02 = BANKING_DATA.sql_queries['q02_approval_by_credit_score_band.sql'].records;
    new Chart(ctxCredit, {
      type: 'bar',
      data: {
        labels: q02.map(r => r.credit_band),
        datasets: [{
          label: 'Approval %',
          data: q02.map(r => r.approval_pct),
          backgroundColor: '#3B82F6',
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => `Approval Rate: ${ctx.parsed.y}%`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            ticks: { color: '#64748B', callback: v => v + '%' },
            grid: { color: '#F1F5F9' }
          },
          x: {
            ticks: { color: '#475569', font: { size: 11 } },
            grid: { display: false }
          }
        }
      }
    });
  }

  // Chart 2: Loan Purpose
  const ctxPurpose = document.getElementById('chartPurpose');
  if (ctxPurpose) {
    const q05 = BANKING_DATA.sql_queries['q05_approval_by_loan_purpose.sql'].records;
    new Chart(ctxPurpose, {
      type: 'bar',
      data: {
        labels: q05.map(r => r.loan_purpose),
        datasets: [{
          data: q05.map(r => r.approval_pct),
          backgroundColor: '#10B981',
          borderRadius: 4
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => `Approval Rate: ${ctx.parsed.x}%`
            }
          }
        },
        scales: {
          x: {
            min: 40,
            max: 70,
            ticks: { color: '#64748B', callback: v => v + '%' },
            grid: { color: '#F1F5F9' }
          },
          y: {
            ticks: { color: '#475569' },
            grid: { display: false }
          }
        }
      }
    });
  }
}

/* ==========================================================================
   Risk Drivers Tab Charts
   ========================================================================== */
function renderDriverCharts() {
  // Chart 1: Odds Ratios
  const ctxOdds = document.getElementById('chartOdds');
  if (ctxOdds) {
    const odds = [
      { name: 'Prior Loan: Paid Off', val: 3.59, pos: true },
      { name: 'Credit Score (+1 SD)', val: 3.11, pos: true },
      { name: 'Collateral Pledged', val: 2.29, pos: true },
      { name: 'Co-Applicant', val: 1.72, pos: true },
      { name: 'Salaried Employment', val: 1.46, pos: true },
      { name: 'Late Payments (-1 SD)', val: 0.53, pos: false },
      { name: 'DTI Ratio (+1 SD)', val: 0.51, pos: false },
      { name: 'Loan Amount (+1 SD)', val: 0.40, pos: false },
      { name: 'Unemployed Status', val: 0.17, pos: false },
      { name: 'Prior Loan: Defaulted', val: 0.07, pos: false }
    ];

    new Chart(ctxOdds, {
      type: 'bar',
      data: {
        labels: odds.map(d => d.name),
        datasets: [{
          data: odds.map(d => d.val),
          backgroundColor: odds.map(d => d.pos ? '#16A34A' : '#DC2626'),
          borderRadius: 3
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => `Odds Ratio: ${ctx.parsed.x}x`
            }
          }
        },
        scales: {
          x: {
            type: 'logarithmic',
            ticks: { color: '#64748B', callback: v => v + 'x' },
            grid: { color: '#F1F5F9' }
          },
          y: {
            ticks: { color: '#475569', font: { size: 11 } },
            grid: { display: false }
          }
        }
      }
    });
  }

  // Chart 2: ROC Curve
  const ctxRoc = document.getElementById('chartRoc');
  if (ctxRoc) {
    const fpr = [0, 0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 1.0];
    const tpr = [0, 0.55, 0.74, 0.87, 0.92, 0.97, 0.99, 1.0];

    new Chart(ctxRoc, {
      type: 'line',
      data: {
        labels: fpr,
        datasets: [{
          label: 'Model (AUC 0.887)',
          data: tpr,
          borderColor: '#2563EB',
          backgroundColor: 'rgba(37, 99, 235, 0.08)',
          fill: true,
          tension: 0.3,
          borderWidth: 2,
          pointRadius: 2
        }, {
          label: 'Baseline',
          data: fpr,
          borderColor: '#94A3B8',
          borderDash: [4, 4],
          fill: false,
          pointRadius: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 12, color: '#64748B' }
          }
        },
        scales: {
          x: {
            title: { display: true, text: 'False Positive Rate', color: '#94A3B8' },
            ticks: { color: '#64748B' },
            grid: { color: '#F1F5F9' }
          },
          y: {
            title: { display: true, text: 'True Positive Rate', color: '#94A3B8' },
            ticks: { color: '#64748B' },
            grid: { color: '#F1F5F9' }
          }
        }
      }
    });
  }
}

/* ==========================================================================
   Loan Simulator
   ========================================================================== */
function initSimulator(simulator) {
  const inputs = {
    Credit_Score: document.getElementById('simCredit'),
    Annual_Income: document.getElementById('simIncome'),
    Loan_Amount: document.getElementById('simAmount'),
    Debt_To_Income_Ratio: document.getElementById('simDti'),
    Late_Payments_Last_2_Years: document.getElementById('simLate'),
    Employment_Status: document.getElementById('simEmployment'),
    Previous_Loan_Status: document.getElementById('simPrevLoan'),
    Loan_Purpose: document.getElementById('simPurpose'),
    Collateral: document.getElementById('simCollateral'),
    Co_Applicant: document.getElementById('simCoApplicant')
  };

  const labels = {
    Credit_Score: document.getElementById('valCredit'),
    Annual_Income: document.getElementById('valIncome'),
    Loan_Amount: document.getElementById('valAmount'),
    Debt_To_Income_Ratio: document.getElementById('valDti'),
    Late_Payments_Last_2_Years: document.getElementById('valLate')
  };

  const verdictBox = document.getElementById('verdictBox');
  const verdictTitle = document.getElementById('verdictTitle');
  const verdictProb = document.getElementById('verdictProb');
  const driversList = document.getElementById('simDriversList');

  function calculate() {
    const payload = {
      Credit_Score: Number(inputs.Credit_Score.value),
      Annual_Income: Number(inputs.Annual_Income.value),
      Loan_Amount: Number(inputs.Loan_Amount.value),
      Debt_To_Income_Ratio: Number(inputs.Debt_To_Income_Ratio.value),
      Late_Payments_Last_2_Years: Number(inputs.Late_Payments_Last_2_Years.value),
      Employment_Status: inputs.Employment_Status.value,
      Previous_Loan_Status: inputs.Previous_Loan_Status.value,
      Loan_Purpose: inputs.Loan_Purpose.value,
      Collateral: inputs.Collateral.dataset.val === '1' ? 1 : 0,
      Co_Applicant: inputs.Co_Applicant.dataset.val === '1' ? 1 : 0
    };

    // Update labels
    labels.Credit_Score.textContent = payload.Credit_Score;
    labels.Annual_Income.textContent = '$' + payload.Annual_Income.toLocaleString();
    labels.Loan_Amount.textContent = '$' + payload.Loan_Amount.toLocaleString();
    labels.Debt_To_Income_Ratio.textContent = payload.Debt_To_Income_Ratio + '%';
    labels.Late_Payments_Last_2_Years.textContent = payload.Late_Payments_Last_2_Years;

    const res = simulator.evaluate(payload);

    // Update verdict box
    let boxClass = 'verdict-box verdict-approved';
    let textTitle = 'APPROVED';

    if (res.probability >= 0.60) {
      boxClass = 'verdict-box verdict-approved';
      textTitle = 'APPROVED';
    } else if (res.probability >= 0.37) {
      boxClass = 'verdict-box verdict-conditional';
      textTitle = 'CONDITIONAL APPROVAL';
    } else {
      boxClass = 'verdict-box verdict-rejected';
      textTitle = 'REJECTED';
    }

    verdictBox.className = boxClass;
    verdictTitle.textContent = textTitle;
    verdictProb.textContent = `Approval Probability: ${res.approvalPct}% • Risk Score: ${res.riskScore}/100`;

    // Render top 3 positive & top 3 negative drivers
    driversList.innerHTML = '';
    const driversToShow = [
      ...res.topPositive.slice(0, 3).map(d => ({ ...d, isPos: true })),
      ...res.topNegative.slice(0, 3).map(d => ({ ...d, isPos: false }))
    ];

    driversToShow.forEach(d => {
      const row = document.createElement('div');
      row.className = 'driver-row ' + (d.isPos ? 'pos' : 'neg');
      row.innerHTML = `
        <span>${d.label}</span>
        <span class="${d.isPos ? 'driver-impact-pos' : 'driver-impact-neg'}">${d.isPos ? '+' : ''}${d.contribution.toFixed(2)}</span>
      `;
      driversList.appendChild(row);
    });
  }

  // Bind change events
  Object.values(inputs).forEach(input => {
    if (input) {
      input.addEventListener('input', calculate);
      input.addEventListener('change', calculate);
    }
  });

  // Switch buttons (Collateral, CoApplicant)
  ['simCollateral', 'simCoApplicant'].forEach(id => {
    const btn = document.getElementById(id);
    if (btn) {
      btn.addEventListener('click', () => {
        const current = btn.dataset.val === '1';
        btn.dataset.val = current ? '0' : '1';
        if (!current) {
          btn.classList.add('active');
          btn.textContent = 'Yes';
        } else {
          btn.classList.remove('active');
          btn.textContent = 'No';
        }
        calculate();
      });
    }
  });

  // Presets
  const presets = document.querySelectorAll('.preset-btn');
  presets.forEach(btn => {
    btn.addEventListener('click', () => {
      presets.forEach(p => p.classList.remove('active'));
      btn.classList.add('active');

      const preset = PRESET_APPLICANTS[btn.dataset.preset];
      if (preset) {
        inputs.Credit_Score.value = preset.Credit_Score;
        inputs.Annual_Income.value = preset.Annual_Income;
        inputs.Loan_Amount.value = preset.Loan_Amount;
        inputs.Debt_To_Income_Ratio.value = preset.Debt_To_Income_Ratio;
        inputs.Late_Payments_Last_2_Years.value = preset.Late_Payments_Last_2_Years;
        inputs.Employment_Status.value = preset.Employment_Status;
        inputs.Previous_Loan_Status.value = preset.Previous_Loan_Status;
        inputs.Loan_Purpose.value = preset.Loan_Purpose;

        inputs.Collateral.dataset.val = preset.Collateral ? '1' : '0';
        inputs.Collateral.className = 'switch-btn ' + (preset.Collateral ? 'active' : '');
        inputs.Collateral.textContent = preset.Collateral ? 'Yes' : 'No';

        inputs.Co_Applicant.dataset.val = preset.Co_Applicant ? '1' : '0';
        inputs.Co_Applicant.className = 'switch-btn ' + (preset.Co_Applicant ? 'active' : '');
        inputs.Co_Applicant.textContent = preset.Co_Applicant ? 'Yes' : 'No';

        calculate();
      }
    });
  });

  calculate();
}
