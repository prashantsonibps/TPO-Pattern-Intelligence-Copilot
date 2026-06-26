"""Streamlit dashboard for TPO Pattern Intelligence Copilot."""

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
    OPENAI_API_KEY,
    OPENAI_MODEL,
    CONFIDENCE_AUTO_THRESHOLD,
)
from poc.agent.graph import run_audit
from poc.agent.nodes import set_claims_data
from poc.models.train_models import main as train_models


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
        with st.spinner("Training models (first run only)..."):
            train_models()


def render_header():
    st.set_page_config(
        page_title="TPO Pattern Intelligence Copilot",
        page_icon="🏥",
        layout="wide",
    )
    st.title("TPO Pattern Intelligence Copilot")
    st.caption(
        "LangGraph claim audit pipeline — policy validation, payment risk scoring, "
        "provider pattern detection, and spend anomaly analysis"
    )

    api_status = "Connected" if OPENAI_API_KEY else "Offline fallback"
    st.info(f"LLM: **{OPENAI_MODEL}** — {api_status}")


def render_case_selector(demo_cases):
    st.sidebar.header("Sample Cases")
    case_labels = [f"{c['case_id']}: {c['title']}" for c in demo_cases]
    selected_idx = st.sidebar.selectbox(
        "Select case", range(len(case_labels)), format_func=lambda i: case_labels[i]
    )
    case = demo_cases[selected_idx]

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Pattern:** `{case['pattern_type']}`")
    st.sidebar.markdown(case["description"])
    st.sidebar.markdown(f"- Member: `{case['member_id']}`")
    st.sidebar.markdown(f"- Provider: `{case['provider_id']}`")
    st.sidebar.markdown(f"- CPT: `{case['cpt']}` | ICD-10: `{case['icd10']}`")

    with st.sidebar.expander("Clinical Note"):
        st.write(case["clinical_note_override"])

    return case


def render_execution_trace(trace):
    st.subheader("Execution Trace")
    for item in trace:
        expanded = item["step"] in ("1", "6", "7")
        with st.expander(
            f"Step {item['step']}: {item['node']} — {item['summary']}", expanded=expanded
        ):
            st.json(item.get("details", {}))


def render_result_banner(result):
    route = result.get("route_decision", "human_escalation")
    score = result.get("confidence_score", 0)

    if route == "auto_resolve":
        st.success(f"Auto-Resolved | Confidence: {score}% (threshold: {CONFIDENCE_AUTO_THRESHOLD}%)")
    else:
        st.warning(f"Requires Human Auditor | Escalation Confidence: {score}%")


def render_tpo_summary(result):
    tpo = result.get("tpo_recommendation", {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### Treatment")
        st.write(tpo.get("treatment", ""))
    with col2:
        st.markdown("#### Payment")
        st.write(tpo.get("payment", ""))
    with col3:
        st.markdown("#### Operations")
        st.write(tpo.get("operations", ""))
    st.markdown(f"**Summary:** {tpo.get('summary', '')}")


def render_payment_risk(payment_risk):
    score = payment_risk.get("payment_risk_score", 0)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Payment Integrity Risk"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#d62728" if score >= 60 else "#2ca02c"},
            "steps": [
                {"range": [0, 40], "color": "#e8f5e9"},
                {"range": [40, 70], "color": "#fff9c4"},
                {"range": [70, 100], "color": "#ffcdd2"},
            ],
        },
    ))
    fig.update_layout(height=280, margin=dict(t=50, b=20, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Top contributing features**")
    for feat in payment_risk.get("top_features", []):
        st.progress(min(feat["importance"], 1.0), text=f"{feat['feature']} ({feat['importance']:.3f})")


def render_cluster(provider_cluster):
    st.metric("Cluster Label", provider_cluster.get("cluster_label", "Unknown"))
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
        fig = px.bar(
            df, x="month", y="total_spend",
            title="Member Monthly Spend", color_discrete_sequence=["#1f77b4"],
        )
        if spend_anomaly.get("is_anomaly"):
            fig.add_annotation(
                text="Anomaly", x=df.iloc[-1]["month"], y=df.iloc[-1]["total_spend"],
                showarrow=True, arrowhead=2, font=dict(color="red"),
            )
        fig.update_layout(height=320, margin=dict(t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Anomaly Detected", "Yes" if spend_anomaly.get("is_anomaly") else "No")
    col2.metric("Z-Score", spend_anomaly.get("z_score", 0))
    col3.metric("Latest Spend", f"${spend_anomaly.get('latest_spend', 0):,.0f}")
    st.write(spend_anomaly.get("anomaly_details", ""))


def render_escalation_payload(payload):
    if payload:
        st.subheader("Escalation Payload")
        st.json(payload)


def main():
    render_header()
    ensure_models()

    try:
        claims, demo_cases = load_data()
    except FileNotFoundError:
        st.error("Data not found. Run the setup commands in README.md")
        if st.button("Generate data and train models"):
            from poc.data.generate_synthetic_data import main as gen
            gen()
            train_models()
            st.cache_data.clear()
            st.rerun()
        return

    set_claims_data(claims)
    case = render_case_selector(demo_cases)

    if st.button("Run Audit", type="primary", use_container_width=True):
        with st.spinner("Running audit pipeline..."):
            progress = st.progress(0, text="Starting...")
            steps = [
                "Extractor", "Policy", "Payment Risk", "Provider Cluster",
                "Anomaly", "Confidence", "Finalize",
            ]
            for i, step in enumerate(steps):
                progress.progress((i + 1) / len(steps), text=f"Running: {step}...")
            result = run_audit(case, claims)
            progress.progress(1.0, text="Complete.")
            st.session_state["audit_result"] = result

    if "audit_result" in st.session_state:
        result = st.session_state["audit_result"]
        render_result_banner(result)

        tabs = st.tabs([
            "Execution Trace", "Payment Risk", "Provider Patterns",
            "Spend Anomaly", "TPO Summary", "Escalation",
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
            render_escalation_payload(result.get("escalation_payload", {}))
            policy = result.get("policy_result", {})
            if policy.get("violations"):
                st.markdown("**Policy Violations**")
                for v in policy["violations"]:
                    st.markdown(f"- {v}")


if __name__ == "__main__":
    main()
