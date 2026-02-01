"""
Philadelphia Crime Incidents Dashboard - Main Entry Point.

Run with: streamlit run dashboard/app.py
"""

import streamlit as st
from pathlib import Path

from dashboard.config import DISPLAY_CONFIG, PAGE_NAMES, FILTER_DEFAULTS
from dashboard.components.cache import load_crime_data, get_data_summary, apply_filters
from dashboard.filters.time_filters import render_time_filters, get_filter_dates
from dashboard.filters.geo_filters import render_geo_filters, get_filter_districts
from dashboard.filters.crime_filters import render_crime_filters, get_filter_categories, get_filter_crime_types

# Configure page
st.set_page_config(
    page_title="Philadelphia Crime Dashboard",
    page_icon=":police_car:",
    layout=DISPLAY_CONFIG["layout"],
    initial_sidebar_state="expanded",
)

# Custom CSS for professional appearance
def _load_custom_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Main dashboard entry point."""
    _load_custom_css()

    # Title
    st.title(DISPLAY_CONFIG["title"])
    st.markdown(f"<p class='sub-header'>{DISPLAY_CONFIG['subtitle']}</p>", unsafe_allow_html=True)

    # Load data (cached)
    with st.spinner("Loading data..."):
        df = load_crime_data()

    # Render time filters in sidebar
    time_state = render_time_filters()
    start_date, end_date = get_filter_dates(time_state)

    # Apply time filters first (to limit other filter options)
    df_time_filtered = apply_filters(df, start_date=start_date, end_date=end_date)

    # Render geo filters
    geo_state = render_geo_filters(df_time_filtered)
    selected_districts = get_filter_districts(geo_state)

    # Apply time + geo filters
    df_tg_filtered = apply_filters(
        df,
        start_date=start_date,
        end_date=end_date,
        districts=selected_districts,
    )

    # Render crime filters
    crime_state = render_crime_filters(df_tg_filtered)
    selected_categories = get_filter_categories(crime_state)
    selected_crime_types = get_filter_crime_types(crime_state)

    # Apply all filters
    filtered_df = apply_filters(
        df,
        start_date=start_date,
        end_date=end_date,
        districts=selected_districts,
        crime_categories=selected_categories,
        crime_types=selected_crime_types,
    )

    # Display summary stats
    summary = get_data_summary(filtered_df)

    st.subheader(f"Filtered Summary: {start_date} to {end_date}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Records", f"{summary['total_records']:,}")
    with col2:
        st.metric("Years", summary.get('years', 'N/A'))
    with col3:
        district_count = len(selected_districts)
        total_districts = summary.get('districts', 23)
        st.metric("Districts", f"{district_count}/{total_districts}")
    with col4:
        coord_pct = summary.get('coord_coverage', {}).get('percentage', 0)
        st.metric("Valid Coordinates", f"{coord_pct:.1f}%")

    # Show active filters
    filter_info = []

    if len(selected_districts) < 23:
        filter_info.append(f"Districts: {', '.join(f'D{d}' for d in sorted(selected_districts))}")

    if len(selected_categories) < 3:
        filter_info.append(f"Categories: {', '.join(selected_categories)}")

    if filter_info:
        st.caption(" | ".join(filter_info))
    else:
        st.caption(":map: All districts, :mag: All categories")

    st.caption(f":link: Share this view: URL encodes your current filter settings")

    st.markdown("---")
    st.info("Main visualizations will be added in plan 04-06.")

if __name__ == "__main__":
    main()
