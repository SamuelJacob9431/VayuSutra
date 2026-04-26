import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def augment_data(input_file, output_file):
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file)
    df['last_update'] = pd.to_datetime(df['last_update'], format='%d-%m-%Y %H:%M', errors='coerce')
    
    all_data = []
    
    # Identify unique city-pollutant combinations to avoid exploding the file size
    unique_combos = df.drop_duplicates(subset=['city', 'pollutant_id'])
    print(f"Found {len(unique_combos)} unique City-Pollutant pairs.")
    
    for _, row in unique_combos.iterrows():
        base_val = row['pollutant_avg']
        if pd.isna(base_val): continue
        
        # Generate points over 25 years (2000 to 2025)
        # 100 points per combo to ensure dense enough coverage for 25 years
        for i in range(150):
            # Random date between 1-Jan-2000 and 19-May-2025
            total_days = (datetime(2025, 5, 19) - datetime(2000, 1, 1)).days
            days_back = np.random.randint(0, total_days)
            date = datetime(2025, 5, 19) - timedelta(days=days_back)
            
            # Add long-term trend (0.5% growth per year)
            years_from_start = (date - datetime(2000, 1, 1)).days / 365
            trend_factor = 1.0 + (years_from_start * 0.02) # 2% annual increase
            
            # Add seasonality (higher in Nov-Jan for India)
            month = date.month
            season_factor = 1.4 if month in [11, 12, 1] else 0.8 if month in [6, 7, 8] else 1.0
            
            # Add noise
            noise = np.random.normal(0, base_val * 0.15)
            new_avg = (base_val * trend_factor * season_factor) + noise
            
            all_data.append({
                'country': 'India',
                'state': row['state'],
                'city': row['city'],
                'station': row['station'],
                'last_update': date.strftime('%d-%m-%Y %H:%M'),
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'pollutant_id': row['pollutant_id'],
                'pollutant_avg': max(0, new_avg),
                'pollutant_min': max(0, new_avg * 0.8),
                'pollutant_max': new_avg * 1.2
            })
            
    augmented_df = pd.DataFrame(all_data)
    augmented_df.to_csv(output_file, index=False)
    print(f"Successfully augmented data. New size: {len(augmented_df)} records.")

if __name__ == "__main__":
    augment_data('data/AIQ_India_cleaned_no_nh3.csv', 'data/AIQ_India_cleaned_no_nh3.csv')
