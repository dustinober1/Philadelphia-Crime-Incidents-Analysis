"""
Correlations page renderer.

Displays external data correlations (weather, economic).
"""

import streamlit as st
import pandas as pd
from pathlib import Path


def render_correlations_page(df: pd.DataFrame) -> None:
    """
    Render the Correlations page.

    Args:
        df: Filtered DataFrame.
    """
    st.header(":chart_with_upwards_trend: External Data Correlations")

    st.caption("Correlations with weather and economic factors")

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
