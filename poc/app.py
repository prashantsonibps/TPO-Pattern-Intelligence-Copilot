"""Streamlit dashboard — Cotiviti-style Payment Accuracy workspace."""

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from poc.config import (
    CLAIMS_PATH,
    DEMO_CASES_PATH,
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    CONFIDENCE_AUTO_THRESHOLD,
)
from poc.agent.graph import run_audit
from poc.agent.nodes import set_claims_data
from poc.models.train_models import main as train_models
from poc.ui.theme import (
    inject_theme,
    render_topbar,
    render_site_header,
    render_hero,
    render_stats,
    render_solution_cards,
)

CHART_COLORS = {"primary": "#0066CC", "accent": "#F5A623", "navy": "#0D2D4E"}


@st.cache_data
def load_data():
    claims = pd.read_csv(CLAIMS_PATH)
    claims["service_date"] = pd.to_datetime(claims["service_date"])
    with open(DEMO_CASES_PATH) as f:
        demo_cases = json.load(f)
    return claims, demo_cases


def ensure_models():
    from poc.config import MODEL_PATH, CLUSTER_MODEL_PATH
    if not MODEL_PATH.exists() or not CLUSTER_MODEL_PATH.exists():
        with st.spinner("Training models..."):
            train_models()


def render_sidebar(demo_cases):
    st.sidebar.markdown('<p class="coti-sidebar-label">Claim Review</p>', unsafe_allow_html=True)
    st.sidebar.markdown("### 360 Pattern Review")
    st.sidebar.caption("Select a sample claim to run through the audit pipeline.")

    case_labels = [f"{c['case_id']}: {c['title']}" for c in demo_cases]
    selected_idx = st.sidebar.selectbox(
        "Sample case", range(len(case_labels)), format_func=lambda i: case_labels[i], label_visibility="collapsed"
    )
    case = demo_cases[selected_idx]

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Pattern type**  \n`{case['pattern_type']}`")
    st.sidebar.markdown(case["description"])

    col1, col2 = st.sidebar.columns(2)
    col1.markdown(f"**Member**  \n`{case['member_id']}`")
    col2.markdown(f"**Provider**  \n`{case['provider_id']}`")
    st.sidebar.markdown(f"**CPT** `{case['cpt']}` · **ICD-10** `{case['icd10']}` · **${case['allowed_amount']}`")

    with st.sidebar.expander("Clinical documentation"):
        st.write(case["clinical_note_override"])

    llm_status = "Anthropic connected" if ANTHROPIC_API_KEY else "Offline mode (regex fallback)"
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Model:** `{ANTHROPIC_MODEL}`")
    st.sidebar.markdown(f"**LLM status:** {llm_status}")

    if not ANTHROPIC_API_KEY:
        st.sidebar.warning("Add `ANTHROPIC_API_KEY` to your `.env` file to enable LLM extraction.")

    return case


def render_result_banner(result):
    route = result.get("route_decision", "human_escalation")
    score = result.get("confidence_score", 0)
    if route == "auto_resolve":
        st.markdown(
            f'<div class="coti-badge-auto">Auto-Resolved — Confidence {score}% (threshold {CONFIDENCE_AUTO_THRESHOLD}%)</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="coti-badge-escalate">Requires Human Auditor — Escalation confidence {score}%</div>',
            unsafe_allow_html=True,
        )


def render_execution_trace(trace):
    for item in trace:
        expanded = item["step"] in ("1", "6", "7")
        with st.expander(f"Step {item['step']}: {item['node']} — {item['summary']}", expanded=expanded):
            st.json(item.get("details", {}))


def render_tpo_summary(result):
    tpo = result.get("tpo_recommendation", {})
    cards = [
        {"title": "Treatment", "desc": tpo.get("treatment", "")},
        {"title": "Payment", "desc": tpo.get("payment", "")},
        {"title": "Operations", "desc": tpo.get("operations", "")},
        {"title": "Summary", "desc": tpo.get("summary", "")},
    ]
    render_solution_cards(cards)


def render_payment_risk(payment_risk):
    score = payment_risk.get("payment_risk_score", 0)
    bar_color = CHART_COLORS["accent"] if score >= 60 else CHART_COLORS["primary"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Payment Integrity Risk", "font": {"color": CHART_COLORS["navy"]}},
        number={"font": {"color": CHART_COLORS["navy"]}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": CHART_COLORS["navy"]},
            "bar": {"color": bar_color},
            "bgcolor": "white",
            "steps": [
                {"range": [0, 40], "color": "#E8F0FA"},
                {"range": [40, 70], "color": "#FFF3D6"},
                {"range": [70, 100], "color": "#FDE8E8"},
            ],
        },
    ))
    fig.update_layout(height=280, margin=dict(t=50, b=20, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("**Top contributing features**")
    for feat in payment_risk.get("top_features", []):
        st.progress(min(feat["importance"], 1.0), text=f"{feat['feature']} ({feat['importance']:.3f})")


def render_cluster(provider_cluster):
    st.metric("Provider cluster", provider_cluster.get("cluster_label", "Unknown"))
    st.write(provider_cluster.get("risk_note", ""))
    stats = provider_cluster.get("provider_stats", {})
    if stats:
        df = pd.DataFrame([stats]).T.reset_index()
        df.columns = ["Metric", "Value"]
        st.dataframe(df, use_container_width=True, hide_index=True)


def render_anomaly(spend_anomaly):
    ts = spend_anomaly.get("timeseries", [])
    if ts:
        df = pd.DataFrame(ts)
        fig = px.bar(df, x="month", y="total_spend", title="Member monthly spend")
        fig.update_traces(marker_color=CHART_COLORS["primary"])
        fig.update_layout(
            height=320, margin=dict(t=40, b=20),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(color=CHART_COLORS["navy"]),
        )
        if spend_anomaly.get("is_anomaly"):
            fig.add_annotation(
                text="Anomaly", x=df.iloc[-1]["month"], y=df.iloc[-1]["total_spend"],
                showarrow=True, arrowhead=2, font=dict(color=CHART_COLORS["accent"]),
            )
        st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Anomaly detected", "Yes" if spend_anomaly.get("is_anomaly") else "No")
    col2.metric("Z-score", spend_anomaly.get("z_score", 0))
    col3.metric("Latest spend", f"${spend_anomaly.get('latest_spend', 0):,.0f}")
    st.write(spend_anomaly.get("anomaly_details", ""))


def main():
    st.set_page_config(page_title="360 Pattern Review | Cotiviti", layout="wide")
    inject_theme()
    render_topbar()
    render_site_header(active="Payment Accuracy")
    render_hero(
        "360 Pattern Review",
        "AI-driven pattern identification and claim audit across prepay and postpay workflows. "
        "LangGraph orchestration with policy validation, risk scoring, and human-in-the-loop escalation.",
    )

    render_stats([
        {"value": "7", "label": "Pipeline stages in LangGraph audit graph"},
        {"value": "100%", "label": "Claims reviewed through integrated TPO signals"},
        {"value": "90%", "label": "Auto-resolve confidence threshold"},
        {"value": "4", "label": "Sample cases with embedded billing patterns"},
    ])

    render_solution_cards([
        {"title": "Determine Claim Responsibility", "desc": "Validate member context and billing policy compliance before payment."},
        {"title": "Ensure Claim Accuracy", "desc": "Extract clinical facts and match documented time against billed CPT levels."},
        {"title": "Detect FWA Patterns", "desc": "Score payment risk, cluster provider behavior, and flag spend anomalies."},
        {"title": "Human-in-the-Loop", "desc": "Route ambiguous claims to analysts with structured escalation payloads."},
    ])

    ensure_models()

    try:
        claims, demo_cases = load_data()
    except FileNotFoundError:
        st.error("Sample data not found. Run setup from README.md.")
        if st.button("Generate data and train models"):
            from poc.data.generate_synthetic_data import main as gen
            gen()
            train_models()
            st.cache_data.clear()
            st.rerun()
        return

    set_claims_data(claims)
    case = render_sidebar(demo_cases)

    st.markdown('<div class="coti-panel">', unsafe_allow_html=True)
    st.markdown('<div class="coti-panel-title">Run claim audit</div>', unsafe_allow_html=True)

    if st.button("Run audit pipeline", type="primary", use_container_width=True):
        with st.spinner("Executing LangGraph pipeline..."):
            progress = st.progress(0, text="Starting...")
            steps = ["Extractor", "Policy", "Payment Risk", "Provider Cluster", "Anomaly", "Confidence", "Finalize"]
            for i, step in enumerate(steps):
                progress.progress((i + 1) / len(steps), text=f"Running: {step}...")
            result = run_audit(case, claims)
            progress.progress(1.0, text="Complete.")
            st.session_state["audit_result"] = result

    if "audit_result" in st.session_state:
        result = st.session_state["audit_result"]
        render_result_banner(result)

        tabs = st.tabs([
            "Execution trace", "Payment risk", "Provider patterns",
            "Spend anomaly", "TPO recommendations", "Escalation payload",
        ])

        with tabs[0]:
            render_execution_trace(result.get("execution_trace", []))
        with tabs[1]:
            render_payment_risk(result.get("payment_risk", {}))
        with tabs[2]:
            render_cluster(result.get("provider_cluster", {}))
        with tabs[3]:
            render_anomaly(result.get("spend_anomaly", {}))
        with tabs[4]:
            render_tpo_summary(result)
        with tabs[5]:
            payload = result.get("escalation_payload", {})
            if payload:
                st.json(payload)
            policy = result.get("policy_result", {})
            if policy.get("violations"):
                st.markdown("**Policy violations**")
                for v in policy["violations"]:
                    st.markdown(f"- {v}")

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
