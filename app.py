"""ITSM Incident and SLA Analytics Dashboard."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_generator import generate_tickets
from src.recommendations import build_action_plan, export_markdown_report
from src.scoring import compute_kpis, score_open_tickets, service_health, train_breach_model

st.set_page_config(
    page_title="ITSM Incident & SLA Analytics",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://github.com/Samadritaacharya/itsm-incident-sla-analytics",
        "Report a bug": "https://github.com/Samadritaacharya/itsm-incident-sla-analytics/issues",
        "About": "Independent ITSM analytics portfolio project using synthetic data.",
    },
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {font-family: Inter, system-ui, sans-serif;}
    .stApp {
        background:
          radial-gradient(circle at 8% 0%, rgba(14,165,164,.10), transparent 28rem),
          radial-gradient(circle at 92% 8%, rgba(59,130,246,.08), transparent 30rem),
          #f7fafc;
    }
    .block-container {max-width: 1480px; padding-top: 1.25rem; padding-bottom: 4rem;}
    .ops-hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(125deg, #071521 0%, #0c2d3c 52%, #0d6f75 100%);
        padding: 2.5rem 2.65rem;
        border-radius: 26px;
        color: white;
        margin-bottom: 1.25rem;
        box-shadow: 0 28px 80px rgba(7, 21, 33, .20);
        border: 1px solid rgba(255,255,255,.09);
    }
    .ops-hero:after {
        content: '';
        position: absolute;
        width: 390px;
        height: 390px;
        border-radius: 999px;
        right: -120px;
        top: -170px;
        background: rgba(45,212,191,.18);
        filter: blur(8px);
    }
    .eyebrow {font-size:.76rem; letter-spacing:.13em; font-weight:800; text-transform:uppercase; color:#7dd3fc; margin-bottom:.7rem;}
    .ops-hero h1 {font-size:clamp(2.25rem,4.7vw,4rem); line-height:1; margin:0 0 .85rem; letter-spacing:-.055em; color:white; max-width:900px;}
    .ops-hero p {font-size:1.05rem; line-height:1.7; max-width:990px; color:#d9edf2; margin:0; position:relative; z-index:1;}
    .chip-row {display:flex; flex-wrap:wrap; gap:.45rem; margin-top:1.2rem; position:relative; z-index:1;}
    .chip {display:inline-flex; align-items:center; gap:.4rem; border:1px solid rgba(255,255,255,.14); background:rgba(255,255,255,.08); color:#edfafa; border-radius:999px; padding:.36rem .68rem; font-size:.78rem; font-weight:650; backdrop-filter:blur(10px);}
    .live-dot {width:.45rem;height:.45rem;border-radius:99px;background:#5eead4;box-shadow:0 0 0 5px rgba(94,234,212,.12);display:inline-block;}
    .flow-strip {display:grid;grid-template-columns:repeat(4,1fr);gap:.65rem;margin:.9rem 0 1.15rem;}
    .flow-step {background:#fff;border:1px solid #dbe7eb;border-radius:16px;padding:.9rem 1rem;box-shadow:0 8px 25px rgba(15,23,42,.04);}
    .flow-step b {display:block;color:#0f2430;font-size:.86rem;margin-bottom:.25rem;}
    .flow-step span {color:#667985;font-size:.77rem;}
    .flow-step em {display:inline-grid;place-items:center;width:1.55rem;height:1.55rem;border-radius:99px;background:#e8f8f7;color:#0d7477;font-style:normal;font-weight:800;font-size:.72rem;margin-right:.35rem;}
    .context-card {
        border:1px solid #d7e6ea;
        border-radius:18px;
        padding:1rem 1.15rem;
        background:rgba(255,255,255,.86);
        box-shadow:0 10px 32px rgba(15,23,42,.045);
        margin-bottom:1rem;
        backdrop-filter: blur(10px);
    }
    .context-card strong {color:#0a5257;}
    .context-card .muted {color:#637784;font-size:.88rem;margin-top:.25rem;}
    .section-kicker {font-size:.75rem;letter-spacing:.11em;text-transform:uppercase;color:#0f7b7e;font-weight:800;margin-top:1.15rem;}
    div[data-testid="stMetric"] {
        background:linear-gradient(180deg,#ffffff,#f8fbfc);
        border:1px solid #dbe7eb;
        border-top:3px solid #1f9b9c;
        padding:14px 16px;
        border-radius:16px;
        box-shadow:0 10px 26px rgba(15,23,42,.045);
    }
    div[data-testid="stMetricLabel"] {color:#60727d;}
    div[data-testid="stMetricValue"] {color:#102b37;letter-spacing:-.035em;}
    [data-testid="stSidebar"] {background:linear-gradient(180deg,#081822 0%,#0b2631 100%);border-right:1px solid rgba(255,255,255,.08);}
    [data-testid="stSidebar"] * {color:#e7f4f6;}
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] input {background:rgba(255,255,255,.08)!important;border-color:rgba(255,255,255,.12)!important;}
    .stButton>button, .stDownloadButton>button {border-radius:12px!important;font-weight:750!important;min-height:2.65rem;transition:transform .18s ease,box-shadow .18s ease!important;}
    .stButton>button:hover, .stDownloadButton>button:hover {transform:translateY(-1px);box-shadow:0 10px 24px rgba(13,116,119,.15)!important;}
    div[data-testid="stExpander"] {background:rgba(255,255,255,.72);border:1px solid #dce8eb;border-radius:14px;}
    div[data-testid="stDataFrame"] {border:1px solid #dbe7eb;border-radius:14px;overflow:hidden;}
    @media (max-width: 900px) {
      .flow-strip {grid-template-columns:1fr 1fr;}
      .ops-hero {padding:2rem 1.45rem;}
    }
    @media (max-width: 560px) {.flow-strip {grid-template-columns:1fr;}}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="ops-hero">
      <div class="eyebrow">Enterprise Service Operations · Decision Cockpit</div>
      <h1>ITSM Incident & SLA Analytics</h1>
      <p>Turn synthetic ServiceNow/Jira-style incident data into an executive operations story: service health, SLA exposure, change impact, root causes, predictive breach risk and an owner-ready PMO action plan.</p>
      <div class="chip-row">
        <span class="chip"><span class="live-dot"></span> Interactive scenario lab</span>
        <span class="chip">SLA risk model</span><span class="chip">Service health</span><span class="chip">Change intelligence</span><span class="chip">PMO exports</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="flow-strip">
      <div class="flow-step"><b><em>01</em>Observe</b><span>Incidents, priorities, services and SLA signals</span></div>
      <div class="flow-step"><b><em>02</em>Predict</b><span>Score open-ticket breach exposure</span></div>
      <div class="flow-step"><b><em>03</em>Diagnose</b><span>Trace root causes and change impact</span></div>
      <div class="flow-step"><b><em>04</em>Act</b><span>Convert findings into PMO ownership</span></div>
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
    fig.update_layout(
        margin=dict(l=18, r=18, t=58, b=18),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color="#304a56"),
        title_font=dict(size=17, color="#102b37"),
        legend_title_text="",
        hoverlabel=dict(font_size=13),
    )
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False})


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
    st.markdown("### ◈ ITSM Control Room")
    st.caption("Choose a scenario, tune the operating window and move through the decision flow.")
    page = st.radio("Workspace", pages)
    st.divider()
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
    days = st.slider("History window", 60, 365, preset[1], step=30, format="%d days")
    seed = int(st.number_input("Simulation seed", value=preset[2], step=1))
    if st.button("Run live analysis →", width="stretch", type="primary"):
        st.session_state.demo_run += 1
    st.divider()
    st.caption("Synthetic portfolio data only. No employer, client, customer or personal data.")

effective_seed = seed + st.session_state.demo_run * 17
df = load_data(n_tickets, days, effective_seed)

with st.expander("Filters · focus the operating view", expanded=False):
    f1, f2 = st.columns(2)
    regions = f1.multiselect("Region", sorted(df["region"].unique()))
    services = f2.multiselect("Service", sorted(df["service"].unique()))
    if regions:
        df = df[df["region"].isin(regions)]
    if services:
        df = df[df["service"].isin(services)]

kpis = compute_kpis(df)
resolved = df[df["status"].isin(["Resolved", "Closed"])]
health_signal = "Stable" if kpis["sla_breach_rate"] < 0.08 else "Watch" if kpis["sla_breach_rate"] < 0.15 else "Escalate"

st.markdown(
    f"""
    <div class="context-card">
      <strong>{scenario}</strong> · {n_tickets:,} synthetic tickets · {days} days · analysis run {st.session_state.demo_run + 1} · operating signal: <strong>{health_signal}</strong>
      <div class="muted">Interview flow: input scenario → SLA exposure → service diagnosis → accountable action plan.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if page.startswith("1"):
    st.markdown('<div class="section-kicker">Leadership view</div>', unsafe_allow_html=True)
    st.subheader("Executive Overview")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total tickets", f"{kpis['total_tickets']:,}")
    c2.metric("Open incidents", kpis["open_incidents"])
    c3.metric("SLA breach rate", f"{kpis['sla_breach_rate']:.1%}")
    c4.metric("MTTR", f"{kpis['mttr_hours']} h")
    c5.metric("Customer impacting", kpis["customer_impacting"])
    weekly = df.set_index("created_at").resample("W")["ticket_id"].count().reset_index()
    col_a, col_b = st.columns([1.55, 1])
    with col_a:
        show(px.area(weekly, x="created_at", y="ticket_id", title="Weekly demand signal"))
    with col_b:
        show(px.pie(df, names="priority", title="Priority mix", hole=0.56))
    st.info(f"Executive readout: the current scenario is **{health_signal.lower()}** with an SLA breach rate of **{kpis['sla_breach_rate']:.1%}**. Continue to breach risk and service health to identify where intervention should start.")

elif page.startswith("2"):
    st.markdown('<div class="section-kicker">Demand & queue health</div>', unsafe_allow_html=True)
    st.subheader("Incident Analytics")
    col1, col2 = st.columns(2)
    with col1:
        show(px.bar(df.groupby("category")["ticket_id"].count().sort_values().reset_index(), x="ticket_id", y="category", orientation="h", title="Tickets by category"))
    with col2:
        show(px.bar(df.groupby("service")["ticket_id"].count().sort_values().reset_index(), x="ticket_id", y="service", orientation="h", title="Tickets by service"))
    heat = df.pivot_table(index="assignment_group", columns="priority", values="ticket_id", aggfunc="count", fill_value=0)
    show(px.imshow(heat, text_auto=True, title="Assignment group × priority"))
    open_df = df[~df["status"].isin(["Resolved", "Closed"])].copy()
    open_df["age_days"] = (pd.Timestamp.now() - open_df["created_at"]).dt.days
    st.subheader("Oldest open work")
    st.dataframe(open_df.sort_values("age_days", ascending=False).head(20), width="stretch", hide_index=True)

elif page.startswith("3"):
    st.markdown('<div class="section-kicker">Predictive triage</div>', unsafe_allow_html=True)
    st.subheader("SLA Breach Risk")
    model, auc = load_model(n_tickets, days, effective_seed)
    scored = score_open_tickets(df, model)
    c1, c2, c3 = st.columns(3)
    c1.metric("Model ROC-AUC", f"{auc:.3f}")
    c2.metric("Open tickets scored", len(scored))
    c3.metric("High-risk tickets", int((scored["risk_level"] == "High").sum()))
    show(px.histogram(scored, x="breach_probability", color="risk_level", title="Breach probability distribution"))
    st.subheader("Priority intervention queue")
    st.dataframe(scored.head(25), width="stretch", hide_index=True)

elif page.startswith("4"):
    st.markdown('<div class="section-kicker">Change intelligence</div>', unsafe_allow_html=True)
    st.subheader("Change Impact")
    change = resolved.groupby("change_related").agg(tickets=("ticket_id", "count"), breach_rate=("sla_breached", "mean"), mttr=("actual_resolution_hours", "mean")).reset_index()
    col1, col2 = st.columns(2)
    with col1:
        show(px.bar(change, x="change_related", y="breach_rate", title="SLA breach rate by change relation"))
    with col2:
        show(px.bar(df[df["change_related"]].groupby("service")["ticket_id"].count().reset_index(), x="service", y="ticket_id", title="Change-related incidents by service"))

elif page.startswith("5"):
    st.markdown('<div class="section-kicker">Problem management</div>', unsafe_allow_html=True)
    st.subheader("Root Cause Analysis")
    root = resolved.groupby("root_cause")["ticket_id"].count().sort_values(ascending=False).reset_index()
    breach = resolved.groupby("root_cause")["sla_breached"].mean().sort_values().reset_index()
    col1, col2 = st.columns(2)
    with col1:
        show(px.bar(root, x="root_cause", y="ticket_id", title="Root cause concentration"))
    with col2:
        show(px.bar(breach, x="sla_breached", y="root_cause", orientation="h", title="Breach rate by root cause"))

elif page.startswith("6"):
    st.markdown('<div class="section-kicker">Service portfolio</div>', unsafe_allow_html=True)
    st.subheader("Service Health")
    health = service_health(df)
    show(px.bar(health.sort_values("health_score"), x="health_score", y="service", color="health_status", orientation="h", title="Service health score"))
    st.dataframe(health, width="stretch", hide_index=True)

else:
    st.markdown('<div class="section-kicker">Decision to execution</div>', unsafe_allow_html=True)
    st.subheader("Recommendations & PMO Action Plan")
    plan = build_action_plan(df)
    st.dataframe(plan, width="stretch", hide_index=True)
    report = export_markdown_report(df, plan)
    c1, c2 = st.columns(2)
    c1.download_button("Download leadership status report", report, file_name="itsm_status_report.md", width="stretch")
    c2.download_button("Download owner action plan", plan.to_csv(index=False), file_name="pmo_action_plan.csv", width="stretch")
    with st.expander("Preview leadership report"):
        st.markdown(report)
