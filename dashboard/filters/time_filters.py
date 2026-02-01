"""
Time range filter controls for the dashboard.

Provides date sliders, preset period selections, and URL state synchronization
for time-based filtering of crime data.
"""

import streamlit as st
from datetime import datetime, date
from typing import NamedTuple

from dashboard.config import FILTER_DEFAULTS


class TimeFilterState(NamedTuple):
    """Immutable container for time filter state."""

    start_date: date
    end_date: date
    preset: str | None  # 'custom', 'last_year', 'last_5_years', etc.

    @property
    def years(self) -> list[int]:
        """Years included in this date range."""
        return list(range(self.start_date.year, self.end_date.year + 1))


# Preset period definitions
PRESETS = {
    "all": {"label": "All Data (2006-2025)", "years": (2006, 2025)},
    "last_5_years": {"label": "Last 5 Years", "years": (2021, 2025)},
    "last_3_years": {"label": "Last 3 Years", "years": (2023, 2025)},
    "last_year": {"label": "Last Year (2025)", "years": (2025, 2025)},
    "covid_period": {"label": "COVID Period (2020-2022)", "years": (2020, 2022)},
    "custom": {"label": "Custom Range", "years": None},
}


def read_time_filters_from_url() -> dict:
    """
    Read time filter state from URL query parameters.

    Returns:
        Dict with start_date, end_date, preset keys (or defaults if not in URL).
    """
    params = st.query_params

    # Default values
    defaults = {
        "start_date": FILTER_DEFAULTS["start_date"],
        "end_date": FILTER_DEFAULTS["end_date"],
        "preset": "all",
    }

    # Read from URL if present
    result = defaults.copy()
    if "start_date" in params:
        result["start_date"] = params["start_date"]
    if "end_date" in params:
        result["end_date"] = params["end_date"]
    if "preset" in params:
        result["preset"] = params["preset"]

    return result


def sync_time_filters_to_url(state: TimeFilterState) -> None:
    """
    Sync time filter state to URL query parameters.

    Args:
        state: Current TimeFilterState to persist.
    """
    params = st.query_params
    params["start_date"] = state.start_date.strftime("%Y-%m-%d")
    params["end_date"] = state.end_date.strftime("%Y-%m-%d")
    params["preset"] = state.preset or "custom"


def render_time_filters(key_prefix: str = "time") -> TimeFilterState:
    """
    Render time range filter controls in the sidebar.

    Creates:
    - Preset period buttons (All Data, Last 5 Years, Last Year, etc.)
    - Date range slider for custom range selection
    - Individual year multi-select for fine-grained control

    Args:
        key_prefix: Prefix for widget keys to avoid conflicts.

    Returns:
        TimeFilterState with current filter values.

    Example:
        >>> time_state = render_time_filters()
        >>> time_state.start_date
        datetime.date(2006, 1, 1)
        >>> time_state.years
        [2006, 2007, ..., 2025]
    """
    with st.sidebar:
        st.subheader(":calendar: Time Range")

        # Initialize from URL or defaults
        url_state = read_time_filters_from_url()

        # Preset period selection
        preset = st.selectbox(
            "Preset Period",
            options=list(PRESETS.keys()),
            format_func=lambda x: PRESETS[x]["label"],
            index=list(PRESETS.keys()).index(url_state["preset"]),
            key=f"{key_prefix}_preset",
        )

        # Determine date range based on preset
        if preset != "custom":
            preset_years = PRESETS[preset]["years"]
            default_start = date(preset_years[0], 1, 1)
            default_end = date(preset_years[1], 12, 31)
        else:
            # Use URL values or defaults
            default_start = datetime.strptime(url_state["start_date"], "%Y-%m-%d").date()
            default_end = datetime.strptime(url_state["end_date"], "%Y-%m-%d").date()

        # Date range slider
        date_range = st.slider(
            "Date Range",
            min_value=date(2006, 1, 1),
            max_value=date(2025, 12, 31),
            value=(default_start, default_end),
            format="YYYY-MM-DD",
            key=f"{key_prefix}_range",
        )

        start_date, end_date = date_range

        # Year multi-select (for cascading filters)
        available_years = list(range(start_date.year, end_date.year + 1))

        # Initialize session state for years
        years_key = f"{key_prefix}_years"
        if years_key not in st.session_state:
            st.session_state[years_key] = available_years

        # Update available years when date range changes
        selected_years = st.multiselect(
            "Select Years",
            options=available_years,
            default=available_years,
            key=f"{key_prefix}_years_select",
        )

        # Season filter (optional)
        season = st.selectbox(
            "Season (Optional)",
            options=["All", "Winter", "Spring", "Summer", "Fall"],
            index=0,
            key=f"{key_prefix}_season",
        )

        # Month filter (optional, cascades from years/season)
        all_months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        if season != "All":
            season_months = {
                "Winter": ["December", "January", "February"],
                "Spring": ["March", "April", "May"],
                "Summer": ["June", "July", "August"],
                "Fall": ["September", "October", "November"],
            }
            month_options = season_months[season]
        else:
            month_options = all_months

        selected_months = st.multiselect(
            "Select Months",
            options=month_options,
            default=month_options,
            key=f"{key_prefix}_months",
        )

        # Reset button
        if st.button(":recycle: Reset Time Filters", key=f"{key_prefix}_reset"):
            st.query_params.clear()
            st.rerun()

    # Create state object
    state = TimeFilterState(
        start_date=start_date,
        end_date=end_date,
        preset=preset if preset != "custom" else None,
    )

    # Sync to URL
    sync_time_filters_to_url(state)

    # Store derived filter values in session state for other components
    st.session_state[f"{key_prefix}_derived"] = {
        "years": selected_years,
        "months": selected_months,
        "season": season,
    }

    return state


def get_filter_dates(state: TimeFilterState) -> tuple[str, str]:
    """
    Convert TimeFilterState to date strings for filtering.

    Args:
        state: TimeFilterState from render_time_filters.

    Returns:
        Tuple of (start_date_str, end_date_str) in YYYY-MM-DD format.
    """
    return (
        state.start_date.strftime("%Y-%m-%d"),
        state.end_date.strftime("%Y-%m-%d"),
    )
