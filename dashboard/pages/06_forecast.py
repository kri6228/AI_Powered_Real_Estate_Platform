# dashboard/pages/06_forecast.py

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engines.forecaster import get_forecast, CITY_CAGR, DEFAULT_CAGR

st.title("🔮 Future Price Forecast")
st.markdown("---")

# ── Two modes ──────────────────────────────────────────────
mode = st.radio("Input Mode",
                ["Use predicted property (from Price Prediction page)",
                 "Enter manually"],
                horizontal=True)

st.markdown("---")

if mode == "Use predicted property (from Price Prediction page)":
    if 'predicted_price' not in st.session_state:
        st.warning("⚠️ Please go to **Price Prediction** page first.")
        st.stop()

    predicted_price = st.session_state['predicted_price']
    inputs = st.session_state['property_inputs']
    city = inputs['city']
    availability = inputs['availability']

    st.info(f"Forecasting for: **{inputs['bhk']}BHK** in **{city}** — ₹{predicted_price}L")

else:
    st.markdown("### Enter Property Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        predicted_price = st.number_input("Current Property Price (Lakhs ₹)",
                                           min_value=10.0,
                                           max_value=500.0,
                                           value=250.0, step=1.0)
    with col2:
        city = st.selectbox("City", sorted(CITY_CAGR.keys()))
    with col3:
        availability = st.selectbox("Availability Status",
                                    ['Ready_to_Move', 'Under_Construction'])

# ── Forecast ───────────────────────────────────────────────
if st.button("🔮 Generate Forecast", use_container_width=True, type='primary'):

    result = get_forecast(predicted_price, city, availability)

    st.markdown("---")
    st.markdown("### 📈 Forecast Results")

    # ── KPI Metrics ────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Price", f"₹{result['current']}L")
    col2.metric("1 Year",
                f"₹{result['forecast_1yr']}L",
                f"+{result['appreciation_1yr']}%")
    col3.metric("3 Years",
                f"₹{result['forecast_3yr']}L",
                f"+{result['appreciation_3yr']}%")
    col4.metric("5 Years",
                f"₹{result['forecast_5yr']}L",
                f"+{result['appreciation_5yr']}%")

    st.markdown("---")

    # ── Line Chart ─────────────────────────────────────────
    st.markdown("### 📊 Price Growth Trajectory")

    years = [0, 1, 3, 5]
    prices = [
        result['current'],
        result['forecast_1yr'],
        result['forecast_3yr'],
        result['forecast_5yr']
    ]
    labels = ['Now', '1 Year', '3 Years', '5 Years']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=prices,
        mode='lines+markers+text',
        text=[f"₹{p}L" for p in prices],
        textposition='top center',
        line=dict(color='#636EFA', width=3),
        marker=dict(size=10, color='#636EFA'),
        fill='tozeroy',
        fillcolor='rgba(99,110,250,0.1)',
        name='Forecasted Price'
    ))
    fig.update_layout(
        title=f'Price Forecast for {city} Property',
        xaxis_title='Time Period',
        yaxis_title='Price (Lakhs ₹)',
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Appreciation Table ─────────────────────────────────
    st.markdown("### 📋 Forecast Summary Table")
    import pandas as pd
    forecast_df = pd.DataFrame({
        'Time Period': ['Current', '1 Year', '3 Years', '5 Years'],
        'Price (Lakhs ₹)': [
            result['current'],
            result['forecast_1yr'],
            result['forecast_3yr'],
            result['forecast_5yr']
        ],
        'Appreciation (%)': [
            '—',
            f"+{result['appreciation_1yr']}%",
            f"+{result['appreciation_3yr']}%",
            f"+{result['appreciation_5yr']}%"
        ],
        'Gain (Lakhs ₹)': [
            '—',
            f"+{round(result['forecast_1yr'] - result['current'], 2)}",
            f"+{round(result['forecast_3yr'] - result['current'], 2)}",
            f"+{round(result['forecast_5yr'] - result['current'], 2)}"
        ]
    })
    st.dataframe(forecast_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── CAGR Info ──────────────────────────────────────────
    st.markdown("### ℹ️ Methodology")
    st.info(f"""
    **Formula:** Future Price = Current Price × (1 + CAGR)ⁿ  
    **City CAGR for {city}:** {result['cagr_percent']}% per year  
    **Source:** Historical Indian real estate appreciation rates by city tier  
    **Adjustment:** Under-construction properties get +1% CAGR on completion premium  
    """)

    # ── City CAGR Comparison ───────────────────────────────
    st.markdown("### 🌆 CAGR by City")
    cagr_df = pd.DataFrame({
        'City': list(CITY_CAGR.keys()),
        'CAGR (%)': [round(v * 100, 1) for v in CITY_CAGR.values()]
    }).sort_values('CAGR (%)', ascending=False)

    fig = px.bar(cagr_df, x='City', y='CAGR (%)',
                 title='Annual Appreciation Rate by City',
                 color='CAGR (%)',
                 color_continuous_scale='Greens')
    fig.update_layout(xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig, use_container_width=True)