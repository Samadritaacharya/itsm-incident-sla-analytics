# ITSM Incident & SLA Analytics Dashboard

**A tested end-to-end IT service management analytics application** for incident trends, SLA breach risk prediction, root-cause analysis, service health scoring and PMO action planning, built as an interactive Streamlit dashboard.

> 🔗 **Live demo:** _add your Streamlit Cloud link here after deployment_  
> 📸 **Screenshots:** see `docs/SCREENSHOTS.md` for the recommended screenshot set.

---

## Business problem

IT operations teams handle many incidents but often lack a consolidated view of what matters most: deteriorating services, open tickets at risk of SLA breach, recurring root causes, change-related instability and ownership for improvement actions.

## Solution

This project simulates a ServiceNow/Jira-style ITSM environment with synthetic data and turns it into decision-ready analytics:

- executive KPI overview
- incident and service deep dives
- machine-learning SLA breach probability scoring
- root-cause and change-impact analysis
- Red/Amber/Green service health scoring
- PMO action plan with owners, priorities and next steps
- Markdown and CSV exports from the dashboard

## Dashboard pages

| # | Page | What it shows |
|---|------|---------------|
| 1 | Executive Overview | Headline KPIs and weekly ticket volume |
| 2 | Incident Analytics | Category, service, assignment group and aging views |
| 3 | SLA Breach Risk | ML breach-probability scoring of the open queue |
| 4 | Change Impact | Change-related incidents and SLA impact |
| 5 | Root Cause Analysis | Pareto and breach-rate analysis by root cause |
| 6 | Service Health | Composite service health score with RAG status |
| 7 | Recommendations / PMO Action Plan | Auto-generated PMO improvement actions and exports |

## Tech stack

`Python` · `Streamlit` · `Pandas` · `NumPy` · `Plotly` · `scikit-learn` · `pytest` · `Docker`

## Architecture

```text
app.py                      # Streamlit UI — 7 pages, filters, exports
src/
├── data_generator.py       # synthetic ServiceNow/Jira-style ticket data
├── scoring.py              # KPIs, ML breach model, service health score
└── recommendations.py      # PMO action plan + Markdown report export
tests/test_project.py       # 13 tests for generation, scoring, planning
Dockerfile                  # containerized deployment
VALIDATION_REPORT.md        # tested results
PUBLISH_GUIDE.md            # Streamlit + GitHub finish steps
```

## Validation status

This repository was tested before publication:

- `13/13` pytest tests passed
- `7/7` dashboard pages rendered successfully with Streamlit AppTest
- Streamlit app booted successfully
- health endpoint returned `200 ok`
- synthetic data generator verified

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

Regenerate local sample data:

```bash
python -m src.data_generator
```

Run with Docker:

```bash
docker build -t itsm-analytics .
docker run -p 8501:8501 itsm-analytics
```

## Deploy to Streamlit Cloud

Use:

```text
Repository: Samadritaacharya/itsm-incident-sla-analytics
Branch: main
Main file path: app.py
```

After deployment, copy the generated Streamlit URL into the **Live demo** line above.

## Skills demonstrated

ITSM & ITIL thinking · incident/problem/change analytics · SLA management · KPI design · executive reporting · machine learning for operational risk · dashboarding · data storytelling · PMO action planning · owner/priority mapping · Python engineering practice

## Why this project is relevant to my target roles

This project translates my IBM/Kyndryl ITSM/ITOM service delivery background into a working analytical tool. It is relevant for:

- Technical Project Management / PMO
- IT Operations / Service Delivery
- Cloud Operations / AIOps
- Digital Transformation
- Business Technology roles in Germany and Europe

## CV bullet

> Built an ITSM Incident & SLA Analytics Dashboard using Python, Streamlit, Pandas, Plotly and scikit-learn to analyze synthetic ServiceNow/Jira-style incident data, identify SLA breach risk, track MTTR, visualize root causes and generate operational improvement insights.

## Disclaimer

All data in this project is synthetic and generated programmatically. No confidential employer, university, client or personal data is used.

---

**Samadrita Acharya** · [LinkedIn](https://www.linkedin.com/in/samadrita-acharya-a07266184/) · [GitHub](https://github.com/Samadritaacharya)
