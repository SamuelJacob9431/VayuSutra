import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def get_aqi_color(value):
    # Reverting to premium blue/cyan status
    if value <= 100: return "#3AAED8", "Satisfactory"
    if value <= 200: return "#F4A261", "Impacted"
    return "#E76F51", "Critical"

def plot_time_series(df, pollutant_name):
    """
    Plots standard historical pollutant trends.
    """
    if df.empty:
        return None
    
    fig = px.line(
        df.sort_values('last_update'), 
        x='last_update', 
        y='pollutant_avg',
        title=f"Historical Trend: {pollutant_name}",
        template="plotly_dark"
    )
    fig.update_traces(line_color='#3AAED8')
    return fig

def plot_map(df):
    """
    Shows standard pollution hotspots using scatter markers.
    """
    if df.empty:
        return None
        
    fig = px.scatter_mapbox(
        df, 
        lat="latitude", 
        lon="longitude", 
        color="pollutant_avg",
        size="pollutant_avg",
        color_continuous_scale="Viridis",
        size_max=12, 
        zoom=3.8,
        mapbox_style="open-street-map",
        hover_name="city",
        title="National Monitoring Grid",
        template="plotly_dark"
    )
    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
    return fig

def plot_forecast(forecast_data, pollutant_name):
    """
    Plots actual data vs Prophet forecast.
    """
    forecast = forecast_data['forecast']
    actual = forecast_data['actual']
    
    fig = go.Figure()
    
    # Confidence Interval
    fig.add_trace(go.Scatter(
        x=forecast['ds'].tolist() + forecast['ds'].tolist()[::-1],
        y=forecast['yhat_upper'].tolist() + forecast['yhat_lower'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(56, 189, 248, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=False,
        name='Confidence Interval'
    ))
    
    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast['ds'], 
        y=forecast['yhat'],
        name='Forecast',
        line=dict(color='#38bdf8', width=3)
    ))
    
    # Actual
    fig.add_trace(go.Scatter(
        x=actual['ds'], 
        y=actual['y'],
        name='Actual',
        mode='markers',
        marker=dict(color='#f472b6', size=6)
    ))
    
    fig.update_layout(
        title=f"AI Long-Term Projection for {pollutant_name} (Until 2030)",
        template="plotly_dark",
        xaxis_title="Date",
        yaxis_title="Pollutant Level",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig
