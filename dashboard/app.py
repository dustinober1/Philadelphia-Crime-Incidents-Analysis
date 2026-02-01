"""
Philadelphia Crime Incidents Dashboard - Main Entry Point.

Run with: streamlit run dashboard/app.py
"""

import streamlit as st
from pathlib import Path

from dashboard.config import DISPLAY_CONFIG, PAGE_NAMES
from dashboard.components.cache import load_crime_data, apply_filters
from dashboard.components.state import (
    has_pending_changes,
    clear_pending_filters,
    update_applied_state,
    get_applied_state,
    initialize_filter_state,
)
from dashboard.components import (
    sync_view_selection_to_url,
    read_view_selection_from_url,
    clear_view_selection_from_url,
)
from dashboard.components.plotly_interactions import (
    ViewSelectionState,
    initialize_view_selection_state,
    get_selection_state,
    clear_selection_state,
)
from dashboard.filters.time_filters import render_time_filters_with_pending, get_filter_dates
from dashboard.filters.geo_filters import render_geo_filters_with_pending, get_filter_districts
from dashboard.filters.crime_filters import render_crime_filters_with_pending, get_filter_categories, get_filter_crime_types
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


def _sync_all_filters_to_url(time_state, geo_state, crime_state) -> None:
    """
    Sync all applied filter states to URL parameters.

    Called when apply button is clicked to make filtered views shareable.

    Args:
        time_state: TimeFilterState from time_filters.py
        geo_state: GeoFilterState from geo_filters.py
        crime_state: CrimeFilterState from crime_filters.py
    """
    from dashboard.filters.time_filters import sync_time_filters_to_url
    from dashboard.filters.geo_filters import sync_geo_filters_to_url
    from dashboard.filters.crime_filters import sync_crime_filters_to_url

    # Time filters
    sync_time_filters_to_url(time_state)
    # Geo filters
    sync_geo_filters_to_url(geo_state)
    # Crime filters
    sync_crime_filters_to_url(crime_state)


def _update_selection_state_from_dict(selection_dict: dict) -> None:
    """Update view selection state from URL parameters dict.

    Args:
        selection_dict: Dict with keys active_view, active_districts,
                       active_crime_types, active_time_range
    """
    import streamlit as st

    selection_state = ViewSelectionState(
        active_view=selection_dict.get("active_view"),
        active_districts=selection_dict.get("active_districts"),
        active_crime_types=selection_dict.get("active_crime_types"),
        active_time_range=selection_dict.get("active_time_range"),
    )
    st.session_state["view_selections"] = {
        "active_view": selection_state.active_view,
        "active_districts": selection_state.active_districts,
        "active_crime_types": selection_state.active_crime_types,
        "active_time_range": selection_state.active_time_range,
    }


def main():
    """Main dashboard entry point."""
    _load_custom_css()

    # Initialize filter state (required for apply button pattern)
    initialize_filter_state()
    # Initialize view selection state (required for cross-filtering)
    initialize_view_selection_state()

    # Load view selections from URL
    url_view_selection = read_view_selection_from_url()
    if url_view_selection.get("active_view"):
        # Restore view selection from URL
        _update_selection_state_from_dict(url_view_selection)

    # Title
    st.title(DISPLAY_CONFIG["title"])
    st.markdown(f"<p class='sub-header'>{DISPLAY_CONFIG['subtitle']}</p>", unsafe_allow_html=True)

    # Load data (cached)
    with st.spinner("Loading data (first load takes ~10s)..."):
        df = load_crime_data()

    # Get applied state for filtering
    applied = get_applied_state()

    # Sidebar: Render all filters with pending state tracking
    with st.sidebar:
        st.header(":wrench: Filters")

        # Time filters
        time_state = render_time_filters_with_pending()

        st.markdown("---")

        # Geo filters (depends on time filter - use applied state for cascading)
        df_time_filtered = apply_filters(df, start_date=applied.start_date, end_date=applied.end_date)
        geo_state = render_geo_filters_with_pending(df_time_filtered)

        st.markdown("---")

        # Crime filters (depends on time + geo - use applied state for cascading)
        df_tg_filtered = apply_filters(
            df, start_date=applied.start_date, end_date=applied.end_date, districts=applied.districts
        )
        crime_state = render_crime_filters_with_pending(df_tg_filtered)

        st.markdown("---")

        # Apply button
        if has_pending_changes():
            if st.button(":white_check_mark: Apply Filters", type="primary", use_container_width=True):
                # Update applied state from current filter values
                update_applied_state(time_state, geo_state, crime_state)
                # Clear pending flags
                clear_pending_filters()
                # Clear view selections (sidebar filters override view selections)
                clear_selection_state()  # Clear session state
                clear_view_selection_from_url()  # Clear URL params
                # Sync to URL
                _sync_all_filters_to_url(time_state, geo_state, crime_state)
                # Rerun to update views
                st.rerun()
        else:
            st.button(":white_check_mark: Apply Filters", disabled=True, use_container_width=True)

        st.markdown("---")
        st.caption("Dashboard v1.0 | Phase 5")

    # Apply all filters using applied state
    filtered_df = apply_filters(
        df,
        start_date=applied.start_date,
        end_date=applied.end_date,
        districts=applied.districts,
        crime_categories=applied.crime_categories,
        crime_types=applied.crime_types,
    )

    # Filter summary banner
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Records", f"{len(filtered_df):,}")
        with col2:
            st.metric("Date Range", f"{applied.start_date[:4]}-{applied.end_date[:4]}")
        with col3:
            st.metric("Districts", len(applied.districts))
        with col4:
            st.metric("Categories", len(applied.crime_categories))

    # Show active filters
    filter_info = []

    if len(applied.districts) < 25:  # 25 districts in data
        filter_info.append(f"Districts: {', '.join(f'D{d}' for d in sorted(applied.districts))}")

    if len(applied.crime_categories) < 3:
        filter_info.append(f"Categories: {', '.join(applied.crime_categories)}")

    if applied.crime_types and len(applied.crime_types) > 0:
        filter_info.append(f"Crime Types: {len(applied.crime_types)} selected")

    if filter_info:
        st.caption(" | ".join(filter_info))
    else:
        st.caption(":map: All districts, :mag: All categories")

    st.caption(":link: Share this view: URL encodes your current filter settings")

    st.markdown("---")

    # Track active tab in session state for detecting tab changes
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = None

    # Create tabs
    tab_names = list(PAGE_NAMES.values())
    tabs = st.tabs(tab_names)

    # Note: Streamlit doesn't provide a direct way to detect which tab is active
    # We sync view selections after rendering, but clear them when sidebar changes

    with tabs[0]:
        render_overview_page(df, filtered_df)

    with tabs[1]:
        render_temporal_page(df, filtered_df)

    with tabs[2]:
        render_spatial_page(df, filtered_df)

    with tabs[3]:
        render_correlations_page(df, filtered_df)

    with tabs[4]:
        render_advanced_page(df, filtered_df)

    # Sync current view selection to URL after tab rendering
    current_selection = get_selection_state()
    if current_selection.active_view:
        sync_view_selection_to_url(current_selection)


if __name__ == "__main__":
    main()
