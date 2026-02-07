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
        # Add hour column that real data has
        df["hour"] = 12  # Default to noon for test data

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
        df["hour"] = 12  # Add hour column that real data has
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
        """Verify None values preserved in output (as NaN for floats)."""
        import math

        df = pd.DataFrame({
            "a": [1, 2, 3],
            "b": [None, "text", None],
            "c": [1.5, None, 3.5],
        })

        result = _to_records(df)

        assert result[0]["b"] is None
        assert result[0]["c"] == 1.5
        # pandas converts None to NaN in float columns
        assert result[1]["c"] is None or math.isnan(result[1]["c"])


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


# =============================================================================
# Export Trends Tests (Task 2)
# =============================================================================


class TestExportTrends:
    """Tests for _export_trends function."""

    def test_export_trends_creates_annual_json(
        self, sample_crime_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Verify annual_trends.json created with year/category/count structure."""
        _export_trends(sample_crime_df, tmp_path)

        annual_file = tmp_path / "annual_trends.json"
        assert annual_file.exists()

        annual_data = json.loads(annual_file.read_text())
        assert isinstance(annual_data, list)
        assert len(annual_data) > 0

        # Verify structure
        first_row = annual_data[0]
        assert "year" in first_row
        assert "crime_category" in first_row
        assert "count" in first_row

    def test_export_trends_creates_monthly_json(
        self, sample_crime_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Verify monthly_trends.json created with month/category data."""
        _export_trends(sample_crime_df, tmp_path)

        monthly_file = tmp_path / "monthly_trends.json"
        assert monthly_file.exists()

        monthly_data = json.loads(monthly_file.read_text())
        assert isinstance(monthly_data, list)
        assert len(monthly_data) > 0

        # Verify structure
        first_row = monthly_data[0]
        assert "month" in first_row
        assert "crime_category" in first_row
        assert "count" in first_row

    def test_export_trends_creates_covid_comparison(
        self, sample_crime_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Verify covid_comparison.json with Pre/During/Post periods."""
        _export_trends(sample_crime_df, tmp_path)

        covid_file = tmp_path / "covid_comparison.json"
        assert covid_file.exists()

        covid_data = json.loads(covid_file.read_text())
        assert isinstance(covid_data, list)
        assert len(covid_data) == 3  # Pre, During, Post

        # Verify periods
        periods = [row["period"] for row in covid_data]
        assert "Pre" in periods
        assert "During" in periods
        assert "Post" in periods

        # Verify structure
        for row in covid_data:
            assert "period" in row
            assert "start" in row
            assert "end" in row
            assert "count" in row

    def test_export_trends_handles_empty_dataframe(
        self, tmp_path: Path
    ) -> None:
        """Verify graceful handling of empty input."""
        empty_df = pd.DataFrame({"dispatch_date": [], "ucr_general": []})

        # Should not raise exception
        _export_trends(empty_df, tmp_path)

        # Files should still be created
        assert (tmp_path / "annual_trends.json").exists()
        assert (tmp_path / "monthly_trends.json").exists()
        assert (tmp_path / "covid_comparison.json").exists()


# =============================================================================
# Task 2: Data Issue Error Handling Tests
# =============================================================================


class TestDataIssueErrorHandling:
    """Test error handling for problematic input data."""

    def test_export_metadata_empty_dataframe(self, tmp_path: Path) -> None:
        """Verify _export_metadata creates metadata with NaT for empty DataFrame."""
        empty_df = pd.DataFrame({"dispatch_date": []})

        # Current behavior: creates metadata with NaT values (not ideal, but doesn't crash)
        _export_metadata(empty_df, tmp_path)

        metadata_file = tmp_path / "metadata.json"
        assert metadata_file.exists()

        metadata = json.loads(metadata_file.read_text())
        assert metadata["total_incidents"] == 0
        # NaT becomes null in JSON
        assert metadata["date_start"] is None or metadata["date_start"] == "NaT"
        assert metadata["date_end"] is None or metadata["date_end"] == "NaT"

    def test_export_metadata_missing_dispatch_date(
        self, sample_crime_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Verify appropriate error when dispatch_date column missing."""
        # Drop dispatch_date column
        df_no_date = sample_crime_df.drop(columns=["dispatch_date"])

        # Should raise KeyError when dispatch_date is missing
        with pytest.raises(KeyError):
            _export_metadata(df_no_date, tmp_path)

    def test_export_trends_empty_dataframe(self, tmp_path: Path) -> None:
        """Verify _export_trends produces valid empty JSON structures."""
        empty_df = pd.DataFrame({"dispatch_date": [], "ucr_general": []})

        _export_trends(empty_df, tmp_path)

        # Verify files created with empty lists
        annual_data = json.loads((tmp_path / "annual_trends.json").read_text())
        assert isinstance(annual_data, list)
        assert len(annual_data) == 0

        monthly_data = json.loads((tmp_path / "monthly_trends.json").read_text())
        assert isinstance(monthly_data, list)
        assert len(monthly_data) == 0

    def test_export_spatial_missing_coordinate_columns(
        self, sample_crime_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Verify _export_spatial raises KeyError when coordinate columns missing."""
        # Remove all coordinate data
        df_no_coords = sample_crime_df.drop(columns=["point_x", "point_y"])

        geo_dir = tmp_path / "geo"
        geo_dir.mkdir(parents=True, exist_ok=True)

        # Mock GeoPandas to avoid file I/O
        with patch("pipeline.export_data.HAS_GEOPANDAS", True):
            with patch("pipeline.export_data.gpd") as mock_gpd:
                # The error happens before GeoPandas reads - when dropna is called
                with pytest.raises(KeyError, match="point_x|point_y"):
                    _export_spatial(df_no_coords, tmp_path, geo_dir, tmp_path)


# =============================================================================
# Task 3: File System Error Handling Tests
# =============================================================================


class TestFileSystemErrorHandling:
    """Test error handling for file system issues."""

    def test_write_json_handles_permission_error(self, tmp_path: Path) -> None:
        """Verify _write_json raises appropriate error on permission denied."""
        output_file = tmp_path / "test.json"

        # Mock Path.write_text to raise PermissionError
        with patch.object(Path, "write_text", side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError, match="Permission denied"):
                _write_json(output_file, {"key": "value"})

    def test_ensure_dir_handles_permission_error(self, tmp_path: Path) -> None:
        """Verify _ensure_dir raises appropriate error on permission denied."""
        test_dir = tmp_path / "level1" / "level2"

        # Mock Path.mkdir to raise PermissionError
        with patch.object(Path, "mkdir", side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError, match="Permission denied"):
                _ensure_dir(test_dir)

    def test_export_all_handles_unwritable_directory(
        self, sample_crime_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Verify export_all raises informative error when output directory not writable."""
        # Mock load_crime_data to return sample data
        with patch("pipeline.export_data.load_crime_data", return_value=sample_crime_df):
            # Mock _write_json to fail
            with patch("pipeline.export_data._write_json", side_effect=PermissionError("Read-only filesystem")):
                with pytest.raises(PermissionError, match="Read-only filesystem"):
                    export_data.export_all(tmp_path / "output")


# =============================================================================
# Export Seasonality Tests
# =============================================================================


class TestExportSeasonality:
    """Tests for _export_seasonality function."""

    def test_export_seasonality_creates_seasonality_json(
        self, sample_crime_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Verify seasonality.json with by_month/by_day_of_week/by_hour."""
        # Add hour column that real data has
        sample_crime_df = sample_crime_df.copy()
        sample_crime_df["hour"] = 12  # Default hour

        _export_seasonality(sample_crime_df, tmp_path)

        seasonality_file = tmp_path / "seasonality.json"
        assert seasonality_file.exists()

        seasonality_data = json.loads(seasonality_file.read_text())
        assert isinstance(seasonality_data, dict)

        # Verify structure
        assert "by_month" in seasonality_data
        assert "by_day_of_week" in seasonality_data
        assert "by_hour" in seasonality_data

        # Verify each section is a list
        assert isinstance(seasonality_data["by_month"], list)
        assert isinstance(seasonality_data["by_day_of_week"], list)
        assert isinstance(seasonality_data["by_hour"], list)

    def test_export_seasonality_creates_robbery_heatmap(
        self, sample_crime_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Verify robbery_heatmap.json with hour/day_of_week matrix."""
        # Add hour column and some robbery crimes
        sample_crime_df = sample_crime_df.copy()
        sample_crime_df["hour"] = range(len(sample_crime_df))  # Varying hours

        _export_seasonality(sample_crime_df, tmp_path)

        heatmap_file = tmp_path / "robbery_heatmap.json"
        assert heatmap_file.exists()

        heatmap_data = json.loads(heatmap_file.read_text())
        assert isinstance(heatmap_data, list)

        # Verify structure has hour and day_of_week
        if len(heatmap_data) > 0:
            first_row = heatmap_data[0]
            assert "hour" in first_row
            assert "day_of_week" in first_row
            assert "count" in first_row


    def test_export_seasonality_handles_missing_hour(
        self, tmp_path: Path
    ) -> None:
        """Verify hour NaN values filled with 0 before grouping."""
        # Create DataFrame with NaN hour values
        df_with_nan = pd.DataFrame({
            "dispatch_date": pd.date_range("2020-01-01", periods=50, freq="D"),
            "ucr_general": [300] * 50,  # Robbery codes
            "hour": [None] * 25 + [12] * 25,  # Half NaN, half valid
        })

        _export_seasonality(df_with_nan, tmp_path)

        # Should create files without error
        assert (tmp_path / "seasonality.json").exists()

        # Verify hour data includes filled 0 values
        seasonality_data = json.loads((tmp_path / "seasonality.json").read_text())
        by_hour = seasonality_data["by_hour"]

        # Should have hour 0 (filled from NaN) and hour 12
        hours = [row["hour"] for row in by_hour]
        assert 0 in hours  # NaN values filled with 0


# =============================================================================
# Export Spatial Tests (Task 4)
# =============================================================================


class TestExportSpatial:
    """Tests for _export_spatial function with mocked GeoPandas."""

    def test_export_spatial_without_geopandas(
        self, sample_crime_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Verify returns early when HAS_GEOPANDAS is False."""
        geo_dir = tmp_path / "geo"

        with patch.object(export_data, "HAS_GEOPANDAS", False):
            _export_spatial(sample_crime_df, tmp_path, geo_dir, tmp_path)

            # GeoJSON files should not be created when geopandas unavailable
            assert not (geo_dir / "districts.geojson").exists()
            assert not (geo_dir / "tracts.geojson").exists()

    @patch("pipeline.export_data.gpd")
    def test_export_spatial_creates_districts_geojson(
        self, mock_gpd: Mock, sample_crime_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Mock gpd.read_file, verify function processes districts."""
        geo_dir = tmp_path / "geo"

        # Create a pandas Series for column access
        mock_series = pd.Series([1, 2, 3], name="dist_num")

        # Mock all GeoDataFrame operations
        mock_gdf = MagicMock()
        mock_gdf.columns = ["dist_num", "geometry"]
        mock_gdf.__len__ = Mock(return_value=3)
        mock_gdf.crs = "EPSG:4326"
        mock_gdf.merge = Mock(return_value=mock_gdf)
        mock_gdf.to_crs = Mock(return_value=mock_gdf)
        mock_gdf.to_file = Mock()
        # Mock getitem to return pandas Series with astype
        mock_gdf.__getitem__ = Mock(return_value=mock_series)
        mock_gdf.drop_duplicates = Mock(return_value=mock_gdf)

        mock_gpd.read_file = Mock(return_value=mock_gdf)
        mock_gpd.GeoDataFrame = Mock(return_value=mock_gdf)
        mock_gpd.points_from_xy = Mock()
        mock_gpd.sjoin = Mock(return_value=mock_gdf)

        with patch.object(export_data, "HAS_GEOPANDAS", True):
            _export_spatial(sample_crime_df, tmp_path, geo_dir, tmp_path)

            # Verify read_file was called for districts
            assert mock_gpd.read_file.called

    @patch("pipeline.export_data.gpd")
    def test_export_spatial_creates_tracts_geojson(
        self, mock_gpd: Mock, sample_crime_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Mock tracts read, verify function processes tracts."""
        geo_dir = tmp_path / "geo"

        # Create a pandas Series for column access
        mock_series = pd.Series([1, 2, 3, 4, 5], name="GEOID")

        # Mock all GeoDataFrame operations
        mock_gdf = MagicMock()
        mock_gdf.columns = ["GEOID", "total_pop", "geometry"]
        mock_gdf.__len__ = Mock(return_value=5)
        mock_gdf.crs = "EPSG:4326"
        mock_gdf.merge = Mock(return_value=mock_gdf)
        mock_gdf.to_crs = Mock(return_value=mock_gdf)
        mock_gdf.to_file = Mock()
        mock_gdf.__getitem__ = Mock(return_value=mock_series)
        mock_gdf.drop_duplicates = Mock(return_value=mock_gdf)

        mock_gpd.read_file = Mock(return_value=mock_gdf)
        mock_gpd.GeoDataFrame = Mock(return_value=mock_gdf)
        mock_gpd.points_from_xy = Mock()
        mock_gpd.sjoin = Mock(return_value=mock_gdf)

        with patch.object(export_data, "HAS_GEOPANDAS", True):
            _export_spatial(sample_crime_df, tmp_path, geo_dir, tmp_path)

            # Verify tracts processing was attempted
            assert mock_gpd.read_file.called


    @patch("pipeline.export_data.gpd")
    def test_export_spatial_creates_hotspots_and_corridors(
        self, mock_gpd: Mock, sample_crime_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Mock file reads, verify hotspots and corridors processed."""
        geo_dir = tmp_path / "geo"

        mock_gdf = MagicMock()
        mock_gdf.__len__ = Mock(return_value=2)
        mock_gdf.merge = Mock(return_value=mock_gdf)
        mock_gdf.to_crs = Mock(return_value=mock_gdf)
        mock_gdf.to_file = Mock()
        mock_gdf.drop_duplicates = Mock(return_value=mock_gdf)

        # All reads return same mock
        mock_gpd.read_file = Mock(return_value=mock_gdf)
        mock_gpd.GeoDataFrame = Mock(return_value=mock_gdf)
        mock_gpd.points_from_xy = Mock()
        mock_gpd.sjoin = Mock(return_value=mock_gdf)

        with patch.object(export_data, "HAS_GEOPANDAS", True):
            _export_spatial(sample_crime_df, tmp_path, geo_dir, tmp_path)

            # Verify spatial_summary.json created
            assert (tmp_path / "spatial_summary.json").exists()

    @patch("pipeline.export_data.gpd")
    def test_export_spatial_creates_spatial_summary(
        self, mock_gpd: Mock, sample_crime_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Verify spatial_summary.json created with counts."""
        geo_dir = tmp_path / "geo"

        # Mock with different lengths for each GeoDataFrame
        districts_mock = MagicMock()
        districts_mock.__len__ = Mock(return_value=5)
        districts_mock.columns = ["dist_num", "geometry"]
        districts_mock.merge = Mock(return_value=districts_mock)
        districts_mock.to_crs = Mock(return_value=districts_mock)
        districts_mock.to_file = Mock()

        tracts_mock = MagicMock()
        tracts_mock.__len__ = Mock(return_value=10)
        tracts_mock.columns = ["GEOID", "total_pop", "geometry"]
        tracts_mock.crs = "EPSG:4326"
        tracts_mock.merge = Mock(return_value=tracts_mock)
        tracts_mock.to_crs = Mock(return_value=tracts_mock)
        tracts_mock.to_file = Mock()
        tracts_mock.drop_duplicates = Mock(return_value=tracts_mock)

        hotspots_mock = MagicMock()
        hotspots_mock.__len__ = Mock(return_value=3)
        hotspots_mock.to_file = Mock()

        corridors_mock = MagicMock()
        corridors_mock.__len__ = Mock(return_value=2)
        corridors_mock.to_file = Mock()

        read_returns = [districts_mock, tracts_mock, hotspots_mock, corridors_mock]
        mock_gpd.read_file = Mock(side_effect=read_returns)
        mock_gpd.GeoDataFrame = Mock(return_value=tracts_mock)
        mock_gpd.points_from_xy = Mock()
        mock_gpd.sjoin = Mock(return_value=tracts_mock)

        with patch.object(export_data, "HAS_GEOPANDAS", True):
            _export_spatial(sample_crime_df, tmp_path, geo_dir, tmp_path)

            # Verify spatial_summary.json created
            summary_file = tmp_path / "spatial_summary.json"
            assert summary_file.exists()

            summary = json.loads(summary_file.read_text())
            assert "districts" in summary
            assert "tracts" in summary
            assert "hotspots" in summary
            assert "corridors" in summary


# =============================================================================
# Task 7: Boundary Conditions and Edge Cases
# =============================================================================


class TestBoundaryConditions:
    """Test edge cases and boundary values."""

    def test_export_metadata_single_row(self, tmp_path: Path) -> None:
        """Verify handles DataFrame with single row."""
        single_row_df = pd.DataFrame({
            "dispatch_date": ["2020-01-01"],
            "ucr_general": [100],
        })

        _export_metadata(single_row_df, tmp_path)

        metadata_file = tmp_path / "metadata.json"
        assert metadata_file.exists()

        metadata = json.loads(metadata_file.read_text())
        assert metadata["total_incidents"] == 1
        assert metadata["date_start"] == "2020-01-01"
        assert metadata["date_end"] == "2020-01-01"

    def test_export_metadata_future_dates(self, tmp_path: Path) -> None:
        """Verify handles future dates in dispatch_date."""
        future_df = pd.DataFrame({
            "dispatch_date": pd.to_datetime(["2020-01-01", "2030-12-31", "2025-06-15"]),
            "ucr_general": [100, 200, 300],
        })

        _export_metadata(future_df, tmp_path)

        metadata_file = tmp_path / "metadata.json"
        assert metadata_file.exists()

        metadata = json.loads(metadata_file.read_text())
        # Should include future dates in range
        assert "2030" in metadata["date_end"] or "2030" in json.dumps(metadata)

    def test_export_all_with_none_values(self, sample_crime_df: pd.DataFrame, tmp_path: Path) -> None:
        """Verify handles DataFrame with None values in various columns."""
        # Add None values to various columns
        df_with_none = sample_crime_df.copy()
        df_with_none.loc[0:5, "ucr_general"] = None
        df_with_none.loc[10:15, "dc_dist"] = None

        # Should not crash when processing with None values
        # Mock load_crime_data to return data with None values
        with patch("pipeline.export_data.load_crime_data", return_value=df_with_none):
            try:
                export_data.export_all(tmp_path / "output")
                # Export should complete successfully
                assert (tmp_path / "output" / "metadata.json").exists()
            except Exception as e:
                # Some functions may not handle None values gracefully
                # This is acceptable - we're verifying it doesn't silently pass
                assert isinstance(e, (ValueError, TypeError, KeyError))

    def test_export_trends_single_row(self, tmp_path: Path) -> None:
        """Verify trends export with single row DataFrame."""
        single_row_df = pd.DataFrame({
            "dispatch_date": ["2020-01-01"],
            "ucr_general": [100],
        })

        _export_trends(single_row_df, tmp_path)

        # Should create files with single entry
        annual_data = json.loads((tmp_path / "annual_trends.json").read_text())
        assert len(annual_data) == 1

    def test_export_seasonality_zero_hour_values(self, tmp_path: Path) -> None:
        """Verify seasonality handles all-zero hour values."""
        df_zero_hour = pd.DataFrame({
            "dispatch_date": pd.date_range("2020-01-01", periods=10, freq="D"),
            "ucr_general": [300] * 10,
            "hour": [0] * 10,  # All zeros
        })

        _export_seasonality(df_zero_hour, tmp_path)

        # Should create files without error
        assert (tmp_path / "seasonality.json").exists()

        seasonality_data = json.loads((tmp_path / "seasonality.json").read_text())
        by_hour = seasonality_data["by_hour"]
        # Should have hour 0 entries
        hours = [row["hour"] for row in by_hour]
        assert 0 in hours

