"""Tests for pipeline exporter."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest
from typer.testing import CliRunner

from pipeline import export_data
from pipeline.export_data import (
    _ensure_dir,
    _export_forecasting,
    _export_metadata,
    _export_policy,
    _export_seasonality,
    _export_spatial,
    _export_trends,
    _to_records,
    _write_json,
    app,
)
from pipeline.refresh_data import app as refresh_app

runner = CliRunner()


def test_export_output_dir_option(tmp_path: Path) -> None:
    output_dir = tmp_path / "api_data"
    result = runner.invoke(app, ["--output-dir", str(output_dir)])
    assert result.exit_code == 0
    assert (output_dir / "metadata.json").exists()
    assert (output_dir / "annual_trends.json").exists()


def test_refresh_and_validate_command(tmp_path: Path) -> None:
    output_dir = tmp_path / "api_data"
    result = runner.invoke(refresh_app, ["--output-dir", str(output_dir)])
    assert result.exit_code == 0
    assert "Validated exports" in result.stdout
    assert (output_dir / "forecast.json").exists()


# Task 1: Missing dependency tests


class TestMissingDependencies:
    """Test graceful fallback when optional dependencies are unavailable."""

    def test_export_spatial_returns_early_without_geopandas(
        self, sample_crime_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Verify _export_spatial returns without error when HAS_GEOPANDAS=False."""
        with patch.object(export_data, "HAS_GEOPANDAS", False):
            # Should not raise any exception
            export_data._export_spatial(
                sample_crime_df, tmp_path, tmp_path / "geo", tmp_path
            )

            # Spatial files should not be created
            assert not (tmp_path / "geo" / "districts.geojson").exists()
            assert not (tmp_path / "geo" / "tracts.geojson").exists()

    def test_export_forecasting_uses_fallback_without_prophet(
        self, sample_crime_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Verify _export_forecasting uses LinearFallback when HAS_PROPHET=False."""
        from analysis.utils.temporal import extract_temporal_features

        # Prepare data with temporal features
        df = extract_temporal_features(sample_crime_df)

        with patch.object(export_data, "HAS_PROPHET", False):
            export_data._export_forecasting(df, tmp_path)

            # Forecast file should be created with fallback model
            forecast_file = tmp_path / "forecast.json"
            assert forecast_file.exists()

            forecast = json.loads(forecast_file.read_text())
            assert forecast["model"] == "LinearFallback"
            assert "historical" in forecast
            assert "forecast" in forecast

    def test_export_forecasting_uses_defaults_without_sklearn(
        self, sample_crime_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Verify classification_features uses defaults when HAS_SKLEARN=False."""
        from analysis.utils.classification import classify_crime_category
        from analysis.utils.temporal import extract_temporal_features

        # Prepare data with temporal features and classification
        df = extract_temporal_features(sample_crime_df)
        df = classify_crime_category(df)

        with patch.object(export_data, "HAS_SKLEARN", False):
            export_data._export_forecasting(df, tmp_path)

            # Classification features file should be created with defaults
            features_file = tmp_path / "classification_features.json"
            assert features_file.exists()

            features = json.loads(features_file.read_text())
            assert len(features) == 4
            # All features should have equal importance (0.25)
            for feature in features:
                assert feature["importance"] == 0.25


# =============================================================================
# Helper Function Tests (Task 1)
# =============================================================================


class TestWriteJson:
    """Tests for _write_json helper function."""

    def test_write_json_creates_valid_file(self, tmp_path: Path) -> None:
        """Verify _write_json creates file with valid JSON content."""
        output_file = tmp_path / "test.json"
        test_data = {"key": "value", "number": 42, "nested": {"a": 1}}

        _write_json(output_file, test_data)

        assert output_file.exists()
        with output_file.open("r") as f:
            loaded = json.load(f)
        assert loaded == test_data

    def test_write_json_handles_path_object(self, tmp_path: Path) -> None:
        """Verify _write_json accepts Path objects."""
        output_file = tmp_path / "subdir" / "test.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        test_data = ["item1", "item2"]
        _write_json(output_file, test_data)

        assert output_file.exists()
        assert json.loads(output_file.read_text()) == test_data


class TestToRecords:
    """Tests for _to_records helper function."""

    def test_to_records_converts_dataframe(self, sample_crime_df: pd.DataFrame) -> None:
        """Verify _to_records converts DataFrame to list of dicts."""
        result = _to_records(sample_crime_df)

        assert isinstance(result, list)
        assert len(result) == len(sample_crime_df)
        assert all(isinstance(row, dict) for row in result)

        # First row should have expected columns
        first_row = result[0]
        assert "objectid" in first_row
        assert "dispatch_date" in first_row
        assert "ucr_general" in first_row

    def test_to_records_handles_datetime(self, sample_crime_df: pd.DataFrame) -> None:
        """Verify datetime values converted to ISO format."""
        result = _to_records(sample_crime_df)

        first_row = result[0]
        dispatch_date = first_row["dispatch_date"]
        assert isinstance(dispatch_date, str)
        assert "T" in dispatch_date  # ISO format has 'T' separator

    def test_to_records_handles_none_values(self, tmp_path: Path) -> None:
        """Verify None values preserved in output."""
        df = pd.DataFrame({
            "a": [1, 2, 3],
            "b": [None, "text", None],
            "c": [1.5, None, 3.5],
        })

        result = _to_records(df)

        assert result[0]["b"] is None
        assert result[0]["c"] == 1.5
        assert result[1]["c"] is None


class TestEnsureDir:
    """Tests for _ensure_dir helper function."""

    def test_ensure_dir_creates_directory(self, tmp_path: Path) -> None:
        """Verify _ensure_dir creates parent directories."""
        test_dir = tmp_path / "level1" / "level2" / "level3"

        _ensure_dir(test_dir)

        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_ensure_dir_idempotent(self, tmp_path: Path) -> None:
        """Verify _ensure_dir safe to call on existing directory."""
        test_dir = tmp_path / "existing"
        test_dir.mkdir()

        # Should not raise exception
        _ensure_dir(test_dir)
        _ensure_dir(test_dir)

        assert test_dir.exists()

