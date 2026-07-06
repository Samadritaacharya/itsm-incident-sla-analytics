"""PMO action plan generator and report export utilities."""
from __future__ import annotations

from datetime import date
import pandas as pd
from .scoring import compute_kpis, service_health

OWNER_MAP = {
    "Configuration Error": "Change Management",
    "Capacity / Resource Exhaustion": "Capacity Planning",
    "Software Defect": "Application Support L2",
    "Failed Change": "Change Advisory Board",
    "Hardware Failure": "Infrastructure Ops",
    "Third-Party Outage": "Vendor Management",
    "Human Error": "Service Desk Training Lead",
    "Expired Certificate": "Security Operations",
    "Unknown / Under Investigation": "Problem Management",
}

NEXT_STEP_MAP = {
    "Configuration Error": "Introduce peer review and automated config validation before deployment",
    "Capacity / Resource Exhaustion": "Define capacity thresholds and proactive scaling runbook",
    "Software Defect": "Feed recurring defects into the product backlog with severity tags",
    "Failed Change": "Tighten CAB approval criteria and enforce rollback plans",
    "Hardware Failure": "Review hardware lifecycle and preventive maintenance schedule",
    "Third-Party Outage": "Renegotiate vendor SLAs and add redundancy for critical paths",
    "Human Error": "Update knowledge articles and run targeted L1 training",
    "Expired Certificate": "Deploy automated certificate expiry monitoring",
    "Unknown / Under Investigation": "Open formal problem records and assign root-cause analysis owners",
}


def build_action_plan(df: pd.DataFrame, top_n: int = 8) -> pd.DataFrame:
    resolved = df[df["status"].isin(["Resolved", "Closed"])]
    rc = resolved.groupby("root_cause").agg(tickets=("ticket_id", "count"), breach_rate=("sla_breached", "mean"), customer_impact=("customer_impact", "sum")).reset_index()
    rc["pain_score"] = rc["tickets"] * (0.4 + rc["breach_rate"]) + rc["customer_impact"] * 2
    rows = []
    for _, r in rc.sort_values("pain_score", ascending=False).head(top_n).iterrows():
        cause = r["root_cause"]
        priority = "High" if r["breach_rate"] > 0.30 or r["customer_impact"] > 50 else ("Medium" if r["breach_rate"] > 0.18 else "Low")
        rows.append({
            "problem": f"Recurring incidents: {cause}",
            "evidence": f"{int(r['tickets'])} tickets, {r['breach_rate']:.0%} SLA breach, {int(r['customer_impact'])} customer-impacting",
            "recommended_owner": OWNER_MAP.get(cause, "Problem Management"),
            "priority": priority,
            "next_step": NEXT_STEP_MAP.get(cause, "Assign problem record and investigate"),
            "target": "2 weeks" if priority == "High" else "4 weeks",
        })
    order = {"High": 0, "Medium": 1, "Low": 2}
    return pd.DataFrame(rows).sort_values("priority", key=lambda s: s.map(order)).reset_index(drop=True)


def export_markdown_report(df: pd.DataFrame, action_plan: pd.DataFrame) -> str:
    k = compute_kpis(df)
    health = service_health(df)
    red = health[health["health_status"] == "Red"]["service"].tolist()
    amber = health[health["health_status"] == "Amber"]["service"].tolist()
    lines = [
        f"# ITSM Operations Status Report — {date.today().isoformat()}",
        "", "## Executive summary",
        f"- Total tickets in window: **{k['total_tickets']}**",
        f"- Open incidents: **{k['open_incidents']}** ({k['high_priority_open']} high priority)",
        f"- SLA breach rate: **{k['sla_breach_rate']:.1%}**",
        f"- Mean time to resolve: **{k['mttr_hours']} h**",
        f"- Customer-impacting incidents: **{k['customer_impacting']}**",
        "", "## Service health",
        f"- Red services: {', '.join(red) if red else 'none'}",
        f"- Amber services: {', '.join(amber) if amber else 'none'}",
        "", "## PMO action plan",
    ]
    for _, r in action_plan.iterrows():
        lines.append(f"- **[{r['priority']}] {r['problem']}** — {r['evidence']}. Owner: {r['recommended_owner']}. Next step: {r['next_step']} (target: {r['target']}).")
    lines += ["", "---", "_Generated from synthetic data. Portfolio project by Samadrita Acharya._"]
    return "\n".join(lines)
