"""
HAZE — Weather Data Analytics Dashboard
=======================================
A minimal, editorial, technical dashboard for historical weather data analysis.
Features biometeorological Heat Index modeling, 24-hour diurnal cycle analysis,
station head-to-head comparative analytics, and unsupervised anomaly detection.
"""

from typing import List, Tuple, Dict, Any
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from utils.analysis import (
    load_dataset,
    filter_data,
    get_summary_metrics,
    aggregate_time_series,
    aggregate_diurnal_cycle,
    get_location_comparison,
    get_head_to_head_comparison,
    detect_anomalies,
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

# High-Fidelity Editorial CSS with Micro-Animations & Glassmorphism
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600;700&display=swap');

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
    font-weight: 600;
    letter-spacing: -0.05em;
    color: #f0f6fc;
    line-height: 1.1;
    margin-bottom: 2px;
}

.haze-subtitle {
    font-size: 1.05rem;
    font-style: italic;
    color: #8b949e;
    margin-bottom: 8px;
}

.haze-metadata {
    font-size: 0.76rem;
    color: #6e7681;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.02em;
    padding-bottom: 12px;
    border-bottom: 1px solid #21262d;
    margin-bottom: 20px;
}

/* Metric Display Cards with Smooth Micro-Animation */
.metric-card {
    background: rgba(22, 27, 34, 0.75);
    backdrop-filter: blur(10px);
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 18px 20px;
    height: 100%;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}

.metric-card:hover {
    transform: translateY(-3px);
    border-color: #5a82a6;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
}

.metric-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: #8b949e;
    margin-bottom: 6px;
}

.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 500;
    color: #f0f6fc;
    line-height: 1.2;
}

.metric-unit {
    font-size: 0.95rem;
    color: #79a8d7;
    margin-left: 3px;
}

.metric-subtext {
    font-size: 0.75rem;
    color: #6e7681;
    margin-top: 6px;
    line-height: 1.35;
}

/* Observation Box */
.obs-card {
    background: rgba(18, 22, 31, 0.85);
    border-left: 3px solid #5a82a6;
    border-top: 1px solid #21262d;
    border-right: 1px solid #21262d;
    border-bottom: 1px solid #21262d;
    padding: 16px 20px;
    margin-bottom: 14px;
    border-radius: 0px 6px 6px 0px;
    transition: transform 0.2s ease, border-left-color 0.2s ease;
}

.obs-card:hover {
    transform: translateX(4px);
    border-left-color: #79a8d7;
}

.obs-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #79a8d7;
    margin-bottom: 4px;
}

.obs-title {
    font-size: 0.94rem;
    font-weight: 500;
    color: #e6edf3;
    margin-bottom: 4px;
}

.obs-detail {
    font-size: 0.83rem;
    color: #8b949e;
    line-height: 1.45;
}

/* Section and Chart Header */
.chart-header {
    font-size: 0.84rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8b949e;
    margin-bottom: 8px;
    font-weight: 500;
}

/* Analytical Limitation & Callout Box */
.limitation-box {
    background: rgba(22, 27, 34, 0.7);
    border: 1px solid #30363d;
    padding: 14px 18px;
    border-radius: 6px;
    font-size: 0.82rem;
    color: #8b949e;
    margin-top: 12px;
    margin-bottom: 18px;
    line-height: 1.45;
}

/* Delta cards for head-to-head comparison */
.delta-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 14px 16px;
    text-align: center;
}

.delta-title {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8b949e;
    margin-bottom: 4px;
}

.delta-stat {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.4rem;
    font-weight: 600;
    color: #79a8d7;
}

/* Clean Streamlit elements */
div[data-testid="stSidebar"] {
    background-color: #0d1117;
    border-right: 1px solid #21262d;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 16px;
    border-bottom: 1px solid #21262d;
}

.stTabs [data-baseweb="tab"] {
    height: 44px;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 4px 4px 0px 0px;
    color: #8b949e;
    font-size: 0.85rem;
    font-family: 'JetBrains Mono', monospace;
    padding-left: 8px;
    padding-right: 8px;
    transition: color 0.2s ease;
}

.stTabs [aria-selected="true"] {
    color: #79a8d7 !important;
    border-bottom-color: #5a82a6 !important;
    font-weight: 600;
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
            bgcolor="rgba(22, 27, 34, 0.85)",
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

    # Initialize Sidebar State cleanly
    all_locs = metadata['locations']
    min_dt = metadata['start_date'].date()
    max_dt = metadata['end_date'].date()

    if "active_locations" not in st.session_state:
        st.session_state["active_locations"] = all_locs

    if "active_dates" not in st.session_state:
        st.session_state["active_dates"] = (min_dt, max_dt)

    if "primary_var" not in st.session_state:
        st.session_state["primary_var"] = "Temperature_C"

    # Sidebar Filter Controls
    with st.sidebar:
        st.markdown(
            """
            <div style="padding-bottom: 12px; border-bottom: 1px solid #21262d; margin-bottom: 16px;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.35rem; font-weight: 600; color: #f0f6fc;">haze</span>
                <span style="font-size: 0.8rem; color: #79a8d7; margin-left: 6px;">v2.0</span>
                <p style="font-size: 0.78rem; color: #8b949e; margin-top: 4px; margin-bottom: 0;">Parameter controls</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_sel1, col_sel2 = st.columns([1, 1])
        if col_sel1.button("Select All", use_container_width=True):
            st.session_state["active_locations"] = all_locs
            st.rerun()

        if col_sel2.button("Reset Filters", use_container_width=True):
            st.session_state["active_locations"] = all_locs
            st.session_state["active_dates"] = (min_dt, max_dt)
            st.session_state["primary_var"] = "Temperature_C"
            st.rerun()

        selected_locations = st.multiselect(
            "Observation Stations",
            options=all_locs,
            default=st.session_state["active_locations"],
            help="Filter observations by one or more stations."
        )
        st.session_state["active_locations"] = selected_locations

        date_range = st.date_input(
            "Observation Interval",
            value=st.session_state["active_dates"],
            min_value=min_dt,
            max_value=max_dt,
            help="Select date range to filter historical records."
        )

        # Validate date range selection
        start_date = None
        end_date = None
        if isinstance(date_range, (tuple, list)):
            if len(date_range) == 2:
                start_date, end_date = date_range
                st.session_state["active_dates"] = date_range
            elif len(date_range) == 1:
                start_date = end_date = date_range[0]
        else:
            start_date = end_date = date_range

        variable_choices = list(EXPECTED_NUMERICAL_COLS.keys()) + ['Heat_Index_C']
        var_labels = {**EXPECTED_NUMERICAL_COLS, 'Heat_Index_C': 'Heat Index (°C)'}

        selected_var = st.selectbox(
            "Primary Weather Variable",
            options=variable_choices,
            format_func=lambda x: var_labels.get(x, x),
            index=variable_choices.index(st.session_state["primary_var"]) if st.session_state["primary_var"] in variable_choices else 0,
            help="Dynamically updates the focal parameter across all dashboard views."
        )
        st.session_state["primary_var"] = selected_var

        time_res = st.select_slider(
            "Time-Series Resolution",
            options=["Daily", "Weekly", "Monthly"],
            value="Daily",
            help="Aggregates high-frequency records for smooth rendering."
        )

        kpi_mode = st.radio(
            "Metric Mode",
            options=["Arithmetic Means", "Parametric Percentiles"],
            index=0,
            horizontal=True,
            help="Switch between standard arithmetic averages and robust non-parametric quantiles."
        )

        st.markdown(
            f"""
            <div style="font-size: 0.72rem; color: #6e7681; font-family: 'JetBrains Mono', monospace; margin-top: 24px; padding-top: 12px; border-top: 1px solid #21262d;">
                Dataset: {metadata['row_count']:,} rows<br>
                Memory: {metadata['memory_mb']} MB (optimized)<br>
                Engine: Vectorized NumPy / Pandas
            </div>
            """,
            unsafe_allow_html=True
        )

    # Filter Validation
    if not selected_locations:
        st.warning("No stations selected. Please select at least one station in the sidebar.")
        return

    if start_date is None or end_date is None:
        st.warning("Please choose a valid start and end date.")
        return

    # Filter Dataset
    df = filter_data(raw_df, locations=selected_locations, start_date=start_date, end_date=end_date)
    filtered_count = len(df)

    # Section A: Editorial Header
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
        st.warning("The selected filter parameters produced zero matching records. Please broaden your selection.")
        return

    # Section C: Summary Metrics (Responsive to KPI mode)
    metrics = get_summary_metrics(df)
    c1, c2, c3, c4 = st.columns(4)

    if kpi_mode == "Arithmetic Means":
        with c1:
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
        with c2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Average Humidity</div>
                    <div class="metric-value">{metrics['avg_humidity']:.1f}<span class="metric-unit">%</span></div>
                    <div class="metric-subtext">Relative atmospheric saturation</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Precipitation Rate</div>
                    <div class="metric-value">{metrics['mean_precip_rate']:.2f}<span class="metric-unit">mm/obs</span></div>
                    <div class="metric-subtext">Mean gauge rate across interval readings</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c4:
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
    else:
        # Parametric Quantile Displays (Robust Statistics)
        p = metrics.get('percentiles', {})
        t_p = p.get('Temperature_C', {})
        h_p = p.get('Humidity_pct', {})
        w_p = p.get('Wind_Speed_kmh', {})
        pr_p = p.get('Precipitation_mm', {})

        with c1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Median Temperature (P50)</div>
                    <div class="metric-value">{t_p.get('p50', 0):.1f}<span class="metric-unit">°C</span></div>
                    <div class="metric-subtext">IQR: {t_p.get('p25', 0):.1f}°C &mdash; {t_p.get('p75', 0):.1f}°C</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Median Humidity (P50)</div>
                    <div class="metric-value">{h_p.get('p50', 0):.1f}<span class="metric-unit">%</span></div>
                    <div class="metric-subtext">IQR: {h_p.get('p25', 0):.1f}% &mdash; {h_p.get('p75', 0):.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Median Precip Rate (P50)</div>
                    <div class="metric-value">{pr_p.get('p50', 0):.2f}<span class="metric-unit">mm</span></div>
                    <div class="metric-subtext">P90 Threshold: {pr_p.get('p90', 0):.2f} mm</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Median Wind Speed (P50)</div>
                    <div class="metric-value">{w_p.get('p50', 0):.1f}<span class="metric-unit">km/h</span></div>
                    <div class="metric-subtext">P90 Gusts: {w_p.get('p90', 0):.1f} km/h</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Tabbed Interactive Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "01 // Overview & Dynamics",
        "02 // Station Head-to-Head",
        "03 // Diurnal Cycles & Heat Index",
        "04 // Anomaly Detection",
        "05 // Data Explorer & Export"
    ])

    var_label = var_labels.get(selected_var, selected_var)

    # ---------------- TAB 1: OVERVIEW & DYNAMICS ----------------
    with tab1:
        # Time-Series Section
        st.markdown(f'<div class="chart-header">Temporal Evolution &mdash; {var_label} ({time_res})</div>', unsafe_allow_html=True)

        c_opt1, c_opt2 = st.columns([3, 1])
        with c_opt2:
            disagg = st.checkbox("Disaggregate by Station", value=False if len(selected_locations) > 3 else True)

        ts_df = aggregate_time_series(df, variable=selected_var, freq=time_res, by_location=disagg)

        if not ts_df.empty:
            if disagg and 'Location' in ts_df.columns:
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
                fig_ts.add_trace(go.Scatter(
                    x=ts_df['Date_Time'],
                    y=ts_df['mean'],
                    mode='lines',
                    name='Mean Value',
                    line=dict(color='#5a82a6', width=2),
                    hovertemplate='%{x|%b %d, %Y}<br>Mean: %{y:.2f}<extra></extra>'
                ))
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

            fig_ts = apply_editorial_theme(fig_ts, title=f"{var_label} Over Time", height=370)
            st.plotly_chart(fig_ts, use_container_width=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # Location Ranking and Distribution (Responsive to selected_var!)
        col_m1, col_m2 = st.columns([1, 1])

        with col_m1:
            st.markdown(f'<div class="chart-header">Station Ranking &mdash; {var_label}</div>', unsafe_allow_html=True)
            loc_df = get_location_comparison(df, metric=selected_var)

            if not loc_df.empty:
                fig_bar = go.Figure(go.Bar(
                    x=loc_df['mean'],
                    y=loc_df['Location'],
                    orientation='h',
                    marker=dict(color='#5a82a6', line=dict(color='#79a8d7', width=1)),
                    hovertemplate='<b>%{y}</b><br>Average: %{x:.2f}<extra></extra>'
                ))
                fig_bar = apply_editorial_theme(fig_bar, title=f"Mean {var_label} by Station", height=350)
                fig_bar.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_bar, use_container_width=True)

        with col_m2:
            st.markdown(f'<div class="chart-header">Frequency Distribution &mdash; {var_label}</div>', unsafe_allow_html=True)
            hist_sample = sample_for_visualization(df, max_points=50000)

            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=hist_sample[selected_var],
                nbinsx=45,
                marker=dict(color='rgba(90, 130, 166, 0.65)', line=dict(color='#79a8d7', width=0.8)),
                hovertemplate='Bin: %{x}<br>Count: %{y}<extra></extra>'
            ))

            var_mean = df[selected_var].mean()
            var_median = df[selected_var].median()

            fig_hist.add_vline(
                x=var_mean,
                line_dash="dash",
                line_color="#e6edf3",
                line_width=1.5,
                annotation_text=f"Mean: {var_mean:.1f}",
                annotation_position="top right",
                annotation_font=dict(size=10, color="#e6edf3", family="JetBrains Mono")
            )
            fig_hist.add_vline(
                x=var_median,
                line_dash="dot",
                line_color="#8b949e",
                line_width=1.5,
                annotation_text=f"Median: {var_median:.1f}",
                annotation_position="bottom right",
                annotation_font=dict(size=10, color="#8b949e", family="JetBrains Mono")
            )

            fig_hist = apply_editorial_theme(fig_hist, title=f"Distribution of {var_label}", height=350)
            st.plotly_chart(fig_hist, use_container_width=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # Bivariate Relationships & Correlation Matrix
        col_r1, col_r2 = st.columns([1, 1])

        with col_r1:
            st.markdown('<div class="chart-header">Bivariate Analysis &mdash; Temperature vs Humidity</div>', unsafe_allow_html=True)
            r_val = df['Temperature_C'].corr(df['Humidity_pct'])
            r_display = f"r = {r_val:.4f}" if pd.notnull(r_val) else "r = N/A"

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
            st.caption("Correlation coefficient r is calculated across all filtered rows. A visual sample is rendered to preserve UI performance.")

        with col_r2:
            st.markdown('<div class="chart-header">Cross-Variable Correlation Heatmap</div>', unsafe_allow_html=True)
            corr_matrix = calculate_correlation_matrix(df)

            if not corr_matrix.empty:
                labels_clean = [var_labels.get(c, c) for c in corr_matrix.columns]
                z_vals = corr_matrix.values

                fig_heat = go.Figure(data=go.Heatmap(
                    z=z_vals,
                    x=labels_clean,
                    y=labels_clean,
                    colorscale=[[0.0, "#0e1117"], [0.5, "#21262d"], [1.0, "#5a82a6"]],
                    zmin=-1.0,
                    zmax=1.0,
                    text=np.around(z_vals, 3),
                    texttemplate="%{text}",
                    textfont={"size": 11, "family": "JetBrains Mono", "color": "#f0f6fc"},
                    hoverongaps=False
                ))

                fig_heat = apply_editorial_theme(fig_heat, title="Pearson Correlation Matrix", height=350)
                st.plotly_chart(fig_heat, use_container_width=True)
                st.caption("Pearson r measures linear association only; correlation does not imply causation.")

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # Observations Section
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

    # ---------------- TAB 2: STATION HEAD-TO-HEAD ----------------
    with tab2:
        st.markdown('<div class="chart-header">Direct Station Comparison &mdash; Hypothesis Testing</div>', unsafe_allow_html=True)

        h2h_c1, h2h_c2, h2h_c3 = st.columns([1, 1, 1])
        with h2h_c1:
            station_a = st.selectbox("Station Alpha (A)", options=all_locs, index=all_locs.index("Phoenix") if "Phoenix" in all_locs else 0)
        with h2h_c2:
            station_b = st.selectbox("Station Beta (B)", options=all_locs, index=all_locs.index("Chicago") if "Chicago" in all_locs else 1)
        with h2h_c3:
            h2h_metric = st.selectbox("Comparison Variable", options=variable_choices, format_func=lambda x: var_labels.get(x, x), index=0)

        h2h_res = get_head_to_head_comparison(df, station_a, station_b, metric=h2h_metric)

        if h2h_res:
            m_unit = "°C" if "Temp" in h2h_metric or "Heat" in h2h_metric else ("%" if "Hum" in h2h_metric else "km/h")
            d1, d2, d3, d4 = st.columns(4)

            with d1:
                st.markdown(
                    f"""
                    <div class="delta-card">
                        <div class="delta-title">Mean ({station_a})</div>
                        <div class="delta-stat">{h2h_res['mean_a']:.2f} {m_unit}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with d2:
                st.markdown(
                    f"""
                    <div class="delta-card">
                        <div class="delta-title">Mean ({station_b})</div>
                        <div class="delta-stat">{h2h_res['mean_b']:.2f} {m_unit}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with d3:
                delta_val = h2h_res['delta_mean']
                st.markdown(
                    f"""
                    <div class="delta-card">
                        <div class="delta-title">Delta (A &minus; B)</div>
                        <div class="delta-stat" style="color: {'#79a8d7' if delta_val >= 0 else '#e06c75'};">
                            {delta_val:+.2f} {m_unit}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with d4:
                spread_val = abs(h2h_res['std_a'] - h2h_res['std_b'])
                st.markdown(
                    f"""
                    <div class="delta-card">
                        <div class="delta-title">Std Deviation Spread</div>
                        <div class="delta-stat">{spread_val:.2f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

            # Side-by-side distribution overlay
            df_a = df[df['Location'] == station_a]
            df_b = df[df['Location'] == station_b]

            samp_a = sample_for_visualization(df_a, max_points=20000)
            samp_b = sample_for_visualization(df_b, max_points=20000)

            fig_h2h = go.Figure()
            fig_h2h.add_trace(go.Histogram(
                x=samp_a[h2h_metric],
                name=f"{station_a} (n={len(df_a):,})",
                marker_color='rgba(90, 130, 166, 0.6)',
                nbinsx=40
            ))
            fig_h2h.add_trace(go.Histogram(
                x=samp_b[h2h_metric],
                name=f"{station_b} (n={len(df_b):,})",
                marker_color='rgba(121, 168, 215, 0.6)',
                nbinsx=40
            ))
            fig_h2h.update_layout(barmode='overlay')
            fig_h2h = apply_editorial_theme(
                fig_h2h,
                title=f"Comparative Distribution Overlay: {station_a} vs {station_b} ({var_labels.get(h2h_metric, h2h_metric)})",
                height=380
            )
            st.plotly_chart(fig_h2h, use_container_width=True)
        else:
            st.info("Please ensure both selected stations have active observations in the filtered dataset.")

    # ---------------- TAB 3: DIURNAL CYCLES & HEAT INDEX ----------------
    with tab3:
        st.markdown('<div class="chart-header">Diurnal 24-Hour Cycle & Atmospheric Heat Index</div>', unsafe_allow_html=True)

        diurnal_c1, diurnal_c2 = st.columns([1, 1])

        with diurnal_c1:
            st.markdown('<div class="chart-header">Diurnal Cycle (Hour 00 to 23)</div>', unsafe_allow_html=True)
            diurnal_var = st.selectbox(
                "Diurnal Metric",
                options=['Temperature_C', 'Humidity_pct', 'Wind_Speed_kmh', 'Heat_Index_C'],
                format_func=lambda x: var_labels.get(x, x),
                index=0
            )
            diurnal_df = aggregate_diurnal_cycle(df, variable=diurnal_var)

            if not diurnal_df.empty:
                fig_diurnal = go.Figure()
                fig_diurnal.add_trace(go.Scatter(
                    x=diurnal_df['Hour'],
                    y=diurnal_df['mean'],
                    mode='lines+markers',
                    name='Hourly Mean',
                    line=dict(color='#5a82a6', width=2.2),
                    marker=dict(size=5, color='#79a8d7'),
                    hovertemplate='Hour %{x}:00<br>Mean: %{y:.2f}<extra></extra>'
                ))
                fig_diurnal.add_trace(go.Scatter(
                    x=diurnal_df['Hour'],
                    y=diurnal_df['mean'] + diurnal_df['std'],
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                fig_diurnal.add_trace(go.Scatter(
                    x=diurnal_df['Hour'],
                    y=diurnal_df['mean'] - diurnal_df['std'],
                    mode='lines',
                    line=dict(width=0),
                    fill='tonexty',
                    fillcolor='rgba(90, 130, 166, 0.12)',
                    name='±1 Std Deviation',
                    hoverinfo='skip'
                ))
                fig_diurnal = apply_editorial_theme(
                    fig_diurnal,
                    title=f"24-Hour Cycle of {var_labels.get(diurnal_var, diurnal_var)}",
                    height=360
                )
                fig_diurnal.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=2))
                st.plotly_chart(fig_diurnal, use_container_width=True)

        with diurnal_c2:
            st.markdown('<div class="chart-header">Biometeorology &mdash; Apparent vs Dry-Bulb Temperature</div>', unsafe_allow_html=True)
            hi_sample = sample_for_visualization(df, max_points=3000)

            fig_hi = go.Figure()
            fig_hi.add_trace(go.Scatter(
                x=hi_sample['Temperature_C'],
                y=hi_sample['Heat_Index_C'],
                mode='markers',
                marker=dict(
                    color=hi_sample['Humidity_pct'],
                    colorscale=[[0.0, "#21262d"], [0.5, "#5a82a6"], [1.0, "#79a8d7"]],
                    size=4,
                    colorbar=dict(title=dict(text="Humidity (%)", font=dict(size=10, color="#8b949e"))),
                    opacity=0.65
                ),
                hovertemplate='Dry Temp: %{x:.1f}°C<br>Heat Index: %{y:.1f}°C<extra></extra>'
            ))
            fig_hi = apply_editorial_theme(
                fig_hi,
                title="NOAA Rothfusz Apparent Temperature Index",
                height=360
            )
            fig_hi.update_layout(xaxis_title="Measured Temperature (°C)", yaxis_title="Heat Index (°C)")
            st.plotly_chart(fig_hi, use_container_width=True)

        st.markdown(
            """
            <div class="limitation-box">
                <b>Biometeorological Methodology:</b> The Heat Index is derived using the standard National Oceanic and Atmospheric Administration (NOAA)
                Rothfusz regression equation. It models perceived thermal stress on the human body resulting from ambient temperature and relative humidity.
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------------- TAB 4: ANOMALY DETECTION ----------------
    with tab4:
        st.markdown('<div class="chart-header">Unsupervised Anomaly Detection &mdash; Standardized Z-Score</div>', unsafe_allow_html=True)

        ano_c1, ano_c2 = st.columns([1, 3])
        with ano_c1:
            ano_var = st.selectbox(
                "Anomaly Feature",
                options=['Temperature_C', 'Wind_Speed_kmh', 'Precipitation_mm'],
                format_func=lambda x: var_labels.get(x, x),
                index=0
            )
            z_thresh = st.slider("Z-Score Threshold (|Z| >= threshold)", min_value=1.5, max_value=3.0, value=2.0, step=0.1)

        anomalies_df = detect_anomalies(df, variable=ano_var, threshold_z=z_thresh, max_records=50)

        with ano_c2:
            st.markdown(
                f"""
                <div style="font-size: 0.82rem; color: #8b949e; padding: 12px 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px;">
                    Standardized Z-Score: <code>Z = (x &minus; &mu;) / &sigma;</code><br>
                    Identifies values that deviate drastically from population norms. In this dataset, a threshold of <code>|Z| &ge; 2.0</code>
                    successfully isolates Phoenix's sub-zero extreme records (temperatures dropping to &minus;19.97°C) and peak wind velocity events.
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        if not anomalies_df.empty:
            st.markdown(f"**Identified Outliers ({len(anomalies_df)} top anomalies displayed):**")
            st.dataframe(anomalies_df, use_container_width=True, hide_index=True)
        else:
            st.info(f"No statistical anomalies detected at |Z| >= {z_thresh}. Lower the threshold to capture more moderate deviations.")

    # ---------------- TAB 5: DATA EXPLORER & EXPORT ----------------
    with tab5:
        st.markdown('<div class="chart-header">Data Explorer &mdash; Filtered Record Inspection</div>', unsafe_allow_html=True)

        exp_c1, exp_c2 = st.columns([3, 1])
        with exp_c1:
            selected_cols = st.multiselect(
                "Visible Columns",
                options=list(df.columns),
                default=list(df.columns),
                help="Select columns to inspect in the preview table."
            )
        with exp_c2:
            preview_rows = st.selectbox(
                "Preview Rows",
                options=[25, 50, 100, 250, 500],
                index=1,
                help="Number of records to preview."
            )

        st.dataframe(
            df[selected_cols].head(preview_rows),
            use_container_width=True,
            hide_index=True
        )

        st.markdown(
            f"<span style='font-family: JetBrains Mono; font-size: 0.75rem; color: #8b949e;'>Displaying top {min(preview_rows, len(df))} of {len(df):,} filtered records.</span>",
            unsafe_allow_html=True
        )

        # Functional CSV Export
        export_count = min(50000, len(df))
        csv_bytes = df[selected_cols].head(export_count).to_csv(index=False).encode('utf-8')

        st.download_button(
            label=f"Export Filtered Records ({export_count:,} rows as CSV)",
            data=csv_bytes,
            file_name="haze_filtered_weather.csv",
            mime="text/csv",
            help="Exports filtered rows directly to CSV."
        )


if __name__ == "__main__":
    main()
