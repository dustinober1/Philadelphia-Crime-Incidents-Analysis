"""
State management for dashboard cross-filtering.

Separates pending filter changes from applied state to support apply button pattern.
"""

import streamlit as st
from datetime import date
from typing import NamedTuple


# Session state keys
PENDING_FILTERS_KEY = "pending_filters"
APPLIED_FILTERS_KEY = "applied_filters"
FILTER_INIT_KEY = "filter_state_initialized"


class PendingFilters(NamedTuple):
    """Container for pending sidebar filter changes."""

    time_pending: bool = False
    geo_pending: bool = False
    crime_pending: bool = False

    @property
    def has_any_pending(self) -> bool:
        """Check if any filters have pending changes."""
        return self.time_pending or self.geo_pending or self.crime_pending


class FilterState(NamedTuple):
    """Container for applied filter state (what's actually used for filtering)."""

    start_date: str  # YYYY-MM-DD format
    end_date: str  # YYYY-MM-DD format
    districts: list[int]  # List of police district integers
    crime_categories: list[str]  # ["Violent", "Property", "Other"] or subset
    crime_types: list[str] | None  # None = all types in selected categories


def initialize_filter_state() -> None:
    """
    Initialize session state for pending and applied filters on first load.

    Called from app.py main() to ensure state is ready before filter rendering.
    """
    if FILTER_INIT_KEY not in st.session_state:
        # Initialize pending filters to all False
        st.session_state[PENDING_FILTERS_KEY] = PendingFilters(
            time_pending=False,
            geo_pending=False,
            crime_pending=False,
        )

        # Initialize applied filters to defaults
        from dashboard.config import FILTER_DEFAULTS
        st.session_state[APPLIED_FILTERS_KEY] = FilterState(
            start_date=FILTER_DEFAULTS["start_date"],
            end_date=FILTER_DEFAULTS["end_date"],
            districts=list(range(1, 24)),  # All districts
            crime_categories=["Violent", "Property", "Other"],
            crime_types=None,
        )

        # Mark as initialized
        st.session_state[FILTER_INIT_KEY] = True


def mark_filter_pending(filter_type: str) -> None:
    """
    Mark a specific filter type as having pending changes.

    Args:
        filter_type: One of "time", "geo", or "crime".
    """
    if PENDING_FILTERS_KEY not in st.session_state:
        initialize_filter_state()

    current = st.session_state[PENDING_FILTERS_KEY]

    if filter_type == "time":
        st.session_state[PENDING_FILTERS_KEY] = current._replace(time_pending=True)
    elif filter_type == "geo":
        st.session_state[PENDING_FILTERS_KEY] = current._replace(geo_pending=True)
    elif filter_type == "crime":
        st.session_state[PENDING_FILTERS_KEY] = current._replace(crime_pending=True)


def clear_pending_filters() -> None:
    """Clear all pending flags (called after apply button click)."""
    st.session_state[PENDING_FILTERS_KEY] = PendingFilters(
        time_pending=False,
        geo_pending=False,
        crime_pending=False,
    )


def has_pending_changes() -> bool:
    """
    Check if any filters have pending changes.

    Returns:
        True if any filter has pending changes, False otherwise.
    """
    if PENDING_FILTERS_KEY not in st.session_state:
        return False

    pending = st.session_state[PENDING_FILTERS_KEY]
    return pending.has_any_pending


def get_applied_state() -> FilterState:
    """
    Get current applied filter state.

    Returns:
        FilterState with currently applied filter values.
    """
    if APPLIED_FILTERS_KEY not in st.session_state:
        initialize_filter_state()

    return st.session_state[APPLIED_FILTERS_KEY]


def update_applied_state(time_state, geo_state, crime_state) -> None:
    """
    Update applied state from current filter values.

    Called when apply button is clicked to sync pending changes to applied state.

    Args:
        time_state: TimeFilterState from time_filters.py
        geo_state: GeoFilterState from geo_filters.py
        crime_state: CrimeFilterState from crime_filters.py
    """
    # Extract values from filter state objects
    start_date_str = time_state.start_date.strftime("%Y-%m-%d")
    end_date_str = time_state.end_date.strftime("%Y-%m-%d")

    # Create new applied state
    st.session_state[APPLIED_FILTERS_KEY] = FilterState(
        start_date=start_date_str,
        end_date=end_date_str,
        districts=geo_state.districts,
        crime_categories=crime_state.categories,
        crime_types=crime_state.crime_types,
    )
