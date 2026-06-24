# dashboard/app.py

import streamlit as st

st.set_page_config(
    page_title="PropIQ — Real Estate Intelligence",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0F1117; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #13151F 0%, #1A1D27 100%);
    border-right: 1px solid #2D3147;
}
[data-testid="stSidebar"] * { color: #C8CAD4 !important; }
[data-testid="stSidebar"] .stRadio label {
    padding: 8px 12px; border-radius: 8px; transition: background 0.2s;
}
[data-testid="stSidebar"] .stRadio label:hover { background: #2D3147; }
h1 { font-family:'Space Grotesk',sans-serif !important; font-weight:700 !important; color:#FFFFFF !important; }
h2,h3 { font-family:'Space Grotesk',sans-serif !important; font-weight:600 !important; color:#E2E4F0 !important; }
[data-testid="metric-container"] {
    background:#1A1D27; border:1px solid #2D3147; border-radius:12px;
    padding:16px 20px !important; transition:border-color 0.2s;
}
[data-testid="metric-container"]:hover { border-color:#4B6EF5; }
[data-testid="stMetricLabel"] { color:#8B8FA8 !important; font-size:12px !important; font-weight:500 !important; text-transform:uppercase; letter-spacing:0.5px; }
[data-testid="stMetricValue"] { color:#FFFFFF !important; font-size:28px !important; font-weight:700 !important; font-family:'Space Grotesk',sans-serif !important; }
.stButton > button {
    background:linear-gradient(135deg,#4B6EF5,#6B4BF5) !important; color:white !important;
    border:none !important; border-radius:10px !important; font-weight:600 !important;
    font-size:14px !important; padding:12px 24px !important; transition:opacity 0.2s,transform 0.1s !important;
}
.stButton > button:hover { opacity:0.9 !important; transform:translateY(-1px) !important; }
.stSelectbox > div > div { background-color:#1A1D27 !important; border:1px solid #2D3147 !important; border-radius:10px !important; color:#E2E4F0 !important; }
.stSlider > div > div > div > div { background:linear-gradient(135deg,#4B6EF5,#6B4BF5) !important; }
.stNumberInput > div > div > input { background-color:#1A1D27 !important; border:1px solid #2D3147 !important; border-radius:10px !important; color:#E2E4F0 !important; }
.stTextInput > div > div > input { background-color:#1A1D27 !important; border:1px solid #2D3147 !important; border-radius:10px !important; color:#E2E4F0 !important; }
hr { border-color:#2D3147 !important; margin:1.5rem 0 !important; }
.stAlert { border-radius:10px !important; }
.re-card { background:#1A1D27; border:1px solid #2D3147; border-radius:14px; padding:20px 24px; margin-bottom:16px; }
.re-card:hover { border-color:#4B6EF5; }
.re-card-title { font-family:'Space Grotesk',sans-serif; font-size:11px; font-weight:700; color:#4B6EF5; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; }
.re-card-value { font-family:'Space Grotesk',sans-serif; font-size:26px; font-weight:700; color:#FFFFFF; }
.re-card-sub { font-size:12px; color:#6B6F87; margin-top:4px; }
.re-tag { display:inline-block; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; letter-spacing:0.5px; }
.re-tag-green  { background:#0D2B1F; color:#34D399; border:1px solid #1A4535; }
.re-tag-yellow { background:#2B2205; color:#FBBF24; border:1px solid #4A3A0A; }
.re-tag-red    { background:#2B0D0D; color:#F87171; border:1px solid #4A1A1A; }
.re-tag-blue   { background:#0D1A3A; color:#60A5FA; border:1px solid #1A2F5A; }
.re-section { font-family:'Space Grotesk',sans-serif; font-size:11px; font-weight:700; color:#4B6EF5; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:12px; }
.re-subtitle { font-size:15px; color:#6B6F87; margin-top:-8px; margin-bottom:24px; }
.re-result-buy  { background:#0D2B1F; border:2px solid #34D399; border-radius:16px; padding:28px; text-align:center; }
.re-result-hold { background:#2B2205; border:2px solid #FBBF24; border-radius:16px; padding:28px; text-align:center; }
.re-result-sell { background:#2B0D0D; border:2px solid #F87171; border-radius:16px; padding:28px; text-align:center; }
.re-result-label { font-family:'Space Grotesk',sans-serif; font-size:52px; font-weight:700; letter-spacing:3px; }
.re-result-sub   { font-size:14px; color:#8B8FA8; margin-top:8px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 8px 0'>
        <div style='font-family:Space Grotesk,sans-serif;font-size:20px;font-weight:700;color:#fff'>
            🏙️ PropIQ
        </div>
        <div style='font-size:11px;color:#6B6F87;margin-top:2px'>Real Estate Intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    PAGES = {
        "🏠  Overview":               "pages/01_overview.py",
        "📊  EDA Dashboard":          "pages/02_eda.py",
        "💰  Price Prediction":       "pages/03_prediction.py",
        "📈  Recommendation":         "pages/04_recommendation.py",
        "⚠️  Risk Analysis":          "pages/05_risk.py",
        "🔮  Price Forecast":         "pages/06_forecast.py",
        "🧠  Explainable AI":         "pages/07_explainability.py",
        "🔍  Property Comparison":    "pages/08_comparison.py",
        "🌆  Market Insights":        "pages/09_market_insights.py",
        "🏆  Property Ranking":       "pages/10_ranking.py",
        "⚡  Real-Time Analyzer":     "pages/11_analyzer.py",
        "🤖  AI Chat Assistant":      "pages/12_chatbot.py",
    }

    selection = st.radio("Navigation", list(PAGES.keys()), label_visibility="collapsed")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:11px;color:#6B6F87;line-height:1.8'>
        <div style='color:#4B6EF5;font-weight:600;margin-bottom:4px'>MODEL</div>
        XGBoost · R² 0.9769
        <div style='color:#4B6EF5;font-weight:600;margin:8px 0 4px'>DATASET</div>
        2,50,000 records<br>42 cities · 20 states
    </div>
    """, unsafe_allow_html=True)

# ── Load Page ──────────────────────────────────────────────
with open(PAGES[selection], encoding='utf-8') as f:
    exec(f.read(), {"__file__": PAGES[selection]})
