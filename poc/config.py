"""Configuration and paths."""

from pathlib import Path
import os

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"

CLAIMS_PATH = DATA_DIR / "claims.csv"
PROVIDERS_PATH = DATA_DIR / "providers.csv"
MEMBERS_PATH = DATA_DIR / "members.csv"
DEMO_CASES_PATH = DATA_DIR / "demo_cases.json"
MODEL_PATH = MODELS_DIR / "payment_risk_model.pkl"
FEATURE_COLUMNS_PATH = MODELS_DIR / "feature_columns.json"
CLUSTER_MODEL_PATH = MODELS_DIR / "provider_cluster_model.pkl"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

CONFIDENCE_AUTO_THRESHOLD = 90.0

CPT_TIME_REQUIREMENTS = {
    "99213": 20,
    "99214": 30,
    "99215": 40,
    "99203": 30,
    "99204": 45,
    "99205": 60,
}

CPT_DESCRIPTIONS = {
    "99213": "Office visit, established patient, low complexity",
    "99214": "Office visit, established patient, moderate complexity",
    "99215": "Office visit, established patient, high complexity",
    "99203": "Office visit, new patient, low complexity",
    "99204": "Office visit, new patient, moderate complexity",
    "99205": "Office visit, new patient, high complexity",
    "99310": "Home visit, moderate complexity",
    "99309": "Home visit, low complexity",
    "G0156": "Home health aide services",
}
