"""
Dashboard components.

Reusable components for data loading, filtering, and visualization.
"""

from dashboard.components.cache import load_crime_data, get_data_summary
from dashboard.components.state import (
    PendingFilters,
    FilterState,
    has_pending_changes,
    get_applied_state,
    initialize_filter_state,
    mark_filter_pending,
    clear_pending_filters,
    update_applied_state,
)
from dashboard.components.plotly_interactions import (
    ViewSelectionState,
    register_plotly_selection,
    get_selection_state,
    clear_selection_state,
    update_selection_from_event,
    has_active_selection,
    get_active_filter_kwargs,
)
from dashboard.components.url_sync import (
    sync_view_selection_to_url,
    read_view_selection_from_url,
    clear_view_selection_from_url,
)

__all__ = [
    "load_crime_data",
    "get_data_summary",
    "PendingFilters",
    "FilterState",
    "has_pending_changes",
    "get_applied_state",
    "initialize_filter_state",
    "mark_filter_pending",
    "clear_pending_filters",
    "update_applied_state",
    "ViewSelectionState",
    "register_plotly_selection",
    "get_selection_state",
    "clear_selection_state",
    "update_selection_from_event",
    "has_active_selection",
    "get_active_filter_kwargs",
    "sync_view_selection_to_url",
    "read_view_selection_from_url",
    "clear_view_selection_from_url",
]
