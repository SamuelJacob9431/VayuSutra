# 📡 वायुसूत्र (Vayusutra): Atmospheric Intelligence Dashboard

**वायुसूत्र (Vayusutra)** is a premium, production-level AI dashboard designed to monitor, analyze, and forecast air quality across the Indian subcontinent. Built with a focus on data storytelling and strategic decision-making, it transforms complex atmospheric signals into actionable insights for government officials, analysts, and the public.

---

## 🚀 Features

### 🔍 Real-Time Intelligence
- **National Monitoring Grid**: Interactive OpenStreetMap visualization of pollution hotspots.
- **Dynamic Data Storytelling**: Natural-language summaries of current air quality and trends.
- **Health Advisory System**: Semantic, color-coded health guidance based on live AQI levels.

### 🧠 AI-Powered Analytics
- **Prophet Strategic Forecasting**: Leverages Meta's Prophet architecture to simulate 1,800+ scenarios and project air quality trends through 2030.
- **Insights Engine**: Automated detection of seasonal variations, anomalies, and multi-year growth patterns.
- **Mathematical Transparency**: Full breakdown of the predictive model: `y(t) = g(t) + s(t) + h(t) + εₜ`.

### 🛡️ Strategic Policy Framework
- **Pathways to Cleaner Skies**: Curated intervention strategies across Urban Emission Control, Rural/Agricultural Shifts, and Data-Led Governance.
- **Comparative Analysis**: Benchmarking mode to compare atmospheric profiles across multiple cities simultaneously.

---

## 🛠️ Technology Stack

- **Frontend/Core**: [Streamlit](https://streamlit.io/) (Python-based interactive framework)
- **Forecasting Engine**: [Prophet](https://facebook.github.io/prophet/) (Meta's time-series forecasting library)
- **Visualizations**: [Plotly](https://plotly.com/) & [Mapbox](https://www.mapbox.com/)
- **Data Processing**: Pandas & NumPy
- **Typography**: Sora & Inter (Google Fonts)

---

## 📂 Project Structure

```text
india-visualising-data/
│
├── app.py              # Main dashboard entry point
├── augment_data.py     # Script for generating 25-year historical dataset
├── data/               # Processed atmospheric datasets
│   └── AIQ_India_cleaned_no_nh3.csv
│
├── modules/            # Modular backend logic
│   ├── data_loader.py  # Optimized data ingestion
│   ├── preprocessing.py# Filtering and metric calculation
│   ├── forecasting.py  # Prophet model implementation
│   ├── insights.py     # Rule-based and AI insight generation
│   └── visualization.py# Plotly/Mapbox chart definitions
│
└── requirements.txt    # Project dependencies
```

---

## 📥 Getting Started

### 1. Prerequisites
Ensure you have Python 3.9+ installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
streamlit run app.py
```
The dashboard will be available at `http://localhost:8501`.

---

## 🎨 Design Philosophy
**वायुसूत्र (Vayusutra)** is built on the **Atmospheric Blue & Horizon Orange** color system. It prioritizes clarity, visual hierarchy, and a "Human-AI Collaboration" feel, ensuring that data is not just seen, but understood.

---

## 📄 License
This project is for demonstration and research purposes. Data is augmented for long-term trend analysis.
