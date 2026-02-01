"""
Dashboard-specific configuration constants.
"""

from analysis.config import STAT_CONFIG, CRIME_DATA_PATH

# Page/tab names
PAGE_NAMES = {
    "overview": "Overview/Stats",
    "temporal": "Temporal Trends",
    "spatial": "Spatial Maps",
    "correlations": "Correlations",
    "advanced": "Advanced Temporal",
}

ALL_TABS = list(PAGE_NAMES.values())

# Filter defaults
FILTER_DEFAULTS = {
    # Date range (full dataset excluding incomplete 2026)
    "start_date": "2006-01-01",
    "end_date": "2025-12-31",
    # Police districts (all districts 1-23)
    "districts": list(range(1, 24)),
    # Crime categories
    "crime_categories": ["Violent", "Property", "Other"],
    # Include 2026 data (incomplete year)
    "include_2026": False,
}

# Cache configuration for data loading
CACHE_CONFIG = {
    "data_ttl": 3600,  # 1 hour
    "data_max_entries": 10,
    "filter_ttl": 1800,  # 30 minutes
    "filter_max_entries": 50,
}

# State management configuration for cross-filtering
STATE_CONFIG = {
    "apply_button_enabled": True,  # Master switch for apply button feature
    "auto_sync_url": False,  # Sidebar filters only sync to URL on apply
    "pending_ttl": 300,  # 5 minutes - pending state persistence
    "view_state_ttl": 1800,  # 30 minutes - view-to-view cross-filter state
}

# Plotly interaction configuration for view-to-view cross-filtering
PLOTLY_CONFIG = {
    # Selection mode for charts
    "selection_mode": "select",  # "select" for box/lasso, False to disable
    # Selection event handling
    "on_select_rerun": True,  # Use on_select="rerun" for instant cross-filtering
    # Visual feedback for selections
    "selected_opacity": 1.0,  # Full opacity for selected elements
    "unselected_opacity": 0.3,  # 30% opacity for unselected (dimmed)
    # Hover behavior
    "hover_mode": "closest",  # Show hover info for nearest data point
    # Selection persistence
    "selection_ttl": 1800,  # 30 minutes - view selections persist longer than pending filters
    # Selection limits
    "max_selections": 100,  # Max points allowed in selection (prevents performance issues)
}

# Dashboard display settings
DISPLAY_CONFIG = {
    "title": "Philadelphia Crime Incidents Dashboard",
    "subtitle": "Exploratory Data Analysis (2006-2025)",
    "layout": "wide",  # Streamlit page layout
}
