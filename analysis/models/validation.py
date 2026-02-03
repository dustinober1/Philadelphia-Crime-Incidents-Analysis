"""
Model Validation Utilities for Crime Analysis

This module provides utilities for time series cross-validation and model
evaluation metrics.

All imports use absolute paths via __file__ to ensure modules work regardless
of working directory.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Callable
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Ensure absolute path resolution
MODULE_DIR = Path(__file__).parent.absolute()
REPO_ROOT = MODULE_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def time_series_cv_score(
    model: Any,
    X: pd.DataFrame,
    y: pd.Series,
    n_splits: int = 5,
    scoring: str = "neg_mean_absolute_error",
) -> Dict[str, Any]:
    """
    Perform time series cross-validation and return scores.

    Args:
        model: Sklearn-compatible model
        X: Feature DataFrame
        y: Target Series
        n_splits: Number of CV splits
        scoring: Scoring metric name

    Returns:
        Dictionary with CV scores and statistics
    """
    from sklearn.model_selection import cross_val_score

    tscv = TimeSeriesSplit(n_splits=n_splits)
    scores = cross_val_score(model, X, y, cv=tscv, scoring=scoring)

    return {
        "scores": scores,
        "mean": scores.mean(),
        "std": scores.std(),
        "min": scores.min(),
        "max": scores.max(),
    }


def walk_forward_validation(
    model_fn: Callable,
    X: pd.DataFrame,
    y: pd.Series,
    initial_train_size: int,
    step_size: int = 1,
    metric_fn: Callable = mean_absolute_error,
) -> pd.DataFrame:
    """
    Perform walk-forward validation for time series.

    Args:
        model_fn: Function that returns a new model instance
        X: Feature DataFrame (sorted by time)
        y: Target Series
        initial_train_size: Initial training window size
        step_size: Number of observations to step forward each iteration
        metric_fn: Function to compute error metric

    Returns:
        DataFrame with predictions and errors for each step
    """
    results = []

    for i in range(initial_train_size, len(X), step_size):
        # Train on all data up to i
        X_train = X.iloc[:i]
        y_train = y.iloc[:i]

        # Test on next step_size observations
        X_test = X.iloc[i : i + step_size]
        y_test = y.iloc[i : i + step_size]

        if len(X_test) == 0:
            break

        # Train model
        model = model_fn()
        model.fit(X_train, y_train)

        # Predict
        y_pred = model.predict(X_test)

        # Compute error
        error = metric_fn(y_test, y_pred)

        results.append(
            {
                "train_end_idx": i,
                "test_start_idx": i,
                "test_end_idx": i + len(X_test),
                "n_train": len(X_train),
                "n_test": len(X_test),
                "error": error,
                "predictions": y_pred,
                "actuals": y_test.values,
            }
        )

    return pd.DataFrame(results)


def compute_regression_metrics(
    y_true: pd.Series, y_pred: pd.Series, prefix: str = ""
) -> Dict[str, float]:
    """
    Compute comprehensive regression metrics.

    Args:
        y_true: True values
        y_pred: Predicted values
        prefix: Prefix for metric names (e.g., 'train_', 'test_')

    Returns:
        Dictionary of metrics
    """
    metrics = {
        f"{prefix}mae": mean_absolute_error(y_true, y_pred),
        f"{prefix}rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
        f"{prefix}r2": r2_score(y_true, y_pred),
        f"{prefix}mape": np.mean(np.abs((y_true - y_pred) / y_true)) * 100,
    }

    # Add bias (mean error)
    metrics[f"{prefix}bias"] = np.mean(y_pred - y_true)

    return metrics


def compute_forecast_accuracy(
    actual: pd.Series, forecast: pd.Series, seasonality: Optional[int] = None
) -> Dict[str, float]:
    """
    Compute forecast accuracy metrics including MASE.

    Args:
        actual: Actual values
        forecast: Forecasted values
        seasonality: Seasonal period for MASE calculation (None = naive forecast)

    Returns:
        Dictionary of forecast accuracy metrics
    """
    # Standard metrics
    metrics = compute_regression_metrics(actual, forecast)

    # MASE (Mean Absolute Scaled Error)
    if seasonality is None:
        # Naive forecast: tomorrow = today
        naive_error = np.mean(np.abs(actual.diff().dropna()))
    else:
        # Seasonal naive: next period = same period last season
        naive_error = np.mean(np.abs(actual.diff(seasonality).dropna()))

    mae = metrics["mae"]
    metrics["mase"] = mae / naive_error if naive_error > 0 else np.inf

    return metrics


def create_model_card(
    model_name: str,
    model_type: str,
    features: List[str],
    train_metrics: Dict[str, float],
    test_metrics: Dict[str, float],
    limitations: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create a model card documenting model performance and limitations.

    Args:
        model_name: Name/identifier for the model
        model_type: Type of model (e.g., 'RandomForest', 'XGBoost', 'Prophet')
        features: List of feature names used
        train_metrics: Training set metrics
        test_metrics: Test set metrics
        limitations: Known limitations or caveats

    Returns:
        Dictionary with model card information
    """
    card = {
        "model_name": model_name,
        "model_type": model_type,
        "n_features": len(features),
        "features": features,
        "train_performance": train_metrics,
        "test_performance": test_metrics,
        "limitations": limitations or [],
        "created_at": pd.Timestamp.now().isoformat(),
    }

    return card


def check_residual_autocorrelation(
    residuals: pd.Series, max_lag: int = 40
) -> Dict[str, Any]:
    """
    Check for autocorrelation in model residuals (important for time series).

    Args:
        residuals: Model residuals (actual - predicted)
        max_lag: Maximum lag to check

    Returns:
        Dictionary with autocorrelation diagnostics
    """
    from scipy import stats

    # Ljung-Box test for autocorrelation
    # Low p-value indicates significant autocorrelation (bad)
    try:
        from statsmodels.stats.diagnostic import acorr_ljungbox

        lb_result = acorr_ljungbox(residuals, lags=min(max_lag, len(residuals) // 4))

        diagnostics = {
            "ljung_box_pvalues": lb_result["lb_pvalue"].values,
            "significant_lags": (lb_result["lb_pvalue"] < 0.05).sum(),
            "autocorrelation_detected": (lb_result["lb_pvalue"] < 0.05).any(),
        }
    except Exception as e:
        diagnostics = {
            "error": str(e),
            "autocorrelation_detected": None,
        }

    return diagnostics


def validate_temporal_split(
    train_dates: pd.Series, test_dates: pd.Series, min_gap_days: int = 0
) -> Dict[str, Any]:
    """
    Validate that train/test split maintains temporal order and gaps.

    Args:
        train_dates: Training set dates
        test_dates: Test set dates
        min_gap_days: Minimum gap required between train and test (0 = consecutive)

    Returns:
        Dictionary with validation results
    """
    train_max = train_dates.max()
    test_min = test_dates.min()

    gap_days = (test_min - train_max).days

    validation = {
        "train_end": train_max,
        "test_start": test_min,
        "gap_days": gap_days,
        "valid_temporal_order": train_max < test_min,
        "sufficient_gap": gap_days >= min_gap_days,
        "train_size": len(train_dates),
        "test_size": len(test_dates),
        "test_ratio": len(test_dates) / (len(train_dates) + len(test_dates)),
    }

    return validation
