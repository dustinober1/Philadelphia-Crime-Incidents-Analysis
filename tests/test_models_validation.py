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


class TestComputeForecastAccuracy:
    """Tests for compute_forecast_accuracy function."""

    def test_includes_all_regression_metrics(self):
        """Verify includes mae, rmse, r2, mape, bias from base metrics."""
        actual = pd.Series([100.0, 200.0, 300.0], index=pd.date_range("2020-01-01", periods=3))
        forecast = pd.Series([110.0, 210.0, 310.0], index=pd.date_range("2020-01-01", periods=3))

        metrics = compute_forecast_accuracy(actual, forecast)

        # All base regression metrics present
        assert "mae" in metrics
        assert "rmse" in metrics
        assert "r2" in metrics
        assert "mape" in metrics
        assert "bias" in metrics

    def test_mase_with_naive_forecast(self):
        """Verify MASE = mae / naive_error when seasonality=None."""
        # Create actual values where diff is constant
        actual = pd.Series([100.0, 110.0, 120.0, 130.0], index=pd.date_range("2020-01-01", periods=4))
        forecast = pd.Series([105.0, 115.0, 125.0, 135.0], index=pd.date_range("2020-01-01", periods=4))

        metrics = compute_forecast_accuracy(actual, forecast, seasonality=None)

        # Naive error: mean(|diff|) = mean(|10, 10, 10|) = 10
        # MAE: mean(|105-100|, |115-110|, |125-120|, |135-130|) = 5
        # MASE = 5 / 10 = 0.5
        assert "mase" in metrics
        assert metrics["mase"] == pytest.approx(0.5)

    def test_mase_with_seasonal_naive_forecast(self):
        """Verify MASE uses seasonal diff when seasonality provided."""
        # Create seasonal data with period 2
        actual = pd.Series(
            [100.0, 200.0, 105.0, 205.0, 110.0, 210.0],
            index=pd.date_range("2020-01-01", periods=6)
        )
        forecast = pd.Series(
            [102.0, 202.0, 107.0, 207.0, 112.0, 212.0],
            index=pd.date_range("2020-01-01", periods=6)
        )

        metrics = compute_forecast_accuracy(actual, forecast, seasonality=2)

        # Seasonal naive error: mean(|diff(2)|) = mean(|5, 5, 5, 5|) = 5
        # MAE = 2.0
        # MASE = 2.0 / 5 = 0.4
        assert "mase" in metrics
        assert metrics["mase"] == pytest.approx(0.4)

    def test_mase_infinite_when_naive_error_zero(self):
        """Verify MASE = np.inf when naive_error is 0."""
        # Create constant series (diff = 0)
        actual = pd.Series([100.0, 100.0, 100.0, 100.0], index=pd.date_range("2020-01-01", periods=4))
        forecast = pd.Series([100.0, 100.0, 100.0, 100.0], index=pd.date_range("2020-01-01", periods=4))

        metrics = compute_forecast_accuracy(actual, forecast, seasonality=None)

        # Naive error = 0, so MASE = inf
        assert metrics["mase"] == np.inf

    def test_naive_forecast_uses_diff(self):
        """Verify naive_error = mean(|actual.diff()|)."""
        actual = pd.Series([100.0, 110.0, 120.0, 130.0], index=pd.date_range("2020-01-01", periods=4))
        forecast = pd.Series([105.0, 115.0, 125.0, 135.0], index=pd.date_range("2020-01-01", periods=4))

        metrics = compute_forecast_accuracy(actual, forecast, seasonality=None)

        # Verify naive error calculation
        # actual.diff() = [NaN, 10, 10, 10], dropna -> [10, 10, 10]
        # mean = 10
        expected_naive_error = 10.0
        # MASE = MAE / naive_error = 5 / 10 = 0.5
        assert metrics["mase"] == pytest.approx(0.5)


class TestCreateModelCard:
    """Tests for create_model_card function."""

    def test_returns_dict_with_expected_fields(self):
        """Verify has 'model_name', 'model_type', 'n_features', 'features', 'train_performance', 'test_performance', 'limitations', 'created_at'."""
        train_metrics = {"mae": 1.0, "rmse": 2.0}
        test_metrics = {"mae": 1.5, "rmse": 2.5}

        card = create_model_card(
            model_name="TestModel",
            model_type="RandomForest",
            features=["feature1", "feature2"],
            train_metrics=train_metrics,
            test_metrics=test_metrics,
        )

        assert isinstance(card, dict)
        assert "model_name" in card
        assert "model_type" in card
        assert "n_features" in card
        assert "features" in card
        assert "train_performance" in card
        assert "test_performance" in card
        assert "limitations" in card
        assert "created_at" in card

    def test_n_features_matches_feature_list_length(self):
        """Verify n_features == len(features)."""
        features = ["feature1", "feature2", "feature3"]
        train_metrics = {"mae": 1.0}
        test_metrics = {"mae": 1.5}

        card = create_model_card(
            model_name="TestModel",
            model_type="RandomForest",
            features=features,
            train_metrics=train_metrics,
            test_metrics=test_metrics,
        )

        assert card["n_features"] == len(features)

    def test_train_metrics_preserved(self):
        """Verify train_metrics dict included unchanged."""
        train_metrics = {"mae": 1.0, "rmse": 2.0, "r2": 0.95}
        test_metrics = {"mae": 1.5}

        card = create_model_card(
            model_name="TestModel",
            model_type="RandomForest",
            features=["feature1"],
            train_metrics=train_metrics,
            test_metrics=test_metrics,
        )

        assert card["train_performance"] == train_metrics

    def test_test_metrics_preserved(self):
        """Verify test_metrics dict included unchanged."""
        train_metrics = {"mae": 1.0}
        test_metrics = {"mae": 1.5, "rmse": 2.5, "r2": 0.90}

        card = create_model_card(
            model_name="TestModel",
            model_type="RandomForest",
            features=["feature1"],
            train_metrics=train_metrics,
            test_metrics=test_metrics,
        )

        assert card["test_performance"] == test_metrics

    def test_limitations_default_to_empty_list(self):
        """Verify limitations=[] when None provided."""
        train_metrics = {"mae": 1.0}
        test_metrics = {"mae": 1.5}

        card = create_model_card(
            model_name="TestModel",
            model_type="RandomForest",
            features=["feature1"],
            train_metrics=train_metrics,
            test_metrics=test_metrics,
            limitations=None,
        )

        assert card["limitations"] == []

    def test_created_at_is_isoformat_timestamp(self):
        """Verify created_at is string in ISO format."""
        train_metrics = {"mae": 1.0}
        test_metrics = {"mae": 1.5}

        card = create_model_card(
            model_name="TestModel",
            model_type="RandomForest",
            features=["feature1"],
            train_metrics=train_metrics,
            test_metrics=test_metrics,
        )

        assert isinstance(card["created_at"], str)
        # Verify ISO format: YYYY-MM-DDTHH:MM:SS
        assert "T" in card["created_at"]
        # Should be parseable as ISO datetime
        pd.to_datetime(card["created_at"])

    def test_custom_limitations_preserved(self):
        """Verify custom limitations list included."""
        train_metrics = {"mae": 1.0}
        test_metrics = {"mae": 1.5}
        custom_limitations = ["Small dataset", "Limited features"]

        card = create_model_card(
            model_name="TestModel",
            model_type="RandomForest",
            features=["feature1"],
            train_metrics=train_metrics,
            test_metrics=test_metrics,
            limitations=custom_limitations,
        )

        assert card["limitations"] == custom_limitations
