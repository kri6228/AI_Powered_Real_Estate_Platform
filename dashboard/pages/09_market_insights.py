# dashboard/pages/09_market_insights.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engines.forecaster import CITY_CAGR
from engines.risk_engine import calculate_risk_score

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
st.title("🌆 Market Insights Dashboard")
st.markdown("---")

# ── Load Data ──────────────────────────────────────────────
@st.cache_data
def load_data():
    df_raw = pd.read_csv(os.path.join(DATA_DIR, 'cleaned_df.csv'))
    df_model = pd.read_csv(os.path.join(DATA_DIR, 'model_df.csv'))
    df_raw['Estimated_Price'] = df_model['Estimated_Price'].values
    df_raw['Infra_Growth_Score'] = df_model['Infra_Growth_Score'].values
    df_raw['Population_Density'] = df_model['Population_Density'].values
    df_raw['Crime_Index'] = df_model['Crime_Index'].values
    df_raw['Floor_Ratio'] = df_model['Floor_Ratio'].values
    return df_raw

df = load_data()

# ── City Summary Table ─────────────────────────────────────
@st.cache_data
def build_city_summary(df):
    city_summary = df.groupby('City').agg(
        Avg_Price=('Estimated_Price', 'mean'),
        Avg_Size=('Size_in_SqFt', 'mean'),
        Avg_Age=('Age_of_Property', 'mean'),
        Avg_Infra=('Infra_Growth_Score', 'mean'),
        Avg_Crime=('Crime_Index', 'mean'),
        Population_Density=('Population_Density', 'first'),
        Total_Listings=('Estimated_Price', 'count')
    ).round(2).reset_index()

    # Add CAGR
    city_summary['CAGR_%'] = city_summary['City'].map(
        {k: round(v * 100, 1) for k, v in CITY_CAGR.items()}
    ).fillna(7.0)

    # Risk Score per city
    city_summary['Risk_Score'] = city_summary.apply(
        lambda row: calculate_risk_score(
            age_of_property=row['Avg_Age'],
            crime_index=row['Avg_Crime'],
            availability_status='Ready_to_Move',
            floor_ratio=0.5,
            infra_growth_score=row['Avg_Infra'],
            population_density=row['Population_Density']
        )['risk_score'], axis=1
    )

    # 5yr forecast appreciation
    city_summary['Forecast_5yr_%'] = city_summary.apply(
        lambda row: round(((1 + CITY_CAGR.get(row['City'], 0.07)) ** 5 - 1) * 100, 1),
        axis=1
    )

    return city_summary

city_summary = build_city_summary(df)

# ── Tabs ───────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Top Investment Areas",
    "📈 High Growth Areas",
    "🛡️ Low Risk Areas",
    "🗺️ Full City Overview"
])

# ── Tab 1: Top Investment Areas ────────────────────────────
with tab1:
    st.markdown("### 🏆 Top Investment Areas")
    st.markdown("Ranked by ROI potential — high CAGR, affordable price, low risk combined.")

    # Investment score = CAGR×0.4 + (10-Risk)×0.4 + Infra×0.2
    city_summary['Investment_Score'] = (
        city_summary['CAGR_%'] * 0.4 +
        (10 - city_summary['Risk_Score']) * 0.4 +
        city_summary['Avg_Infra'] * 0.2
    ).round(2)

    top_invest = city_summary.sort_values('Investment_Score', ascending=False).head(10)

    # Bar chart
    fig = px.bar(
        top_invest, x='City', y='Investment_Score',
        title='Top 10 Cities by Investment Score',
        color='Investment_Score',
        color_continuous_scale='Greens',
        labels={'Investment_Score': 'Investment Score'}
    )
    fig.update_layout(xaxis_tickangle=-30, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Table
    st.dataframe(
        top_invest[['City', 'Avg_Price', 'CAGR_%',
                    'Risk_Score', 'Investment_Score']].rename(columns={
            'Avg_Price': 'Avg Price (L)',
            'CAGR_%': 'CAGR %',
            'Risk_Score': 'Risk Score',
            'Investment_Score': 'Investment Score'
        }),
        use_container_width=True,
        hide_index=True
    )

# ── Tab 2: High Growth Areas ───────────────────────────────
with tab2:
    st.markdown("### 📈 High Growth Areas")
    st.markdown("Cities with highest projected appreciation over 5 years.")

    high_growth = city_summary.sort_values('Forecast_5yr_%', ascending=False).head(10)

    fig = px.bar(
        high_growth, x='City', y='Forecast_5yr_%',
        title='Top 10 High Growth Cities — 5 Year Appreciation',
        color='Forecast_5yr_%',
        color_continuous_scale='Blues',
        labels={'Forecast_5yr_%': '5yr Appreciation %'}
    )
    fig.update_layout(xaxis_tickangle=-30, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Bubble chart — Price vs Growth vs Listings
    fig2 = px.scatter(
        city_summary,
        x='Avg_Price', y='Forecast_5yr_%',
        size='Total_Listings',
        color='CAGR_%',
        hover_name='City',
        title='Price vs Growth Rate (bubble = listing volume)',
        labels={
            'Avg_Price': 'Avg Price (Lakhs)',
            'Forecast_5yr_%': '5yr Appreciation %',
            'CAGR_%': 'CAGR %'
        },
        color_continuous_scale='Viridis'
    )
    fig2.update_layout(height=450)
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        high_growth[['City', 'Avg_Price', 'CAGR_%', 'Forecast_5yr_%']].rename(columns={
            'Avg_Price': 'Avg Price (L)',
            'CAGR_%': 'CAGR %',
            'Forecast_5yr_%': '5yr Growth %'
        }),
        use_container_width=True,
        hide_index=True
    )

# ── Tab 3: Low Risk Areas ──────────────────────────────────
with tab3:
    st.markdown("### 🛡️ Low Risk Areas")
    st.markdown("Safest cities to invest — low crime, good infrastructure, stable market.")

    low_risk = city_summary.sort_values('Risk_Score').head(10)

    fig = px.bar(
        low_risk, x='City', y='Risk_Score',
        title='Top 10 Lowest Risk Cities',
        color='Risk_Score',
        color_continuous_scale='RdYlGn_r',
        labels={'Risk_Score': 'Risk Score (lower = safer)'}
    )
    fig.update_layout(xaxis_tickangle=-30, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Risk vs Infra scatter
    fig2 = px.scatter(
        city_summary,
        x='Avg_Infra', y='Risk_Score',
        hover_name='City',
        color='Risk_Score',
        size='Total_Listings',
        title='Infrastructure Score vs Risk Score',
        labels={
            'Avg_Infra': 'Avg Infrastructure Score',
            'Risk_Score': 'Risk Score'
        },
        color_continuous_scale='RdYlGn_r'
    )
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        low_risk[['City', 'Risk_Score', 'Avg_Crime',
                  'Avg_Infra', 'Avg_Price']].rename(columns={
            'Risk_Score': 'Risk Score',
            'Avg_Crime': 'Crime Index',
            'Avg_Infra': 'Infra Score',
            'Avg_Price': 'Avg Price (L)'
        }),
        use_container_width=True,
        hide_index=True
    )

# ── Tab 4: Full City Overview ──────────────────────────────
with tab4:
    st.markdown("### 🗺️ Full City Overview")

    # State filter
    selected_state = st.selectbox(
        "Filter by State",
        ['All'] + sorted(df['State'].unique())
    )

    if selected_state != 'All':
        cities_in_state = df[df['State'] == selected_state]['City'].unique()
        filtered = city_summary[city_summary['City'].isin(cities_in_state)]
    else:
        filtered = city_summary

    # Heatmap — all metrics
    heatmap_data = filtered.set_index('City')[[
        'Avg_Price', 'CAGR_%', 'Risk_Score',
        'Avg_Infra', 'Forecast_5yr_%', 'Investment_Score'
    ]].copy()

    # Normalize for heatmap
    heatmap_norm = (heatmap_data - heatmap_data.min()) / \
                   (heatmap_data.max() - heatmap_data.min())

    fig = px.imshow(
        heatmap_norm.T,
        title='City Metrics Heatmap (normalized)',
        color_continuous_scale='RdYlGn',
        aspect='auto',
        labels={'color': 'Score (normalized)'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Complete City Data")
    st.dataframe(
        filtered[[
            'City', 'Avg_Price', 'CAGR_%', 'Risk_Score',
            'Avg_Infra', 'Forecast_5yr_%',
            'Investment_Score', 'Total_Listings'
        ]].rename(columns={
            'Avg_Price': 'Avg Price (L)',
            'CAGR_%': 'CAGR %',
            'Risk_Score': 'Risk Score',
            'Avg_Infra': 'Infra Score',
            'Forecast_5yr_%': '5yr Growth %',
            'Investment_Score': 'Invest Score',
            'Total_Listings': 'Listings'
        }).sort_values('Invest Score', ascending=False),
        use_container_width=True,
        hide_index=True
    )