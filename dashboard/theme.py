# dashboard/theme.py
# Shared visual theme — import and call inject_css() at top of every page

import streamlit as st

def inject_css():
    st.markdown("""
    <style>
    /* ── Google Font ─────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

    /* ── Global Reset ────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── App Background ──────────────────────────────────── */
    .stApp {
        background-color: #0F1117;
    }

    /* ── Sidebar ─────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: #1A1D27;
        border-right: 1px solid #2D3147;
    }
    [data-testid="stSidebar"] * {
        color: #C8CAD4 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        padding: 8px 12px;
        border-radius: 8px;
        transition: background 0.2s;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: #2D3147;
    }

    /* ── Page Title ──────────────────────────────────────── */
    h1 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.5px;
    }
    h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        color: #E2E4F0 !important;
    }

    /* ── Metric Cards ────────────────────────────────────── */
    [data-testid="metric-container"] {
        background: #1A1D27;
        border: 1px solid #2D3147;
        border-radius: 12px;
        padding: 16px 20px !important;
        transition: border-color 0.2s;
    }
    [data-testid="metric-container"]:hover {
        border-color: #4B6EF5;
    }
    [data-testid="stMetricLabel"] {
        color: #8B8FA8 !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 12px !important;
    }

    /* ── Buttons ─────────────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, #4B6EF5, #6B4BF5) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 12px 24px !important;
        letter-spacing: 0.3px;
        transition: opacity 0.2s, transform 0.1s !important;
    }
    .stButton > button:hover {
        opacity: 0.9 !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* ── Selectbox / Dropdowns ───────────────────────────── */
    .stSelectbox > div > div {
        background-color: #1A1D27 !important;
        border: 1px solid #2D3147 !important;
        border-radius: 10px !important;
        color: #E2E4F0 !important;
    }

    /* ── Sliders ─────────────────────────────────────────── */
    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #4B6EF5, #6B4BF5) !important;
    }

    /* ── Number Input ────────────────────────────────────── */
    .stNumberInput > div > div > input {
        background-color: #1A1D27 !important;
        border: 1px solid #2D3147 !important;
        border-radius: 10px !important;
        color: #E2E4F0 !important;
    }

    /* ── Text Input ──────────────────────────────────────── */
    .stTextInput > div > div > input {
        background-color: #1A1D27 !important;
        border: 1px solid #2D3147 !important;
        border-radius: 10px !important;
        color: #E2E4F0 !important;
    }

    /* ── Dataframe ───────────────────────────────────────── */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden;
        border: 1px solid #2D3147 !important;
    }

    /* ── Divider ─────────────────────────────────────────── */
    hr {
        border-color: #2D3147 !important;
        margin: 1.5rem 0 !important;
    }

    /* ── Alert / Info / Success / Warning / Error ────────── */
    .stAlert {
        border-radius: 10px !important;
        border-left-width: 4px !important;
    }

    /* ── Plotly charts background ────────────────────────── */
    .js-plotly-plot .plotly .bg {
        fill: #1A1D27 !important;
    }

    /* ── Radio ───────────────────────────────────────────── */
    .stRadio > div {
        gap: 8px;
    }

    /* ── Custom Card Component ───────────────────────────── */
    .re-card {
        background: #1A1D27;
        border: 1px solid #2D3147;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 16px;
        transition: border-color 0.2s;
    }
    .re-card:hover {
        border-color: #4B6EF5;
    }
    .re-card-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 13px;
        font-weight: 600;
        color: #8B8FA8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }
    .re-card-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 26px;
        font-weight: 700;
        color: #FFFFFF;
    }
    .re-card-sub {
        font-size: 12px;
        color: #6B6F87;
        margin-top: 4px;
    }

    /* ── Tag / Badge ─────────────────────────────────────── */
    .re-tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .re-tag-green  { background: #0D2B1F; color: #34D399; border: 1px solid #1A4535; }
    .re-tag-yellow { background: #2B2205; color: #FBBF24; border: 1px solid #4A3A0A; }
    .re-tag-red    { background: #2B0D0D; color: #F87171; border: 1px solid #4A1A1A; }
    .re-tag-blue   { background: #0D1A3A; color: #60A5FA; border: 1px solid #1A2F5A; }

    /* ── Section Header ──────────────────────────────────── */
    .re-section {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 11px;
        font-weight: 700;
        color: #4B6EF5;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 12px;
        margin-top: 8px;
    }

    /* ── Recommendation Result Box ───────────────────────── */
    .re-result-buy  { background:#0D2B1F; border:2px solid #34D399; border-radius:16px; padding:24px; text-align:center; }
    .re-result-hold { background:#2B2205; border:2px solid #FBBF24; border-radius:16px; padding:24px; text-align:center; }
    .re-result-sell { background:#2B0D0D; border:2px solid #F87171; border-radius:16px; padding:24px; text-align:center; }
    .re-result-label { font-family:'Space Grotesk',sans-serif; font-size:48px; font-weight:700; letter-spacing:2px; }
    .re-result-sub   { font-size:14px; color:#8B8FA8; margin-top:8px; }

    /* ── Page subtitle ───────────────────────────────────── */
    .re-subtitle {
        font-size: 15px;
        color: #6B6F87;
        margin-top: -8px;
        margin-bottom: 24px;
    }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    """Render a consistent page title + subtitle."""
    st.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p class='re-subtitle'>{subtitle}</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)


def section(label: str):
    """Render a section eyebrow label."""
    st.markdown(f"<p class='re-section'>{label}</p>", unsafe_allow_html=True)


def stat_card(title: str, value: str, sub: str = ""):
    """Render a custom stat card via HTML."""
    sub_html = f"<div class='re-card-sub'>{sub}</div>" if sub else ""
    st.markdown(f"""
    <div class='re-card'>
        <div class='re-card-title'>{title}</div>
        <div class='re-card-value'>{value}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def tag(label: str, color: str = "blue"):
    """Render an inline tag/badge. color: green | yellow | red | blue"""
    st.markdown(f"<span class='re-tag re-tag-{color}'>{label}</span>",
                unsafe_allow_html=True)


def recommendation_box(rec: str, subtitle: str = ""):
    """Render the big BUY/HOLD/SELL result box."""
    css_class = {
        "BUY":  "re-result-buy",
        "HOLD": "re-result-hold",
        "SELL": "re-result-sell",
    }.get(rec.upper(), "re-result-hold")

    color = {
        "BUY":  "#34D399",
        "HOLD": "#FBBF24",
        "SELL": "#F87171",
    }.get(rec.upper(), "#FBBF24")

    emoji = {"BUY": "↑", "HOLD": "→", "SELL": "↓"}.get(rec.upper(), "→")

    st.markdown(f"""
    <div class='{css_class}'>
        <div class='re-result-label' style='color:{color}'>{emoji} {rec.upper()}</div>
        <div class='re-result-sub'>{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)
