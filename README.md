# haze
> *Weather data, observed.*

`haze` is an interactive, publication-grade weather analytics dashboard engineered for exploring historical weather observations across major meteorological observation stations.

Designed with an intentional publication-grade aesthetic—dark charcoal canvas, muted grey typography, desaturated slate accents, glassmorphic card containers, and micro-animations—`haze` prioritizes analytical clarity, statistical correctness, and high-performance processing.

---

## 1. Key Highlights & Performance

- **Scale**: Analyzes a dataset of **1,000,000 records** locally without lag.
- **Memory Footprint**: Optimized from over 72 MB down to **23.8 MB** in memory via categorized strings and single-precision `float32` representations.
- **Loading Speed**: Loads, validates, and parses 1M rows in **~1.1 seconds** with `@st.cache_data`.
- **Responsive Architecture**: Tabbed technical navigation with decoupled statistical math and GPU-accelerated Plotly visualizations.
- **Biometeorological Modeling**: Computes NOAA Rothfusz Apparent Temperature (Heat Index) combining ambient thermal readings and relative humidity.
- **Unsupervised Anomaly Detection**: Employs standardized Z-score filtering ($|Z| \ge 2.0$) to isolate extreme weather anomalies.
- **Parametric & Non-Parametric Metrics**: Seamless toggle between Arithmetic Means and Robust Percentiles (P10, P25, Median/P50, P75, P90).

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
  - `Temperature_C` (Ambient dry-bulb temperature in °C)
  - `Humidity_pct` (Relative humidity percentage in %)
  - `Precipitation_mm` (Instantaneous precipitation gauge measurement in mm)
  - `Wind_Speed_kmh` (Wind velocity in km/h)
  - `Heat_Index_C` (Engineered NOAA Apparent Temperature in °C)
- **Data Quality**: 0 missing values, 0 duplicate rows.

---

## 3. Architecture & Directory Structure

```
haze/
├── .streamlit/
│   └── config.toml         # Custom dark theme and server settings
├── app.py                  # Streamlit dashboard layout, views, and interactivity
├── requirements.txt        # Python dependencies
├── README.md               # Architecture, execution guide, and analytical methods
├── PRESENTATION_NOTES.md   # Viva examination prep, viva Q&A, and detailed notes
├── data/
│   └── weather_data.csv    # Extracted weather dataset (1M rows)
└── utils/
    └── analysis.py         # Vectorized loading, caching, aggregations, and insights
```

---

## 4. Analytical Findings & Data Semantics

1. **Precipitation Semantics**:
   - Every single observation in the dataset contains a positive precipitation reading (0% zero-value records) sampled across seconds-level intervals.
   - Naively summing the column yields ~500,000 mm of rain, which is physically impossible.
   - **Conclusion**: The column represents instantaneous gauge readings / observation rates. The dashboard computes mean rate (`5.11 mm/obs`) and daily average rate rather than an unweighted cumulative sum.

2. **The Phoenix Anomaly**:
   - 9 stations show temperature bounded tightly within `[-10.0°C, 40.0°C]`.
   - **Phoenix** exhibits an extended negative lower bound down to `-19.97°C` (mean `12.79°C` vs `~15.02°C` elsewhere), making it the coldest station by average temperature in this archive.
   - Phoenix also shows higher mean precipitation (`6.09 mm/obs` vs `~5.00 mm/obs` elsewhere) and higher peak precipitation (`14.97 mm` vs `9.99 mm`).

3. **Variable Orthogonality**:
   - The Pearson correlation coefficient between temperature and humidity is $r \approx -0.0013$ (virtually zero).
   - Cross-variable correlations between all numerical pairs remain bounded within $[-0.01, +0.01]$, demonstrating statistical independence.

---

## 5. Dashboard Sections & Interactive Tabs

1. **Header & Archive Metadata**: Displays archive scope, active record count, and station coverage.
2. **Filter Controls**: Multi-station selector with quick actions ("Select All", "Reset Filters"), interval date picker, variable selector, aggregation resolution slider, and KPI mode switcher.
3. **Animated Metric Cards**: Four micro-animated cards displaying Average Temperature / Median (P50), Humidity, Precipitation Rate, and Wind Speed with contextual subtext.
4. **Tab 01 // Overview & Dynamics**:
   - Time-series evolution chart with min-max confidence envelope.
   - Station ranking bar chart and frequency distribution histogram (dynamically responsive to the selected primary variable).
   - Bivariate scatter plot and cross-variable correlation heatmap.
   - Dynamic data-backed observations cards.
5. **Tab 02 // Station Head-to-Head**:
   - Comparative analytics between any two chosen stations with delta metrics ($\Delta$ Mean, $\Delta$ Range, Std Deviation spread) and an overlapping distribution histogram.
6. **Tab 03 // Diurnal Cycles & Heat Index**:
   - 24-hour diurnal cycle curve (hours 00 to 23) with standard deviation bounds.
   - NOAA Rothfusz Apparent Temperature Index modeling.
7. **Tab 04 // Anomaly Detection**:
   - Standardized Z-Score ($|Z| \ge \text{threshold}$) outlier identification isolating Phoenix sub-zero freezes and peak wind speed events.
8. **Tab 05 // Data Explorer & Export**:
   - Paginated tabular preview with column toggling and filtered CSV export.

---

## 6. Installation and Execution

```bash
# Clone or navigate to the repository
cd d:/projects/haze

# Install required dependencies
pip install -r requirements.txt

# Run the Streamlit dashboard
streamlit run app.py
```

Open your browser at `http://localhost:8501`.
