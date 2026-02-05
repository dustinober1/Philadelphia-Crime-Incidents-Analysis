"""Configuration schemas for Policy evaluation analyses."""

from typing import Literal

from pydantic import Field

from analysis.config.settings import BaseConfig


class RetailTheftConfig(BaseConfig):
    """Configuration for retail theft trend analysis."""

    model_config = {"yaml_file": "config/policy.yaml", "extra": "ignore"}

    # Focus stores (optional)
    focus_stores: list[str] | None = Field(default=None)

    # Comparison period
    baseline_start: str = "2019-01-01"
    baseline_end: str = "2020-02-01"

    # Output
    report_name: str = "retail_theft_report"
    output_format: Literal["png", "svg", "pdf"] = "png"


class VehicleCrimesConfig(BaseConfig):
    """Configuration for vehicle crimes analysis."""

    model_config = {"yaml_file": "config/policy.yaml", "extra": "ignore"}

    # UCR codes for vehicle crimes
    ucr_codes: list[int] = Field(default=[700])

    # Date range
    start_date: str = "2019-01-01"
    end_date: str = "2023-12-31"

    # Output
    report_name: str = "vehicle_crimes_report"
    output_format: Literal["png", "svg", "pdf"] = "png"


class CompositionConfig(BaseConfig):
    """Configuration for crime composition analysis."""

    model_config = {"yaml_file": "config/policy.yaml", "extra": "ignore"}

    # Grouping parameters
    group_by_ucr_hundred: bool = True

    # Output top N categories
    top_n: int = Field(default=10, ge=5, le=20)

    # Output
    report_name: str = "composition_report"
    output_format: Literal["png", "svg", "pdf"] = "png"


class EventsConfig(BaseConfig):
    """Configuration for event impact analysis."""

    model_config = {"yaml_file": "config/policy.yaml", "extra": "ignore"}

    # Event window
    days_before: int = Field(default=7, ge=1, le=30)
    days_after: int = Field(default=7, ge=1, le=30)

    # Event types (from existing event_utils.py)
    event_types: list[str] = Field(
        default=["Eagles_Home", "Phillies_Home", "Sixers_Home", "Flyers_Home"]
    )

    # Output
    report_name: str = "events_impact_report"
    output_format: Literal["png", "svg", "pdf"] = "png"
