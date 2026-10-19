"""
HAZE — Weather Data Analytics Dashboard
=======================================
A minimal, editorial, technical dashboard for historical weather data analysis.
Built with Streamlit, Pandas, NumPy, and Plotly.
"""

import datetime
from typing import List, Tuple
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.analysis import (
    load_dataset,
    filter_data,
    get_summary_metrics,
    aggregate_time_series,
    get_location_comparison,
    sample_for_visualization,
    calculate_correlation_matrix,
    generate_observations,
    EXPECTED_NUMERICAL_COLS
)

# Page configuration
st.set_page_config(
    page_title="haze — weather data, observed",
    page_icon="☁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimalist Editorial CSS
CUSTOM_CSS = """
<style>
/* Base typography & backgrounds */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #c9d1d9;
}

code, .stCode, [data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace;
}

/* Header & Wordmark */
.haze-wordmark {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.2rem;
    font-weight: 500;
    letter-spacing: -0.05em;
    color: #f0f6fc;
    margin-bottom: 0px;
    line-height: 1.1;
}

.haze-subtitle {
    font-size: 1.05rem;
    font-style: italic;
    color: #8b949e;
    margin-top: 2px;
    margin-bottom: 8px;
}

.haze-metadata {
    font-size: 0.78rem;
    color: #6e7681;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.02em;
    padding-bottom: 12px;
    border-bottom: 1px solid #21262d;
    margin-bottom: 24px;
}

/* Metric Display Cards */
.metric-card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 16px 18px;
    height: 100%;
}

.metric-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8b949e;
    margin-bottom: 4px;
}

.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.7rem;
    font-weight: 500;
    color: #f0f6fc;
    line-height: 1.2;
}

.metric-unit {
    font-size: 0.95rem;
    color: #79a8d7;
    margin-left: 2px;
}

.metric-subtext {
    font-size: 0.75rem;
    color: #6e7681;
    margin-top: 6px;
    line-height: 1.3;
}

/* Observation Box */
.obs-card {
    background-color: #12161f;
    border-left: 2px solid #5a82a6;
    border-top: 1px solid #21262d;
    border-right: 1px solid #21262d;
    border-bottom: 1px solid #21262d;
    padding: 14px 18px;
    margin-bottom: 12px;
    border-radius: 0px 4px 4px 0px;
}

.obs-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: #79a8d7;
    margin-bottom: 4px;
}

.obs-title {
    font-size: 0.92rem;
    font-weight: 500;
    color: #e6edf3;
    margin-bottom: 4px;
}

.obs-detail {
    font-size: 0.82rem;
    color: #8b949e;
    line-height: 1.45;
}

/* Chart container styling */
.chart-header {
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8b949e;
    margin-bottom: 8px;
}

/* Data limitation badge */
.limitation-box {
    background: #161b22;
    border: 1px solid #30363d;
    padding: 12px 16px;
    border-radius: 4px;
    font-size: 0.8rem;
    color: #8b949e;
    margin-top: 10px;
    margin-bottom: 16px;
}

/* Clean Streamlit elements */
div[data-testid="stSidebar"] {
    background-color: #0d1117;
    border-right: 1px solid #21262d;
}

div[data-testid="stToolbar"] {
    display: none;
}

footer {
    display: none;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Plotly theme styling helper
def apply_editorial_theme(fig: go.Figure, title: str = "", height: int = 380) -> go.Figure:
    """Applies a minimal, dark technical layout to Plotly figures."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(family="Inter, sans-serif", size=13, color="#c9d1d9"),
            x=0.01,
            y=0.96
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=45, r=25, t=45 if title else 20, b=45),
        font=dict(family="Inter, sans-serif", color="#8b949e", size=11),
        xaxis=dict(
            gridcolor="#21262d",
            zerolinecolor="#30363d",
            showline=True,
            linecolor="#30363d",
            tickfont=dict(color="#8b949e", size=10)
        ),
        yaxis=dict(
            gridcolor="#21262d",
            zerolinecolor="#30363d",
            showline=True,
            linecolor="#30363d",
            tickfont=dict(color="#8b949e", size=10)
        ),
        legend=dict(
            font=dict(color="#c9d1d9", size=10),
            bgcolor="rgba(22, 27, 34, 0.8)",
            bordercolor="#30363d",
            borderwidth=1,
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.02
        ),
        height=height,
        hoverlabel=dict(
            bgcolor="#161b22",
            bordercolor="#30363d",
            font=dict(family="JetBrains Mono, monospace", color="#f0f6fc", size=11)
        )
    )
    return fig


# Cached Data Loader
@st.cache_data(show_spinner="Loading and validating weather dataset...")
def get_data():
    return load_dataset("data/weather_data.csv")


def main():
    try:
        raw_df, metadata = get_data()
    except Exception as err:
        st.error(f"Error initializing HAZE dashboard: {err}")
        st.info("Please verify that 'data/weather_data.csv' exists and contains valid weather data.")
        return

    # Sidebar Filter Controls
    with st.sidebar:
        st.markdown(
            """
            <div style="padding-bottom: 12px; border-bottom: 1px solid #21262d; margin-bottom: 16px;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.3rem; font-weight: 500; color: #f0f6fc;">haze</span>
                <span style="font-size: 0.8rem; color: #79a8d7; margin-left: 6px;">v1.0</span>
                <p style="font-size: 0.78rem; color: #8b949e; margin-top: 4px; margin-bottom: 0;">Parameter controls</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 1. Location Selection
        all_locs = metadata['locations']
        col_sel1, col_sel2 = st.columns([1, 1])
        select_all_clicked = col_sel1.button("Select All", use_container_width=True)
        reset_clicked = col_sel2.button("Reset Filters", use_container_width=True)

        # Session state for locations
        if "selected_locations" not in st.session_state or select_all_clicked or reset_clicked:
            st.session_state["selected_locations"] = all_locs

        selected_locations = st.multiselect(
            "Locations",
            options=all_locs,
            default=st.session_state["selected_locations"],
            help="Filter observations by one or more recording stations."
        )

        # 2. Date Range Selection
        min_dt = metadata['start_date'].date()
        max_dt = metadata['end_date'].date()

        if reset_clicked:
            date_range = (min_dt, max_dt)
        else:
            date_range = st.date_input(
                "Observation Interval",
                value=(min_dt, max_dt),
                min_value=min_dt,
                max_value=max_dt,
                help="Select start and end dates to filter historical observations."
            )

        # Validate date range
        start_date = None
        end_date = None
        if isinstance(date_range, (tuple, list)):
            if len(date_range) == 2:
                start_date, end_date = date_range
            elif len(date_range) == 1:
                start_date = end_date = date_range[0]
        else:
            start_date = end_date = date_range

        # 3. Variable Selection
        selected_var = st.selectbox(
            "Primary Weather Variable",
            options=list(EXPECTED_NUMERICAL_COLS.keys()),
            format_func=lambda x: EXPECTED_NUMERICAL_COLS.get(x, x),
            index=0,
            help="Select the focal parameter for distribution and time-series analyses."
        )

        # 4. Time aggregation resolution
        time_res = st.select_slider(
            "Time-Series Resolution",
            options=["Daily", "Weekly", "Monthly"],
            value="Daily",
            help="Aggregates high-frequency records to eliminate rendering latency."
        )

        st.markdown(
            f"""
            <div style="font-size: 0.72rem; color: #6e7681; font-family: 'JetBrains Mono', monospace; margin-top: 24px;">
                Dataset: {metadata['row_count']:,} rows<br>
                Memory: {metadata['memory_mb']} MB (optimized)<br>
                Engine: Vectorized Pandas / NumPy
            </div>
            """,
            unsafe_allow_html=True
        )

    # Empty filter protection
    if not selected_locations:
        st.warning("No locations selected. Please select at least one location from the sidebar.")
        return

    if start_date is None or end_date is None:
        st.warning("Please specify a valid start and end date.")
        return

    # Filter Dataset
    df = filter_data(raw_df, locations=selected_locations, start_date=start_date, end_date=end_date)
    filtered_count = len(df)

    # Section A: Header
    date_cov_str = f"{metadata['start_date'].strftime('%b %d, %Y')} — {metadata['end_date'].strftime('%b %d, %Y')}"
    st.markdown(
        f"""
        <div style="margin-top: -10px;">
            <div class="haze-wordmark">haze</div>
            <div class="haze-subtitle">Weather data, observed.</div>
            <div class="haze-metadata">
                ARCHIVE: {date_cov_str} &nbsp;|&nbsp; 
                RECORDS: {metadata['row_count']:,} OBS &nbsp;|&nbsp; 
                ACTIVE SELECTION: {filtered_count:,} ({filtered_count / metadata['row_count'] * 100:.1f}%) &nbsp;|&nbsp; 
                STATIONS: {len(selected_locations)} OF {metadata['num_locations']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if df.empty:
        st.warning("The selected filter parameters produced zero matching records. Please broaden the date range or select additional locations.")
        return

    # Section C: Summary Metrics
    metrics = get_summary_metrics(df)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Average Temperature</div>
                <div class="metric-value">{metrics['avg_temp']:.1f}<span class="metric-unit">°C</span></div>
                <div class="metric-subtext">Min: {metrics['min_temp']:.1f}°C &nbsp;|&nbsp; Max: {metrics['max_temp']:.1f}°C</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Average Humidity</div>
                <div class="metric-value">{metrics['avg_humidity']:.1f}<span class="metric-unit">%</span></div>
                <div class="metric-subtext">Filtered mean relative humidity</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        # Highlighting semantic meaning of precipitation
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Precipitation Rate</div>
                <div class="metric-value">{metrics['mean_precip_rate']:.2f}<span class="metric-unit">mm/obs</span></div>
                <div class="metric-subtext">Instantaneous interval reading (mean)</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Average Wind Speed</div>
                <div class="metric-value">{metrics['avg_wind']:.1f}<span class="metric-unit">km/h</span></div>
                <div class="metric-subtext">Peak recorded: {metrics['max_wind']:.1f} km/h</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # Section D: Temperature Over Time
    st.markdown('<div class="chart-header">Temporal Evolution &mdash; Selected Weather Variable</div>', unsafe_allow_html=True)

    c_ts1, c_ts2 = st.columns([3, 1])
    with c_ts2:
        by_location_toggle = st.checkbox("Disaggregate by Location", value=False if len(selected_locations) > 3 else True)

    ts_df = aggregate_time_series(df, variable=selected_var, freq=time_res, by_location=by_location_toggle)

    if not ts_df.empty:
        var_label = EXPECTED_NUMERICAL_COLS.get(selected_var, selected_var)
        if by_location_toggle and 'Location' in ts_df.columns:
            # Color palette with muted desaturated tones
            color_sequence = [
                "#5a82a6", "#79a8d7", "#8b949e", "#a5c2df", "#6e7681",
                "#4a6d8c", "#b0c4de", "#8fa3b7", "#9bb3c7", "#3d5a73"
            ]
            fig_ts = px.line(
                ts_df,
                x='Date_Time',
                y=selected_var,
                color='Location',
                color_discrete_sequence=color_sequence,
                labels={'Date_Time': 'Date', selected_var: var_label}
            )
            fig_ts.update_traces(line=dict(width=1.8))
        else:
            fig_ts = go.Figure()
            # Mean line
            fig_ts.add_trace(go.Scatter(
                x=ts_df['Date_Time'],
                y=ts_df['mean'],
                mode='lines',
                name='Mean Value',
                line=dict(color='#5a82a6', width=2),
                hovertemplate='%{x|%b %d, %Y}<br>Mean: %{y:.2f}<extra></extra>'
            ))
            # Min-Max envelope if daily/weekly
            if 'min' in ts_df.columns and 'max' in ts_df.columns:
                fig_ts.add_trace(go.Scatter(
                    x=ts_df['Date_Time'],
                    y=ts_df['max'],
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                fig_ts.add_trace(go.Scatter(
                    x=ts_df['Date_Time'],
                    y=ts_df['min'],
                    mode='lines',
                    line=dict(width=0),
                    fill='tonexty',
                    fillcolor='rgba(90, 130, 166, 0.12)',
                    name='Min-Max Observed Range',
                    hoverinfo='skip'
                ))

        fig_ts = apply_editorial_theme(fig_ts, title=f"{var_label} ({time_res} Aggregation)", height=370)
        st.plotly_chart(fig_ts, use_container_width=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Section E & Section H: Location Comparison and Distribution
    col_mid1, col_mid2 = st.columns([1, 1])

    with col_mid1:
        st.markdown('<div class="chart-header">Location Comparison &mdash; Average Temperature</div>', unsafe_allow_html=True)
        loc_df = get_location_comparison(df, metric='Temperature_C')

        if not loc_df.empty:
            fig_bar = go.Figure(go.Bar(
                x=loc_df['mean'],
                y=loc_df['Location'],
                orientation='h',
                marker=dict(
                    color='#5a82a6',
                    line=dict(color='#79a8d7', width=1)
                ),
                hovertemplate='<b>%{y}</b><br>Average Temp: %{x:.2f}°C<extra></extra>'
            ))
            fig_bar = apply_editorial_theme(fig_bar, title="Average Temperature by Station (°C)", height=350)
            fig_bar.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Insufficient location data for comparison.")

    with col_mid2:
        st.markdown('<div class="chart-header">Temperature Distribution &mdash; Observation Density</div>', unsafe_allow_html=True)
        # Sample for histogram if dataset is very large to maintain fast responsive rendering
        hist_sample = sample_for_visualization(df, max_points=50000)

        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=hist_sample['Temperature_C'],
            nbinsx=45,
            marker=dict(
                color='rgba(90, 130, 166, 0.65)',
                line=dict(color='#79a8d7', width=0.8)
            ),
            hovertemplate='Bin: %{x}°C<br>Count: %{y}<extra></extra>'
        ))

        # Mean and median lines
        t_mean = df['Temperature_C'].mean()
        t_median = df['Temperature_C'].median()

        fig_hist.add_vline(
            x=t_mean,
            line_dash="dash",
            line_color="#e6edf3",
            line_width=1.5,
            annotation_text=f"Mean: {t_mean:.1f}°C",
            annotation_position="top right",
            annotation_font=dict(size=10, color="#e6edf3", family="JetBrains Mono")
        )
        fig_hist.add_vline(
            x=t_median,
            line_dash="dot",
            line_color="#8b949e",
            line_width=1.5,
            annotation_text=f"Median: {t_median:.1f}°C",
            annotation_position="bottom right",
            annotation_font=dict(size=10, color="#8b949e", family="JetBrains Mono")
        )

        fig_hist = apply_editorial_theme(fig_hist, title="Observed Temperature Frequency Distribution", height=350)
        fig_hist.update_layout(xaxis_title="Temperature (°C)", yaxis_title="Observations")
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Section F & Section G: Weather Relationships & Correlation Heatmap
    col_rel1, col_rel2 = st.columns([1, 1])

    with col_rel1:
        st.markdown('<div class="chart-header">Bivariate Analysis &mdash; Temperature vs Humidity</div>', unsafe_allow_html=True)

        # Full dataset correlation calculation
        r_val = df['Temperature_C'].corr(df['Humidity_pct'])
        r_display = f"r = {r_val:.4f}" if pd.notnull(r_val) else "r = N/A"

        # Representative random sample for rendering
        scatter_sample = sample_for_visualization(df, max_points=4000)

        fig_scatter = px.scatter(
            scatter_sample,
            x='Temperature_C',
            y='Humidity_pct',
            color='Location' if len(selected_locations) <= 5 else None,
            color_discrete_sequence=['#5a82a6', '#79a8d7', '#8b949e', '#a5c2df', '#6e7681'],
            opacity=0.45,
            labels={'Temperature_C': 'Temperature (°C)', 'Humidity_pct': 'Humidity (%)'}
        )
        fig_scatter.update_traces(marker=dict(size=4))
        fig_scatter = apply_editorial_theme(
            fig_scatter,
            title=f"Scatter Analysis ({r_display} | 4k sample rendered)",
            height=350
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.caption(
            "Note: The correlation coefficient r is calculated across all filtered observations. "
            "A visual sample is plotted to preserve smooth interface responsiveness."
        )

    with col_rel2:
        st.markdown('<div class="chart-header">Cross-Variable Correlation Matrix</div>', unsafe_allow_html=True)
        corr_matrix = calculate_correlation_matrix(df)

        if not corr_matrix.empty:
            labels_clean = [EXPECTED_NUMERICAL_COLS.get(c, c) for c in corr_matrix.columns]
            z_vals = corr_matrix.values

            # Editorial cool monochromatic heatmap
            fig_heat = go.Figure(data=go.Heatmap(
                z=z_vals,
                x=labels_clean,
                y=labels_clean,
                colorscale=[
                    [0.0, "#0e1117"],
                    [0.5, "#21262d"],
                    [1.0, "#5a82a6"]
                ],
                zmin=-1.0,
                zmax=1.0,
                text=np.around(z_vals, 3),
                texttemplate="%{text}",
                textfont={"size": 11, "family": "JetBrains Mono", "color": "#f0f6fc"},
                hoverongaps=False
            ))

            fig_heat = apply_editorial_theme(fig_heat, title="Pearson Correlation Coefficients", height=350)
            st.plotly_chart(fig_heat, use_container_width=True)
            st.caption("Pearson r measures linear association only; correlation does not imply causation.")
        else:
            st.info("Insufficient variance or records to compute correlation matrix.")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Section I: Precipitation Analysis
    st.markdown('<div class="chart-header">Precipitation Analysis &mdash; Semantics & Station Comparison</div>', unsafe_allow_html=True)

    c_p1, c_p2 = st.columns([1, 1])
    with c_p1:
        # Station comparison of average precipitation rate
        precip_loc_df = df.groupby('Location', observed=True)['Precipitation_mm'].agg(
            mean_rate='mean',
            max_gauge='max'
        ).reset_index().sort_values('mean_rate', ascending=True)

        fig_precip_loc = go.Figure(go.Bar(
            x=precip_loc_df['mean_rate'],
            y=precip_loc_df['Location'],
            orientation='h',
            marker=dict(color='#4a6d8c', line=dict(color='#79a8d7', width=1)),
            hovertemplate='<b>%{y}</b><br>Mean Rate: %{x:.2f} mm/obs<extra></extra>'
        ))
        fig_precip_loc = apply_editorial_theme(fig_precip_loc, title="Mean Precipitation Rate by Station (mm/obs)", height=320)
        st.plotly_chart(fig_precip_loc, use_container_width=True)

    with c_p2:
        # Daily mean precipitation over time
        precip_ts = aggregate_time_series(df, variable='Precipitation_mm', freq='Daily', by_location=False)
        if not precip_ts.empty:
            fig_precip_ts = go.Figure(go.Scatter(
                x=precip_ts['Date_Time'],
                y=precip_ts['mean'],
                mode='lines',
                line=dict(color='#79a8d7', width=1.8),
                hovertemplate='%{x|%b %d, %Y}<br>Daily Mean Rate: %{y:.2f} mm<extra></extra>'
            ))
            fig_precip_ts = apply_editorial_theme(fig_precip_ts, title="Daily Average Precipitation Rate (mm)", height=320)
            st.plotly_chart(fig_precip_ts, use_container_width=True)

    st.markdown(
        """
        <div class="limitation-box">
            <b>Analytical Rigor Note &mdash; Precipitation Semantics:</b> In this dataset, precipitation values exist continuously for every record
            (zero recorded dry periods) with sampling deltas spanning irregular seconds. Summing raw observations would yield an unrealistic cumulative total
            (~500,000 mm). The dataset represents instantaneous sensor gauge measurements rather than accumulated rainfall buckets.
            Aggregation must therefore employ central tendency (mean/median rate) rather than naive summation.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Section J: Observations (Analytical Findings)
    st.markdown('<div class="chart-header">Observations &mdash; Inferred Findings from Filtered Data</div>', unsafe_allow_html=True)

    observations = generate_observations(df)
    for obs in observations:
        st.markdown(
            f"""
            <div class="obs-card">
                <div class="obs-tag">{obs['category']}</div>
                <div class="obs-title">{obs['title']}</div>
                <div class="obs-detail">{obs['detail']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # Section K: Data Explorer
    st.markdown('<div class="chart-header">Data Explorer &mdash; Filtered Record Inspection</div>', unsafe_allow_html=True)

    explorer_col1, explorer_col2 = st.columns([3, 1])
    with explorer_col1:
        selected_cols = st.multiselect(
            "Visible Columns",
            options=list(df.columns),
            default=list(df.columns),
            help="Select columns to inspect."
        )
    with explorer_col2:
        preview_rows = st.selectbox(
            "Preview Rows",
            options=[25, 50, 100, 250],
            index=1,
            help="Number of rows to render in the preview table."
        )

    # Display preview table
    st.dataframe(
        df[selected_cols].head(preview_rows),
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        f"<span style='font-family: JetBrains Mono; font-size: 0.75rem; color: #8b949e;'>Displaying top {min(preview_rows, len(df))} of {len(df):,} filtered observations.</span>",
        unsafe_allow_html=True
    )

    # CSV Download Button
    csv_bytes = df.head(50000).to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"Export Filtered Records ({min(50000, len(df)):,} rows as CSV)",
        data=csv_bytes,
        file_name="haze_filtered_weather.csv",
        mime="text/csv",
        help="Exports up to 50,000 filtered rows to prevent browser memory exhaustion."
    )


if __name__ == "__main__":
    main()
