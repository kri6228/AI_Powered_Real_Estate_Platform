# dashboard/pages/05_risk.py

import streamlit as st
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engines.risk_engine import calculate_risk_score

st.markdown("<h1>⚠️ Risk Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p class='re-subtitle'>Multi-factor property risk scoring — Low, Medium, or High</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

mode = st.radio(
    "Input source",
    ["Use predicted property", "Enter manually"],
    horizontal=True,
    label_visibility="collapsed"
)
st.caption("Use predicted property — carries over from Price Prediction page · Enter manually — independent analysis")
st.markdown("<hr>", unsafe_allow_html=True)

if mode == "Use predicted property":
    if 'property_inputs' not in st.session_state:
        st.markdown("""
        <div class='re-card' style='border-color:#4A3A0A;text-align:center;padding:32px'>
            <div style='font-size:32px;margin-bottom:8px'>⚠️</div>
            <div style='font-family:Space Grotesk,sans-serif;font-size:16px;
                        font-weight:600;color:#FBBF24'>No Property in Session</div>
            <div style='font-size:13px;color:#6B6F87;margin-top:8px'>
                Go to <strong style='color:#C8CAD4'>Price Prediction</strong> first.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    inputs             = st.session_state['property_inputs']
    age                = inputs['age']
    crime_index        = inputs.get('crime_index', 5.0)
    availability       = inputs['availability']
    floor_ratio        = inputs['floor_ratio']
    infra_growth_score = inputs['infra_growth_score']
    population_density = inputs['population_density']

    pred = st.session_state.get('predicted_price', 'N/A')
    st.markdown(f"""
    <div class='re-card' style='border-color:#1A2F5A'>
        <div style='font-size:13px;color:#60A5FA'>
            Analyzing: <strong style='color:#fff'>{inputs['bhk']}BHK</strong> in 
            <strong style='color:#fff'>{inputs['city']}</strong> — 
            ₹{pred}L
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("<p class='re-section'>Property Details</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        age          = st.slider("Age of Property (years)", 0, 35, 10)
        crime_index  = st.slider("Crime Index (1=safe, 10=high crime)", 1.0, 10.0, 5.0)
        availability = st.selectbox("Availability", ['Ready_to_Move', 'Under_Construction'])
    with col2:
        floor_no           = st.slider("Floor Number", 0, 30, 5)
        total_floors       = st.slider("Total Floors", 1, 30, 10)
        floor_ratio        = round(floor_no / max(total_floors, 1), 2)
        infra_growth_score = st.slider("Infra Growth Score (0-10)", 0.0, 10.0, 5.0)
        population_density = st.number_input("Population Density (persons/km²)",
                                              min_value=100, max_value=30000, value=5000)

st.markdown("<hr>", unsafe_allow_html=True)

if st.button("⚠️ Calculate Risk Score", use_container_width=True, type='primary'):
    result = calculate_risk_score(
        age_of_property    = age,
        crime_index        = crime_index,
        availability_status = availability,
        floor_ratio        = floor_ratio,
        infra_growth_score = infra_growth_score,
        population_density = population_density
    )

    score    = result['risk_score']
    category = result['risk_category']

    risk_color = {"Low": "#34D399", "Medium": "#FBBF24", "High": "#F87171"}.get(category, "#FBBF24")
    risk_bg    = {"Low": "#0D2B1F", "Medium": "#2B2205", "High": "#2B0D0D"}.get(category, "#2B2205")
    risk_border= {"Low": "#1A4535", "Medium": "#4A3A0A", "High": "#4A1A1A"}.get(category, "#4A3A0A")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p class='re-section'>Risk Assessment Result</p>", unsafe_allow_html=True)

    # ── Big score display ──────────────────────────────────
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
        <div style='background:{risk_bg};border:2px solid {risk_border};
                    border-radius:16px;padding:32px;text-align:center'>
            <div style='font-size:11px;font-weight:700;color:{risk_color};
                        text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>
                Risk Score
            </div>
            <div style='font-family:Space Grotesk,sans-serif;font-size:56px;
                        font-weight:700;color:{risk_color}'>
                {score}
            </div>
            <div style='font-size:13px;color:#8B8FA8'>out of 10</div>
            <div style='font-family:Space Grotesk,sans-serif;font-size:20px;
                        font-weight:700;color:{risk_color};margin-top:12px'>
                {category.upper()} RISK
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 10], 'tickcolor': '#8B8FA8',
                         'tickfont': {'color': '#8B8FA8'}},
                'bar':  {'color': risk_color},
                'bgcolor': '#1A1D27',
                'bordercolor': '#2D3147',
                'steps': [
                    {'range': [0, 3.3], 'color': '#0D2B1F'},
                    {'range': [3.3, 6.6], 'color': '#2B2205'},
                    {'range': [6.6, 10], 'color': '#2B0D0D'},
                ],
                'threshold': {
                    'line': {'color': '#FFFFFF', 'width': 3},
                    'thickness': 0.8,
                    'value': score
                }
            },
            number={'font': {'color': '#FFFFFF', 'size': 36,
                             'family': 'Space Grotesk'}}
        ))
        fig.update_layout(
            paper_bgcolor='#1A1D27', font=dict(color='#8B8FA8'),
            height=260, margin=dict(l=16, r=16, t=16, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Factor breakdown ───────────────────────────────────
    st.markdown("<p class='re-section'>Factor Breakdown</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        for factor, val in result['breakdown'].items():
            if val > 6.6:
                fc, fb, fl = "#F87171", "#2B0D0D", "High"
            elif val > 3.3:
                fc, fb, fl = "#FBBF24", "#2B2205", "Med"
            else:
                fc, fb, fl = "#34D399", "#0D2B1F", "Low"

            pct = int((val / 10) * 100)
            st.markdown(f"""
            <div style='margin-bottom:12px'>
                <div style='display:flex;justify-content:space-between;margin-bottom:4px'>
                    <span style='font-size:12px;color:#8B8FA8'>{factor}</span>
                    <span style='font-size:12px;font-weight:600;color:{fc}'>{val}/10 · {fl}</span>
                </div>
                <div style='background:#2D3147;border-radius:4px;height:6px'>
                    <div style='background:{fc};width:{pct}%;height:6px;border-radius:4px'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        fig = go.Figure(go.Bar(
            x=list(result['breakdown'].values()),
            y=list(result['breakdown'].keys()),
            orientation='h',
            marker_color=[
                '#F87171' if v > 6.6 else '#FBBF24' if v > 3.3 else '#34D399'
                for v in result['breakdown'].values()
            ],
            marker_line_width=0
        ))
        fig.update_layout(
            paper_bgcolor='#1A1D27', plot_bgcolor='#1A1D27',
            font=dict(color='#8B8FA8', size=12),
            xaxis=dict(range=[0, 10], gridcolor='#2D3147', showline=False),
            yaxis=dict(gridcolor='#2D3147', showline=False),
            height=280, margin=dict(l=0, r=0, t=8, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Interpretation ─────────────────────────────────────
    st.markdown("<p class='re-section'>What This Means</p>", unsafe_allow_html=True)

    interpretations = {
        "Low": [
            "Property is in a safe area with low crime index",
            "Good infrastructure and high market demand",
            "Suitable for conservative investors",
            "Recommended for long-term buy-and-hold strategy",
        ],
        "Medium": [
            "Moderate risk factors are present",
            "Monitor local market trends before committing",
            "Suitable for investors with moderate risk appetite",
            "Consider reassessing in 6–12 months",
        ],
        "High": [
            "Multiple high risk factors detected",
            "High crime index or low infrastructure growth",
            "Not recommended for conservative investors",
            "Evaluate alternative properties before proceeding",
        ],
    }

    for point in interpretations.get(category, []):
        st.markdown(f"""
        <div style='display:flex;gap:10px;padding:8px 0;border-bottom:1px solid #2D3147'>
            <span style='color:{risk_color};font-size:14px'>›</span>
            <span style='font-size:13px;color:#C8CAD4'>{point}</span>
        </div>
        """, unsafe_allow_html=True)

    st.session_state['risk_result'] = result
