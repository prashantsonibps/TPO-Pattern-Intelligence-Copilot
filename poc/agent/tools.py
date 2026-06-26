"""Tool functions used by LangGraph nodes."""

import json
import re

import pandas as pd

from poc.config import CPT_TIME_REQUIREMENTS, CPT_DESCRIPTIONS, OPENAI_API_KEY, OPENAI_MODEL
from poc.analytics.classifier import score_claim, load_classifier
from poc.analytics.clustering import get_provider_cluster
from poc.analytics.anomaly import detect_spend_anomaly


def extract_facts_from_note(clinical_note, cpt):
    """Extract structured facts from clinical note — LLM with regex fallback."""
    if OPENAI_API_KEY:
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import SystemMessage, HumanMessage

            llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0)
            system = (
                "You extract factual medical events from clinical notes. "
                "Return ONLY valid JSON with keys: documented_minutes (int), "
                "chief_complaint (str), procedures_performed (list[str]), "
                "complexity_level (low|moderate|high), key_phrases (list[str])."
            )
            response = llm.invoke([
                SystemMessage(content=system),
                HumanMessage(content=f"CPT billed: {cpt}\n\nClinical note:\n{clinical_note}"),
            ])
            text = response.content.strip()
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            return json.loads(text)
        except Exception:
            pass

    # Regex fallback
    minutes = 20
    match = re.search(r"(\d+)\s*min", clinical_note, re.I)
    if match:
        minutes = int(match.group(1))

    complexity = "moderate"
    if any(w in clinical_note.lower() for w in ["brief", "stable", "follow-up"]):
        complexity = "low"
    elif any(w in clinical_note.lower() for w in ["comprehensive", "high complexity", "multiple"]):
        complexity = "high"

    return {
        "documented_minutes": minutes,
        "chief_complaint": "Extracted from note (fallback mode)",
        "procedures_performed": ["Office evaluation"],
        "complexity_level": complexity,
        "key_phrases": re.findall(r"\b\w{4,}\b", clinical_note.lower())[:5],
    }


def validate_policy(cpt, documented_minutes, icd10, clinical_note):
    """Compare extracted facts against billing code requirements."""
    required_minutes = CPT_TIME_REQUIREMENTS.get(cpt, 20)
    cpt_desc = CPT_DESCRIPTIONS.get(cpt, "Unknown procedure")
    time_deficit = required_minutes - documented_minutes

    violations = []
    if time_deficit > 0:
        violations.append(
            f"CPT {cpt} ({cpt_desc}) requires ~{required_minutes} min; "
            f"note documents {documented_minutes} min (deficit: {time_deficit} min)."
        )

    high_em_codes = {"99214", "99215", "99204", "99205"}
    if cpt in high_em_codes and documented_minutes < required_minutes:
        violations.append(f"High-complexity E/M code {cpt} billed with insufficient documented time.")

    if "home" in clinical_note.lower() and cpt.startswith("992"):
        violations.append("Office E/M code billed but note references home visit context.")

    compliant = len(violations) == 0
    return {
        "compliant": compliant,
        "required_minutes": required_minutes,
        "documented_minutes": documented_minutes,
        "cpt_description": cpt_desc,
        "violations": violations,
        "policy_score": 100.0 if compliant else max(20.0, 100.0 - len(violations) * 35),
    }


def run_payment_risk(claims, case):
    claim_row = pd.Series({
        "claim_id": case.get("claim_id", f"AUDIT-{case['case_id']}"),
        "member_id": case["member_id"],
        "provider_id": case["provider_id"],
        "service_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "icd10": case["icd10"],
        "cpt": case["cpt"],
        "allowed_amount": case["allowed_amount"],
        "minutes_documented": case.get("minutes_documented", 20),
        "clinical_note": case.get("clinical_note", ""),
        "is_suspicious": 0,
        "claim_type": "Professional",
        "place_of_service": "11",
    })
    try:
        model = load_classifier()
        return score_claim(claims, claim_row, model)
    except FileNotFoundError:
        return {"payment_risk_score": 50.0, "risk_label": "Unknown", "top_features": [], "feature_values": {}}


def run_provider_cluster(claims, provider_id):
    try:
        return get_provider_cluster(claims, provider_id)
    except FileNotFoundError:
        return {"cluster_id": -1, "cluster_label": "Unknown", "risk_note": "Cluster model not trained."}


def run_anomaly_detection(claims, member_id):
    return detect_spend_anomaly(claims, member_id)


def compute_confidence(policy_result, payment_risk, provider_cluster, spend_anomaly):
    """Weighted confidence score for routing decision."""
    policy_score = policy_result.get("policy_score", 50)
    risk_score = payment_risk.get("payment_risk_score", 50)

    cluster_penalty = 0
    cluster_label = provider_cluster.get("cluster_label", "")
    if cluster_label in ("High E/M Utilization", "Home Health Focused", "High-Volume Outlier"):
        cluster_penalty = 15

    anomaly_penalty = 10 if spend_anomaly.get("is_anomaly") else 0
    escalation_score = min(
        100,
        (100 - policy_score) * 0.35 + risk_score * 0.35 + cluster_penalty + anomaly_penalty,
    )
    auto_score = min(100, policy_score * 0.45 + (100 - risk_score) * 0.45)

    needs_escalation = (
        not policy_result.get("compliant", True)
        or risk_score >= 55
        or spend_anomaly.get("is_anomaly", False)
        or (cluster_penalty > 0 and risk_score >= 40)
    )

    if needs_escalation:
        route = "human_escalation"
        confidence_score = escalation_score
    else:
        route = "auto_resolve" if auto_score >= 90 else "human_escalation"
        confidence_score = auto_score if route == "auto_resolve" else escalation_score

    return {
        "confidence_score": round(confidence_score, 1),
        "route_decision": route,
        "breakdown": {
            "policy_score": policy_score,
            "payment_risk_score": risk_score,
            "auto_resolve_score": round(auto_score, 1),
            "escalation_score": round(escalation_score, 1),
            "cluster_label": cluster_label,
            "cluster_penalty": cluster_penalty,
            "anomaly_penalty": anomaly_penalty,
            "anomaly_detected": spend_anomaly.get("is_anomaly", False),
        },
    }


def build_tpo_recommendation(state):
    route = state.get("route_decision", "human_escalation")
    policy = state.get("policy_result", {})
    risk = state.get("payment_risk", {})
    cluster = state.get("provider_cluster", {})
    anomaly = state.get("spend_anomaly", {})

    if route == "auto_resolve":
        return {
            "treatment": "No care gap identified. Documentation supports billed service level.",
            "payment": "Auto-approved for payment. Claim passes prepay policy and risk checks.",
            "operations": "No analyst queue assignment. Claim cleared through automated review.",
            "summary": "High-confidence auto-resolution — all TPO signals within acceptable thresholds.",
        }

    treatment_actions = []
    if not policy.get("compliant"):
        treatment_actions.append("Request additional clinical documentation to support billed complexity.")
    if anomaly.get("is_anomaly"):
        treatment_actions.append("Review care coordination — unusual utilization pattern detected.")

    payment_actions = ["Hold claim for prepay review."]
    if risk.get("payment_risk_score", 0) >= 70:
        payment_actions.append("Refer for fraud, waste, and abuse pattern investigation.")
    if cluster.get("cluster_label") in ("High E/M Utilization", "Home Health Focused"):
        payment_actions.append(f"Flag provider cluster: {cluster['cluster_label']}.")

    ops_actions = [
        "Route to credentialed analyst with structured escalation payload.",
        "Priority queue based on combined risk score and pattern signals.",
    ]

    return {
        "treatment": " ".join(treatment_actions) or "Clinical documentation review recommended.",
        "payment": " ".join(payment_actions),
        "operations": " ".join(ops_actions),
        "summary": "Human-in-the-loop escalation — ambiguous or high-risk TPO signals require analyst review.",
    }


def build_escalation_payload(state):
    return {
        "case_id": state.get("case_id"),
        "route": state.get("route_decision"),
        "confidence_score": state.get("confidence_score"),
        "policy_violations": state.get("policy_violations", []),
        "payment_risk_score": state.get("payment_risk", {}).get("payment_risk_score"),
        "provider_cluster": state.get("provider_cluster", {}).get("cluster_label"),
        "anomaly_detected": state.get("spend_anomaly", {}).get("is_anomaly"),
        "anomaly_details": state.get("spend_anomaly", {}).get("anomaly_details"),
        "evidence_chain": [
            step["summary"] for step in state.get("execution_trace", [])
        ],
        "recommended_action": state.get("tpo_recommendation", {}).get("payment", ""),
    }
