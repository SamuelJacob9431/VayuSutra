import pandas as pd
import streamlit as st

@st.cache_data
def load_data(file_path):
    """
    Loads the air quality dataset, cleans column names, and handles basic preprocessing.
    """
    try:
        df = pd.read_csv(file_path)
        
        # Clean column names (strip whitespace)
        df.columns = df.columns.str.strip()
        
        # Convert date to datetime
        if 'last_update' in df.columns:
            df['last_update'] = pd.to_datetime(df['last_update'], format='%d-%m-%Y %H:%M', errors='coerce')
            # Drop rows where date conversion failed
            df = df.dropna(subset=['last_update'])
            
        # Ensure numeric columns are actually numeric
        numeric_cols = ['pollutant_avg', 'pollutant_min', 'pollutant_max', 'latitude', 'longitude']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()
