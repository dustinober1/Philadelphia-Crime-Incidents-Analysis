"""
Configuration constants for Philadelphia Crime Incidents EDA.

Defines paths, plot settings, analysis parameters, and statistical configuration.
"""

from datetime import timedelta
from pathlib import Path

# =============================================================================
# PATHS
# =============================================================================

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Main dataset
CRIME_DATA_PATH = DATA_DIR / "crime_incidents_combined.parquet"

CLEANED_DATA_PATH = PROCESSED_DATA_DIR / "crime_incidents_cleaned.parquet"

# Output paths
ANALYSIS_DIR = PROJECT_ROOT / "analysis"
REPORTS_DIR = PROJECT_ROOT / "reports"
TEMP_DIR = PROJECT_ROOT / ".temp"

# External data paths
EXTERNAL_DATA_DIR = DATA_DIR / "external"
EXTERNAL_CACHE_DIR = EXTERNAL_DATA_DIR / ".cache"

# =============================================================================
# EXTERNAL DATA CACHING CONFIGURATION
# =============================================================================

# Cache staleness settings for different data sources
# Longer staleness = fewer API calls but potentially stale data
CACHE_CONFIG = {
    # Weather data: 7 days (historical data doesn't change often)
    "weather_staleness": 7,  # days

    # FRED economic data: 30 days (monthly updates, safe cache window)
    "fred_staleness": 30,  # days

    # Census ACS data: 365 days (retroactive data never changes)
    "census_staleness": 365,  # days

    # Cache backend type ('sqlite', 'memory', 'redis')
    "cache_backend": "sqlite",

    # Whether to use cache (set to False to force fresh API calls)
    "cache_enabled": True,
}


def get_cache_staleness(source: str) -> timedelta:
    """
    Get cache staleness duration for a data source.

    Args:
        source: Data source name ('weather', 'fred', 'census').

    Returns:
        timedelta object for the staleness period.

    Raises:
        ValueError: If source name is not recognized.

    Example:
        >>> from analysis.config import get_cache_staleness
        >>> delta = get_cache_staleness('weather')
        >>> print(delta.days)
        7
    """
    key = f"{source.lower()}_staleness"
    if key not in CACHE_CONFIG:
        raise ValueError(f"Unknown cache source: {source}. Use 'weather', 'fred', or 'census'.")
    return timedelta(days=CACHE_CONFIG[key])


# =============================================================================
# TEMPORAL ALIGNMENT CONFIGURATION
# =============================================================================#

# Temporal resolution for different analysis types
# Higher resolution = more data points but requires more aligned data sources
TEMPORAL_CONFIG = {
    # Daily analysis: crime + weather (no economic data due to monthly frequency)
    "daily_start": "2006-01-01",
    "daily_end": "2025-12-31",  # Exclude 2026 (incomplete)

    # Monthly analysis: crime + weather + FRED unemployment
    "monthly_start": "2006-01-01",
    "monthly_end": "2025-12-31",

    # Annual analysis: crime + weather + FRED + Census ACS
    "annual_start": "2010",  # ACS 5-year estimates available from 2010
    "annual_end": "2023",  # Most recent complete ACS data
}


def get_analysis_range(resolution: str = "monthly") -> tuple:
    """
    Get date range for analysis at specified temporal resolution.

    Args:
        resolution: Temporal resolution ('daily', 'monthly', 'annual').

    Returns:
        Tuple of (start_date, end_date) as strings.

    Raises:
        ValueError: If resolution not recognized.

    Example:
        >>> start, end = get_analysis_range('monthly')
        >>> print(f'{start} to {end}')
        '2006-01-01 to 2025-12-31'
    """
    valid_resolutions = ("daily", "monthly", "annual")
    if resolution not in valid_resolutions:
        raise ValueError(f"Unknown resolution: {resolution}. Use 'daily', 'monthly', or 'annual'.")
    return TEMPORAL_CONFIG[f"{resolution}_start"], TEMPORAL_CONFIG[f"{resolution}_end"]


# =============================================================================
# DATASET INFO
# =============================================================================

DATASET_INFO = {
    "total_records": 3_496_353,
    "temporal_range": ("2006-01-01", "2026-01-20"),
    "crime_types": 32,
    "police_districts": 26,
}

# =============================================================================
# PLOT SETTINGS
# =============================================================================#

# Figure sizes (in inches)
FIGURE_SIZES = {
    "small": (8, 6),
    "medium": (12, 8),
    "wide": (16, 8),
    "large": (14, 10),
    "heatmap": (16, 12),
    "square": (10, 10),
}

# Color schemes
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "danger": "#d62728",
    "success": "#2ca02c",
    "warning": "#ffbb00",
    "palette": "tab20",  # matplotlib colormap for categorical data
    "sequential": "YlOrRd",  # for heatmaps
    "diverging": "RdBu_r",  # for diverging data
}

# Philadelphia approximate bounding box
PHILADELPHIA_BBOX = {
    "lon_min": -75.28,
    "lon_max": -74.95,
    "lat_min": 39.86,
    "lat_max": 40.14,
}

# =============================================================================
# STATISTICAL ANALYSIS CONFIGURATION
# =============================================================================

# Statistical parameters for rigorous analysis
# 99% CI chosen for more conservative analysis appropriate to exploratory nature
STAT_CONFIG = {
    # Confidence level for all intervals (99% for conservative analysis)
    "confidence_level": 0.99,

    # Significance alpha for tests (matches 99% CI)
    "alpha": 0.01,

    # Bootstrap parameters
    "bootstrap_n_resamples": 9999,
    "bootstrap_random_state": 42,

    # Normality test threshold
    "normality_alpha": 0.05,

    # Effect size benchmarks (Cohen's d interpretation)
    "effect_size_small": 0.2,
    "effect_size_medium": 0.5,
    "effect_size_large": 0.8,

    # Cliff's Delta thresholds (non-parametric effect size)
    # Source: Romano et al. (2006). Appropriate statistics for ordinal level data.
    "cliffs_delta_negligible": 0.147,
    "cliffs_delta_small": 0.33,
    "cliffs_delta_medium": 0.474,

    # FDR correction method ('bh' = Benjamini-Hochberg, 'by' = Benjamini-Yekutieli)
    "fdr_method": "bh",

    # Random seed for reproducibility (used across all statistical operations)
    "random_seed": 42,

    # Legacy key for backward compatibility
    "significance_threshold": 0.01,  # Same as alpha
}


# =============================================================================
# EFFECT SIZE INTERPRETATION HELPERS
# =============================================================================

def interpret_cliffs_delta(delta: float) -> str:
    """
    Interpret Cliff's Delta effect size using configured thresholds.

    Cliff's Delta is a non-parametric effect size measure for ordinal data.
    More robust than Cohen's d for non-normal distributions.

    Args:
        delta: Cliff's Delta value (-1 to +1)

    Returns:
        Interpretation string: negligible, small, medium, or large

    Interpretation thresholds (Romano et al., 2006):
    - negligible: |d| < 0.147
    - small: 0.147 <= |d| < 0.33
    - medium: 0.33 <= |d| < 0.474
    - large: |d| >= 0.474

    Example:
        >>> interpret_cliffs_delta(0.4)
        'medium'
        >>> interpret_cliffs_delta(-0.6)
        'large'
    """
    abs_d = abs(delta)
    if abs_d < STAT_CONFIG["cliffs_delta_negligible"]:
        return "negligible"
    elif abs_d < STAT_CONFIG["cliffs_delta_small"]:
        return "small"
    elif abs_d < STAT_CONFIG["cliffs_delta_medium"]:
        return "medium"
    else:
        return "large"


# =============================================================================
# ANALYSIS PARAMETERS
# =============================================================================

# Coordinate validation
LON_MIN, LON_MAX = PHILADELPHIA_BBOX["lon_min"], PHILADELPHIA_BBOX["lon_max"]
LAT_MIN, LAT_MAX = PHILADELPHIA_BBOX["lat_min"], PHILADELPHIA_BBOX["lat_max"]

# Date parsing
DATE_COLUMNS = ["dispatch_date", "dispatch_time"]
DATETIME_COLUMN = "dispatch_datetime"

# Missing data threshold for exclusion
MISSING_THRESHOLD = 0.5  # Drop columns with >50% missing

# =============================================================================
# REPORT SETTINGS
# =============================================================================#

REPORT_TITLE = "# Philadelphia Crime Incidents - Exploratory Data Analysis Report"
REPORT_AUTHOR = "Generated by Claude Code"
REPORT_DATE_FORMAT = "%B %d, %Y"

# Markdown section headers
SECTION_HEADERS = {
    "data_quality": "## Phase 1: Data Quality Assessment",
    "temporal": "## Phase 2: Temporal Analysis",
    "categorical": "## Phase 3: Categorical Analysis",
    "spatial": "## Phase 4: Spatial Analysis",
    "cross": "## Phase 5: Cross-Dimensional Analysis",
    "summary": "## Phase 6: Summary and Key Findings",
}

# =============================================================================
# POLICING DATA CONFIGURATION
# =============================================================================

# Philadelphia policing data sources and availability
# Note: No programmatic API exists for Philadelphia policing data
POLICING_DATA_CONFIG = {
    # Data sources that exist but lack API access
    "sources": {
        "controller_reports": {
            "name": "Philadelphia Controller's Office",
            "url": "https://controller.phila.gov/policing-in-philadelphia/",
            "format": "PDF reports",
            "years_available": [2022, 2024],
            "api": False,
            "notes": "Static PDF reports with some data tables. No bulk CSV download.",
        },
        "dao_dashboard": {
            "name": "District Attorney's Office Data Dashboard",
            "url": "https://dao.phila.gov/data/",
            "format": "Interactive web dashboard",
            "years_available": "Recent years only",
            "api": False,
            "notes": "Limited visual dashboard, no export capability.",
        },
        "opendataphilly": {
            "name": "OpenDataPhilly",
            "url": "https://www.opendataphilly.org/",
            "format": "Varies (CSV, API, shapefile)",
            "years_available": "Varies by dataset",
            "api": "Varies by dataset",
            "notes": "May have historical policing datasets. Requires manual search.",
        },
    },

    # Data variables of interest (if available)
    "variables_of_interest": [
        "police_officer_count_by_district",
        "arrest_rates_by_district",
        "response_times",
        "patrol_hours_by_district",
        "budget_allocation",
    ],

    # Assessment status
    "available_for_correlation": False,
    "limitation": "No programmatic API access. Data exists in static PDFs and dashboards.",
    "recommendation": "Manual data entry from PDF reports or web scraping (fragile).",
}


# =============================================================================
# CLUSTERING / RED ZONES ANALYSIS
# =============================================================================#

# Philadelphia center point for map initialization
PHILADELPHIA_CENTER = {"lat": 39.9526, "lon": -75.1652}

# DBSCAN parameters for hotspot detection
# eps_meters: radius for clustering (150m ~ 500ft, patrol-relevant scale)
# min_samples: minimum incidents to form a hotspot
DBSCAN_CONFIG = {
    "eps_meters": 150,  # ~500ft radius for clustering
    "min_samples": 50,  # Minimum incidents for a hotspot
}

# Sampling for performance (full dataset too large for clustering)
CLUSTERING_SAMPLE_SIZE = 500_000  # Sample size for overall hotspot detection

# Crime type groupings for focused hotspot analysis
CRIME_TYPE_FOCUS = {
    "narcotics": ["Narcotics", "Drug Violations"],
    "violent": [
        "Homicide - Criminal",
        "Homicide - Gross Negligence",
        "Rape",
        "Robbery Firearm",
        "Robbery No Firearm",
        "Aggravated Assault Firearm",
        "Aggravated Assault No Firearm",
    ],
    "property": [
        "Burglary Residential",
        "Burglary Non-Residential",
        "Thefts",
        "Theft from Vehicle",
        "Motor Vehicle Theft",
    ],
}

# Hotspot ranking criteria weights
HOTSPOT_WEIGHTS = {
    "incident_count": 0.5,    # 50% weight on total incidents
    "density": 0.3,            # 30% weight on incidents per square km
    "consistency": 0.2,        # 20% weight on year-over-year consistency
}
