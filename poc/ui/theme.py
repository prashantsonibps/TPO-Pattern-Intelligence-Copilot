"""TPO360 UI — glassmorphism layout and styles."""

from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
LOGO_PATH = ASSETS_DIR / "cotiviti-logo.png"

COTIVITI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --glass-bg: rgba(255, 255, 255, 0.68);
    --glass-bg-strong: rgba(255, 255, 255, 0.82);
    --glass-border: rgba(255, 255, 255, 0.85);
    --glass-shadow: 0 8px 32px rgba(15, 35, 65, 0.08);
    --glass-blur: blur(22px) saturate(180%);
    --accent: #0071e3;
    --accent-soft: rgba(0, 113, 227, 0.12);
    --navy: #0d2d4e;
    --text: #1d1d1f;
    --text-muted: #6e6e73;
    --radius-lg: 20px;
    --radius-md: 14px;
    --radius-sm: 10px;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: var(--text);
}

/* App canvas — soft Apple-style gradient mesh */
.stApp {
    background:
        radial-gradient(ellipse 80% 60% at 10% 0%, rgba(0, 113, 227, 0.10), transparent 55%),
        radial-gradient(ellipse 70% 50% at 90% 10%, rgba(90, 200, 250, 0.12), transparent 50%),
        radial-gradient(ellipse 60% 40% at 50% 100%, rgba(13, 45, 78, 0.06), transparent 55%),
        linear-gradient(165deg, #eef2f8 0%, #f7f9fc 45%, #edf1f7 100%) !important;
}

/* Never clip the sidebar or header controls */
.stApp [data-testid="stAppViewContainer"],
.stApp [data-testid="stAppViewContainer"] > section.main,
section[data-testid="stSidebar"] {
    overflow: visible !important;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Header must stay visible — this is the sidebar open/close control */
header[data-testid="stHeader"] {
    visibility: visible !important;
    display: block !important;
    opacity: 1 !important;
    height: 3.25rem !important;
    min-height: 3.25rem !important;
    background: rgba(255, 255, 255, 0.72) !important;
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border-bottom: 1px solid rgba(0, 0, 0, 0.06) !important;
    z-index: 999999 !important;
}

header[data-testid="stHeader"] button,
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
button[data-testid="stSidebarCollapseButton"],
button[data-testid="baseButton-header"] {
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
}

[data-testid="stSidebarCollapsedControl"] {
    background: var(--glass-bg-strong) !important;
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: var(--glass-shadow) !important;
}

/* Sidebar — frosted glass panel, always accessible */
section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.58) !important;
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border-right: 1px solid rgba(255, 255, 255, 0.9) !important;
    box-shadow: 4px 0 28px rgba(15, 35, 65, 0.05) !important;
    min-width: 300px !important;
    width: 300px !important;
    z-index: 999990 !important;
}

section[data-testid="stSidebar"] > div {
    padding-top: 0.75rem;
}

section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding: 0.5rem 1rem 2rem 1rem;
    overflow-y: auto;
    max-height: calc(100vh - 1rem);
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 0.25rem !important;
}

/* Main content — leave room for sidebar toggle, no negative bleed */
.block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1200px;
}

section.main .block-container {
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* Sidebar brand */
.sidebar-brand {
    padding: 0.5rem 0 1.1rem 0;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    margin-bottom: 1rem;
}

.sidebar-brand img {
    height: 26px;
    width: auto;
    margin-bottom: 0.65rem;
    opacity: 0.95;
}

.sidebar-section-title {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    font-weight: 600;
    margin: 0 0 0.25rem 0;
}

.sidebar-product {
    font-size: 1.12rem;
    font-weight: 700;
    color: var(--navy);
    margin: 0 0 0.2rem 0;
    letter-spacing: -0.02em;
}

.sidebar-label {
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text);
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.01em;
}

.sidebar-meta {
    background: var(--glass-bg-strong);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    padding: 0.9rem 1rem;
    margin: 0.75rem 0;
    font-size: 0.86rem;
    line-height: 1.55;
    box-shadow: 0 4px 16px rgba(15, 35, 65, 0.04);
}

.sidebar-meta code {
    font-size: 0.8rem;
    color: var(--accent);
    background: var(--accent-soft);
    padding: 0.1rem 0.35rem;
    border-radius: 6px;
}

.sidebar-steps {
    background: var(--glass-bg);
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-radius: var(--radius-md);
    padding: 0.85rem 1rem;
    font-size: 0.84rem;
    line-height: 1.65;
    color: var(--text-muted);
}

.sidebar-steps strong {
    color: var(--text);
}

.status-pill {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.01em;
}
.status-ok {
    background: rgba(52, 199, 89, 0.15);
    color: #1b7a34;
    border: 1px solid rgba(52, 199, 89, 0.25);
}
.status-warn {
    background: rgba(255, 149, 0, 0.14);
    color: #b45309;
    border: 1px solid rgba(255, 149, 0, 0.25);
}

/* Top strip — no negative margins (those hid the sidebar toggle) */
.coti-topbar {
    background: var(--glass-bg-strong);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    color: var(--navy);
    padding: 0.55rem 1.1rem;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 0 0 1rem 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: var(--radius-md);
    border: 1px solid var(--glass-border);
    box-shadow: 0 4px 16px rgba(15, 35, 65, 0.04);
}

.coti-topbar a {
    color: var(--accent);
    text-decoration: none;
    font-weight: 600;
}

.coti-header {
    background: var(--glass-bg-strong);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 0.9rem 1.25rem;
    margin-bottom: 1rem;
    box-shadow: var(--glass-shadow);
}

.coti-header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
}

.coti-header img { height: 30px; width: auto; }

.coti-nav {
    display: flex;
    gap: 1.1rem;
    font-size: 0.84rem;
    font-weight: 600;
    flex-wrap: wrap;
}

.coti-nav span { color: var(--text-muted); }
.coti-nav .active {
    color: var(--accent);
    background: var(--accent-soft);
    padding: 0.25rem 0.65rem;
    border-radius: 999px;
}

.coti-hero {
    background: linear-gradient(135deg,
        rgba(13, 45, 78, 0.92) 0%,
        rgba(0, 102, 204, 0.88) 55%,
        rgba(90, 180, 255, 0.75) 100%);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    color: #ffffff;
    padding: 2rem 1.75rem;
    border-radius: var(--radius-lg);
    margin-bottom: 1.25rem;
    border: 1px solid rgba(255, 255, 255, 0.25);
    box-shadow: 0 12px 40px rgba(0, 66, 140, 0.18);
    position: relative;
    overflow: hidden;
}

.coti-hero::before {
    content: "";
    position: absolute;
    top: -40%;
    right: -10%;
    width: 280px;
    height: 280px;
    background: radial-gradient(circle, rgba(255,255,255,0.18) 0%, transparent 70%);
    pointer-events: none;
}

.coti-hero h1 {
    color: #ffffff !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    margin: 0 0 0.5rem 0 !important;
    line-height: 1.2 !important;
    letter-spacing: -0.03em !important;
    position: relative;
}

.coti-hero p {
    color: rgba(255, 255, 255, 0.88);
    font-size: 0.96rem;
    margin: 0;
    max-width: 700px;
    line-height: 1.55;
    position: relative;
}

.coti-panel {
    background: var(--glass-bg-strong);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 1.5rem 1.5rem 0.5rem 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: var(--glass-shadow);
}

.coti-panel-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--navy);
    margin: 0 0 1.1rem 0;
    padding-bottom: 0.65rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    letter-spacing: -0.02em;
}

.coti-run-hint {
    font-size: 0.86rem;
    color: var(--text-muted);
    line-height: 1.5;
    padding: 0.65rem 0.9rem;
    background: rgba(255, 255, 255, 0.5);
    border-radius: var(--radius-sm);
    border: 1px solid rgba(0, 0, 0, 0.04);
    margin: 0;
}

.coti-badge-auto {
    background: rgba(52, 199, 89, 0.12);
    color: #1b7a34;
    border: 1px solid rgba(52, 199, 89, 0.28);
    padding: 0.9rem 1.1rem;
    border-radius: var(--radius-md);
    font-weight: 600;
    font-size: 0.92rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(8px);
}

.coti-badge-escalate {
    background: rgba(255, 149, 0, 0.12);
    color: #b45309;
    border: 1px solid rgba(255, 149, 0, 0.28);
    padding: 0.9rem 1.1rem;
    border-radius: var(--radius-md);
    font-weight: 600;
    font-size: 0.92rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(8px);
}

.coti-solutions {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.85rem;
    margin-top: 0.25rem;
}

.coti-solution-card {
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.9);
    padding: 1rem 1.05rem;
    border-radius: var(--radius-md);
    box-shadow: 0 4px 16px rgba(15, 35, 65, 0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.coti-solution-card:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(15, 35, 65, 0.08);
}

.coti-solution-card h4 {
    color: var(--accent);
    font-size: 0.86rem;
    margin: 0 0 0.4rem 0;
    font-weight: 700;
    letter-spacing: -0.01em;
}

.coti-solution-card p {
    color: var(--text-muted);
    font-size: 0.82rem;
    margin: 0;
    line-height: 1.45;
}

.coti-empty {
    text-align: center;
    padding: 2.5rem 1.5rem;
    background: rgba(255, 255, 255, 0.45);
    border-radius: var(--radius-md);
    border: 1px dashed rgba(0, 113, 227, 0.25);
    color: var(--text-muted);
    font-size: 0.92rem;
}

.coti-empty strong {
    color: var(--navy);
    display: block;
    margin-bottom: 0.35rem;
    font-size: 1rem;
}

/* Streamlit widgets — glass polish */
.stButton > button[kind="primary"] {
    background: linear-gradient(180deg, #0077ed 0%, #0066cc 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.35) !important;
    font-weight: 600 !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: 0 4px 14px rgba(0, 102, 204, 0.28) !important;
    padding: 0.55rem 1.25rem !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(180deg, #0084ff 0%, #0071e3 100%) !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(0, 102, 204, 0.35) !important;
}

div[data-baseweb="select"] > div {
    background: rgba(255, 255, 255, 0.85) !important;
    border-radius: var(--radius-sm) !important;
    border-color: rgba(0, 0, 0, 0.08) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: rgba(255, 255, 255, 0.4);
    border-radius: var(--radius-sm);
    padding: 0.25rem;
    border-bottom: none;
    gap: 0.25rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.84rem;
}

.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    background: rgba(255, 255, 255, 0.85) !important;
}

.stExpander {
    background: rgba(255, 255, 255, 0.55) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    border-radius: var(--radius-sm) !important;
    backdrop-filter: blur(8px);
}

[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.65);
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-radius: var(--radius-sm);
    padding: 0.75rem 1rem;
    backdrop-filter: blur(8px);
}

.stAlert {
    border-radius: var(--radius-md) !important;
    backdrop-filter: blur(8px);
}

@media (max-width: 900px) {
    .coti-solutions { grid-template-columns: 1fr; }
    section[data-testid="stSidebar"] {
        min-width: 280px !important;
        width: 280px !important;
    }
    section.main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
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
    return '<span style="font-size:1.35rem;font-weight:700;color:#0071e3;letter-spacing:-0.02em;">cotiviti</span>'


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
            <span><a href="https://www.cotiviti.com/solutions/payment-accuracy" target="_blank">Solutions ↗</a></span>
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
                {_logo_html(30)}
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


def render_empty_state(title, subtitle):
    import streamlit as st
    st.markdown(
        f'<div class="coti-empty"><strong>{title}</strong>{subtitle}</div>',
        unsafe_allow_html=True,
    )
