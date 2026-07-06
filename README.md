# ITSM Incident & SLA Analytics Dashboard

**A tested end-to-end IT service management analytics application** — incident trends, SLA breach risk prediction, root-cause analysis, service health scoring and an automatically generated PMO action plan, built as an interactive multi-page Streamlit dashboard.

> 🔗 **Live demo:** _[add your Streamlit Cloud link here after deployment]_
> 📸 Screenshots: [`assets/screenshots/`](assets/screenshots/)

---

## Business problem

IT operations teams handle thousands of incidents but often lack a consolidated view of what actually matters: Which services are deteriorating? Which open tickets will breach their SLA next? Which root causes keep coming back? Which changes are causing instability? Without this visibility, teams stay reactive — closing tickets instead of removing the causes behind them.

## Solution

This project simulates a ServiceNow/Jira-style ITSM environment with realistic synthetic data and turns it into decision-ready analytics:

- an **executive KPI overview** for leadership,
- **operational deep dives** for team leads,
- a **machine-learning model** that scores the open queue for SLA breach probability and proposes escalation actions,
- a **service health scorecard** with Red/Amber/Green status,
- and a **PMO action plan** generated automatically from recurring root-cause patterns, with recommended owners, priorities and next steps — exportable as Markdown and CSV.

## Pages

| # | Page | What it shows |
|---|------|---------------|
| 1 | Executive Overview | Headline KPIs, weekly volume, priority mix, breach rate vs MTTR trend |
| 2 | Incident Analytics | Category/service breakdowns, group × priority heatmap, aging open tickets |
| 3 | SLA Breach Risk | ML breach-probability scoring of the open queue, escalation list, historical risk heatmap |
| 4 | Change Impact | Change-related vs. normal incidents, breach comparison, affected services |
| 5 | Root Cause Analysis | Pareto chart, breach rate per cause, monthly trend of top causes |
| 6 | Service Health | Composite 0–100 health score per service with RAG status |
| 7 | Recommendations / PMO Action Plan | Auto-generated action plan + Markdown/CSV export |

## Key features

- **KPI dashboard**: total tickets, open incidents, SLA breach rate, MTTR, high-priority queue, customer impact
- **SLA breach prediction**: gradient-boosting classifier (scikit-learn) trained on resolved tickets, scoring live open tickets with probability, risk level and suggested action
- **Root-cause Pareto** and trend analysis for problem management
- **Service health score**: weighted composite of breach rate, MTTR overshoot, open high-priority incidents and customer impact
- **PMO action plan**: recurring problems ranked by pain score, mapped to recommended owners and concrete next steps
- **Report export** as Markdown status report and CSV action plan
- **Demo data generator** with adjustable volume, history window and seed (sidebar controls)
- Full **pytest suite** with 13 tests, **GitHub Actions CI** and **Dockerfile**

## Tech stack

`Python` · `Streamlit` · `Pandas` · `NumPy` · `Plotly` · `scikit-learn` · `pytest` · `GitHub Actions` · `Docker`

## Architecture

```text
app.py                      # Streamlit UI — 7 pages, filters, exports
src/
├── data_generator.py       # synthetic ServiceNow/Jira-style ticket data
├── scoring.py              # KPIs, ML breach model, service health score
└── recommendations.py      # PMO action plan + Markdown report export
tests/test_project.py       # 13 tests for generation, scoring, planning
sample_data/tickets.csv     # pre-generated synthetic sample dataset (500 tickets)
.github/workflows/ci.yml    # CI: pytest on every push/PR
Dockerfile                  # containerized deployment
```

## Validation status

This repository was tested before publication:

- `13/13` pytest tests passed
- `7/7` dashboard pages rendered successfully with Streamlit AppTest
- Streamlit app booted successfully
- Health endpoint returned `200 ok`
- Synthetic data generator and sample dataset verified

See [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md) for details.

## How to run locally

```bash
git clone https://github.com/Samadritaacharya/itsm-incident-sla-analytics.git
cd itsm-incident-sla-analytics
pip install -r requirements.txt
streamlit run app.py
```

Run the tests:

```bash
pytest -v
```

Run with Docker:

```bash
docker build -t itsm-analytics .
docker run -p 8501:8501 itsm-analytics
```

Regenerate the sample dataset:

```bash
python -m src.data_generator
```

## Deploy to Streamlit Cloud (free)

1. Push this repository to GitHub (public).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. **New app** → select this repo → branch `main` → main file `app.py` → **Deploy**.
4. Copy the live URL into the top of this README and into your CV/LinkedIn.

## Example use case

A service delivery manager opens the dashboard on Monday morning. The Executive Overview shows the SLA breach rate creeping up. Page 3 reveals twelve open tickets with >70% breach probability — most sitting with Vendor Escalation. Page 5 shows "Failed Change" is the fastest-growing root cause, and Page 7 already proposes the response: tighten CAB approval criteria, owner Change Advisory Board, priority High, target two weeks. The Markdown status report is exported and attached to the weekly steering meeting.

## Skills demonstrated

ITSM & ITIL thinking (incident, problem, change) · SLA management & escalation logic · KPI design & executive reporting · machine learning for operational risk · dashboarding & data storytelling · PMO action planning & ownership mapping · software engineering practice (tests, CI, Docker, clean structure)

## Why this project is relevant to my target roles

This project translates my hands-on IBM/Kyndryl ITSM/ITOM service delivery experience into a working analytical tool. It demonstrates practical skills for:

- **Technical Project Management / PMO** — action plans with owners, priorities and target dates; executive status reporting
- **IT Operations / Service Delivery** — incident, SLA, change and problem management analytics
- **Cloud Operations / AIOps** — operational risk scoring and service health monitoring concepts
- **Digital Transformation** — turning raw operational data into decisions and governance

## Roadmap

- SLA breach model explainability (feature importance view)
- FastAPI backend + PostgreSQL persistence
- Configurable SLA matrices per service
- Power BI companion report

## Disclaimer

All data in this project is **synthetic**, generated programmatically for demonstration purposes. No confidential SAP, IBM/Kyndryl, university or client data is used.

---

**Samadrita Acharya** · [LinkedIn](https://www.linkedin.com/in/samadrita-acharya-a07266184/) · [GitHub](https://github.com/Samadritaacharya)
