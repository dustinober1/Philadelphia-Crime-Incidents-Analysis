"""Configuration management for analysis scripts.

This package provides Pydantic-based configuration management with
multi-source loading (CLI args > env vars > YAML > defaults).

Configuration hierarchy:
    1. CLI arguments (highest priority)
    2. Environment variables (CRIME_* prefix)
    3. YAML config files (config/{group}.yaml)
    4. Pydantic defaults (lowest priority)

Schemas:
    chief: Chief-level analysis config (trends, seasonality, covid)
    patrol: Patrol analysis config (hotspots, robbery, etc.)
    policy: Policy analysis config (retail theft, vehicle crimes, etc.)
    forecasting: Forecasting config (time series, classification)
"""

from pathlib import Path

from analysis.config.schemas.chief import COVIDConfig, SeasonalityConfig, TrendsConfig
from analysis.config.schemas.forecasting import ClassificationConfig, TimeSeriesConfig
from analysis.config.schemas.patrol import (
    CensusConfig,
    DistrictConfig,
    HotspotsConfig,
    RobberyConfig,
)
from analysis.config.schemas.policy import (
    CompositionConfig,
    EventsConfig,
    RetailTheftConfig,
    VehicleCrimesConfig,
)
from analysis.config.settings import BaseConfig, GlobalConfig

# Backward compatibility: Export legacy constants from old analysis/config.py
# These will be deprecated in favor of GlobalConfig in v1.2
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

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

__all__ = [
    # New configuration system
    "BaseConfig",
    "GlobalConfig",
    "TrendsConfig",
    "SeasonalityConfig",
    "COVIDConfig",
    "HotspotsConfig",
    "RobberyConfig",
    "DistrictConfig",
    "CensusConfig",
    "RetailTheftConfig",
    "VehicleCrimesConfig",
    "CompositionConfig",
    "EventsConfig",
    "TimeSeriesConfig",
    "ClassificationConfig",
    # Legacy exports (backward compatibility)
    "CRIME_DATA_PATH",
    "REPORTS_DIR",
    "COLORS",
]
