"""Configuration schemas for Forecasting analyses."""

from pydantic import Field

from analysis.config.settings import BaseConfig


class TimeSeriesConfig(BaseConfig):
    """Configuration for time series forecasting analysis."""

    model_config = {"yaml_file": "config/forecasting.yaml", "extra": "ignore"}

    # Forecasting parameters
    forecast_horizon: int = Field(default=12, ge=1, le=52)  # weeks/months
    forecast_test_size: float = Field(default=0.2, ge=0.1, le=0.5)

    # Model selection
    model_type: str = Field(default="prophet", pattern="^(prophet|arima|ets)$")

    # Output
    report_name: str = "forecast_report"


class ClassificationConfig(BaseConfig):
    """Configuration for violence classification analysis."""

    model_config = {"yaml_file": "config/forecasting.yaml", "extra": "ignore"}

    # Target definition
    violent_ucr_codes: list[int] = Field(default=[100, 200, 300, 400])

    # Model parameters
    classification_test_size: float = Field(default=0.25, ge=0.1, le=0.5)
    random_state: int = 42

    # Feature importance threshold
    importance_threshold: float = Field(default=0.01, ge=0.001, le=0.1)

    # Output
    report_name: str = "classification_report"
