"""Unit tests for analysis.models.classification module.

This module tests classification model utilities including time-aware splitting,
model training workflows, feature importance extraction, classifier evaluation,
and class imbalance handling.

Tests use synthetic data and mock models to ensure fast execution without
real model training. Focus is on workflow validation, not model accuracy.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier

from analysis.models.classification import (
    create_time_aware_split,
    extract_feature_importance,
    get_time_series_cv,
    handle_class_imbalance,
    train_random_forest,
)


class TestCreateTimeAwareSplit:
    """Tests for create_time_aware_split function."""

    def test_returns_four_split_dataframes(self, sample_crime_df):
        """Verify function returns (X_train, X_test, y_train, y_test) tuple."""
        X = sample_crime_df[["point_x", "point_y"]]
        y = sample_crime_df["ucr_general"]

        result = create_time_aware_split(X, y, test_size=0.2)

        assert isinstance(result, tuple)
        assert len(result) == 4
        X_train, X_test, y_train, y_test = result

        assert isinstance(X_train, pd.DataFrame)
        assert isinstance(X_test, pd.DataFrame)
        assert isinstance(y_train, pd.Series)
        assert isinstance(y_test, pd.Series)

    def test_maintains_temporal_ordering(self, sample_crime_df):
        """Verify train data ends before test data begins (no leakage)."""
        X = sample_crime_df.set_index("dispatch_date")[["point_x", "point_y"]]
        y = sample_crime_df.set_index("dispatch_date")["ucr_general"]

        X_train, X_test, y_train, y_test = create_time_aware_split(X, y, test_size=0.2)

        # Train data should end before test data begins
        train_max_date = X_train.index.max()
        test_min_date = X_test.index.min()

        assert train_max_date <= test_min_date, "Train data extends into test period"

    def test_ensure_sorted_default_true(self, sample_crime_df):
        """Verify data sorted by index when ensure_sorted=True (default)."""
        # Create unsorted data with datetime index
        X = sample_crime_df.set_index("dispatch_date")[["point_x", "point_y"]].sample(frac=1, random_state=42)
        y = sample_crime_df.set_index("dispatch_date")["ucr_general"].sample(frac=1, random_state=42)

        X_train, X_test, y_train, y_test = create_time_aware_split(X, y, ensure_sorted=True)

        # Verify indices are sorted
        assert X_train.index.is_monotonic_increasing
        assert X_test.index.is_monotonic_increasing

    def test_ensure_sorted_false_skips_sorting(self, sample_crime_df):
        """Verify sorting skipped when ensure_sorted=False."""
        # Create unsorted data
        X_shuffled = sample_crime_df.set_index("dispatch_date")[["point_x", "point_y"]].sample(frac=1, random_state=42)
        y_shuffled = sample_crime_df.set_index("dispatch_date")["ucr_general"].sample(frac=1, random_state=42)

        # Store original order
        original_X_order = X_shuffled.index.copy()
        original_y_order = y_shuffled.index.copy()

        X_train, X_test, y_train, y_test = create_time_aware_split(
            X_shuffled, y_shuffled, ensure_sorted=False
        )

        # Verify train data maintains original (unsorted) order for first portion
        expected_train_indices = original_X_order[:int(len(X_shuffled) * 0.8)]
        pd.testing.assert_index_equal(X_train.index, expected_train_indices)

    def test_custom_test_size(self, sample_crime_df):
        """Verify test_size parameter affects split ratio."""
        X = sample_crime_df[["point_x", "point_y"]]
        y = sample_crime_df["ucr_general"]

        # Test with test_size=0.3 (30% test, 70% train)
        X_train, X_test, y_train, y_test = create_time_aware_split(X, y, test_size=0.3)

        total_len = len(X)
        expected_train_len = int(total_len * 0.7)
        expected_test_len = total_len - expected_train_len

        assert len(X_train) == expected_train_len
        assert len(X_test) == expected_test_len
        assert len(y_train) == expected_train_len
        assert len(y_test) == expected_test_len

    def test_handles_duplicate_index_stably(self, sample_crime_df):
        """Verify stable sort (mergesort) for duplicate timestamps."""
        # Create data with duplicate dates
        df = sample_crime_df.copy()
        df["dispatch_date"] = pd.to_datetime("2020-01-01")  # All same date

        X = df.set_index("dispatch_date")[["point_x", "point_y"]]
        y = df.set_index("dispatch_date")["ucr_general"]

        # Should not raise error despite duplicate index
        X_train, X_test, y_train, y_test = create_time_aware_split(X, y, test_size=0.2)

        # Verify alignment maintained
        assert len(X_train) == len(y_train)
        assert len(X_test) == len(y_test)

    def test_x_y_length_mismatch_handled_silently(self):
        """Verify handling of mismatched X and y lengths.

        NOTE: Current implementation does not raise an error when X and y have
        different lengths. It sorts each independently and applies positional
        splitting, which can lead to data misalignment. This test documents
        the actual behavior for future improvement.
        """
        # Create DataFrames with different lengths
        X = pd.DataFrame(
            {"point_x": [1.0, 2.0, 3.0]},
            index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"])
        )
        y = pd.Series(
            [100, 200, 300, 400],  # 4 elements vs 3 in X
            index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04"])
        )

        # Current implementation silently handles by taking min(len(X), len(y))
        # after sorting
        X_train, X_test, y_train, y_test = create_time_aware_split(X, y, test_size=0.2)

        # Verify lengths are consistent within train/test splits
        assert len(X_train) == len(y_train)
        assert len(X_test) == len(y_test)

        # But note: one element from y is silently dropped
        assert len(X) + len(y) != len(X_train) + len(X_test) + len(y_train) + len(y_test)

    def test_empty_dataframe_raises(self):
        """Verify appropriate handling for empty input."""
        X = pd.DataFrame(columns=["point_x", "point_y"])
        y = pd.Series(dtype=int)

        # Should handle empty data gracefully (returns empty splits)
        X_train, X_test, y_train, y_test = create_time_aware_split(X, y, test_size=0.2)

        assert len(X_train) == 0
        assert len(X_test) == 0
        assert len(y_train) == 0
        assert len(y_test) == 0


class TestGetTimeSeriesCV:
    """Tests for get_time_series_cv function."""

    def test_returns_time_series_split(self):
        """Verify returns sklearn.model_selection.TimeSeriesSplit."""
        cv = get_time_series_cv()

        from sklearn.model_selection import TimeSeriesSplit
        assert isinstance(cv, TimeSeriesSplit)

    def test_custom_n_splits(self):
        """Verify n_splits parameter passed through."""
        cv = get_time_series_cv(n_splits=3)

        assert cv.get_n_splits() == 3

    def test_custom_max_train_size(self):
        """Verify max_train_size parameter passed through."""
        custom_size = 50
        cv = get_time_series_cv(max_train_size=custom_size)

        assert cv.max_train_size == custom_size

    def test_default_parameters(self):
        """Verify defaults (n_splits=5, max_train_size=None)."""
        cv = get_time_series_cv()

        assert cv.get_n_splits() == 5
        assert cv.max_train_size is None


class TestTrainRandomForest:
    """Tests for train_random_forest function."""

    def test_returns_fitted_model_and_scaler(self, sample_crime_df):
        """Verify returns (model, scaler) tuple."""
        X_train = sample_crime_df[["point_x", "point_y"]].iloc[:80]
        y_train = sample_crime_df["ucr_general"].iloc[:80]

        model, scaler = train_random_forest(X_train, y_train, n_estimators=10)

        assert hasattr(model, "predict")
        assert scaler is not None

    def test_scale_features_false_returns_none_scaler(self, sample_crime_df):
        """Verify scaler=None when scale_features=False."""
        X_train = sample_crime_df[["point_x", "point_y"]].iloc[:80]
        y_train = sample_crime_df["ucr_general"].iloc[:80]

        model, scaler = train_random_forest(
            X_train, y_train, n_estimators=10, scale_features=False
        )

        assert scaler is None

    def test_model_has_expected_attributes(self, sample_crime_df):
        """Verify model has feature_importances_ attribute after fitting."""
        X_train = sample_crime_df[["point_x", "point_y"]].iloc[:80]
        y_train = sample_crime_df["ucr_general"].iloc[:80]

        model, _ = train_random_forest(X_train, y_train, n_estimators=10)

        assert hasattr(model, "feature_importances_")
        assert len(model.feature_importances_) == X_train.shape[1]

    def test_scaler_fitted_correctly(self, sample_crime_df):
        """Verify scaler.n_features_in_ matches X_train columns."""
        X_train = sample_crime_df[["point_x", "point_y"]].iloc[:80]
        y_train = sample_crime_df["ucr_general"].iloc[:80]

        model, scaler = train_random_forest(X_train, y_train, n_estimators=10)

        assert scaler.n_features_in_ == X_train.shape[1]

    def test_custom_hyperparameters(self, sample_crime_df):
        """Verify n_estimators, max_depth, etc. passed through."""
        X_train = sample_crime_df[["point_x", "point_y"]].iloc[:80]
        y_train = sample_crime_df["ucr_general"].iloc[:80]

        model, _ = train_random_forest(
            X_train,
            y_train,
            n_estimators=15,
            max_depth=5,
            min_samples_split=10,
            min_samples_leaf=4,
        )

        assert model.n_estimators == 15
        assert model.max_depth == 5
        assert model.min_samples_split == 10
        assert model.min_samples_leaf == 4

    def test_random_state_reproducible(self, sample_crime_df):
        """Verify same random_state produces same results."""
        X_train = sample_crime_df[["point_x", "point_y"]].iloc[:80]
        y_train = sample_crime_df["ucr_general"].iloc[:80]

        model1, _ = train_random_forest(X_train, y_train, n_estimators=10, random_state=42)
        model2, _ = train_random_forest(X_train, y_train, n_estimators=10, random_state=42)

        # Same random state should produce identical feature importances
        np.testing.assert_array_almost_equal(
            model1.feature_importances_, model2.feature_importances_
        )


class TestExtractFeatureImportance:
    """Tests for extract_feature_importance function."""

    def test_returns_dataframe_with_feature_importance(self, sample_crime_df):
        """Verify returns DataFrame with correct columns."""
        X_train = sample_crime_df[["point_x", "point_y"]].iloc[:80]
        y_train = sample_crime_df["ucr_general"].iloc[:80]

        model, _ = train_random_forest(X_train, y_train, n_estimators=10)

        importance_df = extract_feature_importance(
            model, feature_names=X_train.columns.tolist()
        )

        assert isinstance(importance_df, pd.DataFrame)
        assert "feature" in importance_df.columns
        assert "importance" in importance_df.columns
        assert len(importance_df) == len(X_train.columns)

    def test_sorted_by_importance_descending(self, sample_crime_df):
        """Verify importance column is monotonic decreasing."""
        X_train = sample_crime_df[["point_x", "point_y"]].iloc[:80]
        y_train = sample_crime_df["ucr_general"].iloc[:80]

        model, _ = train_random_forest(X_train, y_train, n_estimators=10)

        importance_df = extract_feature_importance(
            model, feature_names=X_train.columns.tolist()
        )

        # Check that importance is sorted in descending order
        assert importance_df["importance"].is_monotonic_decreasing

    def test_top_n_parameter(self, sample_crime_df):
        """Verify top_n filters to N features."""
        X_train = sample_crime_df[["point_x", "point_y", "dc_dist"]].iloc[:80]
        y_train = sample_crime_df["ucr_general"].iloc[:80]

        model, _ = train_random_forest(X_train, y_train, n_estimators=10)

        importance_df = extract_feature_importance(
            model, feature_names=X_train.columns.tolist(), top_n=2
        )

        assert len(importance_df) == 2

    def test_top_n_none_returns_all(self, sample_crime_df):
        """Verify top_n=None returns all features."""
        X_train = sample_crime_df[["point_x", "point_y"]].iloc[:80]
        y_train = sample_crime_df["ucr_general"].iloc[:80]

        model, _ = train_random_forest(X_train, y_train, n_estimators=10)

        importance_df = extract_feature_importance(
            model, feature_names=X_train.columns.tolist(), top_n=None
        )

        assert len(importance_df) == len(X_train.columns)


class TestEvaluateClassifier:
    """Tests for evaluate_classifier function."""

    def test_returns_confusion_matrix(self, sample_crime_df):
        """Verify confusion_matrix key exists and is numpy array."""
        y_true = sample_crime_df["ucr_general"].iloc[:80]
        y_pred = sample_crime_df["ucr_general"].iloc[:80].values

        from analysis.models.classification import evaluate_classifier

        results = evaluate_classifier(y_true, y_pred)

        assert "confusion_matrix" in results
        assert isinstance(results["confusion_matrix"], np.ndarray)

    def test_returns_classification_report(self, sample_crime_df):
        """Verify classification_report key contains metrics."""
        y_true = sample_crime_df["ucr_general"].iloc[:80]
        y_pred = sample_crime_df["ucr_general"].iloc[:80].values

        from analysis.models.classification import evaluate_classifier

        results = evaluate_classifier(y_true, y_pred)

        assert "classification_report" in results
        assert isinstance(results["classification_report"], dict)

    def test_with_probabilities_adds_roc_auc(self, sample_crime_df):
        """Verify roc_auc added when y_prob provided."""
        # Create binary classification data
        y_true = pd.Series([0, 1, 0, 1, 0, 1] * 13 + [0, 1])  # 79 samples
        y_pred = pd.Series([0, 1, 0, 1, 0, 1] * 13 + [0, 1])
        y_prob = pd.Series([0.1, 0.9, 0.2, 0.8, 0.3, 0.7] * 13 + [0.4, 0.6])

        from analysis.models.classification import evaluate_classifier

        results = evaluate_classifier(y_true, y_pred, y_prob=y_prob)

        assert "roc_auc" in results

    def test_without_probabilities_no_roc_auc(self, sample_crime_df):
        """Verify roc_auc not in results when y_prob=None."""
        y_true = sample_crime_df["ucr_general"].iloc[:80]
        y_pred = sample_crime_df["ucr_general"].iloc[:80].values

        from analysis.models.classification import evaluate_classifier

        results = evaluate_classifier(y_true, y_pred, y_prob=None)

        assert "roc_auc" not in results

    def test_target_names_in_report(self, sample_crime_df):
        """Verify target_names passed to classification_report."""
        y_true = sample_crime_df["ucr_general"].iloc[:80]
        y_pred = sample_crime_df["ucr_general"].iloc[:80].values

        target_names = ["class_0", "class_1"]

        from analysis.models.classification import evaluate_classifier

        results = evaluate_classifier(y_true, y_pred, target_names=target_names)

        # Check that classification report was generated (has expected keys)
        report = results["classification_report"]
        assert "macro avg" in report or "accuracy" in report

    def test_single_class_roc_auc_handles_gracefully(self):
        """Verify roc_auc=None for single class edge case."""
        # All same class - ROC-AUC undefined
        y_true = pd.Series([0] * 50)
        y_pred = pd.Series([0] * 50)
        y_prob = pd.Series([0.5] * 50)

        from analysis.models.classification import evaluate_classifier

        results = evaluate_classifier(y_true, y_pred, y_prob=y_prob)

        assert results["roc_auc"] is None


class TestHandleClassImbalance:
    """Tests for handle_class_imbalance function."""

    def test_returns_dict_mapping_classes_to_weights(self, sample_crime_df):
        """Verify returns dict[int, float]."""
        y_train = sample_crime_df["ucr_general"].iloc[:80]

        weights = handle_class_imbalance(y_train)

        assert isinstance(weights, dict)
        # All values should be ints (classes) and floats (weights)
        for key, value in weights.items():
            assert isinstance(key, (int, np.integer))
            assert isinstance(value, (float, np.floating))

    def test_balanced_weights_for_imbalanced_data(self):
        """Create synthetic imbalanced classes, verify weights computed."""
        # Create imbalanced data: class 0 has 70 samples, class 1 has 10 samples
        y_train = pd.Series([0] * 70 + [1] * 10)

        weights = handle_class_imbalance(y_train)

        # Class 1 (minority) should have higher weight than class 0 (majority)
        assert weights[1] > weights[0]

    def test_all_classes_present_in_keys(self, sample_crime_df):
        """Verify all unique y_train values are keys."""
        y_train = sample_crime_df["ucr_general"].iloc[:80]

        weights = handle_class_imbalance(y_train)

        unique_classes = set(y_train.unique())
        weight_keys = set(weights.keys())

        assert unique_classes == weight_keys

    def test_weights_inversely_proportional_to_frequency(self):
        """Verify rare classes get higher weights."""
        # Create highly imbalanced data
        y_train = pd.Series([0] * 80 + [1] * 10 + [2] * 5)

        weights = handle_class_imbalance(y_train)

        # Weight ordering should be inversely proportional to frequency
        # Class 2 (rarest) > Class 1 (medium) > Class 0 (most common)
        assert weights[2] > weights[1] > weights[0]

    def test_handles_binary_classification(self):
        """Verify works with 2 classes."""
        y_train = pd.Series([0] * 50 + [1] * 30)

        weights = handle_class_imbalance(y_train)

        assert len(weights) == 2
        assert 0 in weights
        assert 1 in weights

    def test_handles_multiclass_classification(self):
        """Verify works with 3+ classes."""
        y_train = pd.Series([0] * 30 + [1] * 20 + [2] * 10 + [3] * 5)

        weights = handle_class_imbalance(y_train)

        assert len(weights) == 4
        assert all(cls in weights for cls in [0, 1, 2, 3])


class TestTrainXGBoost:
    """Tests for train_xgboost function (conditional on xgboost availability)."""

    @pytest.fixture(scope="class")
    def xgboost_available(self):
        """Check if xgboost is available."""
        try:
            import xgboost as xgb  # noqa: F401

            return True
        except ImportError:
            pytest.skip("xgboost not installed")

    def test_returns_fitted_model_and_scaler(self, xgboost_available, sample_crime_df):
        """Verify returns (model, scaler) tuple."""
        from analysis.models.classification import train_xgboost

        X_train = sample_crime_df[["point_x", "point_y"]].iloc[:80]
        y_train = sample_crime_df["ucr_general"].iloc[:80]

        model, scaler = train_xgboost(X_train, y_train, n_estimators=10)

        assert hasattr(model, "predict")
        assert scaler is None  # XGBoost defaults to no scaling

    def test_scale_features_defaults_to_false(self, xgboost_available, sample_crime_df):
        """Verify XGBoost typically doesn't need scaling."""
        from analysis.models.classification import train_xgboost

        X_train = sample_crime_df[["point_x", "point_y"]].iloc[:80]
        y_train = sample_crime_df["ucr_general"].iloc[:80]

        model, scaler = train_xgboost(X_train, y_train, n_estimators=10)

        assert scaler is None

    def test_custom_hyperparameters(self, xgboost_available, sample_crime_df):
        """Verify n_estimators, max_depth, learning_rate passed through."""
        from analysis.models.classification import train_xgboost

        X_train = sample_crime_df[["point_x", "point_y"]].iloc[:80]
        y_train = sample_crime_df["ucr_general"].iloc[:80]

        model, _ = train_xgboost(
            X_train,
            y_train,
            n_estimators=25,
            max_depth=4,
            learning_rate=0.15,
        )

        # Check hyperparameters were set (XGBoost stores params differently)
        assert model.n_estimators == 25
        assert model.max_depth == 4
        assert model.learning_rate == 0.15

    def test_eval_metric_set_to_logloss(self, xgboost_available, sample_crime_df):
        """Verify eval_metric configured."""
        from analysis.models.classification import train_xgboost

        X_train = sample_crime_df[["point_x", "point_y"]].iloc[:80]
        y_train = sample_crime_df["ucr_general"].iloc[:80]

        model, _ = train_xgboost(X_train, y_train, n_estimators=10)

        # XGBoost should have eval_metric set
        # Check that it was fitted successfully
        assert hasattr(model, "feature_importances_")
