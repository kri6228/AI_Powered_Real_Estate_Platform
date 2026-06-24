# dashboard/pages/08_comparison.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engines.predictor import predict_price, build_input, CITY_DENSITY, STATE_DENSITY
from engines.risk_engine import calculate_risk_score
from engines.recommendation import get_recommendation, calculate_roi
from engines.forecaster import get_forecast

st.title("🔍 Property Comparison Dashboard")
st.markdown("---")
st.markdown("Compare two properties side by side across price, risk, ROI and forecast.")

# Filter cities by selected state
state_city_map = {
    'Andhra Pradesh': ['Vijayawada', 'Vishakhapatnam'],
    'Assam': ['Guwahati', 'Silchar'],
    'Bihar': ['Patna', 'Gaya'],
    'Chhattisgarh': ['Raipur', 'Bilaspur'],
    'Delhi': ['New Delhi', 'Dwarka', 'Noida'],
    'Gujarat': ['Ahmedabad', 'Surat'],
    'Haryana': ['Gurgaon', 'Faridabad'],
    'Jharkhand': ['Jamshedpur', 'Ranchi'],
    'Karnataka': ['Bangalore', 'Mysore', 'Mangalore'],
    'Kerala': ['Kochi', 'Trivandrum'],
    'Madhya Pradesh': ['Bhopal', 'Indore'],
    'Maharashtra': ['Mumbai', 'Pune', 'Nagpur'],
    'Odisha': ['Bhubaneswar', 'Cuttack'],
    'Punjab': ['Ludhiana', 'Amritsar'],
    'Rajasthan': ['Jaipur', 'Jodhpur'],
    'Tamil Nadu': ['Chennai', 'Coimbatore'],
    'Telangana': ['Hyderabad', 'Warangal'],
    'Uttar Pradesh': ['Lucknow'],
    'Uttarakhand': ['Dehradun', 'Haridwar'],
    'West Bengal': ['Kolkata', 'Durgapur'],
}
# ── Helper ─────────────────────────────────────────────────
def get_property_inputs(label):
    st.markdown(f"### 🏠 Property {label}")
    col1, col2, col3 = st.columns(3)

    with col1:
        state = st.selectbox(f"State {label}", sorted(STATE_DENSITY.keys()),
                             key=f"state_{label}")
        available_cities = state_city_map.get(state, sorted(CITY_DENSITY.keys()))
        city = st.selectbox(f"City {label}", available_cities,
                            key=f"city_{label}")
        availability = st.selectbox(f"Availability {label}",
                                    ['Ready_to_Move', 'Under_Construction'],
                                    key=f"avail_{label}")
        actual_price = st.number_input(f"Listed Price (Lakhs ₹) {label}",
                                       min_value=10.0, max_value=500.0,
                                       value=200.0, step=1.0,
                                       key=f"actual_{label}")

    with col2:
        property_type = st.selectbox(f"Property Type {label}",
                                     ['Apartment', 'Independent House', 'Villa'],
                                     key=f"ptype_{label}")
        bhk = st.slider(f"BHK {label}", 1, 5, 2, key=f"bhk_{label}")
        size_sqft = st.slider(f"Size SqFt {label}", 500, 5000, 1200,
                              key=f"size_{label}")
        age = st.slider(f"Age (years) {label}", 0, 35, 5, key=f"age_{label}")
        furnished = st.selectbox(f"Furnished {label}",
                                 ['Furnished', 'Semi-furnished', 'Unfurnished'],
                                 key=f"furn_{label}")

    with col3:
        floor_no = st.slider(f"Floor No {label}", 0, 30, 5, key=f"floor_{label}")
        total_floors = st.slider(f"Total Floors {label}", 1, 30, 10,
                                 key=f"tfloor_{label}")
        nearby_schools = st.slider(f"Nearby Schools {label}", 1, 10, 5,
                                   key=f"sch_{label}")
        nearby_hospitals = st.slider(f"Nearby Hospitals {label}", 1, 10, 5,
                                     key=f"hosp_{label}")
        transport = st.selectbox(f"Transport {label}", ['High', 'Medium', 'Low'],
                                 key=f"trans_{label}")
        parking = st.selectbox(f"Parking {label}", ['Yes', 'No'],
                               key=f"park_{label}")
        security = st.selectbox(f"Security {label}", ['Yes', 'No'],
                                key=f"sec_{label}")
        facing = st.selectbox(f"Facing {label}",
                              ['North', 'South', 'East', 'West'],
                              key=f"face_{label}")
        owner_type = st.selectbox(f"Owner Type {label}",
                                  ['Builder', 'Owner', 'Broker'],
                                  key=f"own_{label}")
        balcony = st.slider(f"Balcony {label}", 0, 3, 1, key=f"bal_{label}")
        amenity_count = st.slider(f"Amenities {label}", 1, 5, 3,
                                  key=f"amen_{label}")

    return {
        'city': city, 'state': state,
        'size_sqft': size_sqft, 'bhk': bhk,
        'age': age, 'floor_no': floor_no,
        'total_floors': total_floors,
        'nearby_schools': nearby_schools,
        'nearby_hospitals': nearby_hospitals,
        'transport': transport,
        'parking': parking, 'security': security,
        'availability': availability,
        'furnished': furnished,
        'property_type': property_type,
        'facing': facing, 'owner_type': owner_type,
        'balcony': balcony,
        'amenity_count': amenity_count,
        'actual_price': actual_price,
        'infra_growth_score': round(
            nearby_schools * 0.30 +
            nearby_hospitals * 0.30 +
            {'High': 10, 'Medium': 5, 'Low': 2}.get(transport, 5) * 0.40, 2
        ),
        'population_density': CITY_DENSITY.get(city, 500),
        'floor_ratio': round(floor_no / max(total_floors, 1), 2),
    }

# ── Property Inputs ────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    inputs_a = get_property_inputs("A")
with col2:
    inputs_b = get_property_inputs("B")

st.markdown("---")

# ── Compare Button ─────────────────────────────────────────
if st.button("🔍 Compare Properties", use_container_width=True, type='primary'):

    results = {}
    for label, inputs in [("A", inputs_a), ("B", inputs_b)]:

        # Predict
        input_df = build_input(**{k: v for k, v in inputs.items()
                                  if k not in ['actual_price',
                                               'infra_growth_score',
                                               'population_density',
                                               'floor_ratio']})
        predicted = predict_price(input_df)

        # Risk
        risk = calculate_risk_score(
            age_of_property=inputs['age'],
            crime_index=5.0,
            availability_status=inputs['availability'],
            floor_ratio=inputs['floor_ratio'],
            infra_growth_score=inputs['infra_growth_score'],
            population_density=inputs['population_density']
        )

        # ROI
        roi = calculate_roi(inputs['actual_price'], predicted)

        # Recommendation
        rec = get_recommendation(roi, risk['risk_score'], inputs['availability'])

        # Forecast
        forecast = get_forecast(predicted, inputs['city'], inputs['availability'])

        results[label] = {
            'predicted': predicted,
            'actual': inputs['actual_price'],
            'roi': roi,
            'risk': risk,
            'rec': rec,
            'forecast': forecast,
            'inputs': inputs,
        }

    # ── Results ────────────────────────────────────────────
    st.markdown("## 📊 Comparison Results")

    # ── Key Metrics ────────────────────────────────────────
    st.markdown("### Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [
        ("Listed Price", "actual", "₹", "L"),
        ("Predicted Price", "predicted", "₹", "L"),
        ("ROI", "roi", "", "%"),
        ("Risk Score", None, "", "/10"),
        ("5yr Forecast", None, "₹", "L"),
    ]

    a, b = results['A'], results['B']

    col1.metric("", "Property A")
    col2.metric("Listed Price", f"₹{a['actual']}L",
                f"vs ₹{b['actual']}L")
    col3.metric("Predicted Price", f"₹{a['predicted']}L",
                f"vs ₹{b['predicted']}L")
    col4.metric("ROI", f"{a['roi']}%",
                f"vs {b['roi']}%")
    col5.metric("Risk Score",
                f"{a['risk']['risk_score']}/10",
                f"vs {b['risk']['risk_score']}/10")

    st.markdown("---")

    # ── Recommendation ─────────────────────────────────────
    st.markdown("### 🎯 Recommendation")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Property A**")
        if a['rec']['recommendation'] == 'BUY':
            st.success(f"## {a['rec']['emoji']} {a['rec']['recommendation']}")
        elif a['rec']['recommendation'] == 'SELL':
            st.error(f"## {a['rec']['emoji']} {a['rec']['recommendation']}")
        else:
            st.warning(f"## {a['rec']['emoji']} {a['rec']['recommendation']}")
        for r in a['rec']['reasons']:
            st.markdown(f"- {r}")

    with col2:
        st.markdown("**Property B**")
        if b['rec']['recommendation'] == 'BUY':
            st.success(f"## {b['rec']['emoji']} {b['rec']['recommendation']}")
        elif b['rec']['recommendation'] == 'SELL':
            st.error(f"## {b['rec']['emoji']} {b['rec']['recommendation']}")
        else:
            st.warning(f"## {b['rec']['emoji']} {b['rec']['recommendation']}")
        for r in b['rec']['reasons']:
            st.markdown(f"- {r}")

    st.markdown("---")

    # ── Radar Chart ────────────────────────────────────────
    st.markdown("### 📡 Property Radar Comparison")

    categories = ['Size Score', 'BHK', 'Schools',
                  'Hospitals', 'Infra Score', 'Floor Ratio']

    def normalize(val, min_val, max_val):
        return round((val - min_val) / (max_val - min_val) * 10, 2)

    a_vals = [
        normalize(a['inputs']['size_sqft'], 500, 5000),
        a['inputs']['bhk'] * 2,
        a['inputs']['nearby_schools'],
        a['inputs']['nearby_hospitals'],
        a['inputs']['infra_growth_score'],
        a['inputs']['floor_ratio'] * 10
    ]
    b_vals = [
        normalize(b['inputs']['size_sqft'], 500, 5000),
        b['inputs']['bhk'] * 2,
        b['inputs']['nearby_schools'],
        b['inputs']['nearby_hospitals'],
        b['inputs']['infra_growth_score'],
        b['inputs']['floor_ratio'] * 10
    ]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=a_vals, theta=categories,
                                   fill='toself', name='Property A'))
    fig.add_trace(go.Scatterpolar(r=b_vals, theta=categories,
                                   fill='toself', name='Property B'))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 10])),
                      title='Property Feature Radar',
                      height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Forecast Comparison ────────────────────────────────
    st.markdown("### 🔮 5-Year Forecast Comparison")
    labels = ['Now', '1 Year', '3 Years', '5 Years']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels,
        y=[a['predicted'], a['forecast']['forecast_1yr'],
           a['forecast']['forecast_3yr'], a['forecast']['forecast_5yr']],
        mode='lines+markers', name='Property A',
        line=dict(color='#636EFA', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=labels,
        y=[b['predicted'], b['forecast']['forecast_1yr'],
           b['forecast']['forecast_3yr'], b['forecast']['forecast_5yr']],
        mode='lines+markers', name='Property B',
        line=dict(color='#EF553B', width=3)
    ))
    fig.update_layout(title='Price Forecast Comparison',
                      xaxis_title='Time Period',
                      yaxis_title='Price (Lakhs ₹)',
                      height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Winner ─────────────────────────────────────────────
    st.markdown("### 🏆 Overall Verdict")
    score_a = (a['roi'] * 0.4) + ((10 - a['risk']['risk_score']) * 0.4) + \
              (a['forecast']['appreciation_5yr'] * 0.2)
    score_b = (b['roi'] * 0.4) + ((10 - b['risk']['risk_score']) * 0.4) + \
              (b['forecast']['appreciation_5yr'] * 0.2)

    if score_a > score_b:
        st.success(f"🏆 **Property A is the better investment** (Score: {score_a:.1f} vs {score_b:.1f})")
    elif score_b > score_a:
        st.success(f"🏆 **Property B is the better investment** (Score: {score_b:.1f} vs {score_a:.1f})")
    else:
        st.info("🟡 Both properties are equally matched")