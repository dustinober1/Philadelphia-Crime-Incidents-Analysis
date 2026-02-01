"""
Geographic filter controls for the dashboard.

Provides police district selection with URL state synchronization.
"""

import streamlit as st
from typing import NamedTuple

from dashboard.config import FILTER_DEFAULTS
from dashboard.components.state import mark_filter_pending, has_pending_changes, PendingFilters


class GeoFilterState(NamedTuple):
    """Immutable container for geographic filter state."""

    districts: list[int]
    select_all: bool


def read_geo_filters_from_url() -> dict:
    """
    Read geographic filter state from URL query parameters.

    Returns:
        Dict with districts key (comma-separated string or None for all).
    """
    params = st.query_params

    result = {"districts": None}  # None = all districts

    if "districts" in params:
        # Parse comma-separated districts
        districts_str = params["districts"]
        try:
            result["districts"] = [int(d) for d in districts_str.split(",")]
        except ValueError:
            # Invalid format, use default
            result["districts"] = None

    return result


def sync_geo_filters_to_url(state: GeoFilterState) -> None:
    """
    Sync geographic filter state to URL query parameters.

    Args:
        state: Current GeoFilterState to persist.
    """
    params = st.query_params

    if state.select_all:
        # Don't encode districts in URL (all districts = cleaner URL)
        if "districts" in params:
            del params["districts"]
    else:
        # Encode as comma-separated
        districts_str = ",".join(str(d) for d in sorted(state.districts))
        params["districts"] = districts_str


def get_district_list_from_data(df) -> list[int]:
    """
    Get list of districts that have data in the current DataFrame.

    Useful for limiting district options to those with data in the filtered
    time range.

    Args:
        df: Filtered DataFrame.

    Returns:
        Sorted list of district integers present in the data.
    """
    if "dc_dist" not in df.columns:
        return list(range(1, 24))  # All districts

    # Handle district values that may be strings or floats
    districts = df["dc_dist"].dropna().unique()

    # Convert to int, handling string values
    district_ints = []
    for d in districts:
        try:
            if isinstance(d, str):
                district_ints.append(int(float(d)))
            else:
                district_ints.append(int(d))
        except (ValueError, TypeError):
            continue

    return sorted(set(district_ints))


def render_geo_filters(df, key_prefix: str = "geo") -> GeoFilterState:
    """
    Render geographic filter controls in the sidebar.

    Creates:
    - Select all districts toggle
    - District multi-select (when not select all)
    - Reset button

    Args:
        df: Filtered DataFrame (used to limit district options).
        key_prefix: Prefix for widget keys to avoid conflicts.

    Returns:
        GeoFilterState with current filter values.

    Example:
        >>> geo_state = render_geo_filters(filtered_df)
        >>> geo_state.districts
        [1, 2, 3, 5, 7]
        >>> geo_state.select_all
        False
    """
    with st.sidebar:
        st.subheader(":map: Geographic Area")

        # Read from URL or default to all districts
        url_state = read_geo_filters_from_url()

        # Get available districts from data
        available_districts = get_district_list_from_data(df)

        # Select all toggle
        select_all = st.checkbox(
            "Select All Districts",
            value=(url_state["districts"] is None),
            key=f"{key_prefix}_select_all",
        )

        if select_all:
            # All districts selected
            selected_districts = available_districts
        else:
            # Default to URL state or available districts
            if url_state["districts"] is not None:
                # Filter to available districts
                default_districts = [d for d in url_state["districts"] if d in available_districts]
                if not default_districts:
                    default_districts = available_districts
            else:
                default_districts = available_districts

            selected_districts = st.multiselect(
                "Police Districts",
                options=available_districts,
                default=default_districts,
                format_func=lambda x: f"District {int(x)}",
                key=f"{key_prefix}_districts",
            )

            # Show "No districts selected" message
            if not selected_districts:
                st.warning("No districts selected. Showing all districts.")
                selected_districts = available_districts

        # Reset button
        if st.button(":recycle: Reset Geo Filters", key=f"{key_prefix}_reset"):
            if "districts" in st.query_params:
                del st.query_params["districts"]
            st.rerun()

    # Create state object
    state = GeoFilterState(
        districts=selected_districts,
        select_all=select_all,
    )

    # Sync to URL
    sync_geo_filters_to_url(state)

    return state


def get_filter_districts(state: GeoFilterState) -> list[int]:
    """
    Convert GeoFilterState to district list for filtering.

    Args:
        state: GeoFilterState from render_geo_filters.

    Returns:
        List of district integers.
    """
    return state.districts


def render_geo_filters_with_pending(df, key_prefix: str = "geo") -> GeoFilterState:
    """
    Render geographic filter controls with pending state tracking.

    This version tracks pending changes separately from applied state.
    URL sync is handled by app.py when apply button is clicked.

    Args:
        df: Filtered DataFrame (used to limit district options).
        key_prefix: Prefix for widget keys to avoid conflicts.

    Returns:
        GeoFilterState with current filter values.
    """
    with st.sidebar:
        # Check for pending changes
        geo_pending = st.session_state.get("pending_filters", PendingFilters()).geo_pending

        # Visual indicator for pending changes
        header_text = ":map: Geographic Area"
        if geo_pending:
            header_text = f":map: Geographic Area 🔵"
        st.subheader(header_text)

        # Get current applied state for defaults
        from dashboard.components.state import get_applied_state
        applied = get_applied_state()

        # Get available districts from data
        available_districts = get_district_list_from_data(df)

        # Determine default from applied state
        default_select_all = len(applied.districts) >= len(available_districts)
        default_districts = applied.districts if not default_select_all else available_districts

        # Callback for marking pending
        def _on_geo_change():
            mark_filter_pending("geo")

        # Select all toggle
        select_all = st.checkbox(
            "Select All Districts",
            value=default_select_all,
            key=f"{key_prefix}_pending_select_all",
            on_change=_on_geo_change,
        )

        if select_all:
            # All districts selected
            selected_districts = available_districts
        else:
            # Filter default districts to available
            default_districts = [d for d in default_districts if d in available_districts]
            if not default_districts:
                default_districts = available_districts

            selected_districts = st.multiselect(
                "Police Districts",
                options=available_districts,
                default=default_districts,
                format_func=lambda x: f"District {int(x)}",
                key=f"{key_prefix}_pending_districts",
                on_change=_on_geo_change,
            )

            # Show "No districts selected" message
            if not selected_districts:
                st.warning("No districts selected. Showing all districts.")
                selected_districts = available_districts

    # Create state object (without URL sync)
    state = GeoFilterState(
        districts=selected_districts,
        select_all=select_all,
    )

    return state
