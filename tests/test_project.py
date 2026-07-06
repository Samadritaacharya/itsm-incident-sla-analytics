"""Tests for data generation, KPI/scoring logic and the action plan."""

import pandas as pd
import pytest

from src.data_generator import generate_tickets, SLA_TARGETS
from src.scoring import compute_kpis, train_breach_model, score_open_tickets, service_health, risk_level, health_status, add_age_hours
from src.recommendations import build_action_plan, export_markdown_report


@pytest.fixture(scope="module")
def df():
    return generate_tickets(n_tickets=1200, days=120, seed=7)


def test_generator_shape_and_columns(df):
    expected = {"ticket_id", "created_at", "resolved_at", "priority", "category", "service", "assignment_group", "status", "sla_target_hours", "actual_resolution_hours", "sla_breached", "root_cause", "change_related", "customer_impact", "region"}
    assert expected.issubset(df.columns)
    assert len(df) == 1200
    assert df["ticket_id"].is_unique


def test_generator_reproducible():
    a = generate_tickets(n_tickets=300, seed=99)
    b = generate_tickets(n_tickets=300, seed=99)
    pd.testing.assert_frame_equal(a, b)


def test_sla_targets_match_priority(df):
    mapped = df["priority"].map(SLA_TARGETS)
    assert (df["sla_target_hours"] == mapped).all()


def test_resolved_tickets_have_resolution_hours(df):
    resolved = df[df["status"].isin(["Resolved", "Closed"])]
    assert resolved["actual_resolution_hours"].notna().all()
    assert (resolved["actual_resolution_hours"] > 0).all()
    open_df = df[~df["status"].isin(["Resolved", "Closed"])]
    assert open_df["actual_resolution_hours"].isna().all()


def test_breach_flag_consistent(df):
    resolved = df[df["status"].isin(["Resolved", "Closed"])]
    expected = resolved["actual_resolution_hours"] > resolved["sla_target_hours"]
    assert (resolved["sla_breached"] == expected).all()


def test_kpis(df):
    k = compute_kpis(df)
    assert k["total_tickets"] == len(df)
    assert k["open_incidents"] + k["resolved_incidents"] == len(df)
    assert 0 <= k["sla_breach_rate"] <= 1
    assert k["mttr_hours"] > 0


def test_add_age_hours_positive(df):
    out = add_age_hours(df)
    assert (out["age_hours"] > 0).all()


def test_model_trains_and_scores(df):
    model, auc = train_breach_model(df)
    assert auc > 0.6
    scored = score_open_tickets(df, model)
    assert scored["breach_probability"].between(0, 1).all()
    assert set(scored["risk_level"]).issubset({"High", "Medium", "Low"})
    assert scored["breach_probability"].is_monotonic_decreasing


def test_risk_level_thresholds():
    assert risk_level(0.9) == "High"
    assert risk_level(0.5) == "Medium"
    assert risk_level(0.1) == "Low"


def test_service_health_scores(df):
    h = service_health(df)
    assert h["health_score"].between(0, 100).all()
    assert set(h["health_status"]).issubset({"Green", "Amber", "Red"})
    assert len(h) == df["service"].nunique()


def test_health_status_bands():
    assert health_status(85) == "Green"
    assert health_status(70) == "Amber"
    assert health_status(40) == "Red"


def test_action_plan(df):
    plan = build_action_plan(df)
    assert not plan.empty
    assert {"problem", "recommended_owner", "priority", "next_step", "target"}.issubset(plan.columns)
    assert set(plan["priority"]).issubset({"High", "Medium", "Low"})


def test_markdown_report(df):
    plan = build_action_plan(df)
    md = export_markdown_report(df, plan)
    assert md.startswith("# ITSM Operations Status Report")
    assert "PMO action plan" in md
    assert "synthetic" in md.lower()
