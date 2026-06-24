# dashboard/pages/02_eda.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
st.title("📊 Exploratory Data Analysis Dashboard")
st.markdown("---")
st.markdown("""
<div class='re-card' style='border-color:#1A2F5A;padding:12px 20px;margin-bottom:8px'>
    <div style='display:flex;align-items:center;gap:10px'>
        <span style='font-size:18px'>←</span>
        <div>
            <span style='font-size:13px;color:#60A5FA;font-weight:600'>Filters are in the sidebar</span>
            <span style='font-size:12px;color:#6B6F87;margin-left:8px'>Scroll down in the left panel to filter by city, property type, BHK, and price range</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Load Data ──────────────────────────────────────────────
@st.cache_data
def load_data():
    df_raw = pd.read_csv(os.path.join(DATA_DIR, 'cleaned_df.csv'))
    df_model = pd.read_csv(os.path.join(DATA_DIR, 'model_df.csv'))
    df_raw['Estimated_Price'] = df_model['Estimated_Price'].values
    return df_raw, df_model

df_raw, df_model = load_data()

# ── Filters ────────────────────────────────────────────────

st.sidebar.markdown("### EDA Filters")
st.sidebar.markdown("""
<div style='background:#0D1A3A;border-radius:8px;padding:10px 12px;margin-bottom:12px'>
    <div style='font-size:11px;font-weight:700;color:#4B6EF5;
                text-transform:uppercase;letter-spacing:1px'>
        📊 EDA Filters
    </div>
    <div style='font-size:11px;color:#6B6F87;margin-top:3px'>
        Adjust filters below to explore the data
    </div>
</div>
""", unsafe_allow_html=True)
selected_states = st.sidebar.multiselect(
    "Filter by State",
    options=sorted(df_raw['State'].unique()),
    default=[]
)
if selected_states:
    df_raw = df_raw[df_raw['State'].isin(selected_states)]

# ── KPI Row ────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Properties", f"{len(df_raw):,}")
col2.metric("Avg Price", f"₹{df_raw['Estimated_Price'].mean():.0f}L")
col3.metric("Avg Size", f"{df_raw['Size_in_SqFt'].mean():.0f} sqft")
col4.metric("Cities", f"{df_raw['City'].nunique()}")

st.markdown("---")

# ── Section 1: Univariate ──────────────────────────────────
st.markdown("### 1. Univariate Analysis")

tab1, tab2, tab3 = st.tabs(["Price Distribution", "Size Distribution", "BHK Distribution"])

with tab1:
    fig = px.histogram(df_raw, x='Estimated_Price', nbins=50,
                       title='Property Price Distribution (Lakhs ₹)',
                       color_discrete_sequence=['#636EFA'],
                       labels={'Estimated_Price': 'Price (Lakhs ₹)'})
    fig.update_layout(bargap=0.05)
    st.plotly_chart(fig, use_container_width=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Min Price", f"₹{df_raw['Estimated_Price'].min():.0f}L")
    col2.metric("Median Price", f"₹{df_raw['Estimated_Price'].median():.0f}L")
    col3.metric("Max Price", f"₹{df_raw['Estimated_Price'].max():.0f}L")

with tab2:
    fig = px.histogram(df_raw, x='Size_in_SqFt', nbins=50,
                       title='Property Size Distribution (SqFt)',
                       color_discrete_sequence=['#EF553B'],
                       labels={'Size_in_SqFt': 'Size (SqFt)'})
    st.plotly_chart(fig, use_container_width=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Min Size", f"{df_raw['Size_in_SqFt'].min()} sqft")
    col2.metric("Median Size", f"{df_raw['Size_in_SqFt'].median():.0f} sqft")
    col3.metric("Max Size", f"{df_raw['Size_in_SqFt'].max()} sqft")

with tab3:
    bhk_counts = df_raw['BHK'].value_counts().sort_index()
    fig = px.bar(x=bhk_counts.index, y=bhk_counts.values,
                 title='BHK Distribution',
                 labels={'x': 'BHK', 'y': 'Count'},
                 color=bhk_counts.values,
                 color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Section 2: Bivariate ───────────────────────────────────
st.markdown("### 2. Bivariate Analysis")

tab1, tab2, tab3 = st.tabs(["Size vs Price", "BHK vs Price", "City vs Price"])

with tab1:
    sample = df_raw.sample(5000, random_state=42)
    fig = px.scatter(sample, x='Size_in_SqFt', y='Estimated_Price',
                     title='Size vs Price (5000 sample)',
                     labels={'Size_in_SqFt': 'Size (SqFt)',
                             'Estimated_Price': 'Price (Lakhs ₹)'},
                     color='BHK', opacity=0.5,
                     color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)
    corr = df_raw['Size_in_SqFt'].corr(df_raw['Estimated_Price'])
    st.info(f"📊 Pearson Correlation — Size vs Price: **{corr:.3f}**")

with tab2:
    fig = px.box(df_raw, x='BHK', y='Estimated_Price',
                 title='BHK vs Price Distribution',
                 labels={'BHK': 'BHK', 'Estimated_Price': 'Price (Lakhs ₹)'},
                 color='BHK')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(
        df_raw.groupby('BHK')['Estimated_Price']
        .agg(['mean', 'median', 'min', 'max'])
        .round(2).rename(columns={
            'mean': 'Avg Price',
            'median': 'Median Price',
            'min': 'Min Price',
            'max': 'Max Price'
        }),
        use_container_width=True
    )

with tab3:
    city_price = df_raw.groupby('City')['Estimated_Price'].mean().round(2).sort_values(ascending=False)
    fig = px.bar(x=city_price.index, y=city_price.values,
                 title='Average Price by City',
                 labels={'x': 'City', 'y': 'Avg Price (Lakhs ₹)'},
                 color=city_price.values,
                 color_continuous_scale='Blues')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Section 3: Multivariate ────────────────────────────────
st.markdown("### 3. Multivariate Analysis")

numeric_cols = ['Size_in_SqFt', 'BHK', 'Age_of_Property', 'Floor_No',
                'Nearby_Schools', 'Nearby_Hospitals', 'Estimated_Price']

corr_matrix = df_raw[numeric_cols].corr().round(3)

fig = px.imshow(corr_matrix,
                title='Feature Correlation Heatmap',
                color_continuous_scale='RdBu_r',
                aspect='auto', text_auto=True)
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Section 4: Property Type & Furnished Status ────────────
st.markdown("### 4. Category Distributions")
col1, col2 = st.columns(2)

with col1:
    fig = px.pie(df_raw, names='Property_Type',
                 title='Property Type Distribution',
                 color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.pie(df_raw, names='Furnished_Status',
                 title='Furnished Status Distribution',
                 color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig, use_container_width=True)