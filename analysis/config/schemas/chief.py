"""Configuration schemas for Chief-level analyses."""

from pydantic import Field

from analysis.config.settings import BaseConfig


class TrendsConfig(BaseConfig):
    """Configuration for annual crime trends analysis."""

    model_config = {"yaml_file": "config/chief.yaml", "extra": "ignore"}

    # Analysis parameters
    start_year: int = Field(default=2015, ge=2006, le=2026)
    end_year: int = Field(default=2024, ge=2006, le=2026)
    min_complete_months: int = Field(default=12, ge=1, le=12)

    # Output
    report_name: str = "annual_trends_report"


class SeasonalityConfig(BaseConfig):
    """Configuration for seasonal crime patterns analysis."""

    model_config = {"yaml_file": "config/chief.yaml", "extra": "ignore"}

    # Season definitions
    summer_months: list[int] = Field(default=[6, 7, 8])
    winter_months: list[int] = Field(default=[12, 1, 2])

    # Statistical parameters
    significance_level: float = Field(default=0.05, ge=0.01, le=0.1)

    # Output
    report_name: str = "seasonality_report"


class COVIDConfig(BaseConfig):
    """Configuration for COVID impact analysis."""

    model_config = {"yaml_file": "config/chief.yaml", "extra": "ignore"}

    # COVID period definition
    lockdown_date: str = Field(default="2020-03-01")
    before_years: list[int] = Field(default=[2018, 2019])
    after_years: list[int] = Field(default=[2021, 2022])

    # Output
    report_name: str = "covid_impact_report"
