"""LangGraph state machine for claim audit."""

import pandas as pd
from langgraph.graph import StateGraph, END

from poc.agent.state import AuditState
from poc.agent.nodes import (
    extractor_node,
    policy_node,
    payment_risk_node,
    provider_pattern_node,
    anomaly_node,
    confidence_scorer_node,
    finalize_node,
    set_claims_data,
)


def build_audit_graph():
    graph = StateGraph(AuditState)

    graph.add_node("extractor", extractor_node)
    graph.add_node("policy", policy_node)
    graph.add_node("payment_risk", payment_risk_node)
    graph.add_node("provider_pattern", provider_pattern_node)
    graph.add_node("anomaly", anomaly_node)
    graph.add_node("confidence_scorer", confidence_scorer_node)
    graph.add_node("finalize", finalize_node)

    graph.set_entry_point("extractor")
    graph.add_edge("extractor", "policy")
    graph.add_edge("policy", "payment_risk")
    graph.add_edge("payment_risk", "provider_pattern")
    graph.add_edge("provider_pattern", "anomaly")
    graph.add_edge("anomaly", "confidence_scorer")
    graph.add_edge("confidence_scorer", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()


def run_audit(case, claims=None):
    if claims is not None:
        set_claims_data(claims)

    initial_state = {
        "case_id": case["case_id"],
        "member_id": case["member_id"],
        "provider_id": case["provider_id"],
        "cpt": case["cpt"],
        "icd10": case["icd10"],
        "allowed_amount": case["allowed_amount"],
        "clinical_note": case["clinical_note_override"],
        "execution_trace": [],
    }

    graph = build_audit_graph()
    return graph.invoke(initial_state)
