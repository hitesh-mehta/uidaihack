
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Set Page Configuration
st.set_page_config(
    page_title="Aadhaar Biometric Insights",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Premium Dark" factor
st.markdown("""
<style>
    /* Global Background Override */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Metric Card - Glassmorphism */
    div.metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        text-align: center;
        transition: transform 0.2s;
    }
    div.metric-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.08);
    }
    
    /* Text Colors for Dark Mode */
    div.metric-card h3 {
        color: #A0AEC0 !important;
        font-size: 1rem;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div.metric-card p {
        color: #F7FAFC !important;
        font-weight: 700;
        margin: 0;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 5px;
        color: #A0AEC0;
        padding: 10px 20px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(255, 255, 255, 0.1);
        color: #F63366;
    }
    
    /* Remove padding from block container to use full space */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

import sys
from pathlib import Path

# Add src to python path to allow imports if running from root
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent # src/dashboard/app.py -> src/dashboard -> src -> uidai_hackathon
sys.path.append(str(project_root))

from uidai_hackathon.src import config

@st.cache_data
def load_data():
    # Biometric
    df = pd.read_csv(config.MASTER_DATA_PATH)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    cols_to_numeric = ['Bio_age_5_17', 'Bio_age_17+']
    for col in cols_to_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['Total_Updates'] = df['Bio_age_5_17'] + df['Bio_age_17+']
    
    # Enrolment
    if os.path.exists(config.MASTER_ENROLMENT_PATH):
        df_enrol = pd.read_csv(config.MASTER_ENROLMENT_PATH)
        df_enrol['Date'] = pd.to_datetime(df_enrol['Date'], dayfirst=True, errors='coerce')
        # Ensure Age cols are numeric if needed, but preprocessor did it.
    else:
        df_enrol = pd.DataFrame(columns=['Date', 'State', 'District', 'Total_Enrolment'])
        
    # Demo
    if os.path.exists(config.MASTER_DEMO_PATH):
        df_demo = pd.read_csv(config.MASTER_DEMO_PATH)
        df_demo['Date'] = pd.to_datetime(df_demo['Date'], dayfirst=True, errors='coerce')
    else:
        df_demo = pd.DataFrame(columns=['Date', 'State', 'District', 'Total_Demo_Updates'])
    
    anomalies = pd.read_csv(config.ANOMALY_OUTPUT_PATH)
    
    return df, df_enrol, df_demo, anomalies

try:
    df, df_enrol, df_demo, anomalies = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Helper to apply unified theme to plots
def update_plot_layout(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FAFAFA'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

# Sidebar
with st.sidebar:
    st.title("Filters 🔍")
    # Unified State List
    all_states = sorted(list(set(df['State'].dropna().unique()) | set(df_enrol['State'].dropna().unique())))
    selected_state = st.selectbox("Select State", ["All"] + all_states)
    
    selected_district = "All"
    if selected_state != "All":
        # Filter all DFs
        filtered_df = df[df['State'] == selected_state]
        filtered_enrol = df_enrol[df_enrol['State'] == selected_state]
        filtered_demo = df_demo[df_demo['State'] == selected_state]
        
        districts = sorted(filtered_df['District'].dropna().unique().tolist())
        selected_district = st.selectbox("Select District", ["All"] + districts)
        if selected_district != "All":
            filtered_df = filtered_df[filtered_df['District'] == selected_district]
            filtered_enrol = filtered_enrol[filtered_enrol['District'] == selected_district]
            filtered_demo = filtered_demo[filtered_demo['District'] == selected_district]
    else:
        filtered_df = df
        filtered_enrol = df_enrol
        filtered_demo = df_demo

    st.markdown("---")
    st.info("Built with ❤️ using Streamlit")

# Main Title
st.title("📊 Aadhaar Analytics")
st.markdown("<p style='color: #A0AEC0; margin-top: -15px;'>Real-time insights across Biometric, Demographic, and Enrolment data.</p>", unsafe_allow_html=True)
st.markdown("---")

# KPI Section
total_updates = filtered_df['Total_Updates'].sum()
total_enrolment = filtered_enrol['Total_Enrolment'].sum()
total_demo = filtered_demo['Total_Demo_Updates'].sum()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Biometric Updates</h3>
        <p class="big-font" style="font-size: 2rem; color: #F63366 !important;">{total_updates:,.0f}</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>New Enrolments</h3>
        <p class="big-font" style="font-size: 2rem; color: #4FD1C5 !important;">{total_enrolment:,.0f}</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Demographic Updates</h3>
        <p class="big-font" style="font-size: 2rem; color: #ECC94B !important;">{total_demo:,.0f}</p>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📈 Trends", "🗺️ Demographics", "🔮 Forecast", "🚨 Anomalies", "🧩 Clustering", "🌳 Hierarchy", "📶 Digital Divide"])

with tab1:
    st.subheader("Temporal Trends")
    
    # Combine trends
    t1 = filtered_df.groupby('Date')['Total_Updates'].sum().reset_index().rename(columns={'Total_Updates': 'Biometric'})
    t2 = filtered_enrol.groupby('Date')['Total_Enrolment'].sum().reset_index().rename(columns={'Total_Enrolment': 'Enrolment'})
    t3 = filtered_demo.groupby('Date')['Total_Demo_Updates'].sum().reset_index().rename(columns={'Total_Demo_Updates': 'Demographic'})
    
    # Merge
    trend_merged = pd.merge(t1, t2, on='Date', how='outer').merge(t3, on='Date', how='outer').fillna(0)
    trend_melt = trend_merged.melt(id_vars='Date', var_name='Metric', value_name='Count')
    
    fig_trend = px.line(trend_melt, x='Date', y='Count', color='Metric', 
                        title='Updates & Enrolments over Time', 
                        color_discrete_map={'Biometric': '#F63366', 'Enrolment': '#4FD1C5', 'Demographic': '#ECC94B'})
    st.plotly_chart(update_plot_layout(fig_trend), use_container_width=True)

with tab2:
    st.subheader("Geographic & Demographic Insights")
    
    # Filter for Map Type
    map_metric = st.radio("Select Metric for Map/Charts", ["Biometric Updates", "Enrolment", "Demographic Updates"], horizontal=True)
    
    if map_metric == "Biometric Updates":
        target_df = filtered_df
        val_col = 'Total_Updates'
        color_scale = 'Viridis'
    elif map_metric == "Enrolment":
        target_df = filtered_enrol
        val_col = 'Total_Enrolment'
        color_scale = 'Teal'
    else:
        target_df = filtered_demo
        val_col = 'Total_Demo_Updates'
        color_scale = 'Solar'
        
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        # Pie Chart Logic
        if map_metric == "Biometric Updates":
             fig_pie = px.pie(names=['Age 5-17', 'Age 17+'], 
                              values=[filtered_df['Bio_age_5_17'].sum(), filtered_df['Bio_age_17+'].sum()], 
                              title='Biometric Age Distribution', hole=0.6, color_discrete_sequence=['#ECC94B', '#4FD1C5'])
             st.plotly_chart(update_plot_layout(fig_pie), use_container_width=True)
        elif map_metric == "Enrolment":
             vals = [filtered_enrol['Age_0_5'].sum(), filtered_enrol['Age_5_17'].sum(), filtered_enrol['Age_18_greater'].sum()]
             fig_pie = px.pie(names=['0-5', '5-17', '18+'], values=vals, 
                              title='Enrolment Age Distribution', hole=0.6)
             st.plotly_chart(update_plot_layout(fig_pie), use_container_width=True)
        else:
             vals = [filtered_demo['Demo_age_5_17'].sum(), filtered_demo['Demo_age_17+'].sum()]
             fig_pie = px.pie(names=['5-17', '17+'], values=vals, 
                              title='Demographic Updates Age Distribution', hole=0.6)
             st.plotly_chart(update_plot_layout(fig_pie), use_container_width=True)
        
    with col_b:
        # Time Slider Toggle
        enable_animation = st.checkbox("Enable Time Animation (Monthly)", value=False)
        
        if selected_state == "All":
            if enable_animation:
                 # Aggregate by Month & State
                 anim_df = target_df.copy()
                 anim_df['Date_Month'] = anim_df['Date'].dt.to_period('M').astype(str)
                 anim_agg = anim_df.groupby(['Date_Month', 'State'])[val_col].sum().reset_index()
                 # Sort by date
                 anim_agg = anim_agg.sort_values('Date_Month')
                 
                 fig_map = px.choropleth(
                    anim_agg,
                    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                    featureidkey='properties.ST_NM',
                    locations='State',
                    color=val_col,
                    animation_frame='Date_Month',
                    color_continuous_scale=color_scale,
                    title=f'Pan-India {map_metric} Heatmap (Time-Lapse)'
                )
            else:
                top_geo = target_df.groupby('State')[val_col].sum().reset_index()
                fig_map = px.choropleth(
                    top_geo,
                    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                    featureidkey='properties.ST_NM',
                    locations='State',
                    color=val_col,
                    color_continuous_scale=color_scale,
                    title=f'Pan-India {map_metric} Heatmap'
                )
            fig_map.update_geos(fitbounds="locations", visible=False, bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(update_plot_layout(fig_map), use_container_width=True)
        else:
            top_geo = target_df.groupby('District')[val_col].sum().nlargest(10).reset_index()
            fig_bar = px.bar(top_geo, x=val_col, y='District', orientation='h', 
                             title=f'Top 10 Districts - {map_metric}', 
                             color=val_col, color_continuous_scale=color_scale)
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(update_plot_layout(fig_bar), use_container_width=True)

with tab3:
    st.subheader("Predictive Forecasting (Holt-Winters)")
    
    forecast_metric = st.radio("Select Metric to Forecast", ["Biometric Updates", "Enrolment", "Demographic Updates"], horizontal=True)
    
    img_map = {
        "Biometric Updates": "forecast_biometric.png",
        "Enrolment": "forecast_enrolment.png",
        "Demographic Updates": "forecast_demo.png"
    }
    
    img_path = config.FIGURES_DIR / img_map[forecast_metric]
    
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        if os.path.exists(img_path):
            st.image(str(img_path), caption=f"{forecast_metric} Forecast (Next 6 Months)", use_container_width=True)
        else:
            st.warning(f"Forecast model for {forecast_metric} is running or insufficient data.")
            
    with col_f2:
        st.info("The Holt-Winters Exponential Smoothing model captures level, trend, and seasonality. The shaded area typically represents confidence intervals (if enabled), while the red line indicates future predictions.")

# Helper function for Benford's Law
def benfords_law_analysis(series, title):
    # Extract first digit
    first_digits = series.astype(str).str[0].astype(int)
    # Count frequencies
    observed_counts = first_digits.value_counts().sort_index()
    total_count = observed_counts.sum()
    observed_freq = observed_counts / total_count
    
    # Expected Benford Frequencies
    expected_freq = pd.Series({d: np.log10(1 + 1/d) for d in range(1, 10)})
    
    # DataFrame for plotting
    benford_df = pd.DataFrame({'Digit': range(1, 10), 'Observed': observed_freq, 'Expected': expected_freq}).fillna(0)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=benford_df['Digit'], y=benford_df['Observed'], name='Observed', marker_color='#F63366'))
    fig.add_trace(go.Scatter(x=benford_df['Digit'], y=benford_df['Expected'], name='Expected (Benford)', line=dict(color='#4FD1C5', width=3)))
    fig.update_layout(title=f"Benford's Law Analysis: {title}", xaxis_title='First Digit', yaxis_title='Frequency')
    return update_plot_layout(fig)

with tab4:
    st.subheader("Anomaly Detection (Isolation Forest & Benford's Law)")
    
    col_x, col_y = st.columns([2, 1])
    
    with col_x:
        # Benford's Law selection
        benford_metric = st.selectbox("Select Metric for Benford's Law", ["Biometric Updates", "Enrolment", "Demographic Updates"])
        if benford_metric == "Biometric Updates":
            target_series = df[df['Total_Updates'] > 0]['Total_Updates']
        elif benford_metric == "Enrolment":
            target_series = df_enrol[df_enrol['Total_Enrolment'] > 0]['Total_Enrolment']
        else:
            target_series = df_demo[df_demo['Total_Demo_Updates'] > 0]['Total_Demo_Updates']
            
        fig_benford = benfords_law_analysis(target_series, benford_metric)
        st.plotly_chart(fig_benford, use_container_width=True)
        st.caption("Benford's Law states that in many naturally occurring collections of numbers, the leading digit is likely to be small. Deviations may indicate data manipulation or operational anomalies.")

    with col_y:
        st.write("### Statistical Outliers (Isolation Forest)")
        if selected_state != "All":
            filtered_anomalies = anomalies[anomalies['State'] == selected_state]
        else:
            filtered_anomalies = anomalies
        st.dataframe(filtered_anomalies[['State', 'District', 'Total_Updates', 'Z_Score']].sort_values('Z_Score', ascending=False), height=400)

with tab5:
    st.subheader("District Clustering (K-Means)")
    
    col_c1, col_c2 = st.columns([2, 1])
    
    with col_c1:
        if os.path.exists(config.CLUSTER_IMG_PATH):
            st.image(str(config.CLUSTER_IMG_PATH), caption="District Segmentation", use_container_width=True)
        else:
            st.warning("Clustering image not found.")
            
    with col_c2:
        st.markdown("""
        <div class="metric-card" style="text-align: left;">
            <h3>Segments</h3>
            <ul style="list-style-type: none; padding: 0; color: #F7FAFC;">
                <li>🏙️ <b>High Volume</b>: Urban Centers</li>
                <li>🏫 <b>Child-Centric</b>: High school enrollment</li>
                <li>🏡 <b>Low Volume</b>: Rural areas</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if os.path.exists(config.CLUSTERING_OUTPUT_PATH):
            cl_df = pd.read_csv(config.CLUSTERING_OUTPUT_PATH)
            st.dataframe(cl_df[['State', 'District', 'Cluster']].head(20), height=250)

# --- NEW TABS ---
tab6, tab7 = st.tabs(["🌳 Hierarchy", "📶 Digital Divide"])

with tab6:
    st.subheader("Multi-Level Hierarchical Visualization")
    
    tree_metric = st.radio("Select Metric for Hierarchy", ["Biometric Updates", "Enrolment", "Demographic Updates"], horizontal=True)
    
    # Prepare Data for Sunburst
    # We need a hierarchy: Country -> State -> District
    # Let's aggregate
    if tree_metric == "Biometric Updates":
        hier_df = df.groupby(['State', 'District'])['Total_Updates'].sum().reset_index()
        hier_df.rename(columns={'Total_Updates': 'Value'}, inplace=True)
    elif tree_metric == "Enrolment":
        hier_df = df_enrol.groupby(['State', 'District'])['Total_Enrolment'].sum().reset_index()
        hier_df.rename(columns={'Total_Enrolment': 'Value'}, inplace=True)
    else:
        hier_df = df_demo.groupby(['State', 'District'])['Total_Demo_Updates'].sum().reset_index()
        hier_df.rename(columns={'Total_Demo_Updates': 'Value'}, inplace=True)
        
    hier_df['Country'] = 'India' # Root node
    
    # Filter out zero values for better chart
    hier_df = hier_df[hier_df['Value'] > 0]
    
    fig_sun = px.sunburst(hier_df, path=['Country', 'State', 'District'], values='Value',
                          title=f'{tree_metric} Distribution Hierarchy',
                          color='Value', color_continuous_scale='Viridis')
    st.plotly_chart(update_plot_layout(fig_sun), use_container_width=True)

with tab7:
    st.subheader("Digital Divide Index (DDI)")
    st.markdown("**(Biometric * 0.4) + (Demographic * 0.3) + (Enrolment * 0.3)** (Normalized)")
    
    # Calculate DDI
    # 1. Aggregate all metrics by District
    t_updates = df.groupby(['State', 'District'])['Total_Updates'].sum().reset_index()
    t_enrol = df_enrol.groupby(['State', 'District'])['Total_Enrolment'].sum().reset_index()
    t_demo = df_demo.groupby(['State', 'District'])['Total_Demo_Updates'].sum().reset_index()
    
    ddi_df = pd.merge(t_updates, t_enrol, on=['State', 'District'], how='outer')
    ddi_df = pd.merge(ddi_df, t_demo, on=['State', 'District'], how='outer').fillna(0)
    
    # 2. Normalize (Min-Max Scaling)
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    ddi_df[['Norm_Bio', 'Norm_Enrol', 'Norm_Demo']] = scaler.fit_transform(ddi_df[['Total_Updates', 'Total_Enrolment', 'Total_Demo_Updates']])
    
    # 3. Calculate Index
    ddi_df['DDI'] = (ddi_df['Norm_Bio'] * 40) + (ddi_df['Norm_Demo'] * 30) + (ddi_df['Norm_Enrol'] * 30)
    
    col_d1, col_d2 = st.columns([2, 1])
    
    with col_d1:
        # DDI Map
        top_ddi_state = ddi_df.groupby('State')['DDI'].mean().reset_index() # State-level avg for map
        fig_ddi_map = px.choropleth(
            top_ddi_state,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM',
            locations='State',
            color='DDI',
            color_continuous_scale='Magma',
            title='Average Digital Divide Index by State'
        )
        fig_ddi_map.update_geos(fitbounds="locations", visible=False, bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(update_plot_layout(fig_ddi_map), use_container_width=True)
        
    with col_d2:
        st.write("### Top Digitally Advanced Districts")
        st.dataframe(ddi_df[['State', 'District', 'DDI']].sort_values('DDI', ascending=False).head(20), height=400)

st.sidebar.markdown("---")
st.sidebar.info("Built with ❤️ using Streamlit for UIDAI Hackathon")
