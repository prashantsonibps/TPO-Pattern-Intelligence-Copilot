"""Time-series anomaly detection on member claim spend."""

from __future__ import annotations

import pandas as pd
import numpy as np


def get_member_spend_timeseries(claims: pd.DataFrame, member_id: str) -> pd.DataFrame:
    """Monthly aggregated allowed amount for a member."""
    subset = claims[claims["member_id"] == member_id].copy()
    subset["service_date"] = pd.to_datetime(subset["service_date"])
    subset["month"] = subset["service_date"].dt.to_period("M").astype(str)

    monthly = (
        subset.groupby("month")
        .agg(claim_count=("claim_id", "count"), total_spend=("allowed_amount", "sum"))
        .reset_index()
        .sort_values("month")
    )
    return monthly


def detect_spend_anomaly(claims: pd.DataFrame, member_id: str, z_threshold: float = 2.0) -> dict:
    """
    Flag anomalous months using rolling z-score on monthly spend.
    Returns anomaly details and chart-ready timeseries.
    """
    monthly = get_member_spend_timeseries(claims, member_id)

    if len(monthly) < 3:
        return {
            "is_anomaly": False,
            "anomaly_score": 0.0,
            "anomaly_month": None,
            "anomaly_details": "Insufficient history for anomaly detection.",
            "timeseries": monthly.to_dict(orient="records"),
        }

    spend = monthly["total_spend"].values
    mean_spend = np.mean(spend[:-1]) if len(spend) > 1 else np.mean(spend)
    std_spend = np.std(spend[:-1]) if len(spend) > 1 else np.std(spend) or 1.0

    latest_spend = spend[-1]
    z_score = (latest_spend - mean_spend) / max(std_spend, 1.0)
    is_anomaly = abs(z_score) >= z_threshold

    anomaly_month = monthly.iloc[-1]["month"] if is_anomaly else None
    details = (
        f"Latest month spend ${latest_spend:,.0f} is {z_score:.1f} std devs from baseline "
        f"(mean ${mean_spend:,.0f}). Operational review recommended."
        if is_anomaly
        else f"Latest month spend ${latest_spend:,.0f} within normal range (z={z_score:.2f})."
    )

    return {
        "is_anomaly": bool(is_anomaly),
        "anomaly_score": round(float(abs(z_score)), 2),
        "z_score": round(float(z_score), 2),
        "anomaly_month": anomaly_month,
        "anomaly_details": details,
        "baseline_mean": round(float(mean_spend), 2),
        "latest_spend": round(float(latest_spend), 2),
        "timeseries": monthly.to_dict(orient="records"),
    }
