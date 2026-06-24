# dashboard/pages/04_recommendation.py

import streamlit as st
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engines.recommendation import get_recommendation, calculate_roi
from engines.risk_engine     import calculate_risk_score

st.markdown("<h1>📈 Investment Recommendation</h1>", unsafe_allow_html=True)
st.markdown("<p class='re-subtitle'>AI-powered BUY / HOLD / SELL decision based on ROI and risk analysis</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

if 'predicted_price' not in st.session_state:
    st.markdown("""
    <div class='re-card' style='border-color:#4A3A0A;text-align:center;padding:32px'>
        <div style='font-size:32px;margin-bottom:8px'>⚠️</div>
        <div style='font-family:Space Grotesk,sans-serif;font-size:16px;
                    font-weight:600;color:#FBBF24'>No Property Predicted Yet</div>
        <div style='font-size:13px;color:#6B6F87;margin-top:8px'>
            Go to <strong style='color:#C8CAD4'>Price Prediction</strong> first, 
            then return here for your recommendation.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

predicted_price = st.session_state['predicted_price']
inputs          = st.session_state['property_inputs']

# ── Property being analyzed ────────────────────────────────
st.markdown("<p class='re-section'>Property Being Analyzed</p>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("City",            inputs['city'])
col2.metric("BHK",             inputs['bhk'])
col3.metric("Predicted Price", f"₹{predicted_price:.2f}L")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Actual price input ─────────────────────────────────────
st.markdown("<p class='re-section'>Market Listed Price</p>", unsafe_allow_html=True)
st.markdown("<div style='font-size:13px;color:#6B6F87;margin-bottom:12px'>Enter the price at which this property is currently listed in the market</div>", unsafe_allow_html=True)

actual_price = st.number_input(
    "Actual Market Price (Lakhs ₹)",
    min_value=10.0, max_value=500.0,
    value=float(round(predicted_price * 0.90, 2)),
    step=1.0
)

st.markdown("<hr>", unsafe_allow_html=True)

if st.button("📊 Get Recommendation", use_container_width=True, type='primary'):

    roi         = calculate_roi(actual_price, predicted_price)
    risk_result = calculate_risk_score(
        age_of_property   = inputs['age'],
        crime_index       = inputs.get('crime_index', 5.0),
        availability_status = inputs['availability'],
        floor_ratio       = inputs['floor_ratio'],
        infra_growth_score = inputs['infra_growth_score'],
        population_density = inputs['population_density']
    )
    rec_result = get_recommendation(
        roi               = roi,
        risk_score        = risk_result['risk_score'],
        availability_status = inputs['availability']
    )

    rec = rec_result['recommendation'].upper()

    # ── Big result box ─────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p class='re-section'>Recommendation</p>", unsafe_allow_html=True)

    colors  = {"BUY": "#34D399", "HOLD": "#FBBF24", "SELL": "#F87171"}
    bgs     = {"BUY": "#0D2B1F", "HOLD": "#2B2205",  "SELL": "#2B0D0D"}
    borders = {"BUY": "#1A4535", "HOLD": "#4A3A0A",  "SELL": "#4A1A1A"}
    arrows  = {"BUY": "↑",       "HOLD": "→",         "SELL": "↓"}

    color  = colors.get(rec,  "#FBBF24")
    bg     = bgs.get(rec,    "#2B2205")
    border = borders.get(rec, "#4A3A0A")
    arrow  = arrows.get(rec,  "→")
    subtitle = rec_result['reasons'][0]
    st.markdown(f"""
    <div style='background:{bg};border:2px solid {border};
                border-radius:16px;padding:36px;text-align:center;margin-bottom:24px'>
        <div style='font-family:Space Grotesk,sans-serif;font-size:56px;
                    font-weight:700;color:{color};letter-spacing:3px'>
            {arrow} {rec}
        </div>
        <div style='font-size:14px;color:#8B8FA8;margin-top:8px'>
            {subtitle}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Key metrics ────────────────────────────────────────
    st.markdown("<p class='re-section'>Analysis Breakdown</p>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Actual Price",    f"₹{actual_price:.2f}L")
    col2.metric("Predicted Price", f"₹{predicted_price:.2f}L")
    col3.metric("ROI Estimate",    f"{roi:.1f}%",
                delta="Undervalued" if roi > 0 else "Overvalued")
    col4.metric("Risk Score",      f"{risk_result['risk_score']}/10",
                delta=risk_result['risk_category'])

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Valuation status ───────────────────────────────────
    st.markdown("<p class='re-section'>Valuation Status</p>", unsafe_allow_html=True)
    if roi > 10:
        tag_color, tag_text, desc = "#34D399", "UNDERVALUED", f"Market price is {roi:.1f}% below AI estimated fair value — potential upside"
    elif roi < -10:
        tag_color, tag_text, desc = "#F87171", "OVERVALUED",  f"Market price is {abs(roi):.1f}% above AI estimated fair value — caution advised"
    else:
        tag_color, tag_text, desc = "#FBBF24", "FAIRLY VALUED", "Market price is within ±10% of AI estimated fair value"

    st.markdown(f"""
    <div class='re-card' style='display:flex;align-items:center;gap:16px'>
        <div style='font-family:Space Grotesk,sans-serif;font-size:18px;
                    font-weight:700;color:{tag_color};white-space:nowrap'>
            {tag_text}
        </div>
        <div style='font-size:13px;color:#8B8FA8'>{desc}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Reasons ────────────────────────────────────────────
    st.markdown("<p class='re-section'>Why This Recommendation</p>", unsafe_allow_html=True)
    for reason in rec_result['reasons']:
        st.markdown(f"""
        <div style='display:flex;gap:10px;padding:8px 0;border-bottom:1px solid #2D3147'>
            <span style='color:#4B6EF5;font-size:14px'>›</span>
            <span style='font-size:13px;color:#C8CAD4'>{reason}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Risk breakdown ─────────────────────────────────────
    st.markdown("<p class='re-section'>Risk Factor Breakdown</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        for factor, score in risk_result['breakdown'].items():
            if score > 6.6:
                badge_color, badge_bg = "#F87171", "#2B0D0D"
                label = "High"
            elif score > 3.3:
                badge_color, badge_bg = "#FBBF24", "#2B2205"
                label = "Med"
            else:
                badge_color, badge_bg = "#34D399", "#0D2B1F"
                label = "Low"
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;align-items:center;
                        padding:8px 0;border-bottom:1px solid #2D3147'>
                <span style='font-size:12px;color:#8B8FA8'>{factor}</span>
                <div style='display:flex;align-items:center;gap:8px'>
                    <span style='font-size:13px;color:#C8CAD4;font-weight:600'>{score}/10</span>
                    <span style='background:{badge_bg};color:{badge_color};
                                 border-radius:4px;padding:2px 6px;font-size:10px;font-weight:700'>
                        {label}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        fig = go.Figure(go.Bar(
            x=list(risk_result['breakdown'].values()),
            y=list(risk_result['breakdown'].keys()),
            orientation='h',
            marker_color=[
                '#F87171' if v > 6.6 else '#FBBF24' if v > 3.3 else '#34D399'
                for v in risk_result['breakdown'].values()
            ],
            marker_line_width=0
        ))
        fig.update_layout(
            paper_bgcolor='#1A1D27', plot_bgcolor='#1A1D27',
            font=dict(color='#8B8FA8', size=12),
            xaxis=dict(range=[0, 10], gridcolor='#2D3147', showline=False),
            yaxis=dict(gridcolor='#2D3147', showline=False),
            height=260, margin=dict(l=0, r=0, t=8, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    # Save session
    st.session_state['roi']          = roi
    st.session_state['risk_result']  = risk_result
    st.session_state['actual_price'] = actual_price
