"""Configuration constants for Phase 1 analyses."""

from pathlib import Path

CRIME_DATA_PATH = Path("data") / "crime_incidents_combined.parquet"
REPORTS_DIR = Path("reports")

COLORS = {
    "Violent": "#E63946",
    "Property": "#457B9D",
    "Other": "#A8DADC",
}
