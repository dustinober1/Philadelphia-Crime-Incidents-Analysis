"""
Overview/Stats page renderer.

Displays summary statistics, key metrics, and high-level insights.
"""

import streamlit as st
import pandas as pd

from dashboard.components.cache import get_data_summary


def render_overview_page(df: pd.DataFrame) -> None:
    """
    Render the Overview/Stats page.

    Args:
        df: Filtered DataFrame.
    """
    st.header(":bar_chart: Overview & Statistics")

    st.caption("High-level metrics and summary statistics for the filtered dataset")

    # Get summary statistics
    summary = get_data_summary(df)

    # Key metrics row
    st.subheader("Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Incidents",
            value=f"{summary['total_records']:,}",
            delta=None,
        )

    with col2:
        years = summary.get('years', 'N/A')
        st.metric(
            label="Time Span",
            value=f"{years} years" if isinstance(years, int) else years,
        )

    with col3:
        districts = summary.get('districts', 'N/A')
        st.metric(
            label="Police Districts",
            value=str(districts),
        )

    with col4:
        coord_pct = summary.get('coord_coverage', {}).get('percentage', 0)
        st.metric(
            label="Valid Coordinates",
            value=f"{coord_pct:.1f}%",
        )

    # Crime category breakdown
    st.subheader("Crime Category Distribution")

    if "crime_category" in df.columns:
        category_counts = df["crime_category"].value_counts()

        col1, col2, col3 = st.columns(3)

        with col1:
            violent = category_counts.get("Violent", 0)
            st.metric("Violent Crimes", f"{violent:,}")

        with col2:
            property_crime = category_counts.get("Property", 0)
            st.metric("Property Crimes", f"{property_crime:,}")

        with col3:
            other = category_counts.get("Other", 0)
            st.metric("Other Offenses", f"{other:,}")

        # Simple bar chart using Streamlit
        st.bar_chart(category_counts)

    # Temporal breakdown
    st.subheader("Temporal Distribution")

    col1, col2 = st.columns(2)

    with col1:
        if "year" in df.columns:
            year_counts = df["year"].value_counts().sort_index()
            st.line_chart(year_counts)

    with col2:
        if "season" in df.columns:
            season_counts = df["season"].value_counts()
            st.bar_chart(season_counts)

    # District breakdown
    st.subheader("District Distribution")

    if "dc_dist" in df.columns:
        district_counts = df["dc_dist"].value_counts().sort_index().head(10)
        st.bar_chart(district_counts)
