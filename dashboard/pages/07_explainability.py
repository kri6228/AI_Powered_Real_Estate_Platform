# dashboard/pages/07_explainability.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import shap
import joblib
import pickle
import json
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

st.title("🧠 Explainable AI Dashboard")
st.markdown("---")

# ── Load SHAP artifacts ────────────────────────────────────
@st.cache_resource
def load_shap():
    with open('../models/shap_explainer.pkl', 'rb') as f:
        explainer = pickle.load(f)
    shap_values = np.load('../models/shap_values.npy')
    X_sample = pd.read_csv('../models/shap_sample.csv')
    shap_importance = pd.read_csv('../models/shap_importance.csv')
    with open('../models/feature_columns.json', 'r') as f:
        features = json.load(f)
    return explainer, shap_values, X_sample, shap_importance, features

explainer, shap_values, X_sample, shap_importance, FEATURES = load_shap()

# ── Tabs ───────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🌍 Global Explainability",
    "📊 Feature Importance",
    "🔍 Local Explainability"
])

# ── Tab 1: Global ──────────────────────────────────────────
with tab1:
    st.markdown("### Global SHAP Summary Plot")
    st.markdown("Each dot represents one property. Color shows feature value (red=high, blue=low). Position shows impact on price.")

    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_sample,
                    feature_names=FEATURES,
                    show=False)
    st.pyplot(plt.gcf(), use_container_width=True)
    plt.clf()

    st.markdown("---")
    st.markdown("### Key Insights")
    col1, col2 = st.columns(2)
    with col1:
        st.success("✅ **Size_in_SqFt** is the strongest price driver — larger properties command significantly higher prices")
        st.success("✅ **Population_Density** captures city tier premium — Mumbai/Chennai properties priced higher")
    with col2:
        st.info("ℹ️ **Availability_Status** shows Ready-to-Move commands premium over Under-Construction")
        st.info("ℹ️ **Mall_Distance_km** shows negative impact — closer to amenities = higher price")

# ── Tab 2: Feature Importance ──────────────────────────────
with tab2:
    st.markdown("### Mean Absolute SHAP Feature Importance")
    st.markdown("Average impact of each feature on the model output across all properties.")

    # Top N slider
    top_n = st.slider("Show top N features", 5, 34, 15)
    top_features = shap_importance.head(top_n)

    fig = px.bar(
        top_features,
        x='SHAP_Importance',
        y='Feature',
        orientation='h',
        title=f'Top {top_n} Features by SHAP Importance',
        color='SHAP_Importance',
        color_continuous_scale='Blues',
        labels={'SHAP_Importance': 'Mean |SHAP Value|',
                'Feature': 'Feature'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'},
                      height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### Full Feature Importance Table")
    st.dataframe(shap_importance, use_container_width=True, hide_index=True)

# ── Tab 3: Local Explainability ────────────────────────────
with tab3:
    st.markdown("### Local SHAP Explanation")
    st.markdown("Explains WHY the model predicted a specific price for one property.")

    # ── Mode selection ─────────────────────────────────────
    local_mode = st.radio(
        "Choose property to explain",
        ["Use my predicted property", "Pick from sample dataset"],
        horizontal=True
    )

    if local_mode == "Use my predicted property":
        if 'input_df' not in st.session_state:
            st.warning("⚠️ Please go to **Price Prediction** page first and predict a property.")
            st.stop()

        input_df = st.session_state['input_df']
        predicted_price = st.session_state['predicted_price']
        inputs = st.session_state['property_inputs']

        st.info(f"Explaining: **{inputs['bhk']}BHK** in **{inputs['city']}** — Predicted ₹{predicted_price}L")

        shap_single = explainer.shap_values(input_df)
        base_value = explainer.expected_value
        display_df = input_df

    else:
        sample_idx = st.slider("Select property index from sample",
                                0, len(X_sample) - 1, 0)
        display_df = X_sample.iloc[sample_idx:sample_idx + 1]
        shap_single = explainer.shap_values(display_df)
        base_value = explainer.expected_value

        model = joblib.load('../models/best_model.pkl')
        predicted_price = round(float(model.predict(display_df)[0]), 2)
        st.info(f"Property #{sample_idx} — Predicted Price: ₹{predicted_price}L")

    # ── Waterfall Plot ─────────────────────────────────────
    st.markdown("### 🌊 SHAP Waterfall Plot")
    st.markdown("Shows how each feature pushes the price above or below the baseline average.")

    plt.figure(figsize=(10, 8))
    shap.waterfall_plot(
        shap.Explanation(
            values=shap_single[0],
            base_values=base_value,
            data=display_df.values[0],
            feature_names=FEATURES
        ),
        show=False
    )
    st.pyplot(plt.gcf(), use_container_width=True)
    plt.clf()

    st.markdown("---")

    # ── Top Contributors Table ─────────────────────────────
    st.markdown("### 📋 Top Price Contributors")
    contrib_df = pd.DataFrame({
        'Feature': FEATURES,
        'Feature Value': display_df.values[0],
        'SHAP Value': shap_single[0]
    }).sort_values('SHAP Value', key=abs, ascending=False).head(10)

    contrib_df['Impact'] = contrib_df['SHAP Value'].apply(
        lambda x: f"↑ +₹{abs(x):.1f}L" if x > 0 else f"↓ -₹{abs(x):.1f}L"
    )

    st.dataframe(
        contrib_df[['Feature', 'Feature Value', 'Impact']],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # ── Explanation Summary ────────────────────────────────
    st.markdown("### 💡 Plain English Explanation")
    st.markdown(f"**Base Price (average property):** ₹{base_value:.2f}L")
    st.markdown(f"**Predicted Price:** ₹{predicted_price}L")
    st.markdown("**Key factors affecting this property:**")

    top_pos = contrib_df[contrib_df['SHAP Value'] > 0].head(3)
    top_neg = contrib_df[contrib_df['SHAP Value'] < 0].head(3)

    for _, row in top_pos.iterrows():
        st.success(f"✅ **{row['Feature']}** increased price by ₹{abs(row['SHAP Value']):.1f}L")

    for _, row in top_neg.iterrows():
        st.error(f"🔴 **{row['Feature']}** decreased price by ₹{abs(row['SHAP Value']):.1f}L")