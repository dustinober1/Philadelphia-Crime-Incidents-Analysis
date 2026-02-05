"""Pydantic schema definitions for each analysis."""

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

__all__ = [
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
]
