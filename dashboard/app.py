"""
Philadelphia Crime Incidents Dashboard - Main Entry Point.

Run with: streamlit run dashboard/app.py
"""

import streamlit as st
from pathlib import Path

from dashboard.config import DISPLAY_CONFIG, PAGE_NAMES
from dashboard.components.cache import load_crime_data, apply_filters
from dashboard.filters.time_filters import render_time_filters, get_filter_dates
from dashboard.filters.geo_filters import render_geo_filters, get_filter_districts
from dashboard.filters.crime_filters import render_crime_filters, get_filter_categories, get_filter_crime_types
from dashboard.pages import (
    render_overview_page,
    render_temporal_page,
    render_spatial_page,
    render_correlations_page,
    render_advanced_page,
)

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
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
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
    with st.spinner("Loading data (first load takes ~10s)..."):
        df = load_crime_data()

    # Sidebar: Render all filters
    with st.sidebar:
        st.header(":wrench: Filters")

        # Time filters
        time_state = render_time_filters()
        start_date, end_date = get_filter_dates(time_state)

        st.markdown("---")

        # Geo filters (depends on time filter)
        df_time_filtered = apply_filters(df, start_date=start_date, end_date=end_date)
        geo_state = render_geo_filters(df_time_filtered)
        selected_districts = get_filter_districts(geo_state)

        st.markdown("---")

        # Crime filters (depends on time + geo)
        df_tg_filtered = apply_filters(
            df, start_date=start_date, end_date=end_date, districts=selected_districts
        )
        crime_state = render_crime_filters(df_tg_filtered)
        selected_categories = get_filter_categories(crime_state)
        selected_crime_types = get_filter_crime_types(crime_state)

        st.markdown("---")
        st.caption("Dashboard v1.0 | Phase 4")

    # Apply all filters
    filtered_df = apply_filters(
        df,
        start_date=start_date,
        end_date=end_date,
        districts=selected_districts,
        crime_categories=selected_categories,
        crime_types=selected_crime_types,
    )

    # Filter summary banner
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Records", f"{len(filtered_df):,}")
        with col2:
            st.metric("Date Range", f"{start_date[:4]}-{end_date[:4]}")
        with col3:
            st.metric("Districts", len(selected_districts))
        with col4:
            st.metric("Categories", len(selected_categories))

    # Show active filters
    filter_info = []

    if len(selected_districts) < 25:  # 25 districts in data
        filter_info.append(f"Districts: {', '.join(f'D{d}' for d in sorted(selected_districts))}")

    if len(selected_categories) < 3:
        filter_info.append(f"Categories: {', '.join(selected_categories)}")

    if selected_crime_types and len(selected_crime_types) > 0:
        filter_info.append(f"Crime Types: {len(selected_crime_types)} selected")

    if filter_info:
        st.caption(" | ".join(filter_info))
    else:
        st.caption(":map: All districts, :mag: All categories")

    st.caption(":link: Share this view: URL encodes your current filter settings")

    st.markdown("---")

    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(list(PAGE_NAMES.values()))

    with tab1:
        render_overview_page(filtered_df)

    with tab2:
        render_temporal_page(filtered_df)

    with tab3:
        render_spatial_page(filtered_df)

    with tab4:
        render_correlations_page(filtered_df)

    with tab5:
        render_advanced_page(filtered_df)


if __name__ == "__main__":
    main()
