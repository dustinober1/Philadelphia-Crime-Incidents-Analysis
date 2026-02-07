"""
Unit tests for models/validation.py module.

This module tests model validation utilities including:
- Time series cross-validation
- Walk-forward validation
- Regression metrics (MAE, RMSE, R², MAPE, bias)
- Forecast accuracy with MASE
- Model cards
- Residual autocorrelation checking
- Temporal split validation

All tests use synthetic data to ensure fast, deterministic execution.
Tests follow behavior-focused patterns from TESTING_QUALITY_CRITERIA.md.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

from analysis.models.validation import (
    check_residual_autocorrelation,
    compute_forecast_accuracy,
    compute_regression_metrics,
    create_model_card,
    time_series_cv_score,
    validate_temporal_split,
    walk_forward_validation,
)


class TestTimeSeriesCVScore:
    """Tests for time_series_cv_score function."""

    def test_returns_dict_with_scores_statistics(self):
        """Returns dict with 'scores', 'mean', 'std', 'min', 'max' keys."""
        np.random.seed(42)
        X = pd.DataFrame({"feature": np.arange(50)})
        y = pd.Series(np.arange(50) + np.random.randn(50) * 0.1)

        model = RandomForestRegressor(n_estimators=5, random_state=42)
        results = time_series_cv_score(model, X, y, n_splits=3)

        assert isinstance(results, dict)
        assert "scores" in results
        assert "mean" in results
        assert "std" in results
        assert "min" in results
        assert "max" in results

    def test_scores_array_length_matches_n_splits(self):
        """Verify len(scores) == n_splits."""
        np.random.seed(42)
        X = pd.DataFrame({"feature": np.arange(50)})
        y = pd.Series(np.arange(50))

        model = RandomForestRegressor(n_estimators=5, random_state=42)

        for n_splits in [3, 5, 7]:
            results = time_series_cv_score(model, X, y, n_splits=n_splits)
            assert len(results["scores"]) == n_splits

    def test_mean_computed_correctly(self):
        """Verify mean equals scores.mean()."""
        np.random.seed(42)
        X = pd.DataFrame({"feature": np.arange(50)})
        y = pd.Series(np.arange(50))

        model = RandomForestRegressor(n_estimators=5, random_state=42)
        results = time_series_cv_score(model, X, y, n_splits=5)

        assert results["mean"] == pytest.approx(results["scores"].mean())

    def test_std_computed_correctly(self):
        """Verify std equals scores.std()."""
        np.random.seed(42)
        X = pd.DataFrame({"feature": np.arange(50)})
        y = pd.Series(np.arange(50))

        model = RandomForestRegressor(n_estimators=5, random_state=42)
        results = time_series_cv_score(model, X, y, n_splits=5)

        assert results["std"] == pytest.approx(results["scores"].std())

    def test_custom_n_splits_parameter(self):
        """Verify n_splits parameter affects score count."""
        np.random.seed(42)
        X = pd.DataFrame({"feature": np.arange(50)})
        y = pd.Series(np.arange(50))

        model = RandomForestRegressor(n_estimators=5, random_state=42)

        results_3 = time_series_cv_score(model, X, y, n_splits=3)
        results_5 = time_series_cv_score(model, X, y, n_splits=5)

        assert len(results_3["scores"]) == 3
        assert len(results_5["scores"]) == 5

    def test_custom_scoring_parameter(self):
        """Verify scoring parameter passed through."""
        np.random.seed(42)
        X = pd.DataFrame({"feature": np.arange(50)})
        y = pd.Series(np.arange(50))

        model = RandomForestRegressor(n_estimators=5, random_state=42)

        # Test different scoring metrics
        for scoring in ["neg_mean_absolute_error", "neg_mean_squared_error", "r2"]:
            results = time_series_cv_score(model, X, y, n_splits=3, scoring=scoring)
            assert "mean" in results
            assert len(results["scores"]) == 3

    def test_default_scoring_neg_mean_absolute_error(self):
        """Verify default scoring is 'neg_mean_absolute_error'."""
        np.random.seed(42)
        X = pd.DataFrame({"feature": np.arange(50)})
        y = pd.Series(np.arange(50))

        model = RandomForestRegressor(n_estimators=5, random_state=42)

        # Call with default (no scoring param)
        results_default = time_series_cv_score(model, X, y, n_splits=3)

        # Call with explicit scoring
        results_explicit = time_series_cv_score(
            model, X, y, n_splits=3, scoring="neg_mean_absolute_error"
        )

        # Should produce same results
        assert results_default["mean"] == pytest.approx(results_explicit["mean"])


class TestComputeRegressionMetrics:
    """Tests for compute_regression_metrics function."""

    def test_returns_dict_with_expected_metrics(self):
        """Verify returns 'mae', 'rmse', 'r2', 'mape', 'bias' keys."""
        y_true = pd.Series([1.0, 2.0, 3.0])
        y_pred = pd.Series([1.1, 2.1, 3.1])

        metrics = compute_regression_metrics(y_true, y_pred)

        assert isinstance(metrics, dict)
        assert "mae" in metrics
        assert "rmse" in metrics
        assert "r2" in metrics
        assert "mape" in metrics
        assert "bias" in metrics

    def test_mae_calculation_with_synthetic_data(self):
        """Verify MAE = mean(|y_true - y_pred|)."""
        y_true = pd.Series([1.0, 2.0, 3.0])
        y_pred = pd.Series([1.1, 2.1, 3.1])

        metrics = compute_regression_metrics(y_true, y_pred)

        # |1-1.1| = 0.1, |2-2.1| = 0.1, |3-3.1| = 0.1
        # Mean = 0.1
        expected_mae = 0.1
        assert metrics["mae"] == pytest.approx(expected_mae)

    def test_rmse_calculation_with_synthetic_data(self):
        """Verify RMSE = sqrt(mean((y_true - y_pred)^2))."""
        y_true = pd.Series([1.0, 2.0, 3.0])
        y_pred = pd.Series([1.1, 2.1, 3.1])

        metrics = compute_regression_metrics(y_true, y_pred)

        # (1-1.1)^2 = 0.01, (2-2.1)^2 = 0.01, (3-3.1)^2 = 0.01
        # Mean = 0.01, sqrt = 0.1
        expected_rmse = 0.1
        assert metrics["rmse"] == pytest.approx(expected_rmse)

    def test_r2_calculation_perfect_prediction(self):
        """Verify R2 = 1.0 for perfect prediction."""
        y_true = pd.Series([1.0, 2.0, 3.0])
        y_pred = pd.Series([1.0, 2.0, 3.0])

        metrics = compute_regression_metrics(y_true, y_pred)

        assert metrics["r2"] == pytest.approx(1.0)

    def test_mape_calculation_with_synthetic_data(self):
        """Verify MAPE = mean(|(y_true - y_pred) / y_true|) * 100."""
        y_true = pd.Series([100.0, 200.0, 300.0])
        y_pred = pd.Series([90.0, 210.0, 330.0])

        metrics = compute_regression_metrics(y_true, y_pred)

        # |(100-90)/100| = 0.10, |(200-210)/200| = 0.05, |(300-330)/300| = 0.10
        # Mean = 0.0833, *100 = 8.33%
        expected_mape = 8.333
        assert metrics["mape"] == pytest.approx(expected_mape, abs=0.01)

    def test_bias_calculation(self):
        """Verify bias = mean(y_pred - y_true)."""
        y_true = pd.Series([100.0, 200.0, 300.0])
        y_pred = pd.Series([110.0, 210.0, 310.0])

        metrics = compute_regression_metrics(y_true, y_pred)

        # (110-100) = 10, (210-200) = 10, (310-300) = 10
        # Mean = 10
        expected_bias = 10.0
        assert metrics["bias"] == pytest.approx(expected_bias)

    def test_prefix_added_to_all_metrics(self):
        """Verify all metric names have prefix when provided."""
        y_true = pd.Series([1.0, 2.0, 3.0])
        y_pred = pd.Series([1.1, 2.1, 3.1])

        metrics = compute_regression_metrics(y_true, y_pred, prefix="test_")

        assert all(key.startswith("test_") for key in metrics.keys())
        assert "test_mae" in metrics
        assert "test_rmse" in metrics
        assert "test_r2" in metrics
        assert "test_mape" in metrics
        assert "test_bias" in metrics

    def test_empty_prefix_no_underscore(self):
        """Verify prefix="" gives 'mae' not '_mae'."""
        y_true = pd.Series([1.0, 2.0, 3.0])
        y_pred = pd.Series([1.1, 2.1, 3.1])

        metrics = compute_regression_metrics(y_true, y_pred, prefix="")

        assert "mae" in metrics
        assert "rmse" in metrics
        assert "_mae" not in metrics  # No underscore prefix

    def test_raises_error_with_nan_values(self):
        """Verify raises ValueError when y_true contains NaN."""
        y_true = pd.Series([1.0, np.nan, 3.0, 4.0])
        y_pred = pd.Series([1.1, 2.1, 3.1, 4.1])

        # sklearn metrics raise ValueError on NaN input
        with pytest.raises(ValueError, match="Input contains NaN"):
            compute_regression_metrics(y_true, y_pred)
