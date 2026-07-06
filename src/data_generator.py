"""Synthetic ServiceNow/Jira-style ITSM ticket data generator."""
from __future__ import annotations
import numpy as np
import pandas as pd

PRIORITIES = ["P1 - Critical", "P2 - High", "P3 - Moderate", "P4 - Low"]
SLA_TARGETS = {"P1 - Critical": 4, "P2 - High": 8, "P3 - Moderate": 24, "P4 - Low": 72}
CATEGORIES = ["Network", "Application", "Database", "Access Management", "Cloud Infrastructure", "Security"]
SERVICES = ["SAP ERP", "E-Commerce Platform", "CRM System", "Data Warehouse", "Payment Gateway", "API Gateway"]
GROUPS = ["Service Desk L1", "Application Support L2", "Infrastructure Ops", "Cloud Platform Team", "Security Operations", "Vendor Escalation"]
ROOT_CAUSES = ["Configuration Error", "Capacity / Resource Exhaustion", "Software Defect", "Failed Change", "Third-Party Outage", "Human Error", "Expired Certificate"]
REGIONS = ["DACH", "EMEA", "Americas", "APAC"]


def generate_tickets(n_tickets: int = 2500, days: int = 180, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    end = pd.Timestamp.today().normalize()
    created_at = end - pd.to_timedelta(rng.integers(0, days, n_tickets), unit="D") + pd.to_timedelta(rng.integers(0, 24, n_tickets), unit="h")
    priority = rng.choice(PRIORITIES, n_tickets, p=[0.07, 0.18, 0.45, 0.30])
    category = rng.choice(CATEGORIES, n_tickets)
    service = rng.choice(SERVICES, n_tickets)
    group = rng.choice(GROUPS, n_tickets)
    root = rng.choice(ROOT_CAUSES, n_tickets, p=[0.22, 0.17, 0.17, 0.16, 0.10, 0.10, 0.08])
    region = rng.choice(REGIONS, n_tickets, p=[0.40, 0.30, 0.18, 0.12])
    change_related = (root == "Failed Change") | ((category == "Cloud Infrastructure") & (rng.random(n_tickets) < 0.25))
    targets = pd.Series(priority).map(SLA_TARGETS).to_numpy(float)
    penalty = np.ones(n_tickets)
    penalty *= np.where(np.isin(service, ["SAP ERP", "Payment Gateway"]), 1.25, 1.0)
    penalty *= np.where(group == "Vendor Escalation", 1.45, 1.0)
    penalty *= np.where(change_related, 1.30, 1.0)
    actual = np.maximum(np.round(rng.lognormal(-0.35, 0.75, n_tickets) * penalty * targets, 1), 0.1)
    age_days = (end - pd.Series(created_at).dt.normalize()).dt.days.to_numpy()
    is_open = rng.random(n_tickets) < np.clip(0.55 - age_days / 30, 0.02, 0.55)
    status = np.where(is_open, rng.choice(["In Progress", "On Hold", "New"], n_tickets), rng.choice(["Resolved", "Closed"], n_tickets))
    resolved_at = pd.Series(created_at) + pd.to_timedelta(actual, unit="h")
    resolved_at = resolved_at.where(~is_open, pd.NaT)
    actual_out = np.where(is_open, np.nan, actual)
    customer_impact = rng.random(n_tickets) < np.select([priority == "P1 - Critical", priority == "P2 - High", priority == "P3 - Moderate"], [0.85, 0.45, 0.15], default=0.05)
    df = pd.DataFrame({"ticket_id": [f"INC{1000000+i}" for i in range(n_tickets)], "created_at": created_at, "resolved_at": resolved_at, "priority": priority, "category": category, "service": service, "assignment_group": group, "status": status, "sla_target_hours": targets, "actual_resolution_hours": actual_out, "sla_breached": (np.where(is_open, actual > targets, actual_out > targets)).astype(bool), "root_cause": root, "change_related": change_related, "customer_impact": customer_impact, "region": region})
    return df.sort_values("created_at").reset_index(drop=True)


def save_sample(path: str = "sample_data/tickets.csv", n_tickets: int = 500) -> pd.DataFrame:
    df = generate_tickets(n_tickets=n_tickets)
    df.to_csv(path, index=False)
    return df

if __name__ == "__main__":
    print(f"Generated {len(save_sample())} tickets -> sample_data/tickets.csv")
