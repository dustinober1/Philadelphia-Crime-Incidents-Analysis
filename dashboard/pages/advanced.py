"""
Advanced Temporal page renderer.

Displays holiday effects, crime type profiles, and shift analysis.
"""

import streamlit as st
import pandas as pd
from pathlib import Path


def render_advanced_page(df: pd.DataFrame) -> None:
    """
    Render the Advanced Temporal page.

    Args:
        df: Filtered DataFrame.
    """
    st.header(":calendar: Advanced Temporal Analysis")

    st.caption("Holiday effects, crime type profiles, and shift patterns")

    # Check for advanced temporal report
    advanced_report = Path("reports/16_advanced_temporal_analysis_report.md")

    if advanced_report.exists():
        st.info(":memo: Displaying pre-generated advanced temporal analysis report")

        with st.spinner("Loading report..."):
            report_content = advanced_report.read_text()

        # Show executive summary by default
        with st.expander(":eye: Executive Summary", expanded=True):
            # Extract executive summary
            lines = report_content.split("\n")
            summary_lines = []
            in_summary = False
            for line in lines:
                if line.startswith("## Executive Summary") or line.startswith("## Key Findings"):
                    in_summary = True
                elif in_summary and line.startswith("## ") and "Executive" not in line and "Key" not in line:
                    break
                if in_summary:
                    summary_lines.append(line)

            if summary_lines:
                st.markdown("\n".join(summary_lines))
            else:
                st.markdown("*Executive summary not found in report*")

        # Holiday effects section
        with st.expander(":calendar: Holiday Effects Analysis"):
            st.markdown("""
            **Holiday Effects Analysis**

            This section examines how crime rates change around major US holidays.

            **Analysis includes:**
            - Pre-holiday period (3 days before)
            - Holiday day
            - Post-holiday period (3 days after)

            **Holidays analyzed:**
            - New Year's Day
            - Martin Luther King Jr. Day
            - Presidents Day
            - Memorial Day
            - Independence Day
            - Labor Day
            - Columbus Day
            - Veterans Day
            - Thanksgiving
            - Christmas Day
            - And more...

            See full report for detailed statistical analysis with FDR correction.
            """)

            # Try to extract holiday section
            lines = report_content.split("\n")
            holiday_lines = []
            in_holiday = False
            for line in lines:
                if "## Holiday" in line or "## Holiday Effects" in line:
                    in_holiday = True
                elif in_holiday and line.startswith("## ") and "Holiday" not in line:
                    break
                if in_holiday:
                    holiday_lines.append(line)

            if holiday_lines and len(holiday_lines) > 5:
                if st.button("Load Holiday Effects Details"):
                    st.markdown("\n".join(holiday_lines))

        # Crime type profiles section
        with st.expander(":mag: Crime Type Profiles"):
            st.markdown("""
            **Individual Crime Type Analysis**

            This section provides detailed temporal and spatial analysis for specific crime types.

            **Crime types analyzed:**
            - Homicide
            - Burglary
            - Theft
            - Vehicle Theft
            - Aggravated Assault

            **Analysis includes:**
            - Long-term temporal trends (Mann-Kendall test)
            - Seasonal patterns
            - Geographic distribution (DBSCAN clustering)
            - Time of day patterns

            See full report for detailed crime type profiles.
            """)

            # Try to extract crime type section
            lines = report_content.split("\n")
            crime_type_lines = []
            in_crime_type = False
            for line in lines:
                if "## Crime Type" in line or "## Individual Crime" in line:
                    in_crime_type = True
                elif in_crime_type and line.startswith("## ") and "Crime Type" not in line and "Individual Crime" not in line:
                    break
                if in_crime_type:
                    crime_type_lines.append(line)

            if crime_type_lines and len(crime_type_lines) > 5:
                if st.button("Load Crime Type Details"):
                    st.markdown("\n".join(crime_type_lines))

        # Shift analysis section
        with st.expander(":clock: Shift Analysis"):
            st.markdown("""
            **Shift-by-Shift Analysis**

            This section analyzes crime patterns across four patrol shifts.

            **Shift definitions:**
            - Late Night (12AM-6AM)
            - Morning (6AM-12PM)
            - Afternoon (12PM-6PM)
            - Evening (6PM-12AM)

            **Analysis includes:**
            - Shift distribution for all crimes
            - Crime type distribution by shift
            - Statistical testing (Chi-square, Cramer's V)
            - Staffing recommendations

            See full report for detailed shift analysis.
            """)

            # Try to extract shift section
            lines = report_content.split("\n")
            shift_lines = []
            in_shift = False
            for line in lines:
                if "## Shift" in line or "## Shift-by-Shift" in line:
                    in_shift = True
                elif in_shift and line.startswith("## ") and "Shift" not in line:
                    break
                if in_shift:
                    shift_lines.append(line)

            if shift_lines and len(shift_lines) > 5:
                if st.button("Load Shift Analysis Details"):
                    st.markdown("\n".join(shift_lines))

        # Cross-analysis section
        with st.expander(":link: Cross-Analysis"):
            st.markdown("""
            **Cross-Analysis: Inter-relationships Between Temporal Dimensions**

            This section examines how different temporal dimensions interact:
            - Holiday effects by crime type
            - Shift patterns by season
            - Crime type patterns by time of day

            See full report for detailed cross-analysis.
            """)

        # Option to view full report
        st.markdown("---")
        if st.button(":book: View Full Report", use_container_width=True):
            st.markdown(report_content)

    else:
        st.warning("""
        **Advanced temporal analysis report not found**

        The unified advanced temporal report
        (`reports/16_advanced_temporal_analysis_report.md`) has not been generated yet.

        To generate this report, run:
        ```bash
        python analysis/03-04-advanced_temporal_report.py
        ```

        **This report combines:**
        - Holiday effects analysis (03-01-holiday_effects.py)
        - Crime type profiles (03-02-crime_type_profiles.py)
        - Shift analysis (03-03-shift_analysis.py)
        """)
