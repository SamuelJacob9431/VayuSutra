import streamlit as st
import pandas as pd
import plotly.express as px
from modules.data_loader import load_data
from modules.preprocessing import filter_data, get_metrics
from modules.forecasting import generate_forecast
from modules.insights import generate_insights, generate_recommendations, get_health_advisory, get_data_explanation
from modules.visualization import plot_time_series, plot_map, plot_forecast, get_aqi_color

# --- Page Configuration ---
st.set_page_config(
    page_title="वायुसूत्र | Atmospheric Intelligence",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');
    .main {
        background-color: #0B0F14;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #121821;
        border-right: 1px solid #1E2632;
    }
    .metric-card {
        background-color: #121821;
        padding: 28px;
        border-radius: 14px;
        border: 1px solid #1E2632;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: all 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #3AAED8;
    }
    .hero-card {
        border-top: 5px solid #3AAED8;
        padding: 36px !important;
        background: linear-gradient(135deg, #121821 0%, #1A222E 100%);
    }
    .metric-label {
        color: #94A3B8;
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 12px;
    }
    .metric-value {
        color: #E6EDF3;
        font-family: 'Sora', sans-serif !important;
        font-size: 3.8rem;
        font-weight: 800;
        line-height: 1;
        margin: 15px 0;
    }
    .metric-category {
        font-size: 1rem;
        font-weight: 800;
        padding: 6px 16px;
        border-radius: 8px;
        display: inline-block;
        text-transform: uppercase;
    }
    .viewing-badge {
        background: rgba(58, 174, 216, 0.1);
        color: #3AAED8;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid rgba(58, 174, 216, 0.2);
        margin-bottom: 20px;
        display: inline-block;
    }
    .health-banner {
        padding: 24px;
        border-radius: 14px;
        margin: 24px 0;
        border-left: 6px solid;
        display: flex;
        align-items: center;
        gap: 15px;
        background-color: rgba(255, 255, 255, 0.02);
    }
    
    /* Custom Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #3AAED8, #2F8FB2) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(58, 174, 216, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Data Loading ---
df = load_data('data/AIQ_India_cleaned_no_nh3.csv')

if df.empty:
    st.error("Dataset not found or empty. Please check the 'data' directory.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1684/1684375.png", width=50)
st.sidebar.header("Intelligence Controls")

with st.sidebar.expander("📍 Location & Mode", expanded=True):
    compare_mode = st.toggle("Enable Comparison Mode", value=False)
    
    states = sorted(df['state'].unique().tolist())
    selected_state = st.selectbox("State", ["All"] + states)
    
    cities = sorted(df[df['state'] == selected_state]['city'].unique().tolist()) if selected_state != "All" else sorted(df['city'].unique().tolist())
    
    if compare_mode:
        selected_cities = st.multiselect("Select Cities to Compare", cities, default=cities[:1] if cities else [])
    else:
        selected_city = st.selectbox("Select City", ["All"] + cities)
        selected_cities = [selected_city] if selected_city != "All" else []

with st.sidebar.expander("🌫 Pollution Profile", expanded=True):
    pollutants = sorted(df['pollutant_id'].unique().tolist())
    selected_pollutant = st.radio("Primary Pollutant", pollutants, horizontal=True)

with st.sidebar.expander("📅 Time Horizon", expanded=True):
    min_year = int(df['last_update'].dt.year.min())
    max_year = int(df['last_update'].dt.year.max())
    year_range = st.slider("Observation Range", min_year, max_year, (min_year, max_year))
    
    st.markdown("**Quick Select:**")
    q_col1, q_col2 = st.columns(2)
    if q_col1.button("Last 5 Years"): year_range = (max_year - 5, max_year)
    if q_col2.button("Full History"): year_range = (min_year, max_year)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset System Filters", use_container_width=True):
    st.rerun()

# --- Filtering Logic ---
if compare_mode and selected_cities:
    filtered_df = df[(df['city'].isin(selected_cities)) & (df['pollutant_id'] == selected_pollutant)]
else:
    filtered_df = filter_data(df, selected_state, selected_cities[0] if selected_cities else "All", selected_pollutant, year_range)

# --- Dynamic Header ---
title_col, time_col = st.columns([3, 1])
with title_col:
    st.title("🛰️ वायुसूत्र")
    
    # Viewing Badge
    curr_loc = selected_cities[0] if (selected_cities and not compare_mode) else "India (Comparative)" if compare_mode else "All India"
    st.markdown(f'<div class="viewing-badge">📡 EXPLORING: {curr_loc.upper()}</div>', unsafe_allow_html=True)
    
    # Dynamic Summary Line
    if not filtered_df.empty:
        avg_val = filtered_df['pollutant_avg'].mean()
        _, cat_name = get_aqi_color(avg_val)
        
        # Calculate growth for summary
        f_val = filtered_df.iloc[0]['pollutant_avg']
        l_val = filtered_df.iloc[-1]['pollutant_avg']
        growth = ((l_val - f_val) / f_val * 100) if f_val != 0 else 0
        trend_str = "stable" if abs(growth) < 2 else f"rising by {abs(growth):.1f}%" if growth > 0 else f"receding by {abs(growth):.1f}%"
        
        st.markdown(f"##### Local data confirms the atmosphere is **{cat_name.upper()}**, with levels appearing **{trend_str}** across this horizon.")
    else:
        st.markdown("##### Mapping atmospheric signals across the Indian subcontinent.")

with time_col:
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption(f"🕒 **System Sync**\n{pd.Timestamp.now().strftime('%d %b %Y, %H:%M')}")


# --- Row 1: Metrics ---
metrics = get_metrics(filtered_df)
hero_color, hero_cat = get_aqi_color(metrics['avg'])

m1, m2, m3, m4 = st.columns([1.5, 1, 1, 1])

with m1:
    st.markdown(f"""
        <div class="metric-card hero-card">
            <div class="metric-label">Air Quality Index</div>
            <div class="metric-value">{metrics['avg']:.1f}</div>
            <div class="metric-category" style="background-color: {hero_color}22; color: {hero_color};">
                {hero_cat}
            </div>
        </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Lowest Recorded</div>
            <div class="metric-value" style="font-size: 1.8rem; font-family: 'Sora', sans-serif;">{metrics['min']:.1f}</div>
            <div style="color: #4CAF50; font-size: 0.8rem; font-weight: 500;">Satisfactory Minimum</div>
        </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Peak Pollution</div>
            <div class="metric-value" style="font-size: 1.8rem; font-family: 'Sora', sans-serif;">{metrics['max']:.1f}</div>
            <div style="color: #E76F51; font-size: 0.8rem; font-weight: 500;">Critical Maximum</div>
        </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Observations</div>
            <div class="metric-value" style="font-size: 1.8rem; font-family: 'Sora', sans-serif;">{metrics['count']:,}</div>
            <div style="color: var(--text-secondary); font-size: 0.8rem; font-weight: 500;">Data Sync Points</div>
        </div>
    """, unsafe_allow_html=True)

# --- Health Advisory ---
h_msg, h_color = get_health_advisory(metrics['avg'])
st.markdown(f"""
    <div class="health-banner" style="background-color: {h_color}10; border-color: {h_color};">
        <div style="font-size: 2rem;">{'✅' if h_color == 'green' else '⚠️' if h_color == 'yellow' else '❗'}</div>
        <div>
            <div style="color: {h_color}; font-weight: 800; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em;">Health Advisory</div>
            <div style="font-size: 1.1rem; font-weight: 500;">{h_msg}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Row 2: Charts & AI Insights ---
st.markdown("<br>", unsafe_allow_html=True)
chart_col, insight_col = st.columns([2.3, 1])

with chart_col:
    if compare_mode and len(selected_cities) > 1:
        # Comparison Chart
        fig = px.line(filtered_df.sort_values('last_update'), x='last_update', y='pollutant_avg', color='city',
                     title="Multi-City Comparative Analysis", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        ts_fig = plot_time_series(filtered_df, selected_pollutant)
        if ts_fig:
            st.plotly_chart(ts_fig, use_container_width=True, theme=None)

with insight_col:
    st.subheader("🧠 Insights Engine")
    
    # Intelligence Features
    if not filtered_df.empty:
        with st.expander("📖 Data Storyteller", expanded=False):
            st.markdown(f"""
                <div style="background-color: rgba(58, 174, 216, 0.05); padding: 18px; border-radius: 10px; border: 1px solid var(--border); line-height: 1.7; font-size: 0.95rem;">
                    {get_data_explanation(filtered_df, curr_loc, selected_pollutant)}
                </div>
            """, unsafe_allow_html=True)
            
    if selected_cities and selected_pollutant:
        forecast_data, _ = generate_forecast(filtered_df)
        if forecast_data:
            insights = generate_insights(forecast_data)
            for ins in insights[:3]: # Limit to 3 most important
                st.markdown(f"""
                    <div class="insight-card">
                        <div style="color: #38bdf8; font-size: 0.75rem; font-weight: 800; margin-bottom: 6px; letter-spacing: 0.05em;">AI SIGNAL</div>
                        <div style="font-size: 0.95rem; line-height: 1.4;">{ins}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("Awaiting more granular data...")
    else:
        st.info("Select specific targets for AI analysis.")

# --- Row 3: Map ---
st.markdown("---")
st.subheader("📍 National Air Quality Grid")
map_fig = plot_map(filtered_df)
if map_fig:
    st.plotly_chart(map_fig, use_container_width=True)

# --- 🔮 Predictive Section ---
st.markdown("---")
if selected_cities and not compare_mode:
    st.header("🔮 Strategic Forecasting (2025-2030)")
    
    # Integrated Prediction Module Preview
    p1, p2 = st.columns([1, 2])
    with p1:
        forecast_data, _ = generate_forecast(filtered_df, periods=30) # Short term preview
        if forecast_data:
            next_val = forecast_data['forecast']['yhat'].iloc[-1]
            st.markdown(f"""
                <div class="metric-card" style="border-top: 5px solid #f472b6;">
                    <div class="metric-label">Predicted Avg Next Month</div>
                    <div class="metric-value" style="color: #f472b6;">{next_val:.1f}</div>
                    <div style="font-size: 0.8rem; color: #9AA4B2;">Forecasted AI Output</div>
                </div>
            """, unsafe_allow_html=True)
            
    with p2:
        st.markdown("""
            <div style="background-color: #121821; padding: 20px; border-radius: 12px; border: 1px solid #1E2632;">
                <div style="color: #3AAED8; font-weight: 700; margin-bottom: 10px;">Prophet Mathematical Architecture</div>
                <div style="font-size: 0.9rem; color: #E6EDF3; line-height: 1.5;">
                    The system decomposes the atmospheric time series using an additive model:
                    <br><br>
                    <center><b>y(t) = g(t) + s(t) + h(t) + εₜ</b></center>
                    <br>
                    • <b>g(t)</b>: Growth (trend) changes over non-periodic shifts.<br>
                    • <b>s(t)</b>: Seasonality (yearly, weekly, daily) signals.<br>
                    • <b>h(t)</b>: Holiday/Event effects (e.g., Diwali spikes).<br>
                    • <b>εₜ</b>: Error term for idiosyncratic changes.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with st.spinner("Processing 5-year simulation..."):
        forecast_data, error = generate_forecast(filtered_df, periods=2000)
        if not error:
            forecast_fig = plot_forecast(forecast_data, selected_pollutant)
            st.plotly_chart(forecast_fig, use_container_width=True)
            
            # --- Pathways to Cleaner Skies Section ---
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("""
                <h2 style='font-family: Sora; letter-spacing: 0.05em;'>PATHWAYS TO CLEANER SKIES</h2>
                <p style='color: #9AA4B2; font-size: 1rem; margin-bottom: 30px;'>
                    Targeted interventions can bend the pollution curve. Focus efforts where the data shows the steepest rise.
                </p>
            """, unsafe_allow_html=True)
            
            path_cols = st.columns(3)
            
            with path_cols[0]:
                st.markdown("""
                    <div style="background-color: #121821; padding: 24px; border-radius: 14px; border: 1px solid #1E2632; height: 100%;">
                        <h4 style="color: #3AAED8; font-family: Sora; font-size: 1.1rem; margin-bottom: 15px;">URBAN EMISSION CONTROL</h4>
                        <p style="font-size: 0.9rem; color: #E6EDF3; margin-bottom: 15px;">
                            Deploy low-emission zones, modernise public transit fleets, and retrofit industrial stacks with continuous monitoring.
                        </p>
                        <ul style="font-size: 0.85rem; color: #9AA4B2; padding-left: 20px;">
                            <li>Enforce BS-VI vehicle compliance</li>
                            <li>Subsidise EV infrastructure</li>
                            <li>Mandate stack scrubbers for industries</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
                
            with path_cols[1]:
                st.markdown("""
                    <div style="background-color: #121821; padding: 24px; border-radius: 14px; border: 1px solid #1E2632; height: 100%;">
                        <h4 style="color: #3AAED8; font-family: Sora; font-size: 1.1rem; margin-bottom: 15px;">RURAL & AGRICULTURAL SHIFT</h4>
                        <p style="font-size: 0.9rem; color: #E6EDF3; margin-bottom: 15px;">
                            Support crop diversification and bio-residue management to end seasonal burning spikes in PM metrics.
                        </p>
                        <ul style="font-size: 0.85rem; color: #9AA4B2; padding-left: 20px;">
                            <li>Incentivise residue-to-energy projects</li>
                            <li>Promote precision irrigation and tilling</li>
                            <li>Deploy community biochar units</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
                
            with path_cols[2]:
                st.markdown("""
                    <div style="background-color: #121821; padding: 24px; border-radius: 14px; border: 1px solid #1E2632; height: 100%;">
                        <h4 style="color: #3AAED8; font-family: Sora; font-size: 1.1rem; margin-bottom: 15px;">DATA-LED GOVERNANCE</h4>
                        <p style="font-size: 0.9rem; color: #E6EDF3; margin-bottom: 15px;">
                            Share real-time dashboards with districts and engage citizens through alerts, indoor air guidance, and micro-mobility.
                        </p>
                        <ul style="font-size: 0.85rem; color: #9AA4B2; padding-left: 20px;">
                            <li>Publish open AQI dashboards</li>
                            <li>Integrate early warning alerts</li>
                            <li>Foster citizen sensor networks</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.caption("Built with ❤️ using Streamlit, Prophet, and Plotly. | India Air Quality Data v1.0")
