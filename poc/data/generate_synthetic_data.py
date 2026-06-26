"""Generate synthetic healthcare claims data with embedded fraud patterns."""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT

ICD10_CODES = [
    "E11.9", "I10", "J06.9", "M54.5", "F41.1",
    "N18.3", "J44.1", "I25.10", "G43.909", "K21.0",
]

CPT_CODES = ["99213", "99214", "99215", "99309", "99310", "G0156"]
EM_CODES = ["99213", "99214", "99215"]
HOME_CODES = ["99309", "99310", "G0156"]

CLINICAL_NOTE_TEMPLATES = {
    "99213": "Patient seen for {minutes} minutes. Brief history and exam performed. Stable chronic conditions reviewed.",
    "99214": "Patient evaluated for {minutes} minutes. Moderate complexity decision-making. Medication adjustments discussed.",
    "99215": "Comprehensive evaluation lasting {minutes} minutes. High complexity management of multiple conditions.",
    "99309": "Home visit completed in {minutes} minutes. Patient assessed, vitals stable, care plan reviewed.",
    "99310": "Extended home health visit of {minutes} minutes. Skilled nursing assessment and wound care documented.",
    "G0156": "Home health aide services provided for {minutes} minutes. Personal care assistance documented.",
}


def _date_range(start: datetime, days: int) -> datetime:
    return start + timedelta(days=random.randint(0, days))


def generate_members(n: int = 25) -> pd.DataFrame:
    members = []
    for i in range(1, n + 1):
        members.append({
            "member_id": f"M-{1000 + i}",
            "age": random.randint(45, 85),
            "gender": random.choice(["F", "M"]),
            "plan_type": random.choice(["Medicare Advantage", "Commercial PPO"]),
        })
    return pd.DataFrame(members)


def generate_providers(n: int = 40) -> pd.DataFrame:
    providers = []
    for i in range(1, n + 1):
        specialty = random.choice(["Primary Care", "Home Health", "Internal Medicine", "Family Medicine"])
        providers.append({
            "provider_id": f"P-{200 + i}",
            "provider_name": f"Provider {i}",
            "specialty": specialty,
            "npi": f"{1000000000 + i}",
        })
    return pd.DataFrame(providers)


def _make_claim(
    claim_id: int,
    member_id: str,
    provider_id: str,
    service_date: datetime,
    cpt: str,
    icd10: str,
    allowed_amount: float,
    minutes_documented: int,
    is_suspicious: bool,
) -> dict:
    note = CLINICAL_NOTE_TEMPLATES.get(cpt, "Clinical encounter documented.").format(minutes=minutes_documented)
    return {
        "claim_id": f"C-{claim_id:05d}",
        "member_id": member_id,
        "provider_id": provider_id,
        "service_date": service_date.strftime("%Y-%m-%d"),
        "icd10": icd10,
        "cpt": cpt,
        "allowed_amount": round(allowed_amount, 2),
        "minutes_documented": minutes_documented,
        "clinical_note": note,
        "is_suspicious": int(is_suspicious),
        "claim_type": "Professional",
        "place_of_service": random.choice(["11", "12", "13"]),
    }


def generate_claims(members: pd.DataFrame, providers: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    claims: list[dict] = []
    claim_counter = 1
    base_date = datetime(2025, 1, 1)

    normal_providers = providers["provider_id"].tolist()[:30]
    suspicious_em_provider = "P-231"
    suspicious_home_provider = "P-232"
    suspicious_pair_provider = "P-233"

    demo_member_em = "M-1001"
    demo_member_home = "M-1002"
    demo_member_pair = "M-1003"

    # Baseline claims across members and providers
    for _, member in members.iterrows():
        n_claims = random.randint(8, 20)
        for _ in range(n_claims):
            provider_id = random.choice(normal_providers)
            cpt = random.choices(CPT_CODES, weights=[0.4, 0.3, 0.1, 0.1, 0.05, 0.05])[0]
            required = {"99213": 20, "99214": 30, "99215": 40, "99309": 25, "99310": 35, "G0156": 30}.get(cpt, 20)
            minutes = required + random.randint(0, 10)
            amount = random.uniform(80, 350)
            claims.append(_make_claim(
                claim_counter, member["member_id"], provider_id,
                _date_range(base_date, 300), cpt, random.choice(ICD10_CODES),
                amount, minutes, False,
            ))
            claim_counter += 1

    # Pattern 1: E/M upcoding — bill 99215 with only 15 min documented
    for week in range(8):
        claims.append(_make_claim(
            claim_counter, demo_member_em, suspicious_em_provider,
            base_date + timedelta(days=30 + week * 7),
            "99215", "I10", 285.0, 15, True,
        ))
        claim_counter += 1

    # Pattern 2: Home health burst — sudden spike in home visits
    for day in range(12):
        claims.append(_make_claim(
            claim_counter, demo_member_home, suspicious_home_provider,
            datetime(2025, 9, 1) + timedelta(days=day),
            random.choice(HOME_CODES), "E11.9", random.uniform(120, 220), 20, True,
        ))
        claim_counter += 1

    # Pattern 3: Unusual code pairing — high E/M + home health same day
    pair_date = datetime(2025, 10, 15)
    claims.append(_make_claim(
        claim_counter, demo_member_pair, suspicious_pair_provider,
        pair_date, "99214", "M54.5", 195.0, 18, True,
    ))
    claim_counter += 1
    claims.append(_make_claim(
        claim_counter, demo_member_pair, suspicious_pair_provider,
        pair_date, "99310", "M54.5", 175.0, 15, True,
    ))
    claim_counter += 1

    # Add normal history for demo members so anomaly detection has baseline
    for mid, pid in [(demo_member_em, suspicious_em_provider), (demo_member_home, suspicious_home_provider), (demo_member_pair, suspicious_pair_provider)]:
        for _ in range(6):
            cpt = random.choice(["99213", "99214"])
            claims.append(_make_claim(
                claim_counter, mid, pid,
                _date_range(base_date, 200), cpt, random.choice(ICD10_CODES),
                random.uniform(90, 160), 25, False,
            ))
            claim_counter += 1

    df = pd.DataFrame(claims)
    df["service_date"] = pd.to_datetime(df["service_date"])

    demo_cases = [
        {
            "case_id": "CASE-001",
            "title": "E/M Level Inflation",
            "description": "Provider bills CPT 99215 (high complexity) but clinical note documents only 15 minutes.",
            "member_id": demo_member_em,
            "provider_id": suspicious_em_provider,
            "target_claim_id": None,
            "pattern_type": "em_upcoding",
            "clinical_note_override": (
                "Patient seen for 15 minutes. Brief follow-up on hypertension. "
                "Vitals reviewed, no medication changes. Stable."
            ),
            "cpt": "99215",
            "icd10": "I10",
            "allowed_amount": 285.0,
            "expected_route": "human_escalation",
        },
        {
            "case_id": "CASE-002",
            "title": "Home Health Billing Burst",
            "description": "Member shows sudden spike in home health claims — operational anomaly plus payment risk.",
            "member_id": demo_member_home,
            "provider_id": suspicious_home_provider,
            "target_claim_id": None,
            "pattern_type": "home_health_burst",
            "clinical_note_override": (
                "Home health visit completed in 20 minutes. Skilled nursing assessment. "
                "Patient stable, glucose monitored."
            ),
            "cpt": "99310",
            "icd10": "E11.9",
            "allowed_amount": 185.0,
            "expected_route": "human_escalation",
        },
        {
            "case_id": "CASE-003",
            "title": "Unusual Code Pairing",
            "description": "High-complexity E/M and home visit billed same day with insufficient documentation.",
            "member_id": demo_member_pair,
            "provider_id": suspicious_pair_provider,
            "target_claim_id": None,
            "pattern_type": "code_pairing",
            "clinical_note_override": (
                "Patient evaluated for 18 minutes in office setting. Moderate complexity. "
                "Also home visit same day documented for 15 minutes."
            ),
            "cpt": "99214",
            "icd10": "M54.5",
            "allowed_amount": 195.0,
            "expected_route": "human_escalation",
        },
        {
            "case_id": "CASE-004",
            "title": "Clean Claim — Auto Resolve",
            "description": "Properly documented visit with appropriate CPT level — auto-resolves despite provider cluster flag.",
            "member_id": "M-1010",
            "provider_id": "P-210",
            "target_claim_id": None,
            "pattern_type": "clean",
            "clinical_note_override": (
                "Patient evaluated for 35 minutes. Moderate complexity decision-making. "
                "Diabetes and hypertension managed. Medication reconciliation completed."
            ),
            "cpt": "99214",
            "icd10": "E11.9",
            "allowed_amount": 165.0,
            "expected_route": "auto_resolve",
        },
    ]

    # Attach latest suspicious claim id per demo case where applicable
    for case in demo_cases[:3]:
        subset = df[(df["member_id"] == case["member_id"]) & (df["is_suspicious"] == 1)]
        if not subset.empty:
            case["target_claim_id"] = subset.sort_values("service_date").iloc[-1]["claim_id"]

    return df, demo_cases


def main() -> None:
    members = generate_members()
    providers = generate_providers()
    claims, demo_cases = generate_claims(members, providers)

    claims.to_csv(DATA_DIR / "claims.csv", index=False)
    members.to_csv(DATA_DIR / "members.csv", index=False)
    providers.to_csv(DATA_DIR / "providers.csv", index=False)

    with open(DATA_DIR / "demo_cases.json", "w") as f:
        json.dump(demo_cases, f, indent=2)

    print(f"Generated {len(claims)} claims, {len(members)} members, {len(providers)} providers")
    print(f"Suspicious claims: {claims['is_suspicious'].sum()}")
    print(f"Demo cases: {len(demo_cases)}")


if __name__ == "__main__":
    main()
