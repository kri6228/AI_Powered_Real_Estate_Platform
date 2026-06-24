# dashboard/pages/03_prediction.py

import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engines.predictor import predict_price, build_input, CITY_DENSITY, STATE_DENSITY

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

st.markdown("<h1>💰 Price Prediction</h1>", unsafe_allow_html=True)
st.markdown("<p class='re-subtitle'>Enter property details to get an AI-powered price estimate</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ── Input Form ─────────────────────────────────────────────
col_loc, col_prop, col_floor = st.columns(3)

with col_loc:
    st.markdown("<p class='re-section'>Location</p>", unsafe_allow_html=True)
    state        = st.selectbox("State", sorted(STATE_DENSITY.keys()))
    city         = st.selectbox("City", sorted(state_city_map.get(state, [])))
    availability = st.selectbox("Availability", ['Ready_to_Move', 'Under_Construction'])

with col_prop:
    st.markdown("<p class='re-section'>Property</p>", unsafe_allow_html=True)
    property_type = st.selectbox("Type", ['Apartment', 'Independent House', 'Villa'])
    bhk           = st.slider("BHK", 1, 5, 2)
    size_sqft     = st.slider("Size (SqFt)", 500, 5000, 1200)
    age           = st.slider("Age (years)", 0, 35, 5)
    furnished     = st.selectbox("Furnished", ['Furnished', 'Semi-furnished', 'Unfurnished'])

with col_floor:
    st.markdown("<p class='re-section'>Floor & Amenities</p>", unsafe_allow_html=True)
    floor_no         = st.slider("Floor Number", 0, 30, 5)
    total_floors     = st.slider("Total Floors", 1, 30, 10)
    nearby_schools   = st.slider("Nearby Schools", 1, 10, 5)
    nearby_hospitals = st.slider("Nearby Hospitals", 1, 10, 5)
    transport        = st.selectbox("Transport", ['High', 'Medium', 'Low'])
    parking          = st.selectbox("Parking", ['Yes', 'No'])
    security         = st.selectbox("Security", ['Yes', 'No'])
    facing           = st.selectbox("Facing", ['North', 'South', 'East', 'West'])
    owner_type       = st.selectbox("Owner Type", ['Builder', 'Owner', 'Broker'])
    balcony          = st.slider("Balcony", 0, 3, 1)
    amenity_count    = st.slider("Amenities", 1, 5, 3)

st.markdown("<hr>", unsafe_allow_html=True)

if st.button("🔮 Predict Price", use_container_width=True, type='primary'):
    if floor_no > total_floors:
        st.error("❌ Floor number cannot exceed total floors.")
    else:
        input_df = build_input(
            city=city, state=state,
            size_sqft=size_sqft, bhk=bhk,
            age=age, floor_no=floor_no,
            total_floors=total_floors,
            nearby_schools=nearby_schools,
            nearby_hospitals=nearby_hospitals,
            transport=transport,
            parking=parking, security=security,
            availability=availability,
            furnished=furnished,
            property_type=property_type,
            facing=facing, owner_type=owner_type,
            balcony=balcony,
            amenity_count=amenity_count
        )
        predicted_price = predict_price(input_df)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<p class='re-section'>Prediction Result</p>", unsafe_allow_html=True)

        # ── Main result card ───────────────────────────────
        crore_text = f"= ₹{predicted_price/100:.2f} Cr" if predicted_price >= 100 else ""
        st.markdown(f"""
        <div class='re-card' style='border-color:#4B6EF5;text-align:center;padding:32px'>
            <div style='font-size:13px;font-weight:600;color:#4B6EF5;
                        text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>
                Estimated Market Value
            </div>
            <div style='font-family:Space Grotesk,sans-serif;font-size:48px;
                        font-weight:700;color:#FFFFFF'>
                ₹{predicted_price:.2f}L
            </div>
            <div style='font-size:14px;color:#6B6F87;margin-top:4px'>{crore_text}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Secondary metrics ──────────────────────────────
        col1, col2, col3 = st.columns(3)
        col1.metric("Price per SqFt",  f"₹{(predicted_price * 100000 / size_sqft):,.0f}")
        col2.metric("City",             city)
        col3.metric("Availability",     availability.replace('_', ' '))

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<p class='re-section'>Property Summary</p>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            details_left = [
                ("Property Type", property_type),
                ("BHK",           str(bhk)),
                ("Size",          f"{size_sqft} sqft"),
                ("Age",           f"{age} years"),
                ("Floor",         f"{floor_no} / {total_floors}"),
                ("Furnished",     furnished),
            ]
            for label, val in details_left:
                st.markdown(f"""
                <div style='display:flex;justify-content:space-between;
                            padding:8px 0;border-bottom:1px solid #2D3147'>
                    <span style='font-size:13px;color:#6B6F87'>{label}</span>
                    <span style='font-size:13px;color:#C8CAD4;font-weight:500'>{val}</span>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            details_right = [
                ("City",          city),
                ("State",         state),
                ("Availability",  availability.replace('_',' ')),
                ("Parking",       parking),
                ("Security",      security),
                ("Transport",     transport),
            ]
            for label, val in details_right:
                st.markdown(f"""
                <div style='display:flex;justify-content:space-between;
                            padding:8px 0;border-bottom:1px solid #2D3147'>
                    <span style='font-size:13px;color:#6B6F87'>{label}</span>
                    <span style='font-size:13px;color:#C8CAD4;font-weight:500'>{val}</span>
                </div>
                """, unsafe_allow_html=True)

        # ── Session state ──────────────────────────────────
        st.session_state['predicted_price'] = predicted_price
        st.session_state['input_df']        = input_df
        st.session_state['property_inputs'] = {
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
            'infra_growth_score': round(
                nearby_schools   * 0.30 +
                nearby_hospitals * 0.30 +
                {'High': 10, 'Medium': 5, 'Low': 2}.get(transport, 5) * 0.40, 2
            ),
            'population_density': CITY_DENSITY.get(city, 500),
            'floor_ratio': round(floor_no / max(total_floors, 1), 2),
        }

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
        <div class='re-card' style='border-color:#1A4535'>
            <div style='font-size:13px;color:#34D399'>
                ✓ Prediction complete — navigate to
                <strong>Recommendation</strong>, <strong>Risk Analysis</strong>, or
                <strong>Forecast</strong> for deeper analysis of this property.
            </div>
        </div>
        """, unsafe_allow_html=True)
