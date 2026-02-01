"""
URL state synchronization for view-to-view cross-filtering.

This module provides utilities for encoding/decoding view selection state
to URL parameters, enabling shareable dashboard views with both sidebar
filters and active view selections.

URL Parameter Keys (short for cleaner URLs):
- av: active_view (which view triggered selection)
- ad: active_districts (selected district IDs)
- act: active_crime_types (selected crime types)
- atr: active_time_range (selected date range)

Clean URL Heuristic:
- Parameters are omitted when None or representing "all selected"
- Example: ?av=spatial&ad=22 (only encodes non-default selections)
"""

import streamlit as st
from typing import NamedTuple

# URL parameter keys (short for cleaner URLs)
ACTIVE_VIEW_PARAM = "av"  # Short for "active_view"
ACTIVE_DISTRICTS_PARAM = "ad"  # Short for "active_districts"
ACTIVE_CRIME_TYPES_PARAM = "act"  # Short for "active_crime_types"
ACTIVE_TIME_RANGE_PARAM = "atr"  # Short for "active_time_range"


def read_view_selection_from_url() -> dict:
    """
    Read view selection parameters from URL query parameters.

    Parses and validates URL parameters for view selections.
    Returns dict with keys: active_view, active_districts, active_crime_types, active_time_range.

    Returns:
        Dict with parsed view selection state (empty dict if no valid params in URL).

    Example:
        >>> # URL: ?av=spatial&ad=22
        >>> selection = read_view_selection_from_url()
        >>> selection["active_view"]
        'spatial'
        >>> selection["active_districts"]
        [22]
    """
    params = st.query_params
    result = {}

    # Read active view parameter
    if ACTIVE_VIEW_PARAM in params:
        view = params[ACTIVE_VIEW_PARAM]
        if view and isinstance(view, str):
            result["active_view"] = view

    # Read active districts parameter
    if ACTIVE_DISTRICTS_PARAM in params:
        districts_str = params[ACTIVE_DISTRICTS_PARAM]
        districts = _parse_and_validate_districts(districts_str)
        if districts:
            result["active_districts"] = districts

    # Read active crime types parameter
    if ACTIVE_CRIME_TYPES_PARAM in params:
        crime_types_str = params[ACTIVE_CRIME_TYPES_PARAM]
        crime_types = _parse_and_validate_crime_types(crime_types_str)
        if crime_types:
            result["active_crime_types"] = crime_types

    # Read active time range parameter
    if ACTIVE_TIME_RANGE_PARAM in params:
        time_range_str = params[ACTIVE_TIME_RANGE_PARAM]
        time_range = _parse_and_validate_time_range(time_range_str)
        if time_range:
            result["active_time_range"] = time_range

    return result


def sync_view_selection_to_url(selection_state: NamedTuple) -> None:
    """
    Encode view selection state to URL parameters.

    Uses short parameter keys (av, ad, act, atr) for clean URLs.
    Omits parameters when value is None or represents "all selected" for cleaner URLs.

    Clean URL Heuristic:
        - active_view=None: Don't encode (no active selection)
        - active_districts=None: Don't encode (all districts)
        - active_districts=[1,2,3]: Encode as "ad=1,2,3"
        - active_crime_types=None: Don't encode (all crime types)
        - active_time_range=None: Don't encode (full time range)

    Args:
        selection_state: ViewSelectionState with active_view, active_districts,
                        active_crime_types, active_time_range attributes.

    Example:
        >>> from dashboard.components.plotly_interactions import ViewSelectionState
        >>> selection = ViewSelectionState(
        ...     active_view="spatial",
        ...     active_districts=[22],
        ...     active_crime_types=None,
        ...     active_time_range=None
        ... )
        >>> sync_view_selection_to_url(selection)
        >>> # URL now: ?av=spatial&ad=22
    """
    params = st.query_params

    # Sync active view
    if selection_state.active_view:
        params[ACTIVE_VIEW_PARAM] = selection_state.active_view
    elif ACTIVE_VIEW_PARAM in params:
        # Remove parameter if None (clean URL)
        del params[ACTIVE_VIEW_PARAM]

    # Sync active districts
    if selection_state.active_districts:
        districts_str = format_selection_for_url(selection_state.active_districts)
        params[ACTIVE_DISTRICTS_PARAM] = districts_str
    elif ACTIVE_DISTRICTS_PARAM in params:
        # Remove parameter if None (clean URL)
        del params[ACTIVE_DISTRICTS_PARAM]

    # Sync active crime types
    if selection_state.active_crime_types:
        crime_types_str = format_selection_for_url(selection_state.active_crime_types)
        params[ACTIVE_CRIME_TYPES_PARAM] = crime_types_str
    elif ACTIVE_CRIME_TYPES_PARAM in params:
        # Remove parameter if None (clean URL)
        del params[ACTIVE_CRIME_TYPES_PARAM]

    # Sync active time range
    if selection_state.active_time_range:
        time_range_str = format_selection_for_url(selection_state.active_time_range)
        params[ACTIVE_TIME_RANGE_PARAM] = time_range_str
    elif ACTIVE_TIME_RANGE_PARAM in params:
        # Remove parameter if None (clean URL)
        del params[ACTIVE_TIME_RANGE_PARAM]


def clear_view_selection_from_url() -> None:
    """
    Remove all view selection parameters from URL.

    Called when user clears selection or changes sidebar filters.
    Removes av, ad, act, atr params if present.

    Example:
        >>> # URL: ?av=spatial&ad=22&start_date=2020-01-01
        >>> clear_view_selection_from_url()
        >>> # URL now: ?start_date=2020-01-01 (sidebar params preserved)
    """
    params = st.query_params

    # Remove all view selection parameters
    for param in [ACTIVE_VIEW_PARAM, ACTIVE_DISTRICTS_PARAM,
                  ACTIVE_CRIME_TYPES_PARAM, ACTIVE_TIME_RANGE_PARAM]:
        if param in params:
            del params[param]


def format_selection_for_url(value) -> str | None:
    """
    Format value for URL encoding.

    Args:
        value: Value to format (list, tuple, str, int, or None)

    Returns:
        Formatted string for URL or None if value should be omitted.

    Examples:
        >>> format_selection_for_url([1, 2, 3])
        '1,2,3'
        >>> format_selection_for_url(('2020-01-01', '2022-12-31'))
        '2020-01-01,2022-12-31'
        >>> format_selection_for_url(None)
        None
    """
    if value is None:
        return None

    if isinstance(value, list):
        # Join list elements with commas
        return ",".join(str(v) for v in value)

    if isinstance(value, tuple):
        # Join tuple elements with commas
        return ",".join(str(v) for v in value)

    # Strings and ints convert to string
    return str(value)


def _parse_and_validate_districts(districts_str: str) -> list[int] | None:
    """
    Parse and validate comma-separated district IDs from URL.

    Args:
        districts_str: Comma-separated district IDs (e.g., "1,2,3,22")

    Returns:
        List of valid district IDs or None if parsing fails.

    Validation:
        - Must be integers
        - Must be in valid range (1-99 for Philadelphia districts)
        - Returns None if any district is invalid
    """
    try:
        districts = []
        for part in districts_str.split(","):
            district_id = int(float(part))  # Handle "1.0" format
            if 1 <= district_id <= 99:  # Valid district range
                districts.append(district_id)
            else:
                return None  # Invalid district range
        return districts if districts else None
    except (ValueError, TypeError, AttributeError):
        return None


def _parse_and_validate_crime_types(crime_types_str: str) -> list[str] | None:
    """
    Parse and validate comma-separated crime types from URL.

    Args:
        crime_types_str: Comma-separated crime types (e.g., "Theft,Burglary")

    Returns:
        List of crime types or None if parsing fails.

    Validation:
        - Non-empty strings only
        - Lenient validation (doesn't check against known types)
        - Returns None if empty string or parsing fails
    """
    try:
        crime_types = []
        for part in crime_types_str.split(","):
            crime_type = part.strip()
            if crime_type:  # Non-empty strings only
                crime_types.append(crime_type)
        return crime_types if crime_types else None
    except (ValueError, TypeError, AttributeError):
        return None


def _parse_and_validate_time_range(time_range_str: str) -> tuple[str, str] | None:
    """
    Parse and validate time range from URL.

    Args:
        time_range_str: Comma-separated date range (e.g., "2020-01-01,2022-12-31")

    Returns:
        Tuple of (start_date, end_date) strings or None if parsing fails.

    Validation:
        - Must be in "YYYY-MM-DD,YYYY-MM-DD" format
        - Must have exactly 2 dates
        - Start date must be <= end date (logical range)
        - Returns None if format is invalid
    """
    try:
        parts = time_range_str.split(",")
        if len(parts) != 2:
            return None

        start_date, end_date = parts[0].strip(), parts[1].strip()

        # Basic date format validation (YYYY-MM-DD)
        if len(start_date) != 10 or len(end_date) != 10:
            return None

        # Check for valid date structure (basic validation)
        if start_date <= end_date:
            return (start_date, end_date)
        else:
            return None  # Invalid logical range
    except (ValueError, TypeError, AttributeError):
        return None
