"""LangGraph pipeline nodes."""

import pandas as pd

from poc.agent.tools import (
    extract_facts_from_note,
    validate_policy,
    run_payment_risk,
    run_provider_cluster,
    run_anomaly_detection,
    compute_confidence,
    build_tpo_recommendation,
    build_escalation_payload,
)

_claims_cache = None


def set_claims_data(claims):
    global _claims_cache
    _claims_cache = claims


def get_claims():
    global _claims_cache
    if _claims_cache is None:
        from poc.config import CLAIMS_PATH
        _claims_cache = pd.read_csv(CLAIMS_PATH)
        _claims_cache["service_date"] = pd.to_datetime(_claims_cache["service_date"])
    return _claims_cache


def _trace(step, node, summary, details=None):
    return [{"step": step, "node": node, "summary": summary, "details": details or {}}]


def extractor_node(state):
    facts = extract_facts_from_note(state["clinical_note"], state["cpt"])
    return {
        "extracted_facts": facts,
        "documented_minutes": facts.get("documented_minutes", 20),
        "execution_trace": _trace(
            "1", "Extractor",
            f"Extracted {facts.get('documented_minutes', '?')} documented minutes; "
            f"complexity={facts.get('complexity_level', 'unknown')}.",
            facts,
        ),
    }


def policy_node(state):
    result = validate_policy(
        state["cpt"],
        state.get("documented_minutes", 20),
        state["icd10"],
        state["clinical_note"],
    )
    summary = (
        "Policy compliant."
        if result["compliant"]
        else f"{len(result['violations'])} policy violation(s) detected."
    )
    return {
        "policy_result": result,
        "policy_violations": result["violations"],
        "execution_trace": _trace("2", "Policy", summary, result),
    }


def payment_risk_node(state):
    claims = get_claims()
    case = {
        "case_id": state.get("case_id", "AUDIT"),
        "member_id": state["member_id"],
        "provider_id": state["provider_id"],
        "cpt": state["cpt"],
        "icd10": state["icd10"],
        "allowed_amount": state["allowed_amount"],
        "minutes_documented": state.get("documented_minutes", 20),
        "clinical_note": state["clinical_note"],
    }
    risk = run_payment_risk(claims, case)
    return {
        "payment_risk": risk,
        "execution_trace": _trace(
            "3", "PaymentRiskClassifier",
            f"Payment integrity risk score: {risk['payment_risk_score']}% ({risk['risk_label']}).",
            risk,
        ),
    }


def provider_pattern_node(state):
    claims = get_claims()
    cluster = run_provider_cluster(claims, state["provider_id"])
    return {
        "provider_cluster": cluster,
        "execution_trace": _trace(
            "4", "ProviderPatternCluster",
            f"Provider assigned to cluster: {cluster['cluster_label']}.",
            cluster,
        ),
    }


def anomaly_node(state):
    claims = get_claims()
    anomaly = run_anomaly_detection(claims, state["member_id"])
    summary = "Spend anomaly detected." if anomaly["is_anomaly"] else "Spend within normal range."
    return {
        "spend_anomaly": anomaly,
        "execution_trace": _trace("5", "TimeSeriesAnomaly", summary, anomaly),
    }


def confidence_scorer_node(state):
    result = compute_confidence(
        state.get("policy_result", {}),
        state.get("payment_risk", {}),
        state.get("provider_cluster", {}),
        state.get("spend_anomaly", {}),
    )
    return {
        "confidence_score": result["confidence_score"],
        "confidence_breakdown": result["breakdown"],
        "route_decision": result["route_decision"],
        "execution_trace": _trace(
            "6", "ConfidenceScorer",
            f"Confidence: {result['confidence_score']}% → route={result['route_decision']}.",
            result,
        ),
    }


def finalize_node(state):
    tpo = build_tpo_recommendation(state)
    escalation = (
        build_escalation_payload(state)
        if state.get("route_decision") == "human_escalation"
        else {}
    )

    route = state.get("route_decision", "human_escalation")
    node_name = "AutoResolve" if route == "auto_resolve" else "HumanEscalation"
    summary = "Claim auto-resolved." if route == "auto_resolve" else "Claim escalated to human auditor."

    return {
        "tpo_recommendation": tpo,
        "escalation_payload": escalation,
        "execution_trace": _trace("7", node_name, summary, {"tpo": tpo, "escalation": escalation}),
    }
