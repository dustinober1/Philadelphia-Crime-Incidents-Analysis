"""
Dashboard filter controls.

Provides sidebar filter widgets for time, geographic, and crime category filtering.
"""

# Geographic filters (04-04)
from dashboard.filters.geo_filters import (
    render_geo_filters,
    sync_geo_filters_to_url,
    read_geo_filters_from_url,
    GeoFilterState,
    get_filter_districts,
    get_district_list_from_data,
)

# Time filters (04-03)
try:
    from dashboard.filters.time_filters import (
        render_time_filters,
        sync_time_filters_to_url,
        read_time_filters_from_url,
        TimeFilterState,
        get_filter_dates,
    )
    _has_time_filters = True
except ImportError:
    _has_time_filters = False

__all__ = [
    "render_geo_filters",
    "sync_geo_filters_to_url",
    "read_geo_filters_from_url",
    "GeoFilterState",
    "get_filter_districts",
    "get_district_list_from_data",
]

# Add time filters to exports if available
if _has_time_filters:
    __all__.extend([
        "render_time_filters",
        "sync_time_filters_to_url",
        "read_time_filters_from_url",
        "TimeFilterState",
        "get_filter_dates",
    ])
