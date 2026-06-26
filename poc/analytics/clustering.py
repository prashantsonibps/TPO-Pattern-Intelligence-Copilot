"""Provider billing pattern clustering."""

from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from poc.config import CLAIMS_PATH, CLUSTER_MODEL_PATH, MODELS_DIR

CLUSTER_LABELS = {
    0: "Standard Primary Care",
    1: "High E/M Utilization",
    2: "Home Health Focused",
    3: "High-Volume Outlier",
}


def build_provider_features(claims: pd.DataFrame) -> pd.DataFrame:
    claims = claims.copy()
    em_codes = {"99213", "99214", "99215"}
    home_codes = {"99309", "99310", "G0156"}

    rows = []
    for provider_id, group in claims.groupby("provider_id"):
        rows.append({
            "provider_id": provider_id,
            "claim_volume": len(group),
            "avg_allowed_amount": group["allowed_amount"].mean(),
            "em_ratio": group["cpt"].isin(em_codes).mean(),
            "high_em_ratio": group["cpt"].isin({"99214", "99215"}).mean(),
            "home_health_ratio": group["cpt"].isin(home_codes).mean(),
            "code_diversity": group["cpt"].nunique(),
            "avg_minutes": group["minutes_documented"].mean(),
            "suspicious_rate": group["is_suspicious"].mean(),
        })
    return pd.DataFrame(rows)


PROVIDER_FEATURE_COLS = [
    "claim_volume", "avg_allowed_amount", "em_ratio", "high_em_ratio",
    "home_health_ratio", "code_diversity", "avg_minutes", "suspicious_rate",
]


def train_cluster_model(claims: pd.DataFrame, n_clusters: int = 4) -> dict:
    pf = build_provider_features(claims)
    scaler = StandardScaler()
    X = scaler.fit_transform(pf[PROVIDER_FEATURE_COLS])

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    pf["cluster"] = kmeans.fit_predict(X)

    artifact = {"scaler": scaler, "kmeans": kmeans, "provider_features": pf}
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CLUSTER_MODEL_PATH, "wb") as f:
        pickle.dump(artifact, f)

    return artifact


def load_cluster_model() -> dict:
    if not CLUSTER_MODEL_PATH.exists():
        raise FileNotFoundError(f"Cluster model not found. Run train_models.py first.")
    with open(CLUSTER_MODEL_PATH, "rb") as f:
        return pickle.load(f)


def get_provider_cluster(claims: pd.DataFrame, provider_id: str, artifact: dict | None = None) -> dict:
    if artifact is None:
        artifact = load_cluster_model()

    pf = build_provider_features(claims)
    provider_row = pf[pf["provider_id"] == provider_id]
    if provider_row.empty:
        return {"cluster_id": -1, "cluster_label": "Unknown", "risk_note": "Provider not found"}

    scaler = artifact["scaler"]
    kmeans = artifact["kmeans"]
    X = scaler.transform(provider_row[PROVIDER_FEATURE_COLS])
    cluster_id = int(kmeans.predict(X)[0])
    label = CLUSTER_LABELS.get(cluster_id, f"Cluster {cluster_id}")

    risk_notes = {
        "High E/M Utilization": "Provider billing pattern matches cluster with elevated E/M code usage — prepay review recommended.",
        "Home Health Focused": "Provider cluster shows concentrated home health billing — verify medical necessity.",
        "High-Volume Outlier": "Provider exhibits high claim volume relative to peers — SIU pattern review candidate.",
        "Standard Primary Care": "Provider billing pattern within normal primary care range.",
    }

    return {
        "cluster_id": cluster_id,
        "cluster_label": label,
        "risk_note": risk_notes.get(label, ""),
        "provider_stats": provider_row.iloc[0][PROVIDER_FEATURE_COLS].to_dict(),
    }


if __name__ == "__main__":
    claims = pd.read_csv(CLAIMS_PATH)
    train_cluster_model(claims)
    print(get_provider_cluster(claims, "P-231"))
