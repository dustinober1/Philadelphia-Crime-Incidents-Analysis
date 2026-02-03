"""
Time Series Forecasting Utilities for Crime Analysis

This module provides utilities for time series preprocessing, Prophet model
configuration, and forecast evaluation.

All imports use absolute paths via __file__ to ensure modules work regardless
of working directory.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Optional, Tuple, Dict, Any

# Ensure absolute path resolution
MODULE_DIR = Path(__file__).parent.absolute()
REPO_ROOT = MODULE_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def prepare_prophet_data(
    df: pd.DataFrame, date_col: str, value_col: str
) -> pd.DataFrame:
    """
    Prepare time series data in Prophet format (ds, y columns).

    Args:
        df: Input dataframe with time series data
        date_col: Name of the date column
        value_col: Name of the value column to forecast

    Returns:
        DataFrame with 'ds' (datetime) and 'y' (numeric) columns
    """
    prophet_df = df[[date_col, value_col]].copy()
    prophet_df.columns = ["ds", "y"]
    prophet_df["ds"] = pd.to_datetime(prophet_df["ds"])
    prophet_df = prophet_df.sort_values("ds").reset_index(drop=True)

    return prophet_df


def create_train_test_split(
    df: pd.DataFrame, test_days: int = 30
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create time-aware train/test split for time series validation.

    Args:
        df: DataFrame with 'ds' column (Prophet format)
        test_days: Number of days to hold out for testing

    Returns:
        Tuple of (train_df, test_df)
    """
    if "ds" not in df.columns:
        raise ValueError("DataFrame must have 'ds' column (Prophet format)")

    train_end = df["ds"].max() - pd.Timedelta(days=test_days)
    train_df = df[df["ds"] <= train_end].copy()
    test_df = df[df["ds"] > train_end].copy()

    return train_df, test_df


def get_prophet_config(
    seasonality_mode: str = "multiplicative",
    yearly: bool = True,
    weekly: bool = True,
    daily: bool = False,
    changepoint_prior_scale: float = 0.05,
    interval_width: float = 0.95,
) -> Dict[str, Any]:
    """
    Get standard Prophet model configuration for crime forecasting.

    Args:
        seasonality_mode: 'additive' or 'multiplicative'
        yearly: Include yearly seasonality
        weekly: Include weekly seasonality
        daily: Include daily seasonality (False for aggregated data)
        changepoint_prior_scale: Flexibility of trend (lower = less flexible)
        interval_width: Width of uncertainty intervals (default 95%)

    Returns:
        Dictionary of Prophet initialization parameters
    """
    config = {
        "seasonality_mode": seasonality_mode,
        "yearly_seasonality": yearly,
        "weekly_seasonality": weekly,
        "daily_seasonality": daily,
        "changepoint_prior_scale": changepoint_prior_scale,
        "interval_width": interval_width,
    }

    return config


def evaluate_forecast(
    actual: pd.Series,
    predicted: pd.Series,
    lower: Optional[pd.Series] = None,
    upper: Optional[pd.Series] = None,
) -> Dict[str, float]:
    """
    Evaluate forecast performance using common metrics.

    Args:
        actual: Actual values (pandas Series or numpy array)
        predicted: Predicted values (pandas Series or numpy array)
        lower: Lower bound of prediction interval (optional)
        upper: Upper bound of prediction interval (optional)

    Returns:
        Dictionary of evaluation metrics
    """
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    # Convert to numpy arrays if needed
    actual_arr = np.asarray(actual)
    predicted_arr = np.asarray(predicted)

    # Filter out NaN values
    mask = ~(np.isnan(actual_arr) | np.isnan(predicted_arr))
    actual_clean = actual_arr[mask]
    predicted_clean = predicted_arr[mask]

    metrics = {
        "mae": mean_absolute_error(actual_clean, predicted_clean),
        "rmse": np.sqrt(mean_squared_error(actual_clean, predicted_clean)),
        "mape": np.mean(np.abs((actual_clean - predicted_clean) / actual_clean)) * 100,
        "r2": r2_score(actual_clean, predicted_clean),
    }

    # Coverage of prediction intervals if provided
    if lower is not None and upper is not None:
        lower_arr = np.asarray(lower)
        upper_arr = np.asarray(upper)
        lower_clean = lower_arr[mask]
        upper_clean = upper_arr[mask]
        in_interval = (actual_clean >= lower_clean) & (actual_clean <= upper_clean)
        metrics["coverage"] = in_interval.mean()

    return metrics


def detect_anomalies(
    df: pd.DataFrame,
    actual_col: str = "y",
    predicted_col: str = "yhat",
    lower_col: str = "yhat_lower",
    upper_col: str = "yhat_upper",
    threshold_std: float = 2.0,
) -> pd.Series:
    """
    Detect anomalies in time series based on forecast residuals.

    Args:
        df: DataFrame with actual and predicted values
        actual_col: Column name for actual values
        predicted_col: Column name for predictions
        lower_col: Column name for lower bound
        upper_col: Column name for upper bound
        threshold_std: Number of standard deviations for anomaly threshold

    Returns:
        Boolean series indicating anomalies
    """
    residuals = df[actual_col] - df[predicted_col]
    residual_std = residuals.std()
    residual_mean = residuals.mean()

    # Anomaly if residual exceeds threshold OR outside prediction interval
    threshold_anomaly = np.abs(residuals - residual_mean) > (
        threshold_std * residual_std
    )
    interval_anomaly = (df[actual_col] < df[lower_col]) | (
        df[actual_col] > df[upper_col]
    )

    anomalies = threshold_anomaly | interval_anomaly

    return anomalies
