"""
Crime type filter controls for the dashboard.

Provides UCR category and specific crime type selection with URL state
synchronization.
"""

import streamlit as st
from typing import NamedTuple

from analysis.utils import VIOLENT_CRIME_UCR, PROPERTY_CRIME_UCR
from dashboard.config import FILTER_DEFAULTS


# UCR category definitions
UCR_CATEGORIES = {
    "Violent": VIOLENT_CRIME_UCR,  # [100, 200, 300, 400]
    "Property": PROPERTY_CRIME_UCR,  # [500, 600, 700]
    "Other": None,  # Everything else
}

# Category to UCR code mapping for filtering
CATEGORY_UCR_MAP = {
    "Violent": VIOLENT_CRIME_UCR,
    "Property": PROPERTY_CRIME_UCR,
    "Other": "other",  # Special marker for non-violent/property
}


class CrimeFilterState(NamedTuple):
    """Immutable container for crime type filter state."""

    categories: list[str]  # ["Violent", "Property", "Other"] or subset
    crime_types: list[str] | None  # None = all types in selected categories
    select_all_types: bool


def read_crime_filters_from_url() -> dict:
    """
    Read crime filter state from URL query parameters.

    Returns:
        Dict with categories (comma-separated) and crime_types keys.
    """
    params = st.query_params

    result = {
        "categories": None,  # None = all categories
        "crime_types": None,  # None = all crime types
    }

    if "categories" in params:
        categories_str = params["categories"]
        result["categories"] = categories_str.split(",")

    if "crime_types" in params:
        crime_types_str = params["crime_types"]
        result["crime_types"] = crime_types_str.split(",")

    return result


def sync_crime_filters_to_url(state: CrimeFilterState) -> None:
    """
    Sync crime filter state to URL query parameters.

    Args:
        state: Current CrimeFilterState to persist.
    """
    params = st.query_params

    # Encode categories
    if state.select_all_types or len(state.categories) == 3:
        # All categories selected - cleaner URL
        if "categories" in params:
            del params["categories"]
    else:
        params["categories"] = ",".join(state.categories)

    # Encode specific crime types (only if not select all)
    if not state.select_all_types and state.crime_types:
        params["crime_types"] = ",".join(state.crime_types)
    elif "crime_types" in params:
        del params["crime_types"]


def get_crime_categories_from_data(df) -> list[str]:
    """
    Get list of crime categories present in the current DataFrame.

    Args:
        df: Filtered DataFrame.

    Returns:
        List of category names present in data.
    """
    if "crime_category" not in df.columns:
        return ["Violent", "Property", "Other"]

    return sorted(df["crime_category"].unique().tolist())


def get_crime_types_from_data(df, categories: list[str] | None = None) -> list[str]:
    """
    Get list of specific crime types for the selected categories.

    Args:
        df: Filtered DataFrame.
        categories: List of categories to include (None = all).

    Returns:
        Sorted list of crime type names (text_general_code values).
    """
    if "text_general_code" not in df.columns:
        return []

    result_df = df.copy()

    # Filter by categories if specified
    if categories is not None and "crime_category" in df.columns:
        result_df = result_df[result_df["crime_category"].isin(categories)]

    # Get unique crime types
    crime_types = result_df["text_general_code"].dropna().unique().tolist()

    return sorted(crime_types)


def render_crime_filters(df, key_prefix: str = "crime") -> CrimeFilterState:
    """
    Render crime type filter controls in the sidebar.

    Creates:
    - Category multi-select (Violent, Property, Other)
    - Select all crime types toggle
    - Crime type multi-select (when not select all)

    Args:
        df: Filtered DataFrame (used to limit crime type options).
        key_prefix: Prefix for widget keys to avoid conflicts.

    Returns:
        CrimeFilterState with current filter values.

    Example:
        >>> crime_state = render_crime_filters(filtered_df)
        >>> crime_state.categories
        ['Violent', 'Property']
        >>> crime_state.crime_types
        ['Homicide - Criminal', 'Aggravated Assault Firearm', ...]
    """
    with st.sidebar:
        st.subheader(":mag: Crime Type")

        # Read from URL or default to all categories
        url_state = read_crime_filters_from_url()

        # Get available categories from data
        available_categories = get_crime_categories_from_data(df)

        # Category multi-select
        if url_state["categories"] is None:
            default_categories = available_categories
        else:
            # Filter to available categories
            default_categories = [c for c in url_state["categories"] if c in available_categories]
            if not default_categories:
                default_categories = available_categories

        selected_categories = st.multiselect(
            "UCR Categories",
            options=["Violent", "Property", "Other"],
            default=default_categories,
            key=f"{key_prefix}_categories",
        )

        if not selected_categories:
            st.warning("No categories selected. Showing all categories.")
            selected_categories = available_categories

        # Get crime types for selected categories
        available_crime_types = get_crime_types_from_data(df, selected_categories)

        # Select all toggle
        select_all_types = st.checkbox(
            "Select All Crime Types",
            value=(url_state["crime_types"] is None),
            key=f"{key_prefix}_select_all",
        )

        if select_all_types:
            selected_crime_types = None
        else:
            # Default to URL state or available types
            if url_state["crime_types"] is not None:
                default_types = [t for t in url_state["crime_types"] if t in available_crime_types]
                if not default_types:
                    default_types = available_crime_types[:10]  # First 10 as default
            else:
                default_types = available_crime_types[:10] if len(available_crime_types) > 10 else available_crime_types

            selected_crime_types = st.multiselect(
                "Specific Crime Types",
                options=available_crime_types,
                default=default_types,
                key=f"{key_prefix}_types",
            )

            if not selected_crime_types:
                st.info("All crime types in selected categories will be shown.")
                selected_crime_types = None

        # Reset button
        if st.button(":recycle: Reset Crime Filters", key=f"{key_prefix}_reset"):
            if "categories" in st.query_params:
                del st.query_params["categories"]
            if "crime_types" in st.query_params:
                del st.query_params["crime_types"]
            st.rerun()

    # Create state object
    state = CrimeFilterState(
        categories=selected_categories,
        crime_types=selected_crime_types,
        select_all_types=select_all_types,
    )

    # Sync to URL
    sync_crime_filters_to_url(state)

    return state


def get_filter_categories(state: CrimeFilterState) -> list[str]:
    """
    Convert CrimeFilterState to category list for filtering.

    Args:
        state: CrimeFilterState from render_crime_filters.

    Returns:
        List of category names.
    """
    return state.categories


def get_filter_crime_types(state: CrimeFilterState) -> list[str] | None:
    """
    Convert CrimeFilterState to crime type list for filtering.

    Args:
        state: CrimeFilterState from render_crime_filters.

    Returns:
        List of crime type names or None for all.
    """
    return state.crime_types
