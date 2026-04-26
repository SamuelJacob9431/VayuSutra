def generate_insights(forecast_data):
    """
    Generates dynamic insights based on forecast trends.
    """
    forecast = forecast_data['forecast']
    actual = forecast_data['actual']
    
    insights = []
    
    # 1. Trend detection
    recent_yhat = forecast['yhat'].iloc[-30:].mean()
    start_yhat = forecast['yhat'].iloc[0:30].mean()
    
    if recent_yhat > start_yhat * 1.05:
        insights.append("📈 <b>Increasing Trend</b>: The AI predicts a significant rise in pollution levels over the next year.")
    elif recent_yhat < start_yhat * 0.95:
        insights.append("📉 <b>Improving Trend</b>: Good news! Pollution levels are projected to gradually decrease.")
    else:
        insights.append("➡️ <b>Stable Projection</b>: Pollution levels are expected to remain consistent with current trends.")

    # 2. Seasonality
    if 'yearly' in forecast.columns:
        yearly_max = forecast['yearly'].max()
        if yearly_max > forecast['yhat'].mean() * 0.1:
            insights.append("📅 <b>Seasonal Variation</b>: Strong seasonal patterns detected. Expect spikes during specific months.")

    # 3. Peak Detection
    max_val = forecast['yhat'].max()
    insights.append(f"⚠️ <b>Peak Alert</b>: The maximum projected level for this pollutant is {max_val:.1f} units.")
    
    return insights

def generate_recommendations(insights):
    """
    Provides actionable suggestions based on detected insights.
    """
    recs = []
    
    trend_text = " ".join(insights)
    
    if "Increasing Trend" in trend_text:
        recs.append("🔴 <b>Urgent Action</b>: Implement stricter emission controls and promote public transport immediately.")
    
    if "Seasonal Variation" in trend_text:
        recs.append("🟠 <b>Preventive Measure</b>: Issue health advisories during peak seasons and limit outdoor activities.")
    
    if "Improving Trend" not in trend_text:
        recs.append("🔵 <b>Infrastructure</b>: Invest in more IoT sensors for hyperlocal monitoring in hotspots.")
    else:
        recs.append("🟢 <b>Maintenance</b>: Continue existing green initiatives to sustain the downward trend.")
        
    return recs

def get_data_explanation(df, city, pollutant):
    """
    Generates a human-friendly explanation of the current data state.
    """
    if df.empty:
        return "No data available for the current selection."
    
    avg = df['pollutant_avg'].mean()
    count = len(df)
    
    # Simple trend logic
    first_val = df.iloc[0]['pollutant_avg']
    last_val = df.iloc[-1]['pollutant_avg']
    diff = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0
    
    trend_desc = "has increased" if diff > 0 else "has decreased"
    
    explanation = (
        f"This dataset for <b>{city}</b> shows <b>{count} records</b> of <b>{pollutant}</b> levels. "
        f"The average concentration is <b>{avg:.1f}</b>, which {trend_desc} by <b>{abs(diff):.1f}%</b> "
        f"over the observed period. The AI has analyzed these patterns to predict future outcomes."
    )
    return explanation

def get_health_advisory(aqi_value):
    """
    Returns health impact messages based on AQI level.
    """
    if aqi_value <= 50:
        return "✅ <b>Good</b>: Air quality is satisfactory, and air pollution poses little or no risk.", "green"
    if aqi_value <= 100:
        return "⚠️ <b>Moderate</b>: Air quality is acceptable; however, there may be a risk for some people who are unusually sensitive.", "yellow"
    if aqi_value <= 200:
        return "🟠 <b>Unhealthy</b>: Members of sensitive groups may experience health effects. The general public is less likely to be affected.", "orange"
    if aqi_value <= 300:
        return "🔴 <b>Very Unhealthy</b>: Health alert: The risk of health effects is increased for everyone.", "red"
    return "☠️ <b>Hazardous</b>: Health warnings of emergency conditions. The entire population is more likely to be affected.", "purple"
