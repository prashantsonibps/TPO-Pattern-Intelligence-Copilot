"""TPO360 UI — Cotiviti-inspired layout and styles."""

from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
LOGO_PATH = ASSETS_DIR / "cotiviti-logo.png"

COTIVITI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Source Sans 3', 'Helvetica Neue', Arial, sans-serif;
    color: #1a2b4a;
}

/* Keep Streamlit header visible so the sidebar toggle always works */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

header[data-testid="stHeader"] {
    background: #ffffff !important;
    border-bottom: 1px solid #dde3ea;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1180px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #f4f6f8 !important;
    border-right: 1px solid #dde3ea;
    min-width: 320px !important;
    width: 320px !important;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1rem;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 0.5rem !important;
}

.sidebar-brand {
    padding: 0.25rem 0 1rem 0;
    border-bottom: 1px solid #dde3ea;
    margin-bottom: 1rem;
}

.sidebar-brand img {
    height: 28px;
    width: auto;
    margin-bottom: 0.75rem;
}

.sidebar-section-title {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #5a6b7d;
    font-weight: 700;
    margin: 0 0 0.35rem 0;
}

.sidebar-product {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0d2d4e;
    margin: 0 0 0.25rem 0;
}

.sidebar-meta {
    background: #ffffff;
    border: 1px solid #dde3ea;
    border-radius: 4px;
    padding: 0.75rem;
    margin: 0.75rem 0;
    font-size: 0.88rem;
    line-height: 1.5;
}

.sidebar-meta code {
    font-size: 0.82rem;
    color: #0066cc;
}

.status-pill {
    display: inline-block;
    padding: 0.15rem 0.55rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
}
.status-ok { background: #e8f5e9; color: #2e7d32; }
.status-warn { background: #fff3e0; color: #e65100; }

.coti-topbar {
    background: #0d2d4e;
    color: #ffffff;
    padding: 0.5rem 1.25rem;
    font-size: 0.82rem;
    margin: -1rem -1rem 1rem -1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.coti-topbar a { color: #7ec8ff; text-decoration: none; }

.coti-header {
    background: #ffffff;
    border: 1px solid #dde3ea;
    border-radius: 4px;
    padding: 0.85rem 1.15rem;
    margin-bottom: 1rem;
}

.coti-header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
}

.coti-header img { height: 32px; width: auto; }

.coti-nav {
    display: flex;
    gap: 1.25rem;
    font-size: 0.88rem;
    font-weight: 600;
    flex-wrap: wrap;
}

.coti-nav span { color: #5a6b7d; }
.coti-nav .active {
    color: #0066cc;
    border-bottom: 2px solid #0066cc;
    padding-bottom: 0.1rem;
}

.coti-hero {
    background: linear-gradient(135deg, #0d2d4e 0%, #1a4a7a 50%, #0066cc 100%);
    color: #ffffff;
    padding: 1.75rem 1.5rem;
    border-radius: 4px;
    margin-bottom: 1rem;
}

.coti-hero h1 {
    color: #ffffff !important;
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    margin: 0 0 0.45rem 0 !important;
    line-height: 1.25 !important;
}

.coti-hero p {
    color: #d8e8f8;
    font-size: 0.98rem;
    margin: 0;
    max-width: 680px;
    line-height: 1.5;
}

.coti-panel {
    background: #ffffff;
    border: 1px solid #dde3ea;
    border-radius: 4px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}

.coti-panel-title {
    font-size: 1rem;
    font-weight: 700;
    color: #1a2b4a;
    margin: 0 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #eef2f6;
}

.coti-badge-auto {
    background: #e8f5e9;
    color: #2e7d32;
    border-left: 4px solid #43a047;
    padding: 0.85rem 1rem;
    border-radius: 4px;
    font-weight: 600;
    margin-bottom: 1rem;
}

.coti-badge-escalate {
    background: #fff8e1;
    color: #e65100;
    border-left: 4px solid #f5a623;
    padding: 0.85rem 1rem;
    border-radius: 4px;
    font-weight: 600;
    margin-bottom: 1rem;
}

.coti-solutions {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
    margin-top: 0.5rem;
}

.coti-solution-card {
    background: #f8fafc;
    border: 1px solid #dde3ea;
    padding: 0.85rem;
    border-radius: 4px;
}

.coti-solution-card h4 {
    color: #0066cc;
    font-size: 0.88rem;
    margin: 0 0 0.35rem 0;
    font-weight: 700;
}

.coti-solution-card p {
    color: #5a6b7d;
    font-size: 0.8rem;
    margin: 0;
    line-height: 1.4;
}

.stButton > button[kind="primary"] {
    background: #0066cc !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 4px !important;
}

.stButton > button[kind="primary"]:hover {
    background: #0052a3 !important;
}

.stTabs [data-baseweb="tab-list"] {
    border-bottom: 2px solid #dde3ea;
}

.stTabs [aria-selected="true"] {
    color: #0066cc !important;
    font-weight: 700;
}

@media (max-width: 900px) {
    .coti-solutions { grid-template-columns: 1fr; }
    section[data-testid="stSidebar"] {
        min-width: 280px !important;
        width: 280px !important;
    }
}
</style>
"""


def inject_theme():
    import streamlit as st
    st.markdown(COTIVITI_CSS, unsafe_allow_html=True)


def _logo_html(height=32):
    if LOGO_PATH.exists():
        import base64
        b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()
        return f'<img src="data:image/png;base64,{b64}" alt="Cotiviti" style="height:{height}px;width:auto;" />'
    return '<span style="font-size:1.4rem;font-weight:700;color:#0066cc;">cotiviti</span>'


def render_sidebar_brand():
    import streamlit as st
    st.markdown(
        f'<div class="sidebar-brand">{_logo_html(26)}'
        f'<p class="sidebar-product">TPO360 Pattern Review</p>'
        f'<p class="sidebar-section-title">Claim audit workspace</p></div>',
        unsafe_allow_html=True,
    )


def render_topbar():
    import streamlit as st
    st.markdown(
        """
        <div class="coti-topbar">
            <span>Payment Accuracy · Prepay &amp; Postpay Pattern Review</span>
            <span><a href="https://www.cotiviti.com/solutions/payment-accuracy" target="_blank">Solutions</a></span>
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
            <div class="coti-header-row">
                {_logo_html(32)}
                <div class="coti-nav">{nav_html}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title, subtitle):
    import streamlit as st
    st.markdown(
        f'<div class="coti-hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def render_solution_cards(cards):
    import streamlit as st
    html = "".join(
        f'<div class="coti-solution-card"><h4>{c["title"]}</h4><p>{c["desc"]}</p></div>'
        for c in cards
    )
    st.markdown(f'<div class="coti-solutions">{html}</div>', unsafe_allow_html=True)
