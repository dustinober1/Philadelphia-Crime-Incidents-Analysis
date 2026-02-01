"""
Dashboard page renderers.

Each page corresponds to a tab in the main dashboard.
"""

from dashboard.pages.overview import render_overview_page
from dashboard.pages.temporal import render_temporal_page
from dashboard.pages.spatial import render_spatial_page
from dashboard.pages.correlations import render_correlations_page
from dashboard.pages.advanced import render_advanced_page

__all__ = [
    "render_overview_page",
    "render_temporal_page",
    "render_spatial_page",
    "render_correlations_page",
    "render_advanced_page",
]
