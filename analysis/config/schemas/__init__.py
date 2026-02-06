"""Configuration schemas for analysis groups.

This package contains Pydantic Settings models for configuring analysis
scripts, with support for YAML files, environment variables, and CLI overrides.

Schemas:
    BaseConfig: Shared configuration (data paths, output directories)
    ChiefConfig: Chief-level analysis configuration
    PatrolConfig: Patrol analysis configuration
    PolicyConfig: Policy analysis configuration
    ForecastingConfig: Forecasting analysis configuration
"""

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
