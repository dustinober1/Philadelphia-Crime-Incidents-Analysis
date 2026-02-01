"""
Correlations page renderer.

Displays external data correlations (weather, economic).
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from dashboard.components import (
    get_selection_state,
    get_active_filter_kwargs,
    clear_selection_state,
    has_active_selection,
)
from dashboard.components.cache import apply_filters


def render_correlations_page(full_df: pd.DataFrame, filtered_df: pd.DataFrame) -> None:
    """
    Render the Correlations page.

    Args:
        full_df: The complete, unfiltered DataFrame.
        filtered_df: The currently filtered DataFrame.
    """
    st.header(":chart_with_upwards_trend: External Data Correlations")

    st.caption("Correlations with weather and economic factors")

    # Get selection state for cross-filtering
    selection_state = get_selection_state()

    # Display active cross-filter hint and clear button
    if selection_state.active_view and selection_state.active_view != "correlations":
        source_view_name = selection_state.active_view.title()

        # Format selection details for display
        selection_details = []
        if selection_state.active_districts:
            selection_details.append(f"Districts: {', '.join(map(str, selection_state.active_districts[:5]))}{'...' if len(selection_state.active_districts) > 5 else ''}")
        if selection_state.active_crime_types:
            selection_details.append(f"Crime Types: {', '.join(selection_state.active_crime_types[:3])}{'...' if len(selection_state.active_crime_types) > 3 else ''}")
        if selection_state.active_time_range:
            selection_details.append(f"Time Range: {selection_state.active_time_range[0]} to {selection_state.active_time_range[1]}")

        selection_info = ", ".join(selection_details) if selection_details else "Active selection"

        col1, col2 = st.columns([4, 1])
        with col1:
            st.info(f":link: **Active cross-filter from {source_view_name} view**: {selection_info}")
        with col2:
            if st.button(":x: Clear", key="correlations_clear"):
                clear_selection_state()
                st.rerun()

        # Apply cross-filter if active selection from other views
        cross_filter_kwargs = get_active_filter_kwargs()
        if cross_filter_kwargs:
            filtered_df = apply_filters(filtered_df, **cross_filter_kwargs)
            st.caption(f":information_source: Analysis based on {len(filtered_df):,} records after cross-filter")

    # Check for correlation reports
    correlation_report = Path("reports/12_report_correlations.md")

    if correlation_report.exists():
        st.info(":memo: Displaying pre-generated correlation analysis report")

        with st.spinner("Loading report..."):
            report_content = correlation_report.read_text()

        # Display as markdown
        st.markdown(report_content)
    else:
        st.warning("""
        **Correlation analysis report not found**

        The correlation analysis report (`reports/12_report_correlations.md`)
        has not been generated yet.

        To generate this report, run:
        ```bash
        python analysis/12_report_correlations.py
        ```

        Note: External data sources require API keys:
        - FRED API for unemployment data
        - Census API for income/poverty data

        See `.env.example` for setup instructions.
        """)

        # Show what correlations would be available
        st.subheader("Expected Correlation Analyses")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **Weather-Crime Correlations**

            - Temperature vs. Crime count
            - Precipitation vs. Crime count
            - Lagged effects (1-7 days)
            - Seasonal patterns

            *Data source: Meteostat API*
            """)

        with col2:
            st.markdown("""
            **Economic-Crime Correlations**

            - Unemployment rate vs. Crime
            - Median income vs. Crime
            - Poverty rate vs. Crime
            - Detrended correlations

            *Data sources: FRED API, Census ACS API*
            """)
