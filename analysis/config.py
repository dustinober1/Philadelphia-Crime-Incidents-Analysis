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
