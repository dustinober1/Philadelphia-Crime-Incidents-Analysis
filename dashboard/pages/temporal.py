"""
Temporal Trends page renderer.

Displays time series plots and seasonal patterns using analysis module functions.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

from dashboard.components.cache import load_cached_report
from dashboard.components import (
    register_plotly_selection,
    update_selection_from_event,
    get_selection_state,
    get_active_filter_kwargs,
    clear_selection_state,
    has_active_selection,
)
from dashboard.config import PLOTLY_CONFIG


def render_temporal_page(full_df: pd.DataFrame, filtered_df: pd.DataFrame) -> None:
    """
    Render the Temporal Trends page.

    Args:
        full_df: The complete, unfiltered DataFrame.
        filtered_df: The currently filtered DataFrame.
    """
    st.header(":clock: Temporal Trends")

    st.caption("Time-based patterns and trends in crime incidents")

    # Get selection state for cross-filtering
    selection_state = get_selection_state()

    # Display active cross-filter hint and clear button
    if selection_state.active_view and selection_state.active_view != "temporal":
        source_view_name = selection_state.active_view.title()
        col1, col2 = st.columns([4, 1])
        with col1:
            st.info(f":link: **Active cross-filter from {source_view_name} view**")
        with col2:
            if st.button(":x: Clear", key="temporal_clear"):
                clear_selection_state()
                st.rerun()

    # Apply cross-filter if active selection from other views
    if selection_state.active_view and selection_state.active_view != "temporal":
        from dashboard.components.cache import apply_filters
        cross_filter_kwargs = get_active_filter_kwargs()
        if cross_filter_kwargs:
            filtered_df = apply_filters(filtered_df, **cross_filter_kwargs)

    # Option: Show pre-generated report OR run filtered analysis
    col1, col2 = st.columns([3, 1])

    with col2:
        use_filtered = st.checkbox(
            "Use filtered data",
            value=False,
            help="Uncheck to view full analysis report (faster). Check to analyze current filter."
        )

    if not use_filtered:
        # Display pre-generated report (CONTEXT.md decision: "Existing reports embedded")
        st.info(":memo: Displaying pre-generated temporal analysis from EDA report (full dataset)")

        # Try multiple possible report paths
        report_paths = [
            "reports/02_temporal_analysis_report.md",
            "reports/01_eda_report.md",
        ]

        report_found = False
        for report_path in report_paths:
            try:
                report_content = load_cached_report(report_path)
                if report_content:
                    # Extract temporal section if in EDA report
                    if "01_eda_report.md" in report_path:
                        st.markdown("### Temporal Analysis Section")
                        # Look for temporal section in the report
                        lines = report_content.split("\n")
                        temporal_lines = []
                        in_temporal = False
                        for i, line in enumerate(lines):
                            if "## Temporal" in line or "## Time" in line:
                                in_temporal = True
                            elif in_temporal and line.startswith("## ") and "Temporal" not in line and "Time" not in line:
                                break
                            if in_temporal:
                                temporal_lines.append(line)

                        if temporal_lines:
                            st.markdown("\n".join(temporal_lines))
                        else:
                            # If no temporal section found, show full report
                            st.markdown(report_content)
                    else:
                        st.markdown(report_content)

                    report_found = True
                    break
            except Exception:
                continue

        if not report_found:
            st.warning("""
            **Temporal analysis report not found**

            The temporal analysis report has not been generated yet.

            To generate this report, run:
            ```bash
            python analysis/temporal_analysis.py
            ```
            """)
    else:
        # Run analysis on filtered data (reuses analysis module logic)
        st.warning(":hourglass: Analyzing filtered data - this may take a moment...")

        # Sample for performance if dataset is large
        sample_size = min(500000, len(filtered_df))
        df_sample = filtered_df.sample(n=sample_size, random_state=42) if len(filtered_df) > sample_size else filtered_df

        try:
            # Display basic temporal visualizations using Plotly for cross-filtering
            st.subheader("Yearly Trend")

            if "year" in df_sample.columns:
                year_counts = df_sample["year"].value_counts().sort_index().reset_index()
                year_counts.columns = ["year", "count"]

                fig_years = px.line(year_counts, x="year", y="count",
                                    labels={"year": "Year", "count": "Number of Incidents"},
                                    title="Yearly Trend",
                                    markers=True)

                fig_years = register_plotly_selection(fig_years, key="temporal_years")
                selection_event_years = st.plotly_chart(fig_years, on_select="rerun", key="temporal_years_chart", use_container_width=True)

                if selection_event_years.selection["points"]:
                    update_selection_from_event(selection_event_years, source_view="temporal")

                # Year-over-year change
                if len(year_counts) > 1:
                    yoy_change = year_counts["count"].pct_change() * 100
                    fig_yoy = px.bar(x=year_counts["year"], y=yoy_change,
                                     labels={"x": "Year", "y": "% Change"},
                                     title="Year-over-Year Change")
                    st.plotly_chart(fig_yoy, use_container_width=True)

            st.subheader("Monthly Distribution")

            if "month" in df_sample.columns:
                month_names = {
                    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
                }
                month_counts = df_sample["month"].value_counts().sort_index().reset_index()
                month_counts.columns = ["month", "count"]
                month_counts["month_name"] = month_counts["month"].map(lambda x: month_names.get(x, str(x)))

                fig_months = px.bar(month_counts, x="month_name", y="count",
                                    labels={"month_name": "Month", "count": "Number of Incidents"},
                                    title="Monthly Distribution")

                fig_months = register_plotly_selection(fig_months, key="temporal_months")
                selection_event_months = st.plotly_chart(fig_months, on_select="rerun", key="temporal_months_chart", use_container_width=True)

                if selection_event_months.selection["points"]:
                    update_selection_from_event(selection_event_months, source_view="temporal")

            st.subheader("Day of Week Distribution")

            if "day_of_week" in df_sample.columns:
                dow_names = {
                    0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"
                }
                dow_counts = df_sample["day_of_week"].value_counts().sort_index().reset_index()
                dow_counts.columns = ["day_of_week", "count"]
                dow_counts["dow_name"] = dow_counts["day_of_week"].map(lambda x: dow_names.get(x, str(x)))

                fig_dow = px.bar(dow_counts, x="dow_name", y="count",
                                 labels={"dow_name": "Day of Week", "count": "Number of Incidents"},
                                 title="Day of Week Distribution")

                fig_dow = register_plotly_selection(fig_dow, key="temporal_dow")
                selection_event_dow = st.plotly_chart(fig_dow, on_select="rerun", key="temporal_dow_chart", use_container_width=True)

                if selection_event_dow.selection["points"]:
                    update_selection_from_event(selection_event_dow, source_view="temporal")

            st.subheader("Seasonal Patterns")

            col1, col2 = st.columns(2)

            with col1:
                if "season" in df_sample.columns:
                    season_counts = df_sample["season"].value_counts().reset_index()
                    season_counts.columns = ["season", "count"]

                    fig_seasons = px.bar(season_counts, x="season", y="count",
                                         labels={"season": "Season", "count": "Number of Incidents"},
                                         title="Seasonal Patterns")

                    fig_seasons = register_plotly_selection(fig_seasons, key="temporal_seasons")
                    selection_event_seasons = st.plotly_chart(fig_seasons, on_select="rerun", key="temporal_seasons_chart", use_container_width=True)

                    if selection_event_seasons.selection["points"]:
                        update_selection_from_event(selection_event_seasons, source_view="temporal")

            with col2:
                if "hour" in df_sample.columns:
                    # Bin hours into time periods
                    hour_counts = df_sample["hour"].value_counts().sort_index().reset_index()
                    hour_counts.columns = ["hour", "count"]

                    fig_hours = px.line(hour_counts, x="hour", y="count",
                                        labels={"hour": "Hour of Day", "count": "Number of Incidents"},
                                        title="Hourly Distribution",
                                        markers=True)

                    fig_hours = register_plotly_selection(fig_hours, key="temporal_hours")
                    selection_event_hours = st.plotly_chart(fig_hours, on_select="rerun", key="temporal_hours_chart", use_container_width=True)

                    if selection_event_hours.selection["points"]:
                        update_selection_from_event(selection_event_hours, source_view="temporal")

            st.caption("Note: For full statistical analysis with significance testing, uncheck 'Use filtered data' to view the pre-generated report.")

        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.info("Try unchecking 'Use filtered data' to view the pre-generated report.")
