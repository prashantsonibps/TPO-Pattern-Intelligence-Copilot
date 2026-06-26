"""TPO360 — Payment pattern review workspace."""

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
    render_solution_cards,
    render_sidebar_brand,
)

CHART_COLORS = {"primary": "#0066CC", "accent": "#F5A623", "navy": "#0D2D4E"}

CASE_HINTS = {
    "CASE-001": "Expected: human escalation (E/M upcoding)",
    "CASE-002": "Expected: human escalation (spend anomaly)",
    "CASE-003": "Expected: human escalation (code pairing)",
    "CASE-004": "Expected: auto-resolve (clean claim)",
}


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
        with st.spinner("Initializing models…"):
            train_models()


def render_sidebar(demo_cases):
    render_sidebar_brand()

    st.markdown("**Select claim scenario**")
    case_labels = [f"{c['case_id']}: {c['title']}" for c in demo_cases]
    selected_idx = st.selectbox(
        "Claim scenario",
        range(len(case_labels)),
        format_func=lambda i: case_labels[i],
        label_visibility="collapsed",
        key="case_selector",
    )
    case = demo_cases[selected_idx]

    if st.session_state.get("last_case_id") != case["case_id"]:
        st.session_state["last_case_id"] = case["case_id"]
        st.session_state.pop("audit_result", None)

    st.caption(CASE_HINTS.get(case["case_id"], ""))

    st.markdown(
        f"""<div class="sidebar-meta">
        <strong>{case['title']}</strong><br/>
        {case['description']}<br/><br/>
        Member <code>{case['member_id']}</code> · Provider <code>{case['provider_id']}</code><br/>
        CPT <code>{case['cpt']}</code> · ICD-10 <code>{case['icd10']}</code> · ${case['allowed_amount']}
        </div>""",
        unsafe_allow_html=True,
    )

    with st.expander("Clinical documentation", expanded=False):
        st.write(case["clinical_note_override"])

    st.markdown("---")
    st.markdown("**System status**")
    if ANTHROPIC_API_KEY:
        st.markdown('<span class="status-pill status-ok">LLM connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-pill status-warn">Offline extraction</span>', unsafe_allow_html=True)
    st.caption(f"Model: `{ANTHROPIC_MODEL}`")

    st.markdown("---")
    st.markdown("**How to run**")
    st.markdown("1. Pick a scenario above\n2. Click **Run audit**\n3. Review tabs below")

    return case


def render_result_banner(result):
    route = result.get("route_decision", "human_escalation")
    score = result.get("confidence_score", 0)
    if route == "auto_resolve":
        st.markdown(
            f'<div class="coti-badge-auto">Auto-resolved · Confidence {score}% (threshold {CONFIDENCE_AUTO_THRESHOLD}%)</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="coti-badge-escalate">Human review required · Escalation confidence {score}%</div>',
            unsafe_allow_html=True,
        )


def render_execution_trace(trace):
    for item in trace:
        expanded = item["step"] in ("1", "6", "7")
        with st.expander(f"Step {item['step']}: {item['node']} — {item['summary']}", expanded=expanded):
            st.json(item.get("details", {}))


def render_tpo_summary(result):
    tpo = result.get("tpo_recommendation", {})
    render_solution_cards([
        {"title": "Treatment", "desc": tpo.get("treatment", "")},
        {"title": "Payment", "desc": tpo.get("payment", "")},
        {"title": "Operations", "desc": tpo.get("operations", "")},
        {"title": "Summary", "desc": tpo.get("summary", "")},
    ])


def render_payment_risk(payment_risk):
    score = payment_risk.get("payment_risk_score", 0)
    bar_color = CHART_COLORS["accent"] if score >= 60 else CHART_COLORS["primary"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Payment integrity risk", "font": {"color": CHART_COLORS["navy"], "size": 16}},
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
    fig.update_layout(height=260, margin=dict(t=40, b=10, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
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
        fig.update_layout(height=300, margin=dict(t=40, b=20), plot_bgcolor="white", paper_bgcolor="white")
        if spend_anomaly.get("is_anomaly"):
            fig.add_annotation(
                text="Anomaly", x=df.iloc[-1]["month"], y=df.iloc[-1]["total_spend"],
                showarrow=True, arrowhead=2, font=dict(color=CHART_COLORS["accent"]),
            )
        st.plotly_chart(fig, use_container_width=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Anomaly", "Yes" if spend_anomaly.get("is_anomaly") else "No")
    c2.metric("Z-score", spend_anomaly.get("z_score", 0))
    c3.metric("Latest spend", f"${spend_anomaly.get('latest_spend', 0):,.0f}")
    st.caption(spend_anomaly.get("anomaly_details", ""))


def main():
    st.set_page_config(
        page_title="TPO360 Pattern Review",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_theme()
    ensure_models()

    try:
        claims, demo_cases = load_data()
    except FileNotFoundError:
        st.error("Sample data missing. Run `python poc/data/generate_synthetic_data.py` locally.")
        return

    set_claims_data(claims)

    with st.sidebar:
        case = render_sidebar(demo_cases)

    render_topbar()
    render_site_header(active="Payment Accuracy")
    render_hero(
        "360 Pattern Review",
        "LangGraph claim audit across prepay and postpay workflows — policy validation, "
        "payment risk scoring, provider pattern detection, and human-in-the-loop routing.",
    )

    st.markdown('<div class="coti-panel">', unsafe_allow_html=True)
    st.markdown('<p class="coti-panel-title">Audit workspace</p>', unsafe_allow_html=True)

    col_run, col_info = st.columns([1, 2])
    with col_run:
        run_clicked = st.button("Run audit", type="primary", use_container_width=True)
    with col_info:
        st.caption(
            f"Running **{case['case_id']}** through 7 pipeline stages: "
            "Extractor → Policy → Risk → Cluster → Anomaly → Confidence → Route"
        )

    if run_clicked:
        with st.spinner("Running LangGraph pipeline…"):
            st.session_state["audit_result"] = run_audit(case, claims)

    if "audit_result" in st.session_state:
        result = st.session_state["audit_result"]
        render_result_banner(result)

        tabs = st.tabs([
            "Execution trace", "Payment risk", "Provider patterns",
            "Spend anomaly", "TPO output", "Escalation JSON",
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
            else:
                st.info("No escalation payload — claim was auto-resolved.")
            violations = result.get("policy_result", {}).get("violations", [])
            if violations:
                st.markdown("**Policy violations**")
                for v in violations:
                    st.markdown(f"- {v}")
    else:
        st.info("Select a claim scenario in the sidebar, then click **Run audit**.")

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
