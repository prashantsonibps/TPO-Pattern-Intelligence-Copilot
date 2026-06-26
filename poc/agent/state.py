"""LangGraph shared state for the audit pipeline."""

import operator
from typing import Annotated, TypedDict


class AuditState(TypedDict, total=False):
    case_id: str
    member_id: str
    provider_id: str
    cpt: str
    icd10: str
    allowed_amount: float
    clinical_note: str
    extracted_facts: dict
    documented_minutes: int
    policy_result: dict
    policy_violations: list
    payment_risk: dict
    provider_cluster: dict
    spend_anomaly: dict
    confidence_score: float
    confidence_breakdown: dict
    route_decision: str
    tpo_recommendation: dict
    escalation_payload: dict
    execution_trace: Annotated[list, operator.add]
