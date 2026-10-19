# HAZE — College Presentation Notes & Viva Preparation Guide

This document is engineered to prepare you for your project presentation, defense, and viva examination. It breaks down the theoretical foundations, implementation choices, actual empirical findings, and 14 technical viva questions with direct, concise answers.

---

## 1. Problem Statement

Modern weather data collection systems generate vast volumes of continuous, high-frequency observational data. However, generic dashboard templates often fall prey to critical analytical errors:
- **Misinterpreting measurement semantics**: For instance, summing high-frequency instantaneous sensor gauge measurements as cumulative rainfall totals.
- **Performance bottlenecks**: Attempting to render millions of raw SVG/DOM elements directly in a browser, freezing client machines.
- **Superficial visual decoration**: Emphasizing decorative gradients, oversized cards, and arbitrary icons over scientific clarity and typographic hierarchy.

**HAZE** solves these issues by presenting a publication-grade, minimal, editorial analytics dashboard built with strict mathematical rigor, optimized memory utilization, and transparent data limitations.

---

## 2. Project Objectives

1. **Scalable Local Processing**: Efficiently load, process, and analyze 1,000,000 weather observations locally without a database, external cloud API, or heavy JavaScript framework.
2. **Editorial Aesthetic & Usability**: Develop a cohesive dark-mode visual identity with understated typography (`Inter` + `JetBrains Mono`), thin borders, and desaturated cool slate accents (`#5a82a6`).
3. **Analytical Correctness**: Accurately distinguish interval sampling from cumulative quantities, report population-wide statistical coefficients, and enforce separation between correlation and causation.
4. **Dynamic Responsiveness**: Provide smooth interactive filtering across stations, date ranges, and time aggregations.

---

## 3. Dataset Overview & Source

- **File Name**: `data/weather_data.csv` (extracted from `weather_dataset.zip`)
- **Total Records**: 1,000,000 rows, 6 columns
- **Temporal Coverage**: January 01, 2024 `00:00:06` to May 18, 2024 `19:44:10` (~138.8 days)
- **Monitoring Stations (10)**: Chicago, Dallas, Houston, Los Angeles, New York, Philadelphia, Phoenix, San Antonio, San Diego, San Jose (~100,000 observations each)
- **Schema & Data Types**:
  - `Location`: Station name (Categorical string)
  - `Date_Time`: Timestamp (ISO 8601 formatted datetime)
  - `Temperature_C`: Ambient temperature in Celsius (float)
  - `Humidity_pct`: Relative humidity in percentage (float)
  - `Precipitation_mm`: Instantaneous gauge reading in millimeters (float)
  - `Wind_Speed_kmh`: Instantaneous wind speed in kilometers per hour (float)
- **Data Quality**: 0 missing values, 0 duplicate rows, 0 null timestamps.

---

## 4. Libraries Used & Technical Rationale

| Library | Version | Purpose & Rationale |
| :--- | :--- | :--- |
| **Python** | 3.11+ | Fast execution, robust standard library, modern type hinting. |
| **Streamlit** | $\ge$ 1.30 | Reactive, pure-Python web UI. Eliminates complex JS builds while providing fast session state management and `@st.cache_data`. |
| **Pandas** | $\ge$ 2.0 | High-performance columnar data manipulation and grouping. Used with optimized dtypes (`category`, `float32`) to reduce memory from 72 MB to 23.8 MB. |
| **NumPy** | $\ge$ 1.24 | Vectorized numerical operations, fast array slicing, and correlation matrix math. |
| **Plotly** | $\ge$ 5.18 | High-fidelity, GPU-accelerated interactive visualizations with responsive tooltips and custom dark layouts. |

---

## 5. Data Cleaning & Optimization Decisions

1. **Downcasting Precision**:
   - `float64` was downcasted to `float32`. Ambient temperature and wind speed do not require double-precision floating point (53-bit mantissa); single-precision (24-bit mantissa) is more than sufficient and halves memory consumption.
2. **Categorical Encoding**:
   - `Location` was converted from Python object strings to Pandas `category` dtype. With only 10 unique strings repeated across 1M rows, this reduced memory footprint from ~60 MB to under 1 MB for that column.
3. **Timestamp Indexing**:
   - Verified that all timestamps parsed without NaT errors. Rows were pre-sorted by `Date_Time` to enable instantaneous range filtering ($O(\log N)$ or contiguous mask).
4. **Preservation of Raw Data**:
   - The original CSV was maintained untouched in `data/weather_data.csv`. All aggregations and type conversions occur in-memory through `utils/analysis.py`.

---

## 6. Exploratory Data Analysis (EDA) & Key Findings

### Finding 1: The Precipitation Semantics Discovery
- **Observation**: Every observation in the dataset contains a positive non-zero precipitation value (`min = 0.000009 mm`, `max = 14.97 mm`, zero count = 0%).
- **Sampling Frequency**: Records occur at irregular intervals of a few seconds.
- **The Pitfall**: Naively taking `sum(Precipitation_mm)` yields **5,109,639 mm** (~5.1 kilometers of rain across all stations combined, or ~500 meters per station). In reality, annual global rainfall rarely exceeds 12,000 mm in the wettest places on Earth!
- **Scientific Decision**: The column represents **instantaneous sensor rates / gauge levels**, not accumulated buckets. The dashboard displays the **mean rate** (`5.11 mm/obs`) and **daily mean rate** rather than an unweighted sum.

### Finding 2: The Phoenix Statistical Anomaly
- While 9 cities (Chicago, Dallas, Houston, LA, NY, Philadelphia, San Antonio, San Diego, San Jose) have temperature bounded between `[-10.0°C, +40.0°C]` with a mean of `~15.02°C`, **Phoenix** has:
  - Minimum temperature of **-19.97°C** (mean **12.79°C**).
  - Maximum precipitation of **14.97 mm** (mean **6.09 mm/obs** vs ~5.00 mm elsewhere).
- Counter-intuitively compared to geography, Phoenix is the **coolest station** on average in this dataset.

### Finding 3: Variable Orthogonality (Independence)
- The Pearson correlation matrix between all pairs of variables (`Temperature_C`, `Humidity_pct`, `Precipitation_mm`, `Wind_Speed_kmh`) reveals values between **-0.010 and +0.001**.
- The variables vary independently without linear coupling. This indicates synthetic or benchmark-generated characteristics, which the dashboard transparently notes.

---

## 7. Explanation of Every Visual Component

1. **Header & Metadata Bar**:
   - Communicates project identity (`haze`), dataset temporal coverage, active record count, and active percentage. Explicitly avoids misleading "live" badges.
2. **Summary Metric Cards**:
   - Four compact cards displaying Average Temperature (°C), Average Humidity (%), Precipitation Rate (mm/obs), and Average Wind Speed (km/h) with contextual subtext (min/max ranges).
3. **Temporal Evolution (Time-Series)**:
   - Line chart aggregating 1,000,000 rows into daily, weekly, or monthly intervals.
   - Includes a subtle min-max shaded envelope when aggregated across all stations, or individual colored traces when disaggregated by location.
4. **Location Comparison**:
   - Horizontal bar chart ranking stations by calculated mean temperature, making station differences immediately legible.
5. **Temperature Distribution**:
   - Histogram featuring 45 bins with vertical dashed reference lines denoting the population mean and median.
6. **Bivariate Scatter Plot (Temperature vs. Humidity)**:
   - Evaluates correlation. Renders a stratified 4,000-point sample to prevent browser DOM lag while calculating the exact Pearson correlation coefficient $r$ on 100% of the filtered dataset.
7. **Cross-Variable Correlation Heatmap**:
   - $4 \times 4$ matrix showing Pearson correlation coefficients with a dark monochromatic colorscale. Includes an analytical note distinguishing correlation from causation.
8. **Precipitation Analysis**:
   - Station comparison bar chart and daily time series of mean gauge rates, accompanied by an explicit data limitations callout.
9. **Observations (`observations`)**:
   - Programmatically derived analytical statements citing exact extremes, station names, timestamps, and statistical relationships.
10. **Data Explorer**:
    - Interactive table with configurable row preview (25, 50, 100, 250 rows) and an export button to download filtered records as CSV.

---

## 8. Architecture & Data Flow

```
+-----------------------------------------------------------+
|                    Browser / Client UI                    |
+-----------------------------------------------------------+
                           |   ^
        Sidebar Parameters |   | Rendered Plotly / HTML
                           v   |
+-----------------------------------------------------------+
|                          app.py                           |
|  - Session State & Sidebar Controls                       |
|  - Layout Orchestration & Custom CSS                      |
|  - Component Invocation & Plotly Figures                  |
+-----------------------------------------------------------+
                           |   ^
           Filter Requests |   | Aggregated Data & Metrics
                           v   |
+-----------------------------------------------------------+
|                    utils/analysis.py                      |
|  - load_dataset(): Cached loading & dtype optimization    |
|  - filter_data(): Vectorized Boolean masking              |
|  - aggregate_time_series(): Resampling by D/W/M           |
|  - calculate_correlation_matrix(): Full-data Pearson r    |
|  - generate_observations(): Dynamic findings derivation   |
+-----------------------------------------------------------+
                           |   ^
          Disk Read (Once) |   | Parsed DataFrame
                           v   |
+-----------------------------------------------------------+
|                 data/weather_data.csv                     |
|                 (1,000,000 Rows x 6 Cols)                 |
+-----------------------------------------------------------+
```

---

## 9. Limitations & Future Enhancements

### Current Limitations
1. **Sampling Interval Uniformity**: Observation intervals range randomly between 1 second and several minutes, meaning raw observation counts do not correlate uniformly with elapsed time.
2. **Variable Independence**: The dataset exhibits near-zero correlation between temperature and humidity, reflecting synthetic generation characteristics rather than real-world psychrometric curves.
3. **Absence of Geolocation Coordinates**: Stations are identified by city name without explicit latitude/longitude, precluding geographic map overlays.

### Future Work
1. **Geospatial Mapping**: Incorporating station coordinates to render interactive geospatial isobar or isotherm layers.
2. **Automated Anomaly Detection**: Implementing Isolation Forests or Z-score outlier detection to isolate sudden sensor spikes.
3. **Parquet Storage Format**: Converting the CSV archive to Apache Parquet with Snappy compression for sub-second cold starts and columnar disk reads.

---

## 10. Viva Questions & Answers (Preparation)

### Q1: What is the core objective of the HAZE project?
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

### Q9: How does the application handle empty selections or invalid date ranges?
**Answer**: `utils/analysis.py` contains validation checks that return an empty DataFrame or fallback boundaries. In `app.py`, conditional guards detect empty selections and render clean warning prompts instead of crashing with unhandled exceptions.

### Q10: How does Streamlit's caching mechanism (`@st.cache_data`) improve performance?
**Answer**: `@st.cache_data` stores the output of the data loader in memory. Subsequent interactions (filtering locations, changing date ranges, adjusting time resolution) reuse the cached DataFrame without reading the 99 MB CSV from disk again.

### Q11: What is the difference between Mean and Median in the temperature distribution?
**Answer**: The Mean is the arithmetic average of all observations, sensitive to extreme values. The Median is the 50th percentile (the middle value). In our dataset, the mean (14.78°C) and median (14.78°C) are nearly identical because the uniform-like distribution is symmetrical.

### Q12: Why did you downcast `float64` to `float32`? Does it lose analytical accuracy?
**Answer**: `float32` provides 7 decimal digits of precision (e.g., `10.68300°C`), which far exceeds the accuracy of physical meteorological sensors (typically ±0.1°C). Downcasting cuts memory usage in half with zero perceptible loss in analytical validity.

### Q13: How is modularity enforced in your project architecture?
**Answer**: We separated concerns into `utils/analysis.py` for data loading, validation, aggregation, and statistical logic, and `app.py` for UI presentation, layout, and user interactions. This enables automated unit testing of data functions independent of Streamlit's runtime.

### Q14: If you had another week on this project, what would you add?
**Answer**: I would convert the raw CSV into an Apache Parquet file for faster columnar reads, introduce automated anomaly detection using Isolation Forests, and add geospatial mapping with station coordinates.
