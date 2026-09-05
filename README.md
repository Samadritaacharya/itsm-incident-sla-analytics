# ITSM Incident & SLA Analytics Dashboard

[![Python CI](https://github.com/Samadritaacharya/itsm-incident-sla-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/Samadritaacharya/itsm-incident-sla-analytics/actions/workflows/ci.yml)

**An IT service-management analytics application for incident trends, SLA breach-risk prediction, root-cause analysis, service-health scoring, change impact, and prioritized operational action planning.**

[**Open live app →**](https://itsm-incident-sla-analytics.streamlit.app/) · [Validation evidence](VALIDATION_REPORT.md) · [Source](https://github.com/Samadritaacharya/itsm-incident-sla-analytics)

> All incident records are synthetic and generated programmatically. No confidential employer, customer, or client information is used.

## What it answers

- Which services are deteriorating?
- Which open incidents are most likely to breach SLA?
- Are recent changes driving instability?
- Which causes explain most recurring incidents?
- Who owns the next corrective action?

## Working capabilities

- executive KPIs and weekly demand trends
- incident analysis by category, service, assignment group, and age
- ML-based SLA breach-risk scoring
- change-related incident analysis
- Pareto and breach-rate root-cause views
- composite Red/Amber/Green service-health scoring
- prioritized action plans with owners and next steps
- downloadable Markdown and CSV outputs

## Dashboard pages

| # | Page | Decision supported |
|---|---|---|
| 1 | Executive Overview | What is the current operational situation? |
| 2 | Incident Analytics | Where are ticket volume and aging concentrated? |
| 3 | SLA Breach Risk | Which open incidents require immediate attention? |
| 4 | Change Impact | Are deployments or changes increasing incident risk? |
| 5 | Root Cause Analysis | Which causes drive most incidents and breaches? |
| 6 | Service Health | Which services are Green, Amber, or Red? |
| 7 | Action Plan | What should happen next, by whom, and with what priority? |

## Architecture

```text
app.py
├── seven-page Streamlit interface
├── scenario controls and filters
├── interactive charts and risk views
└── Markdown / CSV exports

src/data_generator.py
└── synthetic ServiceNow/Jira-style incident generation

src/scoring.py
├── KPI and SLA calculations
├── breach-risk model
└── composite service-health score

src/recommendations.py
└── prioritized actions and status-report generation
```

## Verification snapshot

The recorded validation includes:

- `13/13` pytest tests passed
- `7/7` Streamlit pages rendered with Streamlit AppTest
- Streamlit health endpoint returned `200 ok`
- synthetic data generation, breach-risk scoring, service-health scoring, and exports verified

GitHub Actions reruns the automated checks on future changes. See [VALIDATION_REPORT.md](VALIDATION_REPORT.md) for scope and limitations.

## Technology

`Python` · `Streamlit` · `Pandas` · `NumPy` · `Plotly` · `scikit-learn` · `pytest` · `GitHub Actions` · `Docker`

## Run locally

```bash
git clone https://github.com/Samadritaacharya/itsm-incident-sla-analytics.git
cd itsm-incident-sla-analytics
python -m venv .venv
```

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

## Design principle

ITSM analytics should connect operational signals to ownership and action—not stop at charts. The project therefore keeps risk, change impact, service health, and next-step recommendations in the same workflow.
