"""KPI computation, SLA breach probability model and service health scoring."""
from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

FEATURE_COLS = ["priority", "service", "category", "assignment_group", "change_related", "age_hours"]


def compute_kpis(df: pd.DataFrame) -> dict:
    resolved = df[df["status"].isin(["Resolved", "Closed"])]
    open_df = df[~df["status"].isin(["Resolved", "Closed"])]
    breach_rate = float(resolved["sla_breached"].mean()) if len(resolved) else 0.0
    mttr = float(resolved["actual_resolution_hours"].mean()) if len(resolved) else 0.0
    return {
        "total_tickets": len(df),
        "open_incidents": int(len(open_df)),
        "resolved_incidents": int(len(resolved)),
        "sla_breach_rate": round(breach_rate, 4),
        "mttr_hours": round(mttr, 1),
        "high_priority_open": int(open_df["priority"].isin(["P1 - Critical", "P2 - High"]).sum()),
        "customer_impacting": int(df["customer_impact"].sum()),
    }


def add_age_hours(df: pd.DataFrame, now: pd.Timestamp | None = None) -> pd.DataFrame:
    now = now or pd.Timestamp.now()
    df = df.copy()
    open_mask = df["actual_resolution_hours"].isna()
    df["age_hours"] = df["actual_resolution_hours"]
    df.loc[open_mask, "age_hours"] = (now - pd.to_datetime(df.loc[open_mask, "created_at"])).dt.total_seconds() / 3600.0
    df["age_hours"] = df["age_hours"].clip(lower=0.1)
    return df


def train_breach_model(df: pd.DataFrame, random_state: int = 42):
    data = add_age_hours(df)
    resolved = data[data["status"].isin(["Resolved", "Closed"])].dropna(subset=["actual_resolution_hours"])
    X = resolved[FEATURE_COLS]
    y = resolved["sla_breached"].astype(int)
    pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), ["priority", "service", "category", "assignment_group"])], remainder="passthrough")
    model = Pipeline([("pre", pre), ("clf", GradientBoostingClassifier(random_state=random_state))])
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=random_state, stratify=y)
    model.fit(X_tr, y_tr)
    auc = roc_auc_score(y_te, model.predict_proba(X_te)[:, 1])
    return model, float(auc)


def score_open_tickets(df: pd.DataFrame, model) -> pd.DataFrame:
    data = add_age_hours(df)
    open_df = data[~data["status"].isin(["Resolved", "Closed"])].copy()
    if open_df.empty:
        open_df["breach_probability"] = []
        open_df["risk_level"] = []
        return open_df
    open_df["breach_probability"] = model.predict_proba(open_df[FEATURE_COLS])[:, 1]
    open_df["risk_level"] = open_df["breach_probability"].apply(risk_level)
    open_df["suggested_action"] = open_df.apply(_suggest_action, axis=1)
    return open_df.sort_values("breach_probability", ascending=False)


def risk_level(p: float) -> str:
    if p >= 0.7:
        return "High"
    if p >= 0.4:
        return "Medium"
    return "Low"


def _suggest_action(row: pd.Series) -> str:
    if row["breach_probability"] >= 0.7:
        if row["priority"] in ("P1 - Critical", "P2 - High"):
            return "Escalate to major incident manager"
        return "Reassign or raise priority review"
    if row["breach_probability"] >= 0.4:
        return "Chase assignment group and verify owner"
    return "Monitor within normal queue"


def service_health(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for svc, g in df.groupby("service"):
        resolved = g[g["status"].isin(["Resolved", "Closed"])]
        open_g = g[~g["status"].isin(["Resolved", "Closed"])]
        breach = resolved["sla_breached"].mean() if len(resolved) else 0.0
        mttr_ratio = (resolved["actual_resolution_hours"] / resolved["sla_target_hours"]).mean() if len(resolved) else 0.0
        hp_open = open_g["priority"].isin(["P1 - Critical", "P2 - High"]).sum()
        impact_rate = g["customer_impact"].mean()
        score = 100.0 - min(breach * 100 * 0.45, 45) - min(max(mttr_ratio - 1, 0) * 20, 20) - min(hp_open * 2.5, 20) - min(impact_rate * 100 * 0.15, 15)
        score = round(max(score, 0), 1)
        rows.append({"service": svc, "tickets": len(g), "open": len(open_g), "sla_breach_rate": round(float(breach), 3), "avg_mttr_ratio": round(float(mttr_ratio), 2), "high_priority_open": int(hp_open), "customer_impact_rate": round(float(impact_rate), 3), "health_score": score, "health_status": health_status(score)})
    return pd.DataFrame(rows).sort_values("health_score")


def health_status(score: float) -> str:
    if score >= 80:
        return "Green"
    if score >= 60:
        return "Amber"
    return "Red"
