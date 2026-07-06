"""ITSM Incident and SLA Analytics Dashboard."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_generator import generate_tickets
from src.recommendations import build_action_plan, export_markdown_report
from src.scoring import compute_kpis, score_open_tickets, service_health, train_breach_model

st.set_page_config(page_title="ITSM Incident and SLA Analytics", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #123456 58%, #1b8a8f 100%);
        padding: 2rem 2.2rem;
        border-radius: 22px;
        color: white;
        margin-bottom: 1.4rem;
        box-shadow: 0 18px 55px rgba(15, 23, 42, 0.22);
    }
    .hero h1 {font-size: 2.35rem; margin: 0 0 .55rem 0; letter-spacing: -.04em;}
    .hero p {font-size: 1.02rem; max-width: 980px; color: #e5f4f5; margin: 0;}
    .demo-card {
        border: 1px solid #d9e6e8;
        border-left: 5px solid #1b8a8f;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        background: #f7fbfc;
        margin-bottom: 1rem;
    }
    div[data-testid="stMetric"] {
        background: #f5f8fa;
        border-left: 4px solid #1b8a8f;
        padding: 12px 16px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>📊 ITSM Incident & SLA Analytics</h1>
      <p>Interactive ServiceNow/Jira-style analytics for incident volume, SLA breach risk, root causes, service health and PMO action planning. Use the sidebar to generate a scenario, then click <b>Run ITSM analysis</b> to explain the workflow live.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_data(n: int, days: int, seed: int):
    return generate_tickets(n_tickets=n, days=days, seed=seed)

@st.cache_resource
def load_model(n: int, days: int, seed: int):
    return train_breach_model(load_data(n, days, seed))

def show(fig):
    st.plotly_chart(fig, width="stretch")

pages = [
    "1 Executive Overview",
    "2 Incident Analytics",
    "3 SLA Breach Risk",
    "4 Change Impact",
    "5 Root Cause Analysis",
    "6 Service Health",
    "7 Recommendations and PMO Action Plan",
]

if "demo_run" not in st.session_state:
    st.session_state.demo_run = 0

with st.sidebar:
    st.header("🎛️ Live demo inputs")
    page = st.radio("Navigation", pages)
    scenario = st.selectbox(
        "Scenario preset",
        ["Balanced operations", "SLA pressure week", "Change-related incident wave", "High-volume service desk"],
        help="Choose a story to explain before running the analysis.",
    )
    preset = {
        "Balanced operations": (2500, 180, 42),
        "SLA pressure week": (3500, 120, 91),
        "Change-related incident wave": (4200, 150, 143),
        "High-volume service desk": (6000, 240, 77),
    }[scenario]
    n_tickets = st.slider("Ticket volume", 500, 6000, preset[0], step=500)
    days = st.slider("History window in days", 60, 365, preset[1], step=30)
    seed = int(st.number_input("Simulation seed", value=preset[2], step=1))
    if st.button("🚀 Run ITSM analysis", width="stretch", type="primary"):
        st.session_state.demo_run += 1
    st.caption("Change the inputs, click the button, then walk through the output pages like a real PMO/ITSM review.")

st.markdown(
    f"""
    <div class="demo-card">
      <b>Current live input:</b> {scenario} · {n_tickets:,} synthetic tickets · {days} days · run #{st.session_state.demo_run + 1}<br>
      <span style="color:#405264;">Explain this as: input data → SLA risk model → service health → PMO action plan.</span>
    </div>
    """,
    unsafe_allow_html=True,
)

effective_seed = seed + st.session_state.demo_run * 17
df = load_data(n_tickets, days, effective_seed)

with st.expander("🔎 Optional filters for live explanation", expanded=False):
    f1, f2 = st.columns(2)
    regions = f1.multiselect("Filter region", sorted(df["region"].unique()))
    services = f2.multiselect("Filter service", sorted(df["service"].unique()))
    if regions:
        df = df[df["region"].isin(regions)]
    if services:
        df = df[df["service"].isin(services)]

kpis = compute_kpis(df)
resolved = df[df["status"].isin(["Resolved", "Closed"])]

if page.startswith("1"):
    st.subheader("Executive Overview")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total tickets", f"{kpis['total_tickets']:,}")
    c2.metric("Open incidents", kpis["open_incidents"])
    c3.metric("SLA breach rate", f"{kpis['sla_breach_rate']:.1%}")
    c4.metric("MTTR", f"{kpis['mttr_hours']} h")
    c5.metric("Customer impacting", kpis["customer_impacting"])
    weekly = df.set_index("created_at").resample("W")["ticket_id"].count().reset_index()
    show(px.area(weekly, x="created_at", y="ticket_id", title="Weekly ticket volume"))
    show(px.pie(df, names="priority", title="Priority distribution", hole=0.4))

elif page.startswith("2"):
    st.subheader("Incident Analytics")
    col1, col2 = st.columns(2)
    with col1:
        show(px.bar(df.groupby("category")["ticket_id"].count().sort_values().reset_index(), x="ticket_id", y="category", orientation="h", title="Tickets by category"))
    with col2:
        show(px.bar(df.groupby("service")["ticket_id"].count().sort_values().reset_index(), x="ticket_id", y="service", orientation="h", title="Tickets by service"))
    heat = df.pivot_table(index="assignment_group", columns="priority", values="ticket_id", aggfunc="count", fill_value=0)
    show(px.imshow(heat, text_auto=True, title="Assignment group by priority"))
    open_df = df[~df["status"].isin(["Resolved", "Closed"])].copy()
    open_df["age_days"] = (pd.Timestamp.now() - open_df["created_at"]).dt.days
    st.dataframe(open_df.sort_values("age_days", ascending=False).head(20), width="stretch", hide_index=True)

elif page.startswith("3"):
    st.subheader("SLA Breach Risk")
    model, auc = load_model(n_tickets, days, effective_seed)
    scored = score_open_tickets(df, model)
    c1, c2, c3 = st.columns(3)
    c1.metric("Model ROC-AUC", f"{auc:.3f}")
    c2.metric("Open tickets scored", len(scored))
    c3.metric("High-risk tickets", int((scored["risk_level"] == "High").sum()))
    show(px.histogram(scored, x="breach_probability", color="risk_level", title="SLA breach probability"))
    st.dataframe(scored.head(25), width="stretch", hide_index=True)

elif page.startswith("4"):
    st.subheader("Change Impact")
    change = resolved.groupby("change_related").agg(tickets=("ticket_id", "count"), breach_rate=("sla_breached", "mean"), mttr=("actual_resolution_hours", "mean")).reset_index()
    show(px.bar(change, x="change_related", y="breach_rate", title="SLA breach rate by change relation"))
    show(px.bar(df[df["change_related"]].groupby("service")["ticket_id"].count().reset_index(), x="service", y="ticket_id", title="Change-related incidents by service"))

elif page.startswith("5"):
    st.subheader("Root Cause Analysis")
    root = resolved.groupby("root_cause")["ticket_id"].count().sort_values(ascending=False).reset_index()
    show(px.bar(root, x="root_cause", y="ticket_id", title="Root cause Pareto"))
    breach = resolved.groupby("root_cause")["sla_breached"].mean().sort_values().reset_index()
    show(px.bar(breach, x="sla_breached", y="root_cause", orientation="h", title="Breach rate by root cause"))

elif page.startswith("6"):
    st.subheader("Service Health")
    health = service_health(df)
    show(px.bar(health.sort_values("health_score"), x="health_score", y="service", color="health_status", orientation="h", title="Service health score"))
    st.dataframe(health, width="stretch", hide_index=True)

else:
    st.subheader("Recommendations and PMO Action Plan")
    plan = build_action_plan(df)
    st.dataframe(plan, width="stretch", hide_index=True)
    report = export_markdown_report(df, plan)
    c1, c2 = st.columns(2)
    c1.download_button("Download Markdown status report", report, file_name="itsm_status_report.md", width="stretch")
    c2.download_button("Download CSV action plan", plan.to_csv(index=False), file_name="pmo_action_plan.csv", width="stretch")
    with st.expander("Preview report"):
        st.markdown(report)
