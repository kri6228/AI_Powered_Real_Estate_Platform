# dashboard/pages/11_analyzer.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engines.predictor import predict_price, build_input, CITY_DENSITY, STATE_DENSITY
from engines.risk_engine import calculate_risk_score
from engines.recommendation import get_recommendation, calculate_roi
from engines.forecaster import get_forecast, CITY_CAGR

st.title("⚡ Real-Time Property Analyzer")
st.markdown("---")
st.markdown("Upload a CSV file with property details and get instant **Price Prediction**, **Risk Score**, and **Investment Recommendation** for every property.")

# ── Template Download ──────────────────────────────────────
st.markdown("### 📥 Step 1 — Download Template")
st.markdown("Your CSV must have these columns:")

template_cols = {
    'city': ['Mumbai', 'Pune'],
    'state': ['Maharashtra', 'Maharashtra'],
    'size_sqft': [1200, 2500],
    'bhk': [2, 3],
    'age': [5, 10],
    'floor_no': [3, 7],
    'total_floors': [10, 15],
    'nearby_schools': [5, 8],
    'nearby_hospitals': [4, 6],
    'transport': ['High', 'Medium'],
    'parking': ['Yes', 'No'],
    'security': ['Yes', 'Yes'],
    'availability': ['Ready_to_Move', 'Under_Construction'],
    'furnished': ['Furnished', 'Semi-furnished'],
    'property_type': ['Apartment', 'Villa'],
    'facing': ['North', 'East'],
    'owner_type': ['Builder', 'Owner'],
    'balcony': [1, 2],
    'amenity_count': [3, 5],
    'actual_price': [180.0, 320.0],
}

template_df = pd.DataFrame(template_cols)
st.dataframe(template_df, use_container_width=True, hide_index=True)

csv_template = template_df.to_csv(index=False)
st.download_button(
    label="⬇️ Download Template CSV",
    data=csv_template,
    file_name="property_template.csv",
    mime="text/csv",
    use_container_width=True
)

st.markdown("---")

# ── Upload ─────────────────────────────────────────────────
st.markdown("### 📤 Step 2 — Upload Your CSV")
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])


if uploaded_file is not None:
    try:
        df_upload = pd.read_csv(uploaded_file)
        
        st.success(f"✅ Uploaded {len(df_upload)} properties successfully")
        st.dataframe(df_upload.head(), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        st.stop()

    st.session_state["analyzer_df"] = df_upload      
    st.session_state["analyzer_df_name"] = uploaded_file.name  # ← optional, for display
    
    # ── Validate columns ───────────────────────────────────
    required_cols = list(template_cols.keys())
    missing_cols = [c for c in required_cols if c not in df_upload.columns]

    if missing_cols:
        st.error(f"❌ Missing columns: {missing_cols}")
        st.stop()

    st.markdown("---")

    # ── Analyze Button ─────────────────────────────────────
    if st.button("⚡ Analyze All Properties",
                 use_container_width=True, type='primary'):

        results = []
        progress = st.progress(0)
        status = st.empty()

        for idx, row in df_upload.iterrows():
            status.text(f"Analyzing property {idx + 1} of {len(df_upload)}...")
            progress.progress((idx + 1) / len(df_upload))

            try:
                # Validate floor
                floor_no = int(row['floor_no'])
                total_floors = int(row['total_floors'])
                if floor_no > total_floors:
                    floor_no, total_floors = total_floors, floor_no

                # Build input
                input_df = build_input(
                    city=str(row['city']),
                    state=str(row['state']),
                    size_sqft=int(row['size_sqft']),
                    bhk=int(row['bhk']),
                    age=int(row['age']),
                    floor_no=floor_no,
                    total_floors=total_floors,
                    nearby_schools=int(row['nearby_schools']),
                    nearby_hospitals=int(row['nearby_hospitals']),
                    transport=str(row['transport']),
                    parking=str(row['parking']),
                    security=str(row['security']),
                    availability=str(row['availability']),
                    furnished=str(row['furnished']),
                    property_type=str(row['property_type']),
                    facing=str(row['facing']),
                    owner_type=str(row['owner_type']),
                    balcony=int(row['balcony']),
                    amenity_count=int(row['amenity_count'])
                )

                # Predict
                predicted = predict_price(input_df)
                actual = float(row['actual_price'])

                # Risk
                infra_score = round(
                    int(row['nearby_schools']) * 0.30 +
                    int(row['nearby_hospitals']) * 0.30 +
                    {'High': 10, 'Medium': 5, 'Low': 2}.get(
                        str(row['transport']), 5) * 0.40, 2
                )
                pop_density = CITY_DENSITY.get(str(row['city']), 500)
                floor_ratio = round(floor_no / max(total_floors, 1), 2)

                risk = calculate_risk_score(
                    age_of_property=int(row['age']),
                    crime_index=5.0,
                    availability_status=str(row['availability']),
                    floor_ratio=floor_ratio,
                    infra_growth_score=infra_score,
                    population_density=pop_density
                )

                # ROI + Recommendation
                roi = calculate_roi(actual, predicted)
                rec = get_recommendation(
                    roi=roi,
                    risk_score=risk['risk_score'],
                    availability_status=str(row['availability'])
                )

                # Forecast
                forecast = get_forecast(
                    predicted, str(row['city']), str(row['availability'])
                )

                results.append({
                    'City': row['city'],
                    'State': row['state'],
                    'BHK': row['bhk'],
                    'Size (sqft)': row['size_sqft'],
                    'Listed Price (L)': actual,
                    'Predicted Price (L)': predicted,
                    'ROI %': roi,
                    'Risk Score': risk['risk_score'],
                    'Risk Category': risk['risk_category'],
                    'Recommendation': rec['recommendation'],
                    '1yr Forecast (L)': forecast['forecast_1yr'],
                    '3yr Forecast (L)': forecast['forecast_3yr'],
                    '5yr Forecast (L)': forecast['forecast_5yr'],
                    'Valuation': 'Undervalued' if roi > 10
                                 else 'Overvalued' if roi < -10
                                 else 'Fair Value'
                })

            except Exception as e:
                results.append({
                    'City': row.get('city', 'Unknown'),
                    'State': row.get('state', 'Unknown'),
                    'BHK': row.get('bhk', '?'),
                    'Size (sqft)': row.get('size_sqft', '?'),
                    'Listed Price (L)': row.get('actual_price', '?'),
                    'Predicted Price (L)': 'ERROR',
                    'ROI %': 'ERROR',
                    'Risk Score': 'ERROR',
                    'Risk Category': 'ERROR',
                    'Recommendation': 'ERROR',
                    '1yr Forecast (L)': 'ERROR',
                    '3yr Forecast (L)': 'ERROR',
                    '5yr Forecast (L)': 'ERROR',
                    'Valuation': f'Error: {str(e)}'
                })

        progress.progress(1.0)
        status.text("✅ Analysis complete!")

        results_df = pd.DataFrame(results)

        st.markdown("---")
        st.markdown("### 📊 Analysis Results")

        # ── Summary KPIs ───────────────────────────────────
        valid = results_df[results_df['Recommendation'] != 'ERROR']
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Analyzed", len(results_df))
        col2.metric("BUY signals",
                    len(valid[valid['Recommendation'] == 'BUY']))
        col3.metric("HOLD signals",
                    len(valid[valid['Recommendation'] == 'HOLD']))
        col4.metric("SELL signals",
                    len(valid[valid['Recommendation'] == 'SELL']))

        st.markdown("---")

        # ── Color coded table ──────────────────────────────
        st.markdown("### 📋 Full Results Table")

        def color_rec(val):
            if val == 'BUY':
                return 'background-color: #d4edda; color: #155724'
            elif val == 'SELL':
                return 'background-color: #f8d7da; color: #721c24'
            elif val == 'HOLD':
                return 'background-color: #fff3cd; color: #856404'
            return ''

        def color_risk(val):
            if val == 'Low':
                return 'background-color: #d4edda'
            elif val == 'High':
                return 'background-color: #f8d7da'
            elif val == 'Medium':
                return 'background-color: #fff3cd'
            return ''

        styled = results_df.style\
            .map(color_rec, subset=['Recommendation'])\
            .map(color_risk, subset=['Risk Category'])

        st.dataframe(styled, use_container_width=True, hide_index=True)

        st.markdown("---")

        # ── Charts ─────────────────────────────────────────
        st.markdown("### 📈 Visualizations")
        tab1, tab2, tab3 = st.tabs([
            "Recommendation Distribution",
            "ROI vs Risk",
            "Price Comparison"
        ])

        with tab1:
            rec_counts = valid['Recommendation'].value_counts()
            fig = px.pie(
                values=rec_counts.values,
                names=rec_counts.index,
                title='Recommendation Distribution',
                color=rec_counts.index,
                color_discrete_map={
                    'BUY': '#00CC96',
                    'HOLD': '#FFA500',
                    'SELL': '#EF553B'
                }
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            valid_num = valid.copy()
            valid_num['ROI %'] = pd.to_numeric(valid_num['ROI %'],
                                                errors='coerce')
            valid_num['Risk Score'] = pd.to_numeric(valid_num['Risk Score'],
                                                     errors='coerce')
            fig = px.scatter(
                valid_num,
                x='Risk Score', y='ROI %',
                color='Recommendation',
                hover_data=['City', 'BHK', 'Predicted Price (L)'],
                title='ROI % vs Risk Score',
                color_discrete_map={
                    'BUY': '#00CC96',
                    'HOLD': '#FFA500',
                    'SELL': '#EF553B'
                }
            )
            fig.add_hline(y=15, line_dash='dash',
                          annotation_text='BUY threshold (ROI>15%)')
            fig.add_vline(x=3.3, line_dash='dash',
                          annotation_text='Low risk threshold')
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            valid_num = valid.copy()
            valid_num['Listed Price (L)'] = pd.to_numeric(
                valid_num['Listed Price (L)'], errors='coerce')
            valid_num['Predicted Price (L)'] = pd.to_numeric(
                valid_num['Predicted Price (L)'], errors='coerce')

            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Listed Price',
                x=valid_num.index,
                y=valid_num['Listed Price (L)'],
                marker_color='#636EFA'
            ))
            fig.add_trace(go.Bar(
                name='Predicted Price',
                x=valid_num.index,
                y=valid_num['Predicted Price (L)'],
                marker_color='#EF553B'
            ))
            fig.update_layout(
                barmode='group',
                title='Listed vs Predicted Price',
                xaxis_title='Property Index',
                yaxis_title='Price (Lakhs ₹)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # ── Download Results ───────────────────────────────
        st.markdown("### ⬇️ Download Results")
        csv_out = results_df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Full Analysis CSV",
            data=csv_out,
            file_name="property_analysis_results.csv",
            mime="text/csv",
            use_container_width=True
        )