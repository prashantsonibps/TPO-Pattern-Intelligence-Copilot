"""Train ML models for payment risk and provider clustering."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from poc.config import CLAIMS_PATH
from poc.analytics.classifier import train_classifier
from poc.analytics.clustering import train_cluster_model
import pandas as pd


def main():
    if not CLAIMS_PATH.exists():
        print("Claims data not found. Running data generator...")
        from poc.data.generate_synthetic_data import main as gen
        gen()

    claims = pd.read_csv(CLAIMS_PATH)
    claims["service_date"] = pd.to_datetime(claims["service_date"])

    print("Training payment risk classifier...")
    train_classifier(claims)

    print("Training provider cluster model...")
    train_cluster_model(claims)

    print("Models saved successfully.")


if __name__ == "__main__":
    main()
