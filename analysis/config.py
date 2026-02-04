"""Configuration constants for Phase 1 analyses."""

from pathlib import Path

# Resolve repo root from this module's location (analysis/config.py -> repo root)
_REPO_ROOT = Path(__file__).resolve().parent.parent

CRIME_DATA_PATH = _REPO_ROOT / "data" / "crime_incidents_combined.parquet"
REPORTS_DIR = _REPO_ROOT / "reports"

COLORS = {
    "Violent": "#E63946",
    "Property": "#457B9D",
    "Other": "#A8DADC",
}

# Philadelphia coordinate bounds for validation
PHILLY_LON_MIN: float = -75.30
PHILLY_LON_MAX: float = -74.95
PHILLY_LAT_MIN: float = 39.85
PHILLY_LAT_MAX: float = 40.15

# Severity weights based on FBI UCR hierarchy
# UCR hundred-bands: 100=Homicide, 200=Rape, 300=Robbery, 400=Agg Assault,
# 500=Burglary, 600=Theft, 700=Vehicle Theft, 800=Arson, 900=Other
SEVERITY_WEIGHTS: dict[int, float] = {
    100: 10.0,  # Homicide
    200: 8.0,  # Rape
    300: 6.0,  # Robbery
    400: 5.0,  # Aggravated Assault
    500: 3.0,  # Burglary
    600: 1.0,  # Theft
    700: 2.0,  # Vehicle Theft
    800: 4.0,  # Arson
    900: 0.5,  # Other
}
