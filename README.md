# haze
> *Weather data, observed.*

`haze` is a minimal, editorial, technical weather analytics dashboard engineered for exploring historical weather observations across major meteorological observation stations.

Designed with an intentional publication-grade aesthetic—dark charcoal canvas, muted grey typography, desaturated slate accents, and generous whitespace—`haze` prioritizes analytical clarity, statistical correctness, and high-performance processing over generic templates.

---

## 1. Key Highlights & Performance

- **Scale**: Analyzes a dataset of **1,000,000 records** without lag.
- **Memory Footprint**: Optimized from over 72 MB down to **23.8 MB** in memory via categorized strings and single-precision `float32` representations.
- **Loading Speed**: Loads, validates, and parses 1M rows in **~1.1 seconds** with `@st.cache_data`.
- **Render Responsiveness**: Decouples full-dataset statistical calculations (e.g. Pearson $r$ across 100% of records) from visual rendering (stratified sampling for WebGL/SVG scatter plots).
- **Analytical Rigor**: Accurately addresses precipitation semantics, distinguishing instantaneous gauge observations from cumulative rainfall sums.

---

## 2. Dataset Overview

- **Source File**: `data/weather_data.csv`
- **Total Records**: 1,000,000 observations
- **Temporal Coverage**: January 01, 2024 `00:00:06` to May 18, 2024 `19:44:10` (~138.8 days)
- **Stations (10 Locations)**:
  - Chicago, Dallas, Houston, Los Angeles, New York, Philadelphia, Phoenix, San Antonio, San Diego, San Jose (~100,000 records each)
- **Variables**:
  - `Location` (Categorical station identifier)
  - `Date_Time` (Timestamp at irregular high-frequency intervals)
  - `Temperature_C` (Ambient temperature in °C)
  - `Humidity_pct` (Relative humidity percentage in %)
  - `Precipitation_mm` (Instantaneous precipitation gauge measurement in mm)
  - `Wind_Speed_kmh` (Wind velocity in km/h)
- **Data Quality**: 0 missing values, 0 duplicate rows.

---

## 3. Architecture & Directory Structure

```
haze/
├── .streamlit/
│   └── config.toml         # Custom dark theme and server settings
├── app.py                  # Streamlit dashboard layout, views, and interactivity
├── requirements.txt        # Minimal Python dependencies
├── README.md               # Architecture, execution guide, and analytical methods
├── PRESENTATION_NOTES.md   # Viva examination prep, viva Q&A, and detailed notes
├── data/
│   └── weather_data.csv    # Extracted weather dataset (1M rows)
└── utils/
    └── analysis.py         # Vectorized loading, caching, aggregations, and insights
```

### Module Responsibilities

- **`app.py`**:
  - Encapsulates Streamlit interface, sidebar filter bindings, metric card layout, Plotly visual orchestration, and user session management.
- **`utils/analysis.py`**:
  - Encapsulates core data engineering: schema validation, optimized type coercion, dynamic temporal aggregation (`Daily`, `Weekly`, `Monthly`), correlation calculation, and automated analytical insight derivation.

---

## 4. Analytical Findings & Data Semantics

1. **Precipitation Semantics**:
   - Every single observation in the dataset contains a positive precipitation reading (0% zero-value records), with records logged at irregular seconds-level intervals.
   - A naive sum of the `Precipitation_mm` column yields ~500,000 mm (~500 meters of water), which is physically impossible.
   - **Conclusion**: The column represents instantaneous gauge readings / observation rates. The dashboard computes mean rate (`5.11 mm/obs`) and daily average rate rather than an unweighted cumulative sum.

2. **The Phoenix Anomaly**:
   - 9 stations show temperature bounded tightly within `[-10.0°C, 40.0°C]`.
   - **Phoenix** exhibits an extended negative lower bound down to `-19.97°C` (mean `12.79°C` vs `~15.02°C` elsewhere), making it the coldest station by average temperature in this archive.
   - Phoenix also shows higher mean precipitation (`6.09 mm/obs` vs `~5.00 mm/obs` elsewhere) and higher peak precipitation (`14.97 mm` vs `9.99 mm`).

3. **Variable Orthogonality**:
   - The Pearson correlation coefficient between temperature and humidity is $r \approx -0.0013$ (virtually zero).
   - Cross-variable correlations between all numerical pairs remain bounded within $[-0.01, +0.01]$, demonstrating statistical independence.

---

## 5. Installation and Execution

### Prerequisites
- Python 3.9+ (Python 3.11 recommended)

### Setup

```bash
# Clone or navigate to the repository
cd d:/projects/haze

# Install required dependencies
pip install -r requirements.txt

# Run the Streamlit dashboard
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 6. Dashboard Sections

1. **Header & Archive Metadata**: Displays archive scope, active record count, and station coverage.
2. **Filter Controls**: Multi-location selector with quick actions ("Select All", "Reset Filters"), interval date picker, variable selector, and aggregation resolution slider.
3. **Summary Metric Cards**: Four compact KPIs (Average Temperature, Average Humidity, Precipitation Rate, Average Wind Speed) with min/max and contextual subtext.
4. **Temporal Evolution**: Interactive line chart showing the progression of any selected weather parameter with min-max confidence bands and optional station disaggregation.
5. **Location Comparison**: Horizontal bar chart ranking stations by average parameter values.
6. **Temperature Distribution**: Histogram with mean and median reference lines.
7. **Bivariate Scatter & Correlation Matrix**: Scatter plot with rendered sample and full-population correlation coefficient, paired with a Pearson correlation heatmap.
8. **Precipitation Analysis**: Station comparison of mean gauge rates and temporal trends, accompanied by an analytical methodology note.
9. **Observations (`observations`)**: Dynamically generated, data-grounded insights citing exact values, locations, and timestamps.
10. **Data Explorer**: Paginated tabular preview with column toggling and filtered CSV export.
