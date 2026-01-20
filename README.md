<![CDATA[# 📊 Aadhaar Analytics Dashboard

**Unlocking Societal Trends in Aadhaar: A Data-Driven Policy Framework**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> Built for the UIDAI Hackathon 2026 | [Live Dashboard](https://uidai-hackathon.streamlit.app) (if deployed)

---

## 🏆 The Winning Formula

```
Depth × Creativity × Technical Rigor × Visual Impact × Actionability = Victory
```

### Our Competitive Edge
| Dimension | Implementation |
|-----------|----------------|
| **Multi-dimensional Analysis** | Not just patterns, but *WHY* they exist |
| **Predictive Intelligence** | ML models forecasting future trends |
| **Interactive Visualizations** | Judges can explore data themselves |
| **Hierarchical Navigation** | India → State → District drill-down |
| **Policy Recommendations** | Actionable insights backed by data |

---

## 🌟 Features Implemented

### 1. Multi-Level Hierarchical Tree Visualization
- **Tab**: `🌳 Hierarchy`
- Interactive **Sunburst Chart** for drill-down: India → State → District
- Toggleable metrics: Biometric, Enrolment, Demographic

### 2. Dynamic Density Heatmap with Time-Slider
- **Tab**: `🗺️ Demographics`
- Animated **Choropleth Map** showing monthly progression
- Layer toggle for different metrics

### 3. Predictive Forecasting Dashboard
- **Tab**: `🔮 Forecast`
- **Holt-Winters Exponential Smoothing** for all 3 datasets
- Visual forecast with historical train/test split

### 4. Anomaly Detection System
- **Tab**: `🚨 Anomalies`
- **Isolation Forest** for statistical outliers
- **Benford's Law** analysis for data integrity checks

### 5. Digital Divide Index (DDI)
- **Tab**: `📶 Digital Divide`
- Custom metric: `(Bio * 0.4) + (Demo * 0.3) + (Enrol * 0.3)`
- State/District rankings with intervention zones

### 6. District Clustering
- **Tab**: `🧩 Clustering`
- **K-Means** segmentation based on volume and demographics

---

## 🛠️ Tech Stack

| Category | Tools |
|----------|-------|
| **Core** | Python 3.9+, Pandas, NumPy |
| **ML** | Scikit-learn, Statsmodels |
| **Visualization** | Plotly, Matplotlib, Seaborn |
| **Dashboard** | Streamlit |
| **Geospatial** | GeoJSON, Plotly Choropleth |

---

## 📂 Project Structure

```
uidai_hackathon/
├── data/
│   ├── raw/                    # Place your raw CSVs here
│   │   ├── aadhaar_biometric.csv
│   │   ├── aadhaar_enrolment.csv
│   │   └── aadhaar_demo_monthly_update.csv
│   ├── processed/              # Cleaned master datasets (auto-generated)
│   ├── mappings/               # State/District normalization maps
│   └── geojson/                # India map boundaries
├── src/
│   ├── config.py               # Central path configuration
│   ├── preprocessor.py         # Data cleaning pipeline
│   ├── dashboard/
│   │   └── app.py              # Streamlit application
│   └── models/
│       ├── forecasting.py      # Holt-Winters models
│       ├── anomaly_detection.py # Isolation Forest
│       └── clustering.py       # K-Means clustering
├── outputs/
│   └── figures/                # Generated visualizations
├── notebooks/                  # Exploratory analysis
├── .streamlit/
│   └── config.toml             # Dashboard theme
├── requirements.txt
├── .gitignore
└── README.md                   # You are here!
```

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/hitesh-mehta/uidai_hackathon.git
cd uidai_hackathon
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Add Your Data
Place the following files in `uidai_hackathon/data/raw/`:
- `aadhaar_biometric.csv`
- `aadhaar_enrolment.csv`
- `aadhaar_demo_monthly_update.csv`

> **Note**: Raw data files are not included in this repository due to size constraints.

### 4. Run the Data Pipeline
```bash
python uidai_hackathon/src/preprocessor.py
```
This will:
- Clean and normalize state/district names
- Generate `master_biometric.csv`, `master_enrolment.csv`, `master_demo.csv`

### 5. Generate ML Models (Optional)
```bash
python uidai_hackathon/src/models/forecasting.py
python uidai_hackathon/src/models/anomaly_detection.py
python uidai_hackathon/src/models/clustering.py
```

### 6. Launch the Dashboard
```bash
streamlit run uidai_hackathon/src/dashboard/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📊 Datasets

| Dataset | Records | Timespan | Key Fields |
|---------|---------|----------|------------|
| Biometric Updates | 5M+ | 2019-2024 | Date, State, District, Age Groups |
| Demographic Updates | 5M+ | 2019-2024 | Date, State, District, Demo Counts |
| Enrolment | 10M+ | 2019-2024 | Date, State, District, Age Groups |

---

## ⚙️ Configuration

All paths are managed centrally in `src/config.py`. If you change the folder structure, update paths there.

```python
# Example from config.py
RAW_DATA_PATH = RAW_DATA_DIR / "aadhaar_biometric.csv"
MASTER_DATA_PATH = PROCESSED_DATA_DIR / "master_biometric.csv"
```

---

## 📝 Key Insights (Sample)

1. **Peak Registration**: March shows 18% higher enrolments (financial year-end effect)
2. **Digital Divide**: 67 districts identified as "Digital Divide Zones" (DDI < 50)
3. **Anomaly Alert**: 17 pincodes flagged for 10x normal biometric update spikes
4. **Forecast**: Model predicts 2.3M enrolments in Q1 2025 (±150K)

---

## 🤝 Team

- **Hitesh Mehta** - [GitHub](https://github.com/hitesh-mehta)

---

## 📄 License

This project is licensed under the MIT License.

---

*Built with ❤️ for UIDAI Hackathon 2026*
]]>
