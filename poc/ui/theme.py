"""Cotiviti-inspired UI theme and layout helpers."""

COTIVITI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Source Sans 3', 'Helvetica Neue', Arial, sans-serif;
    color: #1a2b4a;
}

#MainMenu, footer, header[data-testid="stHeader"] {
    visibility: hidden;
    height: 0;
}

.block-container {
    padding-top: 0 !important;
    max-width: 1200px;
}

.coti-topbar {
    background: #0d2d4e;
    color: #ffffff;
    padding: 0.45rem 1.5rem;
    font-size: 0.82rem;
    margin: -1rem -1rem 0 -1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.coti-topbar a {
    color: #7ec8ff;
    text-decoration: none;
}

.coti-header {
    background: #ffffff;
    border-bottom: 1px solid #dde3ea;
    padding: 1rem 1.5rem 1.25rem;
    margin: 0 -1rem 1.5rem -1rem;
}

.coti-logo {
    font-size: 1.85rem;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: #0066cc;
    margin: 0;
    line-height: 1;
}

.coti-logo span {
    color: #f5a623;
}

.coti-nav {
    display: flex;
    gap: 1.75rem;
    margin-top: 0.85rem;
    font-size: 0.92rem;
    font-weight: 600;
}

.coti-nav span {
    color: #5a6b7d;
    cursor: default;
}

.coti-nav .active {
    color: #0066cc;
    border-bottom: 2px solid #0066cc;
    padding-bottom: 0.15rem;
}

.coti-hero {
    background: linear-gradient(135deg, #0d2d4e 0%, #1a4a7a 55%, #0066cc 100%);
    color: #ffffff;
    padding: 2rem 1.75rem;
    border-radius: 4px;
    margin-bottom: 1.5rem;
}

.coti-hero h1 {
    color: #ffffff !important;
    font-size: 1.85rem !important;
    font-weight: 700 !important;
    margin-bottom: 0.5rem !important;
}

.coti-hero p {
    color: #d8e8f8;
    font-size: 1.02rem;
    margin: 0;
    max-width: 720px;
}

.coti-stat-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.coti-stat {
    background: #ffffff;
    border: 1px solid #dde3ea;
    border-top: 3px solid #0066cc;
    padding: 1.1rem 1rem;
    border-radius: 2px;
}

.coti-stat .value {
    font-size: 1.55rem;
    font-weight: 700;
    color: #0066cc;
    line-height: 1.2;
}

.coti-stat .label {
    font-size: 0.78rem;
    color: #5a6b7d;
    margin-top: 0.35rem;
    line-height: 1.35;
}

.coti-solutions {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.coti-solution-card {
    background: #ffffff;
    border: 1px solid #dde3ea;
    padding: 1.15rem;
    border-radius: 2px;
    min-height: 130px;
}

.coti-solution-card h4 {
    color: #0066cc;
    font-size: 0.95rem;
    margin: 0 0 0.45rem 0;
    font-weight: 700;
}

.coti-solution-card p {
    color: #5a6b7d;
    font-size: 0.82rem;
    margin: 0;
    line-height: 1.45;
}

.coti-panel {
    background: #ffffff;
    border: 1px solid #dde3ea;
    border-radius: 2px;
    padding: 1.25rem 1.35rem;
    margin-bottom: 1rem;
}

.coti-panel-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1a2b4a;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #eef2f6;
}

.coti-badge-auto {
    background: #e8f5e9;
    color: #2e7d32;
    border-left: 4px solid #43a047;
    padding: 0.85rem 1rem;
    border-radius: 2px;
    font-weight: 600;
    margin-bottom: 1rem;
}

.coti-badge-escalate {
    background: #fff8e1;
    color: #e65100;
    border-left: 4px solid #f5a623;
    padding: 0.85rem 1rem;
    border-radius: 2px;
    font-weight: 600;
    margin-bottom: 1rem;
}

.coti-sidebar-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #5a6b7d;
    font-weight: 700;
    margin-bottom: 0.35rem;
}

div[data-testid="stSidebar"] {
    background: #f4f6f8;
    border-right: 1px solid #dde3ea;
}

div[data-testid="stSidebar"] .block-container {
    padding-top: 1rem;
}

.stButton > button[kind="primary"] {
    background: #0066cc !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 2px !important;
}

.stButton > button[kind="primary"]:hover {
    background: #0052a3 !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid #dde3ea;
}

.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    color: #5a6b7d;
}

.stTabs [aria-selected="true"] {
    color: #0066cc !important;
}

@media (max-width: 900px) {
    .coti-stat-row, .coti-solutions {
        grid-template-columns: repeat(2, 1fr);
    }
}
</style>
"""


def inject_theme():
    import streamlit as st
    st.markdown(COTIVITI_CSS, unsafe_allow_html=True)


def render_topbar():
    import streamlit as st
    st.markdown(
        """
        <div class="coti-topbar">
            <span>Pattern Intelligence Platform — Prepay &amp; Postpay Review</span>
            <span><a href="#">Client Center</a></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_site_header(active="Payment Accuracy"):
    import streamlit as st
    nav_items = ["Payment Accuracy", "Risk Adjustment", "Quality and Stars", "Engagement"]
    nav_html = "".join(
        f'<span class="{"active" if item == active else ""}">{item}</span>'
        for item in nav_items
    )
    st.markdown(
        f"""
        <div class="coti-header">
            <p class="coti-logo">coti<span>viti</span></p>
            <div class="coti-nav">{nav_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title, subtitle):
    import streamlit as st
    st.markdown(
        f"""
        <div class="coti-hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stats(stats):
    import streamlit as st
    cards = "".join(
        f'<div class="coti-stat"><div class="value">{s["value"]}</div><div class="label">{s["label"]}</div></div>'
        for s in stats
    )
    st.markdown(f'<div class="coti-stat-row">{cards}</div>', unsafe_allow_html=True)


def render_solution_cards(cards):
    import streamlit as st
    html = "".join(
        f'<div class="coti-solution-card"><h4>{c["title"]}</h4><p>{c["desc"]}</p></div>'
        for c in cards
    )
    st.markdown(f'<div class="coti-solutions">{html}</div>', unsafe_allow_html=True)


def render_panel(title, content_fn):
    import streamlit as st
    st.markdown(f'<div class="coti-panel-title">{title}</div>', unsafe_allow_html=True)
    content_fn()
