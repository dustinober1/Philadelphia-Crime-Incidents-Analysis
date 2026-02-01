"""
Plotly selection event handling for view-to-view cross-filtering.

This module provides utilities for managing Plotly selection events and
session state for active selections across dashboard views.
"""

from typing import NamedTuple
import streamlit as st
import plotly.graph_objects as go

# View selection state keys
VIEW_SELECTION_KEY = "view_selections"
ACTIVE_VIEW_KEY = "active_view"
ACTIVE_DISTRICTS_KEY = "active_districts"
ACTIVE_CRIME_TYPES_KEY = "active_crime_types"
ACTIVE_TIME_RANGE_KEY = "active_time_range"


class ViewSelectionState(NamedTuple):
    """Container for current view-to-view selection state.

    Attributes:
        active_view: Which view triggered selection (e.g., "spatial", "temporal")
        active_districts: Selected districts from spatial view
        active_crime_types: Selected crime types from overview/correlations
        active_time_range: Selected time range from temporal view
    """
    active_view: str | None  # Which view triggered selection
    active_districts: list[int] | None  # Selected districts from spatial view
    active_crime_types: list[str] | None  # Selected crime types from overview/correlations
    active_time_range: tuple[str, str] | None  # Selected time range from temporal view


def initialize_view_selection_state() -> None:
    """Initialize session state for view selections if not exists.

    Creates default empty state for all view selections.
    Should be called once at app startup.
    """
    if VIEW_SELECTION_KEY not in st.session_state:
        st.session_state[VIEW_SELECTION_KEY] = {
            ACTIVE_VIEW_KEY: None,
            ACTIVE_DISTRICTS_KEY: None,
            ACTIVE_CRIME_TYPES_KEY: None,
            ACTIVE_TIME_RANGE_KEY: None,
        }


def register_plotly_selection(fig: go.Figure, key: str) -> go.Figure:
    """Configure Plotly figure for selection events.

    Args:
        fig: Plotly figure object to configure
        key: Unique identifier for the chart (used to identify selection source)

    Returns:
        Configured figure with selection enabled

    Example:
        fig = px.bar(df, x='district', y='count')
        fig = register_plotly_selection(fig, 'district_chart')
        st.plotly_chart(fig, on_select='rerun', key='district_chart')
    """
    # Enable box/lasso select mode
    fig.update_layout(dragmode='select')

    # Store the key in figure metadata for identification
    fig.layout.update({'_selection_key': key})

    return fig


def update_selection_from_event(selection_event: dict, source_view: str) -> None:
    """Parse selection event and update session state with new selection.

    Args:
        selection_event: Selection event dict from st.plotly_chart on_select
        source_view: View that generated the selection (e.g., "spatial", "temporal", "overview")

    The selection event structure is:
    {
        'selection': {
            'points': [
                {'customdata': [...], 'x': ..., 'y': ..., ...},
                ...
            ]
        }
    }
    """
    initialize_view_selection_state()

    # Extract selection points
    try:
        points = selection_event.get('selection', {}).get('points', [])
    except (AttributeError, TypeError):
        points = []

    if not points:
        # Empty selection - clear all selections
        clear_selection_state()
        return

    # Update active view
    st.session_state[VIEW_SELECTION_KEY][ACTIVE_VIEW_KEY] = source_view

    # Parse selection based on source view
    if source_view == "spatial":
        districts = _extract_districts_from_selection(points)
        st.session_state[VIEW_SELECTION_KEY][ACTIVE_DISTRICTS_KEY] = districts
        # Clear other selections when spatial selection changes
        st.session_state[VIEW_SELECTION_KEY][ACTIVE_CRIME_TYPES_KEY] = None
        st.session_state[VIEW_SELECTION_KEY][ACTIVE_TIME_RANGE_KEY] = None

    elif source_view == "overview" or source_view == "correlations":
        crime_types = _extract_crime_types_from_selection(points)
        st.session_state[VIEW_SELECTION_KEY][ACTIVE_CRIME_TYPES_KEY] = crime_types
        # Clear other selections when crime type selection changes
        st.session_state[VIEW_SELECTION_KEY][ACTIVE_DISTRICTS_KEY] = None
        st.session_state[VIEW_SELECTION_KEY][ACTIVE_TIME_RANGE_KEY] = None

    elif source_view == "temporal":
        time_range = _extract_time_range_from_selection(points)
        st.session_state[VIEW_SELECTION_KEY][ACTIVE_TIME_RANGE_KEY] = time_range
        # Clear other selections when time range selection changes
        st.session_state[VIEW_SELECTION_KEY][ACTIVE_DISTRICTS_KEY] = None
        st.session_state[VIEW_SELECTION_KEY][ACTIVE_CRIME_TYPES_KEY] = None


def get_selection_state() -> ViewSelectionState:
    """Return current view selection state from session state.

    Returns:
        ViewSelectionState with current selections (empty state if not initialized)
    """
    initialize_view_selection_state()

    state = st.session_state[VIEW_SELECTION_KEY]

    return ViewSelectionState(
        active_view=state.get(ACTIVE_VIEW_KEY),
        active_districts=state.get(ACTIVE_DISTRICTS_KEY),
        active_crime_types=state.get(ACTIVE_CRIME_TYPES_KEY),
        active_time_range=state.get(ACTIVE_TIME_RANGE_KEY),
    )


def clear_selection_state() -> None:
    """Reset all view selections to None.

    Called when user clicks in sidebar or changes tab.
    """
    initialize_view_selection_state()

    st.session_state[VIEW_SELECTION_KEY][ACTIVE_VIEW_KEY] = None
    st.session_state[VIEW_SELECTION_KEY][ACTIVE_DISTRICTS_KEY] = None
    st.session_state[VIEW_SELECTION_KEY][ACTIVE_CRIME_TYPES_KEY] = None
    st.session_state[VIEW_SELECTION_KEY][ACTIVE_TIME_RANGE_KEY] = None


def has_active_selection() -> bool:
    """Return True if any view selection is active.

    Returns:
        True if active_view, active_districts, active_crime_types, or active_time_range is set
    """
    state = get_selection_state()
    return (
        state.active_view is not None
        or state.active_districts is not None
        or state.active_crime_types is not None
        or state.active_time_range is not None
    )


def get_active_filter_kwargs() -> dict:
    """Convert selection state to filter kwargs for apply_filters().

    Returns:
        Dict with filter kwargs: {"districts": [...], "crime_types": [...],
        "start_date": ..., "end_date": ...}
        Only includes non-None selections
    """
    state = get_selection_state()
    kwargs = {}

    if state.active_districts:
        kwargs["districts"] = state.active_districts

    if state.active_crime_types:
        kwargs["crime_types"] = state.active_crime_types

    if state.active_time_range:
        kwargs["start_date"] = state.active_time_range[0]
        kwargs["end_date"] = state.active_time_range[1]

    return kwargs


# Private helper functions for selection parsing

def _extract_districts_from_selection(selection_points: list) -> list[int] | None:
    """Parse district IDs from selected plot points.

    Args:
        selection_points: List of point dicts from Plotly selection event

    Returns:
        List of unique district IDs or None if no districts found
    """
    districts = set()

    for point in selection_points:
        try:
            # Try customdata first (may contain district ID)
            if 'customdata' in point and point['customdata']:
                # customdata can be a list or tuple
                customdata = point['customdata']
                if isinstance(customdata, (list, tuple)) and len(customdata) > 0:
                    # Assume first element is district ID
                    district_id = int(float(customdata[0]))
                    districts.add(district_id)
                else:
                    # Single value in customdata
                    district_id = int(float(customdata))
                    districts.add(district_id)
            # Fall back to x or y values if they look like district IDs
            elif 'x' in point:
                x_val = point['x']
                if isinstance(x_val, (int, float)) and 1 <= x_val <= 99:
                    districts.add(int(x_val))
            elif 'y' in point:
                y_val = point['y']
                if isinstance(y_val, (int, float)) and 1 <= y_val <= 99:
                    districts.add(int(y_val))
        except (ValueError, TypeError, KeyError):
            # Skip invalid point data
            continue

    return sorted(districts) if districts else None


def _extract_crime_types_from_selection(selection_points: list) -> list[str] | None:
    """Parse crime types from selected plot points.

    Args:
        selection_points: List of point dicts from Plotly selection event

    Returns:
        List of unique crime types or None if no crime types found
    """
    crime_types = set()

    for point in selection_points:
        try:
            # Try customdata first (may contain crime type)
            if 'customdata' in point and point['customdata']:
                customdata = point['customdata']
                if isinstance(customdata, (list, tuple)) and len(customdata) > 0:
                    # Assume first element is crime type
                    crime_type = str(customdata[0])
                    crime_types.add(crime_type)
                else:
                    crime_type = str(customdata)
                    crime_types.add(crime_type)
            # Fall back to axis values
            elif 'x' in point:
                crime_types.add(str(point['x']))
            elif 'y' in point:
                crime_types.add(str(point['y']))
        except (KeyError, TypeError):
            # Skip invalid point data
            continue

    return sorted(crime_types) if crime_types else None


def _extract_time_range_from_selection(selection_points: list) -> tuple[str, str] | None:
    """Parse min/max time from selected plot points.

    Args:
        selection_points: List of point dicts from Plotly selection event

    Returns:
        Tuple of (start_date, end_date) strings or None if no time range found
    """
    if not selection_points:
        return None

    dates = []

    for point in selection_points:
        try:
            # Try x axis first (time usually on x)
            if 'x' in point:
                x_val = point['x']
                # Handle different date formats
                if isinstance(x_val, str):
                    dates.append(x_val)
                elif hasattr(x_val, 'isoformat'):  # datetime-like
                    dates.append(x_val.isoformat())
                else:
                    dates.append(str(x_val))
            # Try y axis as fallback
            elif 'y' in point:
                y_val = point['y']
                if isinstance(y_val, str):
                    dates.append(y_val)
                elif hasattr(y_val, 'isoformat'):
                    dates.append(y_val.isoformat())
                else:
                    dates.append(str(y_val))
        except (KeyError, TypeError):
            continue

    if not dates:
        return None

    # Return min and max dates
    return (min(dates), max(dates))
