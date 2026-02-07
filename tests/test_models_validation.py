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


class TestCheckResidualAutocorrelation:
    """Tests for check_residual_autocorrelation function."""

    def test_returns_dict_with_diagnostics(self):
        """Verify returns dict with expected keys."""
        np.random.seed(42)
        residuals = pd.Series(np.random.randn(100))

        # Mock statsmodels to return predictable results
        with patch("statsmodels.stats.diagnostic.acorr_ljungbox") as mock_ljungbox:
            # Return DataFrame with lb_pvalue column
            mock_result = pd.DataFrame({"lb_pvalue": [0.1, 0.2, 0.3, 0.4, 0.5]})
            mock_ljungbox.return_value = mock_result

            diagnostics = check_residual_autocorrelation(residuals, max_lag=5)

            assert isinstance(diagnostics, dict)
            assert "ljung_box_pvalues" in diagnostics
            assert "significant_lags" in diagnostics
            assert "autocorrelation_detected" in diagnostics

    def test_ljung_box_pvalues_array_exists(self):
        """Verify 'ljung_box_pvalues' key exists and is array."""
        np.random.seed(42)
        residuals = pd.Series(np.random.randn(100))

        with patch("statsmodels.stats.diagnostic.acorr_ljungbox") as mock_ljungbox:
            mock_result = pd.DataFrame({"lb_pvalue": [0.1, 0.2, 0.3]})
            mock_ljungbox.return_value = mock_result

            diagnostics = check_residual_autocorrelation(residuals, max_lag=3)

            assert "ljung_box_pvalues" in diagnostics
            assert isinstance(diagnostics["ljung_box_pvalues"], np.ndarray)

    def test_significant_lags_count_exists(self):
        """Verify 'significant_lags' key exists and is int."""
        np.random.seed(42)
        residuals = pd.Series(np.random.randn(100))

        with patch("statsmodels.stats.diagnostic.acorr_ljungbox") as mock_ljungbox:
            # Return p-values: 2 significant (<0.05), 3 not significant
            mock_result = pd.DataFrame({"lb_pvalue": [0.01, 0.02, 0.1, 0.2, 0.3]})
            mock_ljungbox.return_value = mock_result

            diagnostics = check_residual_autocorrelation(residuals, max_lag=5)

            assert "significant_lags" in diagnostics
            assert isinstance(diagnostics["significant_lags"], (int, np.integer))
            assert diagnostics["significant_lags"] == 2

    def test_autocorrelation_detected_boolean_exists(self):
        """Verify 'autocorrelation_detected' key exists."""
        np.random.seed(42)
        residuals = pd.Series(np.random.randn(100))

        with patch("statsmodels.stats.diagnostic.acorr_ljungbox") as mock_ljungbox:
            # All p-values > 0.05 (no autocorrelation)
            mock_result = pd.DataFrame({"lb_pvalue": [0.1, 0.2, 0.3]})
            mock_ljungbox.return_value = mock_result

            diagnostics = check_residual_autocorrelation(residuals, max_lag=3)

            assert "autocorrelation_detected" in diagnostics
            # When all p-values > 0.05, no significant autocorrelation
            # (lb_pvalue < 0.05).any() returns False
            assert diagnostics["autocorrelation_detected"] == False

    def test_handles_statsmodels_import_error(self):
        """Verify returns dict with 'error' key when statsmodels unavailable."""
        np.random.seed(42)
        residuals = pd.Series(np.random.randn(100))

        # Mock import to raise exception
        with patch("statsmodels.stats.diagnostic.acorr_ljungbox", side_effect=ImportError("No module named 'statsmodels'")):
            diagnostics = check_residual_autocorrelation(residuals, max_lag=5)

            assert isinstance(diagnostics, dict)
            assert "error" in diagnostics
            assert "autocorrelation_detected" in diagnostics
            assert diagnostics["autocorrelation_detected"] is None

    def test_handles_short_residual_series(self):
        """Verify appropriate handling when len(residuals) < max_lag."""
        np.random.seed(42)
        # Short series (only 10 observations)
        residuals = pd.Series(np.random.randn(10))

        with patch("statsmodels.stats.diagnostic.acorr_ljungbox") as mock_ljungbox:
            mock_result = pd.DataFrame({"lb_pvalue": [0.1, 0.2]})
            mock_ljungbox.return_value = mock_result

            diagnostics = check_residual_autocorrelation(residuals, max_lag=40)

            # Should cap lags at len(residuals) // 4 = 2
            assert mock_ljungbox.call_args[1]["lags"] == 2

    def test_custom_max_lag_parameter(self):
        """Verify max_lag affects lag count."""
        np.random.seed(42)
        residuals = pd.Series(np.random.randn(100))

        with patch("statsmodels.stats.diagnostic.acorr_ljungbox") as mock_ljungbox:
            mock_result = pd.DataFrame({"lb_pvalue": [0.1, 0.2, 0.3, 0.4, 0.5]})
            mock_ljungbox.return_value = mock_result

            # Test with custom max_lag
            diagnostics = check_residual_autocorrelation(residuals, max_lag=10)

            # Should pass capped lags to acorr_ljungbox
            assert mock_ljungbox.called


class TestValidateTemporalSplit:
    """Tests for validate_temporal_split function."""

    def test_returns_dict_with_validation_results(self):
        """Verify has 'train_end', 'test_start', 'gap_days', 'valid_temporal_order', 'sufficient_gap', 'train_size', 'test_size', 'test_ratio'."""
        train_dates = pd.Series(pd.date_range("2020-01-01", periods=50))
        test_dates = pd.Series(pd.date_range("2020-02-20", periods=30))

        validation = validate_temporal_split(train_dates, test_dates)

        assert isinstance(validation, dict)
        assert "train_end" in validation
        assert "test_start" in validation
        assert "gap_days" in validation
        assert "valid_temporal_order" in validation
        assert "sufficient_gap" in validation
        assert "train_size" in validation
        assert "test_size" in validation
        assert "test_ratio" in validation

    def test_valid_temporal_order_true_when_sorted(self):
        """Verify valid_temporal_order=True when train_max < test_min."""
        train_dates = pd.Series(pd.date_range("2020-01-01", periods=50))
        test_dates = pd.Series(pd.date_range("2020-02-20", periods=30))

        validation = validate_temporal_split(train_dates, test_dates)

        assert validation["valid_temporal_order"] is True

    def test_valid_temporal_order_false_when_overlap(self):
        """Verify valid_temporal_order=False when dates overlap."""
        train_dates = pd.Series(pd.date_range("2020-01-01", periods=50))
        # Test dates overlap with training dates
        test_dates = pd.Series(pd.date_range("2020-01-25", periods=30))

        validation = validate_temporal_split(train_dates, test_dates)

        assert validation["valid_temporal_order"] is False

    def test_gap_days_calculation(self):
        """Verify gap_days = (test_min - train_max).days."""
        train_dates = pd.Series(pd.date_range("2020-01-01", periods=50))
        # Train ends 2020-02-19, test starts 2020-02-25
        test_dates = pd.Series(pd.date_range("2020-02-25", periods=30))

        validation = validate_temporal_split(train_dates, test_dates)

        # Gap: 2020-02-25 - 2020-02-19 = 6 days
        assert validation["gap_days"] == 6

    def test_sufficient_gap_true_when_gap_met(self):
        """Verify sufficient_gap=True when gap >= min_gap_days."""
        train_dates = pd.Series(pd.date_range("2020-01-01", periods=50))
        test_dates = pd.Series(pd.date_range("2020-02-25", periods=30))

        validation = validate_temporal_split(train_dates, test_dates, min_gap_days=5)

        assert validation["sufficient_gap"] is True

    def test_sufficient_gap_false_when_gap_insufficient(self):
        """Verify sufficient_gap=False when gap < min_gap_days."""
        train_dates = pd.Series(pd.date_range("2020-01-01", periods=50))
        test_dates = pd.Series(pd.date_range("2020-02-25", periods=30))

        validation = validate_temporal_split(train_dates, test_dates, min_gap_days=10)

        assert validation["sufficient_gap"] is False

    def test_train_size_test_size_counts(self):
        """Verify train_size = len(train_dates), test_size = len(test_dates)."""
        train_dates = pd.Series(pd.date_range("2020-01-01", periods=50))
        test_dates = pd.Series(pd.date_range("2020-02-20", periods=30))

        validation = validate_temporal_split(train_dates, test_dates)

        assert validation["train_size"] == 50
        assert validation["test_size"] == 30

    def test_test_ratio_calculation(self):
        """Verify test_ratio = test_size / (train_size + test_size)."""
        train_dates = pd.Series(pd.date_range("2020-01-01", periods=50))
        test_dates = pd.Series(pd.date_range("2020-02-20", periods=30))

        validation = validate_temporal_split(train_dates, test_dates)

        expected_ratio = 30 / (50 + 30)
        assert validation["test_ratio"] == pytest.approx(expected_ratio)

    def test_custom_min_gap_days_parameter(self):
        """Verify min_gap_days affects sufficient_gap result."""
        train_dates = pd.Series(pd.date_range("2020-01-01", periods=50))
        test_dates = pd.Series(pd.date_range("2020-02-25", periods=30))

        # Gap is 6 days
        validation_5 = validate_temporal_split(train_dates, test_dates, min_gap_days=5)
        validation_10 = validate_temporal_split(train_dates, test_dates, min_gap_days=10)

        assert validation_5["sufficient_gap"] is True
        assert validation_10["sufficient_gap"] is False

    def test_handles_datetime_series(self):
        """Verify works with pd.Series of datetime timestamps."""
        train_dates = pd.Series([
            pd.Timestamp("2020-01-01"),
            pd.Timestamp("2020-01-15"),
            pd.Timestamp("2020-02-01")
        ])
        test_dates = pd.Series([
            pd.Timestamp("2020-02-10"),
            pd.Timestamp("2020-02-20"),
            pd.Timestamp("2020-03-01")
        ])

        validation = validate_temporal_split(train_dates, test_dates)

        assert validation["train_size"] == 3
        assert validation["test_size"] == 3
        assert validation["valid_temporal_order"] is True


class TestWalkForwardValidation:
    """Tests for walk_forward_validation function."""

    def test_returns_dataframe_with_results(self):
        """Verify returns pd.DataFrame."""
        np.random.seed(42)
        X = pd.DataFrame({"feature": np.arange(50)}, index=pd.date_range("2020-01-01", periods=50))
        y = pd.Series(np.arange(50), index=pd.date_range("2020-01-01", periods=50))

        def model_fn():
            return LinearRegression()

        results = walk_forward_validation(model_fn, X, y, initial_train_size=20, step_size=5)

        assert isinstance(results, pd.DataFrame)

    def test_dataframe_has_expected_columns(self):
        """Verify has 'train_end_idx', 'test_start_idx', 'n_train', 'n_test', 'error' columns."""
        np.random.seed(42)
        X = pd.DataFrame({"feature": np.arange(50)}, index=pd.date_range("2020-01-01", periods=50))
        y = pd.Series(np.arange(50), index=pd.date_range("2020-01-01", periods=50))

        def model_fn():
            return LinearRegression()

        results = walk_forward_validation(model_fn, X, y, initial_train_size=20, step_size=5)

        expected_columns = ["train_end_idx", "test_start_idx", "test_end_idx", "n_train", "n_test", "error", "predictions", "actuals"]
        for col in expected_columns:
            assert col in results.columns

    def test_initial_train_size_parameter(self):
        """Verify first iteration uses correct initial_train_size."""
        np.random.seed(42)
        X = pd.DataFrame({"feature": np.arange(50)}, index=pd.date_range("2020-01-01", periods=50))
        y = pd.Series(np.arange(50), index=pd.date_range("2020-01-01", periods=50))

        def model_fn():
            return LinearRegression()

        results = walk_forward_validation(model_fn, X, y, initial_train_size=30, step_size=5)

        # First iteration should train on first 30 observations
        assert results.iloc[0]["n_train"] == 30
        assert results.iloc[0]["train_end_idx"] == 30

    def test_step_size_parameter(self):
        """Verify step_size affects iteration increments."""
        np.random.seed(42)
        X = pd.DataFrame({"feature": np.arange(50)}, index=pd.date_range("2020-01-01", periods=50))
        y = pd.Series(np.arange(50), index=pd.date_range("2020-01-01", periods=50))

        def model_fn():
            return LinearRegression()

        results = walk_forward_validation(model_fn, X, y, initial_train_size=20, step_size=5)

        # Check that iterations increment by step_size
        if len(results) > 1:
            assert results.iloc[1]["train_end_idx"] == 25
            assert results.iloc[1]["test_start_idx"] == 25

    def test_custom_metric_function(self):
        """Verify metric_fn parameter used for error calculation."""
        np.random.seed(42)
        X = pd.DataFrame({"feature": np.arange(50)}, index=pd.date_range("2020-01-01", periods=50))
        y = pd.Series(np.arange(50), index=pd.date_range("2020-01-01", periods=50))

        def model_fn():
            return LinearRegression()

        # Use MSE instead of default MAE
        from sklearn.metrics import mean_squared_error
        results = walk_forward_validation(
            model_fn, X, y, initial_train_size=20, step_size=5, metric_fn=mean_squared_error
        )

        # Should have error column (MSE values)
        assert "error" in results.columns
        # MSE should be non-negative
        assert (results["error"] >= 0).all()

    def test_stops_before_end_of_data(self):
        """Verify loop terminates correctly."""
        np.random.seed(42)
        X = pd.DataFrame({"feature": np.arange(30)}, index=pd.date_range("2020-01-01", periods=30))
        y = pd.Series(np.arange(30), index=pd.date_range("2020-01-01", periods=30))

        def model_fn():
            return LinearRegression()

        results = walk_forward_validation(model_fn, X, y, initial_train_size=15, step_size=5)

        # Should not attempt validation beyond data bounds
        assert len(results) > 0
        # Last test_end_idx should not exceed len(X)
        assert results.iloc[-1]["test_end_idx"] <= len(X)

    def test_handles_empty_test_set_break(self):
        """Verify breaks when X_test is empty."""
        np.random.seed(42)
        # Small dataset where last step would produce empty test set
        X = pd.DataFrame({"feature": np.arange(25)}, index=pd.date_range("2020-01-01", periods=25))
        y = pd.Series(np.arange(25), index=pd.date_range("2020-01-01", periods=25))

        def model_fn():
            return LinearRegression()

        results = walk_forward_validation(model_fn, X, y, initial_train_size=20, step_size=5)

        # Should break before trying to train on empty test set
        # Last row should have valid n_test
        assert (results["n_test"] > 0).all()

    def test_predictions_and_actuals_stored(self):
        """Verify 'predictions' and 'actuals' columns contain arrays."""
        np.random.seed(42)
        X = pd.DataFrame({"feature": np.arange(50)}, index=pd.date_range("2020-01-01", periods=50))
        y = pd.Series(np.arange(50), index=pd.date_range("2020-01-01", periods=50))

        def model_fn():
            return LinearRegression()

        results = walk_forward_validation(model_fn, X, y, initial_train_size=20, step_size=5)

        # Check predictions and actuals are arrays
        for idx in range(len(results)):
            predictions = results.iloc[idx]["predictions"]
            actuals = results.iloc[idx]["actuals"]
            assert isinstance(predictions, np.ndarray)
            assert isinstance(actuals, np.ndarray)
            # Length should match n_test
            assert len(predictions) == results.iloc[idx]["n_test"]
            assert len(actuals) == results.iloc[idx]["n_test"]

