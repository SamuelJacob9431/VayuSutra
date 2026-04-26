import pandas as pd

def filter_data(df, state=None, city=None, pollutant=None, year_range=None):
    """
    Filters the dataframe based on user selections.
    """
    filtered_df = df.copy()
    
    if state and state != "All":
        filtered_df = filtered_df[filtered_df['state'] == state]
        
    if city and city != "All":
        filtered_df = filtered_df[filtered_df['city'] == city]
        
    if pollutant and pollutant != "All":
        filtered_df = filtered_df[filtered_df['pollutant_id'] == pollutant]
        
    if year_range:
        filtered_df = filtered_df[
            (filtered_df['last_update'].dt.year >= year_range[0]) & 
            (filtered_df['last_update'].dt.year <= year_range[1])
        ]
        
    return filtered_df

def get_metrics(df):
    """
    Calculates summary metrics for the filtered data.
    """
    if df.empty:
        return {"avg": 0, "min": 0, "max": 0, "count": 0}
        
    return {
        "avg": df['pollutant_avg'].mean(),
        "min": df['pollutant_min'].min(),
        "max": df['pollutant_max'].max(),
        "count": len(df)
    }
