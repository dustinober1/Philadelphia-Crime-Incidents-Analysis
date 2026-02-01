"""
Temporal Trends page renderer.

Displays time series plots and seasonal patterns using analysis module functions.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from dashboard.components.cache import load_cached_report


def render_temporal_page(df: pd.DataFrame) -> None:
    """
    Render the Temporal Trends page.

    Args:
        df: Filtered DataFrame.
    """
    st.header(":clock: Temporal Trends")

    st.caption("Time-based patterns and trends in crime incidents")

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
        sample_size = min(500000, len(df))
        df_sample = df.sample(n=sample_size, random_state=42) if len(df) > sample_size else df

        try:
            # Display basic temporal visualizations using Streamlit native charts
            st.subheader("Yearly Trend")

            if "year" in df_sample.columns:
                year_counts = df_sample["year"].value_counts().sort_index()
                st.line_chart(year_counts)

                # Year-over-year change
                if len(year_counts) > 1:
                    yoy_change = year_counts.pct_change() * 100
                    st.bar_chart(yoy_change)

            st.subheader("Monthly Distribution")

            if "month" in df_sample.columns:
                month_names = {
                    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
                }
                month_counts = df_sample["month"].value_counts().sort_index()
                month_counts.index = month_counts.index.map(lambda x: month_names.get(x, str(x)))
                st.bar_chart(month_counts)

            st.subheader("Day of Week Distribution")

            if "day_of_week" in df_sample.columns:
                dow_names = {
                    0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"
                }
                dow_counts = df_sample["day_of_week"].value_counts().sort_index()
                dow_counts.index = dow_counts.index.map(lambda x: dow_names.get(x, str(x)))
                st.bar_chart(dow_counts)

            st.subheader("Seasonal Patterns")

            col1, col2 = st.columns(2)

            with col1:
                if "season" in df_sample.columns:
                    season_counts = df_sample["season"].value_counts()
                    st.bar_chart(season_counts)

            with col2:
                if "hour" in df_sample.columns:
                    # Bin hours into time periods
                    hour_counts = df_sample["hour"].value_counts().sort_index()
                    st.line_chart(hour_counts)

            st.caption("Note: For full statistical analysis with significance testing, uncheck 'Use filtered data' to view the pre-generated report.")

        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.info("Try unchecking 'Use filtered data' to view the pre-generated report.")
