"""Payment integrity risk classification."""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from poc.config import CLAIMS_PATH, MODEL_PATH, FEATURE_COLUMNS_PATH, MODELS_DIR


def build_claim_features(claims: pd.DataFrame) -> pd.DataFrame:
    """Engineer features for a single claim using historical context."""
    claims = claims.copy()
    claims["service_date"] = pd.to_datetime(claims["service_date"])

    em_codes = {"99213", "99214", "99215", "99203", "99204", "99205"}
    home_codes = {"99309", "99310", "G0156"}

    cpt_time_req = {"99213": 20, "99214": 30, "99215": 40, "99309": 25, "99310": 35, "G0156": 30}

    features = []
    for _, row in claims.iterrows():
        member_history = claims[
            (claims["member_id"] == row["member_id"]) & (claims["service_date"] < row["service_date"])
        ]
        provider_history = claims[
            (claims["provider_id"] == row["provider_id"]) & (claims["service_date"] <= row["service_date"])
        ]

        required_minutes = cpt_time_req.get(row["cpt"], 20)
        time_gap = required_minutes - row["minutes_documented"]

        same_day_claims = claims[
            (claims["member_id"] == row["member_id"])
            & (claims["service_date"] == row["service_date"])
            & (claims["claim_id"] != row["claim_id"])
        ]

        provider_em_ratio = (
            provider_history["cpt"].isin(em_codes).mean() if len(provider_history) > 0 else 0
        )
        provider_avg_amount = provider_history["allowed_amount"].mean() if len(provider_history) > 0 else row["allowed_amount"]
        member_monthly_spend = member_history[
            member_history["service_date"] >= row["service_date"] - pd.Timedelta(days=30)
        ]["allowed_amount"].sum()

        features.append({
            "claim_id": row["claim_id"],
            "allowed_amount": row["allowed_amount"],
            "minutes_documented": row["minutes_documented"],
            "time_gap": time_gap,
            "is_high_em": int(row["cpt"] in {"99214", "99215"}),
            "is_home_health": int(row["cpt"] in home_codes),
            "same_day_claim_count": len(same_day_claims),
            "provider_claim_volume": len(provider_history),
            "provider_em_ratio": provider_em_ratio,
            "provider_avg_amount": provider_avg_amount,
            "member_prior_claims": len(member_history),
            "member_30d_spend": member_monthly_spend,
            "amount_vs_provider_avg": row["allowed_amount"] / max(provider_avg_amount, 1),
            "is_suspicious": row["is_suspicious"],
        })

    return pd.DataFrame(features)


FEATURE_COLUMNS = [
    "allowed_amount", "minutes_documented", "time_gap", "is_high_em", "is_home_health",
    "same_day_claim_count", "provider_claim_volume", "provider_em_ratio",
    "provider_avg_amount", "member_prior_claims", "member_30d_spend", "amount_vs_provider_avg",
]


def train_classifier(claims: pd.DataFrame) -> RandomForestClassifier:
    df = build_claim_features(claims)
    X = df[FEATURE_COLUMNS]
    y = df["is_suspicious"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42, class_weight="balanced")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, zero_division=0))

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(FEATURE_COLUMNS_PATH, "w") as f:
        json.dump(FEATURE_COLUMNS, f)

    return model


def load_classifier() -> RandomForestClassifier:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run train_models.py first.")
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


def score_claim(claims: pd.DataFrame, claim_row: pd.Series, model: RandomForestClassifier | None = None) -> dict:
    """Return payment risk score and feature importances for a claim."""
    if model is None:
        model = load_classifier()

    combined = pd.concat([claims, claim_row.to_frame().T], ignore_index=True)
    combined = combined.drop_duplicates(subset=["claim_id"], keep="last")
    feat_df = build_claim_features(combined)
    row = feat_df[feat_df["claim_id"] == claim_row["claim_id"]].iloc[0]

    X = pd.DataFrame([row[FEATURE_COLUMNS].values], columns=FEATURE_COLUMNS)
    prob = float(model.predict_proba(X)[0][1])
    importances = sorted(
        zip(FEATURE_COLUMNS, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True,
    )[:3]

    return {
        "payment_risk_score": round(prob * 100, 1),
        "risk_label": "High" if prob >= 0.5 else "Low",
        "top_features": [{"feature": f, "importance": round(float(i), 3)} for f, i in importances],
        "feature_values": {col: float(row[col]) for col in FEATURE_COLUMNS},
    }


if __name__ == "__main__":
    claims = pd.read_csv(CLAIMS_PATH)
    train_classifier(claims)
