# ITSM Incident & SLA Analytics Dashboard

An end-to-end IT service management analytics application for incident trends, SLA breach-risk prediction, root-cause analysis, service-health scoring, change impact, and PMO action planning.

[![Python CI](https://github.com/Samadritaacharya/itsm-incident-sla-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/Samadritaacharya/itsm-incident-sla-analytics/actions/workflows/ci.yml)

**Live application:** [itsm-incident-sla-analytics.streamlit.app](https://itsm-incident-sla-analytics.streamlit.app/)  
**Validation evidence:** [VALIDATION_REPORT.md](VALIDATION_REPORT.md)  
**Portfolio owner:** [Samadrita Acharya](https://www.linkedin.com/in/samadrita-acharya-a07266184/)

## Recruiter quick view

| Area | Evidence in this project |
|---|---|
| Business problem | IT operations teams need to identify deteriorating services, SLA risk, recurring causes, and accountable improvement actions. |
| Product solution | A seven-page Streamlit dashboard using synthetic ServiceNow/Jira-style incident data. |
| Analytics | KPI calculation, MTTR and SLA analysis, change impact, Pareto/root-cause analysis, and service-health scoring. |
| Machine learning | SLA breach-probability scoring for the open incident queue using scikit-learn. |
| PMO value | RAG service health, prioritized recommendations, owners, deadlines, and downloadable action plans. |
| Engineering | Modular Python code, automated tests, GitHub Actions, Docker support, and documented validation. |
| Data/privacy | All records are generated synthetic data; no confidential employer or client information is used. |

## Business problem

IT operations teams handle large incident queues but often lack one decision-ready view of the questions leadership and service owners care about:

- Which services are deteriorating?
- Which open incidents are most likely to breach SLA?
- Are recent changes driving instability?
- Which causes explain most recurring incidents?
- Who owns the next corrective action?

## Solution

The application simulates a realistic ITSM environment and converts operational records into:

- executive KPIs and weekly demand trends
- incident analysis by category, service, assignment group, and age
- ML-based SLA breach-risk scoring
- change-related incident analysis
- Pareto and breach-rate root-cause views
- composite Red/Amber/Green service-health scores
- prioritized PMO action plans with owners and next steps
- downloadable Markdown and CSV outputs

## Two-minute recruiter demo

1. Open the [live app](https://itsm-incident-sla-analytics.streamlit.app/).
2. Select **SLA pressure week** or **Change-related incident wave**.
3. Click **Run ITSM analysis**.
4. Review the executive KPIs and high-risk open queue.
5. Explain the change-impact and root-cause findings.
6. Finish with the service-health view and PMO action plan.

## Dashboard pages

| # | Page | Decision supported |
|---|---|---|
| 1 | Executive Overview | What is the current operational situation? |
| 2 | Incident Analytics | Where is ticket volume and aging concentrated? |
| 3 | SLA Breach Risk | Which open incidents require immediate attention? |
| 4 | Change Impact | Are deployments or changes increasing incident risk? |
| 5 | Root Cause Analysis | Which causes drive the majority of incidents and breaches? |
| 6 | Service Health | Which services are Green, Amber, or Red? |
| 7 | Recommendations / PMO Action Plan | What should happen next, by whom, and with what priority? |

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
└── prioritized PMO actions and status-report generation

tests/test_project.py
└── data, scoring, prediction, recommendation, and app-render tests

.github/workflows/ci.yml
└── automated pytest execution on pushes and pull requests
```

## Validation status

The repository includes a documented pre-publication validation report:

- `13/13` pytest tests passed
- `7/7` Streamlit pages rendered with Streamlit AppTest
- Streamlit server started successfully
- health endpoint returned `200 ok`
- synthetic data generation, breach-risk scoring, service-health scoring, and exports were verified

See [VALIDATION_REPORT.md](VALIDATION_REPORT.md) for the recorded validation scope. GitHub Actions now reruns the test suite for future changes.

## Technology stack

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

## Skills demonstrated

ITSM and ITIL thinking · incident/problem/change analytics · SLA management · operational KPI design · service-health scoring · machine learning for operational risk · executive reporting · PMO action planning · Python engineering · data storytelling

## Why this project is relevant to my profile

This project translates my IBM/Kyndryl ITSM/ITOM service-delivery background into a working analytics product and connects it with my SAP cloud-delivery and PMO experience. It is relevant to Technical Project Management, PMO, IT Operations, Service Delivery, Cloud Operations, AIOps, and Digital Transformation roles.

## CV / LinkedIn project description

> Built a tested ITSM Incident & SLA Analytics Dashboard using Python, Streamlit, Pandas, Plotly, and scikit-learn to analyze synthetic ServiceNow/Jira-style incidents, predict SLA breach risk, monitor MTTR and service health, assess change impact, identify root causes, and generate prioritized PMO action plans.

## Responsible portfolio use

All data is synthetic and generated programmatically. The project is independent and contains no confidential SAP, IBM, Kyndryl, university, employer, customer, or client data.
