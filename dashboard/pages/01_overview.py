# dashboard/pages/01_overview.py

import streamlit as st

st.markdown("<h1>🏙️ PropIQ — Real Estate Intelligence</h1>", unsafe_allow_html=True)
st.markdown("<p class='re-subtitle'>End-to-end AI platform for Indian property investment decisions</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ── Key Metrics ────────────────────────────────────────────
st.markdown("<p class='re-section'>Platform Stats</p>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Dataset Size",   "2,50,000",  "properties")
col2.metric("Best Model R²",  "0.9769",    "XGBoost")
col3.metric("Cities Covered", "42",        "across India")
col4.metric("States Covered", "20",        "states")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Capability Cards ───────────────────────────────────────
st.markdown("<p class='re-section'>What This Platform Does</p>", unsafe_allow_html=True)

capabilities = [
    ("💰", "Price Prediction",       "Predict property value using 34 engineered features powered by XGBoost (R²=0.9769)"),
    ("📈", "Investment ROI",         "Estimate return on investment and identify undervalued vs overvalued properties"),
    ("🧠", "Explainable AI",         "Understand WHY a property is priced using SHAP global and local feature explanations"),
    ("⚠️", "Risk Scoring",           "Calculate Low / Medium / High risk based on crime index, age, floor ratio, and demand"),
    ("✅", "Buy / Hold / Sell",      "Get intelligent investment recommendations based on ROI, risk, and market valuation"),
    ("🔍", "Property Comparison",    "Compare two properties side-by-side across price, risk, ROI, and forecast metrics"),
    ("🔮", "Price Forecasting",      "Project property value at 1, 3, and 5 years using city-tier CAGR growth models"),
    ("🌆", "Market Insights",        "Discover top investment areas, high-growth cities, and low-risk zones across India"),
    ("🤖", "AI Chat Assistant",      "Ask PropBot anything — powered by Groq, Gemini, OpenAI, Mistral, Cohere, or Claude"),
]

cols = st.columns(3)
for i, (icon, title, desc) in enumerate(capabilities):
    with cols[i % 3]:
        st.markdown(f"""
        <div class='re-card'>
            <div style='font-size:24px;margin-bottom:8px'>{icon}</div>
            <div class='re-card-title'>{title}</div>
            <div style='font-size:13px;color:#8B8FA8;line-height:1.5'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Project Phases ─────────────────────────────────────────
st.markdown("<p class='re-section'>Project Phases</p>", unsafe_allow_html=True)

phases = [
    ("01", "Requirement Analysis"),
    ("02", "Data Collection & Validation"),
    ("03", "Data Cleaning"),
    ("04", "Exploratory Data Analysis"),
    ("05", "Feature Engineering"),
    ("06", "ML Model Development"),
    ("07", "Explainable AI — SHAP"),
    ("08", "Investment Recommendation Engine"),
    ("09", "Risk Score Engine"),
    ("10", "Future Price Forecasting"),
    ("11", "Streamlit Dashboard"),
]

col1, col2 = st.columns(2)
for i, (num, name) in enumerate(phases):
    target = col1 if i < 6 else col2
    with target:
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #2D3147'>
            <div style='font-family:Space Grotesk,sans-serif;font-size:11px;font-weight:700;
                        color:#4B6EF5;background:#0D1A3A;border-radius:6px;
                        padding:3px 8px;min-width:30px;text-align:center'>
                {num}
            </div>
            <div style='font-size:13px;color:#C8CAD4;flex:1'>{name}</div>
            <span class='re-tag re-tag-green'>✓ Done</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Tech Stack ─────────────────────────────────────────────
st.markdown("<p class='re-section'>Technology Stack</p>", unsafe_allow_html=True)

stack = {
    "Data":          ["Python", "Pandas", "NumPy"],
    "ML Models":     ["XGBoost", "CatBoost", "LightGBM", "Scikit-Learn"],
    "Explainability":["SHAP"],
    "Visualization": ["Plotly", "Matplotlib", "Seaborn"],
    "Deployment":    ["Streamlit"],
    "AI Chatbot":    ["Groq", "Gemini", "OpenAI", "Mistral"],
}

cols = st.columns(len(stack))
for col, (category, items) in zip(cols, stack.items()):
    with col:
        st.markdown(f"<div class='re-card-title' style='margin-bottom:8px'>{category}</div>", unsafe_allow_html=True)
        for item in items:
            st.markdown(f"<div style='font-size:13px;color:#C8CAD4;padding:3px 0'>· {item}</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Dataset Info ───────────────────────────────────────────
st.markdown("<p class='re-section'>Dataset</p>", unsafe_allow_html=True)
st.markdown("""
<div class='re-card'>
    <div style='display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:16px'>
        <div>
            <div class='re-card-title'>Primary Source</div>
            <div style='font-size:13px;color:#C8CAD4'>Kaggle — ankushpanday1/<br>india-house-price-prediction</div>
        </div>
        <div>
            <div class='re-card-title'>Secondary Source</div>
            <div style='font-size:13px;color:#C8CAD4'>Census 2011 — Population<br>density by city/state</div>
        </div>
        <div>
            <div class='re-card-title'>Records & Features</div>
            <div style='font-size:13px;color:#C8CAD4'>2,50,000 records<br>23 original → 34 engineered</div>
        </div>
        <div>
            <div class='re-card-title'>Target Variable</div>
            <div style='font-size:13px;color:#C8CAD4'>Estimated_Price<br>(domain-weighted)</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
