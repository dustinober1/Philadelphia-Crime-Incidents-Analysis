"""Configuration system for crime analysis CLI.

Uses pydantic-settings for multi-source configuration:
- YAML files (defaults)
- Environment variables (overrides)
- CLI arguments (highest priority)
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
