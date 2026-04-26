import pandas as pd
from prophet import Prophet
import streamlit as st

def generate_forecast(df, periods=365):
    """
    Trains a Prophet model on the provided data and generates future predictions.
    """
    if len(df) < 2:
        return None, "Insufficient data for forecasting (need at least 2 data points)."

    try:
        # Prepare data for Prophet
        prophet_df = df[['last_update', 'pollutant_avg']].rename(
            columns={'last_update': 'ds', 'pollutant_avg': 'y'}
        )
        
        # Aggregate by date if multiple stations exist
        prophet_df = prophet_df.groupby('ds').mean().reset_index()
        
        if len(prophet_df) < 2:
            return None, "Data points collapse into a single date. Need more historical spread."

        # Initialize and fit model
        m = Prophet(yearly_seasonality=True, daily_seasonality=False, weekly_seasonality=True)
        m.fit(prophet_df)
        
        # Make future dataframe
        future = m.make_future_dataframe(periods=periods)
        forecast = m.predict(future)
        
        return {
            "forecast": forecast,
            "model": m,
            "actual": prophet_df
        }, None
    except Exception as e:
        return None, f"Forecasting Error: {str(e)}"
