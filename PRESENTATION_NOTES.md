# HAZE — College Presentation Notes & Viva Preparation Guide

This document prepares you for your technical defense, presentation, and viva examination for **haze**. It provides theoretical foundations, architectural diagrams, empirical findings, and 16 likely technical viva questions with concise, technically correct answers.

---

## 1. Problem Statement

Modern environmental monitoring networks record massive streams of high-frequency weather observations. Standard analytics templates often suffer from:
1. **Semantic Misinterpretations**: Erroneously summing high-frequency instantaneous sensor gauge measurements as cumulative rainfall totals.
2. **Client-Side Rendering Freezes**: Attempting to inject millions of raw SVG/DOM points into web browsers.
3. **Superficial Feature Sets**: Plotting basic raw columns without applying biometeorological domain logic (e.g., apparent temperature) or diurnal periodicity.
4. **Poor Visual Hierarchy**: Relying on excessive decorative cards and generic icons instead of clean, publication-grade typography and glassmorphic micro-animations.

**HAZE** overcomes these issues by providing a minimal, editorial, technical analytics dashboard engineered for mathematical rigor, optimized memory utilization, and transparent communication of statistical realities.

---

## 2. Project Objectives

1. **Scalable Local Execution**: Process and explore 1,000,000 weather observations locally in pure Python without an external database or heavy JavaScript framework.
2. **Editorial Aesthetic & Micro-Interactions**: Implement a dark charcoal aesthetic (`#0d1017`) featuring `Inter` typography, `JetBrains Mono` numerals, glassmorphic card containers, and smooth hover micro-animations.
3. **Domain-Specific Biometeorology**: Implement the NOAA Rothfusz regression algorithm to compute human thermal comfort (Apparent Heat Index) from dry-bulb temperature and relative humidity.
4. **Multi-Faceted Analysis**: Provide five dedicated analytical perspectives:
   - *Overview & Dynamics* (temporal progression, distributions, correlations).
   - *Station Head-to-Head* (comparative delta stats and overlapping distribution histograms).
   - *Diurnal Cycles & Heat Index* (24-hour hour-of-day cycles).
   - *Anomaly Detection* (unsupervised Z-score outlier detection).
   - *Data Explorer & Export* (paginated tabular inspection and CSV export).

---

## 3. Dataset Characteristics

- **Source File**: `data/weather_data.csv` (1,000,000 rows, 6 columns, 99.28 MB)
- **Temporal Span**: January 01, 2024 `00:00:06` to May 18, 2024 `19:44:10` (~138.8 days)
- **Monitoring Stations (10)**: Chicago, Dallas, Houston, Los Angeles, New York, Philadelphia, Phoenix, San Antonio, San Diego, San Jose (~100,000 records each)
- **Data Quality**: 0 missing values, 0 duplicate rows, 0 null timestamps.
- **Variables**:
  - `Location`: Categorical station identifier.
  - `Date_Time`: High-frequency irregular timestamps.
  - `Temperature_C`: Ambient dry-bulb temperature in °C.
  - `Humidity_pct`: Relative humidity in %.
  - `Precipitation_mm`: Instantaneous gauge reading in mm.
  - `Wind_Speed_kmh`: Wind speed in km/h.
  - `Heat_Index_C`: Engineered NOAA Rothfusz apparent temperature in °C.

---

## 4. Technical Stack & Rationale

| Technology | Purpose & Rationale |
| :--- | :--- |
| **Python 3.11** | High-performance execution, strong typing, and rich data science ecosystem. |
| **Streamlit** | Pure-Python reactive framework. Built-in session state and `@st.cache_data` eliminate REST API overhead. |
| **Pandas** | High-speed tabular operations with optimized dtypes (`category`, `float32`) reducing memory footprint from 72.1 MB to 23.8 MB (67% reduction). |
| **NumPy** | Vectorized array mathematical operations for instantaneous Heat Index and Z-score calculations across 1,000,000 rows in milliseconds. |
| **Plotly** | GPU-accelerated interactive charts with custom dark editorial layouts and tooltips. |

---

## 5. Architectural Data Flow

```
+-----------------------------------------------------------+
|                   Browser Client View                     |
|  - 5 Tabbed Panes (Overview, H2H, Diurnal, Anomalies, Data)|
|  - Metric Cards with Micro-Animations & Percentile Toggle  |
+-----------------------------------------------------------+
                           |   ^
        Sidebar Parameters |   | Rendered Plotly / HTML
                           v   |
+-----------------------------------------------------------+
|                          app.py                           |
|  - Streamlit Session State & Reactive Filters             |
|  - Editorial Layout Orchestration & Custom CSS            |
+-----------------------------------------------------------+
                           |   ^
        Computation Demand |   | Aggregated Data & Metrics
                           v   |
+-----------------------------------------------------------+
|                    utils/analysis.py                      |
|  - load_dataset(): Vectorized Heat Index computation      |
|  - filter_data(): Vectorized Boolean masking              |
|  - aggregate_diurnal_cycle(): 24h hourly cycle            |
|  - get_head_to_head_comparison(): Delta metrics & overlay |
|  - detect_anomalies(): Standardized Z-Score calculation   |
|  - calculate_correlation_matrix(): Full-data Pearson r    |
+-----------------------------------------------------------+
                           |   ^
          Disk Read (Once) |   | Parsed In-Memory DataFrame
                           v   |
+-----------------------------------------------------------+
|                 data/weather_data.csv                     |
+-----------------------------------------------------------+
```

---

## 6. Key Empirical Findings

1. **Precipitation Semantics**:
   - Zero dry periods exist in the data (100% positive values). Observations are logged at high, irregular seconds frequencies.
   - Naively summing the column yields ~500,000 mm of rain, which is physically impossible.
   - **Conclusion**: The column represents instantaneous gauge readings / observation rates. The dashboard computes mean rate (`5.11 mm/obs`) and daily average rate rather than an unweighted cumulative sum.

2. **The Phoenix Anomaly**:
   - 9 stations show temperature bounded tightly within `[-10.0°C, 40.0°C]`.
   - **Phoenix** exhibits an extended negative lower bound down to `-19.97°C` (mean `12.79°C` vs `~15.02°C` elsewhere), making it the coldest station by average temperature in this archive.
   - Phoenix also shows higher mean precipitation (`6.09 mm/obs` vs `~5.00 mm/obs` elsewhere) and higher peak precipitation (`14.97 mm` vs `9.99 mm`).

3. **Variable Orthogonality**:
   - The Pearson correlation coefficient between temperature and humidity is $r \approx -0.0013$ (virtually zero).
   - Cross-variable correlations between all numerical pairs remain bounded within $[-0.01, +0.01]$, demonstrating statistical independence.

4. **Biometeorological Perceived Heat**:
   - While measured dry-bulb temperatures average 14.78°C, periods of elevated humidity elevate apparent temperatures up to 41.2°C via NOAA Heat Index modeling.

---

## 7. Viva Questions & Answers (16 Preparation Questions)

### Q1: What is the core goal of the HAZE project?
**Answer**: HAZE is an interactive, publication-grade weather analytics dashboard designed to process and analyze 1,000,000 historical weather observations locally. It focuses on statistical correctness, optimized memory management, and a clean, technical visual identity.

### Q2: Why did you choose Streamlit instead of a traditional React or Next.js stack?
**Answer**: Streamlit allows end-to-end Python execution. Since data science and numerical operations (Pandas, NumPy, Plotly) execute in Python, Streamlit eliminates the need for an intermediate REST API or Node.js server. Its built-in `@st.cache_data` provides seamless memory caching.

### Q3: How did you optimize memory usage for 1,000,000 records?
**Answer**: By casting `float64` columns to `float32` and converting the repetitive `Location` string column to a Pandas `category` dtype, we reduced memory consumption from over 72 MB down to **23.8 MB**, a 67% reduction that loads in ~1.1 seconds.

### Q4: Why didn't you plot all 1,000,000 points on the scatter plot and time-series chart?
**Answer**: Plotting 1,000,000 raw DOM/SVG nodes causes severe client browser freezes and memory exhaustion. For the time series, we mathematically aggregate records to Daily, Weekly, or Monthly means. For the scatter plot, we render a representative random sample (4,000 points) for visualization, while calculating the correlation coefficient across 100% of the filtered dataset.

### Q5: What anomaly did you discover regarding precipitation, and how did you resolve it?
**Answer**: Every record contained positive precipitation at irregular seconds-level intervals. A naive sum yielded over 500,000 mm of rain per station, which is physically impossible. We recognized that the data represents instantaneous gauge rates rather than cumulative rainfall buckets, and therefore aggregated using central tendency (mean rate) rather than summation.

### Q6: What is the "Phoenix Anomaly" in this dataset?
**Answer**: While 9 of the 10 stations have temperatures bounded between -10°C and 40°C with an average of ~15.02°C, Phoenix has an extended lower range down to -19.97°C (mean 12.79°C). Statistically, Phoenix is the coolest station on average in this dataset.

### Q7: What did the correlation matrix reveal about the variables?
**Answer**: The Pearson correlation coefficients between all variable pairs were nearly zero ($|r| < 0.01$). This proves that in this dataset, temperature, humidity, precipitation, and wind speed vary independently (orthogonal variables).

### Q8: Explain the difference between correlation and causation in this context.
**Answer**: Correlation measures the strength and direction of a linear relationship between two variables. Causation implies that a change in one variable directly causes a change in another. Even if temperature and humidity showed a high correlation, that alone would not prove causation without a physical atmospheric mechanism and controlled experimentation.

### Q9: What is the NOAA Heat Index and how did you calculate it?
**Answer**: The Heat Index (Apparent Temperature) models the thermal stress experienced by the human body by combining dry-bulb temperature and relative humidity. We used the NOAA Rothfusz multivariable polynomial regression equation, implemented vectorially with NumPy to calculate values across 1,000,000 rows in milliseconds.

### Q10: How does your Anomaly Detection module work?
**Answer**: It uses standardized Z-scores: $Z = (X - \mu) / \sigma$. Points where $|Z| \ge 2.0$ deviate significantly from the population mean. In our dataset, this successfully isolates extreme freezing events in Phoenix (temperatures dropping to -19.97°C) and peak wind velocity events exceeding 29.5 km/h.

### Q11: What is the benefit of the Station Head-to-Head feature?
**Answer**: It allows comparative hypothesis testing between any two chosen stations. It calculates mean and standard deviation deltas ($\Delta \text{Mean} = \mu_A - \mu_B$) and overlays their distributions on a unified histogram to clearly reveal localized station differences.

### Q12: Why did you provide both Arithmetic Means and Parametric Percentiles?
**Answer**: Arithmetic means can be sensitive to skewed distributions and extreme outliers. Parametric percentiles (P10, P25, Median/P50, P75, P90) provide non-parametric, robust measures of central tendency and spread (IQR) that remain reliable regardless of distribution symmetry.

### Q13: How does Streamlit's caching mechanism (`@st.cache_data`) improve performance?
**Answer**: `@st.cache_data` stores the output of the data loader in memory. Subsequent interactions (filtering locations, changing date ranges, adjusting time resolution) reuse the cached DataFrame without reading the 99 MB CSV from disk again.

### Q14: How does the Diurnal Cycle analysis help?
**Answer**: It extracts the hour component (`Date_Time.dt.hour`) and aggregates observations across the 24 hours of the day (00:00 to 23:00) with standard deviation error envelopes. This reveals cyclical day-night atmospheric fluctuations.

### Q15: How did you ensure all UI features are reactive and functional?
**Answer**: We bound all sidebar filters directly to Streamlit session state keys, ensuring that "Select All" and "Reset Filters" immediately trigger a clean rerun. Furthermore, all charts (ranking bar chart, distribution histogram, temporal chart) dynamically reference the user's selected primary variable.

### Q16: If you had another week on this project, what would you add?
**Answer**: I would convert the raw CSV into an Apache Parquet file with Snappy compression for sub-second cold starts, introduce geospatial map layers with station latitude/longitude coordinates, and build an automated forecasting module using ARIMA or Prophet.
