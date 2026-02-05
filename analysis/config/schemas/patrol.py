"""Configuration schemas for Patrol operations analyses."""

from pydantic import Field

from analysis.config.settings import BaseConfig


class HotspotsConfig(BaseConfig):
    """Configuration for crime hotspot clustering analysis."""

    model_config = {"yaml_file": "config/patrol.yaml", "extra": "ignore"}

    # Clustering parameters
    eps_degrees: float = Field(default=0.002, ge=0.0001, le=0.01)
    min_samples: int = Field(default=50, ge=10, le=500)
    algorithm: str = Field(default="DBSCAN")

    # Spatial filtering
    lon_min: float = -75.30
    lon_max: float = -74.95
    lat_min: float = 39.85
    lat_max: float = 40.15

    # Output
    report_name: str = "hotspots_report"


class RobberyConfig(BaseConfig):
    """Configuration for robbery temporal hotspot analysis."""

    model_config = {"yaml_file": "config/patrol.yaml", "extra": "ignore"}

    # Time binning
    time_bin_size: int = Field(default=60, ge=15, le=240)  # minutes

    # Heatmap settings
    grid_size: int = Field(default=20, ge=10, le=50)

    # Output
    report_name: str = "robbery_heatmap_report"


class DistrictConfig(BaseConfig):
    """Configuration for district severity scoring analysis."""

    model_config = {"yaml_file": "config/patrol.yaml", "extra": "ignore"}

    # Severity weights (optional override of defaults)
    enable_custom_weights: bool = False
    # If enable_custom_weights is True, load from YAML

    # District filtering
    districts: list[int] | None = Field(default=None)  # None = all districts

    # Output
    report_name: str = "district_severity_report"


class CensusConfig(BaseConfig):
    """Configuration for census tract crime rate analysis."""

    model_config = {"yaml_file": "config/patrol.yaml", "extra": "ignore"}

    # Census data source
    census_file: str = "census_tracts.geojson"

    # Rate normalization
    population_threshold: int = Field(default=100, ge=0)  # Minimum population

    # Output
    report_name: str = "census_rates_report"
