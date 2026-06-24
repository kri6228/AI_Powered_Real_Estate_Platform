# dashboard/pages/10_ranking.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
st.title("🏆 Property Ranking System")
st.markdown("---")
st.markdown("Automatically ranks top 10 properties from the dataset based on investment potential.")

# ── Load Data ──────────────────────────────────────────────
@st.cache_data
def load_data():
    df_raw = pd.read_csv(os.path.join(DATA_DIR, 'cleaned_df.csv'))
    df_model = pd.read_csv(os.path.join(DATA_DIR, 'model_df.csv'))
    df_raw['Estimated_Price']    = df_model['Estimated_Price'].values
    df_raw['Infra_Growth_Score'] = df_model['Infra_Growth_Score'].values
    df_raw['Crime_Index']        = df_model['Crime_Index'].values
    df_raw['Population_Density'] = df_model['Population_Density'].values
    df_raw['Floor_Ratio']        = df_model['Floor_Ratio'].values
    df_raw['Amenity_Count']      = df_model['Amenity_Count'].values
    return df_raw

df = load_data()

# ── Filters ────────────────────────────────────────────────
st.markdown("### 🔧 Ranking Filters")
col1, col2, col3 = st.columns(3)

with col1:
    selected_state = st.selectbox("Filter by State",
                                   ['All'] + sorted(df['State'].unique()))
    selected_city = st.selectbox(
        "Filter by City",
        ['All'] + sorted(
            df[df['State'] == selected_state]['City'].unique()
            if selected_state != 'All'
            else df['City'].unique()
        )
    )

with col2:
    selected_bhk = st.multiselect("BHK", sorted(df['BHK'].unique()),
                                   default=sorted(df['BHK'].unique()))
    selected_type = st.multiselect(
        "Property Type",
        df['Property_Type'].unique(),
        default=list(df['Property_Type'].unique())
    )

with col3:
    price_min, price_max = st.slider(
        "Price Range (Lakhs ₹)",
        min_value=int(df['Estimated_Price'].min()),
        max_value=int(df['Estimated_Price'].max()),
        value=(int(df['Estimated_Price'].min()),
               int(df['Estimated_Price'].max()))
    )
    availability = st.selectbox(
        "Availability",
        ['All', 'Ready_to_Move', 'Under_Construction']
    )

# ── Ranking Weights ────────────────────────────────────────
st.markdown("### ⚖️ Customize Ranking Weights")
st.markdown("Adjust weights to match your investment priorities (must add to 100%)")
col1, col2, col3, col4 = st.columns(4)
w_infra  = col1.slider("Infra Score %",  0, 100, 30)
w_crime  = col2.slider("Low Crime %",    0, 100, 30)
w_price  = col3.slider("Price Value %",  0, 100, 20)
w_amenity = col4.slider("Amenities %",   0, 100, 20)

total_weight = w_infra + w_crime + w_price + w_amenity
if total_weight != 100:
    st.warning(f"⚠️ Weights sum to {total_weight}% — please adjust to 100%")

st.markdown("---")

# ── Rank Button ────────────────────────────────────────────
if st.button("🏆 Rank Top 10 Properties", use_container_width=True, type='primary'):

    if total_weight != 100:
        st.error("❌ Weights must sum to 100% before ranking.")
        st.stop()

    # ── Apply Filters ──────────────────────────────────────
    filtered = df.copy()
    if selected_state != 'All':
        filtered = filtered[filtered['State'] == selected_state]
    if selected_city != 'All':
        filtered = filtered[filtered['City'] == selected_city]
    if selected_bhk:
        filtered = filtered[filtered['BHK'].isin(selected_bhk)]
    if selected_type:
        filtered = filtered[filtered['Property_Type'].isin(selected_type)]
    if availability != 'All':
        filtered = filtered[filtered['Availability_Status'] == availability]
    filtered = filtered[
        (filtered['Estimated_Price'] >= price_min) &
        (filtered['Estimated_Price'] <= price_max)
    ]

    if len(filtered) == 0:
        st.error("❌ No properties match your filters. Please adjust.")
        st.stop()

    # ── Normalize features 0-10 ────────────────────────────
    def norm(series):
        mn, mx = series.min(), series.max()
        if mx == mn:
            return pd.Series([5] * len(series), index=series.index)
        return (series - mn) / (mx - mn) * 10

    filtered = filtered.copy()
    filtered['Infra_Norm']   = norm(filtered['Infra_Growth_Score'])
    filtered['Crime_Norm']   = 10 - norm(filtered['Crime_Index'])  # inverse
    filtered['Price_Norm']   = 10 - norm(filtered['Estimated_Price'])  # cheaper = better value
    filtered['Amenity_Norm'] = norm(filtered['Amenity_Count'])

    # ── Investment Score ───────────────────────────────────
    filtered['Investment_Score'] = (
        filtered['Infra_Norm']   * (w_infra   / 100) +
        filtered['Crime_Norm']   * (w_crime   / 100) +
        filtered['Price_Norm']   * (w_price   / 100) +
        filtered['Amenity_Norm'] * (w_amenity / 100)
    ).round(2)

    top10 = filtered.nlargest(10, 'Investment_Score').reset_index(drop=True)
    top10.index += 1  # rank starts from 1

    # ── Results ────────────────────────────────────────────
    st.markdown(f"### 🏆 Top 10 Properties ({len(filtered):,} matched)")

    # ── Podium ─────────────────────────────────────────────
    st.markdown("### 🥇 Top 3 Podium")
    col1, col2, col3 = st.columns(3)
    podium = [col1, col2, col3]
    medals = ['🥇', '🥈', '🥉']

    for i, col in enumerate(podium):
        if i < len(top10):
            row = top10.iloc[i]
            col.success(f"""
            {medals[i]} **Rank {i+1}**
            
            **{row['Property_Type']}** — {row['BHK']}BHK  
            📍 {row['City']}, {row['State']}  
            💰 ₹{row['Estimated_Price']:.1f}L  
            ⚙️ Score: **{row['Investment_Score']}/10**  
            🏗️ {row['Availability_Status'].replace('_', ' ')}
            """)

    st.markdown("---")

    # ── Full Top 10 Table ──────────────────────────────────
    st.markdown("### 📋 Full Top 10 Rankings")
    display_cols = {
        'City': 'City',
        'State': 'State',
        'Property_Type': 'Type',
        'BHK': 'BHK',
        'Size_in_SqFt': 'Size (sqft)',
        'Estimated_Price': 'Price (L)',
        'Availability_Status': 'Availability',
        'Infra_Growth_Score': 'Infra Score',
        'Crime_Index': 'Crime Index',
        'Amenity_Count': 'Amenities',
        'Investment_Score': 'Invest Score'
    }
    st.dataframe(
        top10[list(display_cols.keys())].rename(columns=display_cols),
        use_container_width=True
    )

    st.markdown("---")

    # ── Score Breakdown Chart ──────────────────────────────
    st.markdown("### 📊 Score Breakdown — Top 10")
    fig = px.bar(
        top10,
        x=top10.index,
        y='Investment_Score',
        title='Investment Score — Top 10 Properties',
        labels={'x': 'Rank', 'Investment_Score': 'Score'},
        color='Investment_Score',
        color_continuous_scale='Greens',
        hover_data=['City', 'BHK', 'Estimated_Price', 'Property_Type']
    )
    fig.update_layout(height=400, xaxis_title='Rank')
    st.plotly_chart(fig, use_container_width=True)

    # ── Radar for top 3 ───────────────────────────────────
    st.markdown("### 📡 Top 3 Properties Radar")
    categories = ['Infra Score', 'Low Crime', 'Price Value', 'Amenities']

    fig = go.Figure()
    colors = ['#636EFA', '#EF553B', '#00CC96']
    for i in range(min(3, len(top10))):
        row = top10.iloc[i]
        vals = [
            row['Infra_Norm'],
            row['Crime_Norm'],
            row['Price_Norm'],
            row['Amenity_Norm']
        ]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=categories,
            fill='toself',
            name=f"#{i+1} {row['City']} {row['BHK']}BHK",
            line=dict(color=colors[i])
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 10])),
        title='Top 3 Properties — Feature Radar',
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)