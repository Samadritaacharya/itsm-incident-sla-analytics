"""ITSM Incident and SLA Analytics Dashboard."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_generator import generate_tickets
from src.recommendations import build_action_plan, export_markdown_report
from src.scoring import compute_kpis, score_open_tickets, service_health, train_breach_model

st.set_page_config(page_title="ITSM Incident and SLA Analytics", page_icon="📊", layout="wide")
st.title("ITSM Incident and SLA Analytics Dashboard")
st.caption("Synthetic ServiceNow/Jira-style incident analytics for ITSM, SLA risk, service health and PMO action planning.")

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
with st.sidebar:
    page = st.radio("Navigation", pages)
    n_tickets = st.slider("Tickets", 500, 6000, 2500, step=500)
    days = st.slider("History days", 60, 365, 180, step=30)
    seed = int(st.number_input("Random seed", value=42, step=1))
    st.caption("All data is synthetic. No employer or client data is used.")

df = load_data(n_tickets, days, seed)
kpis = compute_kpis(df)
resolved = df[df["status"].isin(["Resolved", "Closed"])]

if page.startswith("1"):
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
    col1, col2 = st.columns(2)
    with col1:
        show(px.bar(df.groupby("category")["ticket_id"].count().sort_values().reset_index(), x="ticket_id", y="category", orientation="h", title="Tickets by category"))
    with col2:
        show(px.bar(df.groupby("service")["ticket_id"].count().sort_values().reset_index(), x="ticket_id", y="service", orientation="h", title="Tickets by service"))
    heat = df.pivot_table(index="assignment_group", columns="priority", values="ticket_id", aggfunc="count", fill_value=0)
    show(px.imshow(heat, text_auto=True, title="Assignment group by priority"))
    open_df = df[~df["status"].isin(["Resolved", "Closed"])].copy()
    open_df["age_days"] = (pd.Timestamp.now() - open_df["created_at"]).dt.days
    st.dataframe(open_df.sort_values("age_days", ascending=False).head(20), width="stretch")

elif page.startswith("3"):
    model, auc = load_model(n_tickets, days, seed)
    scored = score_open_tickets(df, model)
    c1, c2, c3 = st.columns(3)
    c1.metric("Model ROC-AUC", f"{auc:.3f}")
    c2.metric("Open tickets scored", len(scored))
    c3.metric("High-risk tickets", int((scored["risk_level"] == "High").sum()))
    show(px.histogram(scored, x="breach_probability", color="risk_level", title="SLA breach probability"))
    st.dataframe(scored.head(25), width="stretch")

elif page.startswith("4"):
    change = resolved.groupby("change_related").agg(tickets=("ticket_id", "count"), breach_rate=("sla_breached", "mean"), mttr=("actual_resolution_hours", "mean")).reset_index()
    show(px.bar(change, x="change_related", y="breach_rate", title="SLA breach rate by change relation"))
    show(px.bar(df[df["change_related"]].groupby("service")["ticket_id"].count().reset_index(), x="service", y="ticket_id", title="Change-related incidents by service"))

elif page.startswith("5"):
    root = resolved.groupby("root_cause")["ticket_id"].count().sort_values(ascending=False).reset_index()
    show(px.bar(root, x="root_cause", y="ticket_id", title="Root cause Pareto"))
    breach = resolved.groupby("root_cause")["sla_breached"].mean().sort_values().reset_index()
    show(px.bar(breach, x="sla_breached", y="root_cause", orientation="h", title="Breach rate by root cause"))

elif page.startswith("6"):
    health = service_health(df)
    show(px.bar(health.sort_values("health_score"), x="health_score", y="service", color="health_status", orientation="h", title="Service health score"))
    st.dataframe(health, width="stretch")

else:
    plan = build_action_plan(df)
    st.dataframe(plan, width="stretch")
    report = export_markdown_report(df, plan)
    st.download_button("Download Markdown status report", report, file_name="itsm_status_report.md")
    st.download_button("Download CSV action plan", plan.to_csv(index=False), file_name="pmo_action_plan.csv")
    with st.expander("Preview report"):
        st.markdown(report)
