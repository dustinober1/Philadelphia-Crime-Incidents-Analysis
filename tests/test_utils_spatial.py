"""Unit tests for utils/spatial.py spatial utilities.

This module tests coordinate cleaning, spatial joins, severity scoring,
and coordinate statistics with mocked GeoPandas operations.

Testing strategy:
- Use synthetic coordinate data for fast, deterministic tests
- Mock GeoPandas operations to avoid slow spatial joins
- Test coordinate filtering bounds checking
- Test severity score UCR band mapping
- Test spatial join logic (column renaming, cleanup)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Point

from analysis.config import (
    PHILLY_LAT_MAX,
    PHILLY_LAT_MIN,
    PHILLY_LON_MAX,
    PHILLY_LON_MIN,
    SEVERITY_WEIGHTS,
)
from analysis.utils.spatial import (
    clean_coordinates,
    calculate_severity_score,
    df_to_geodataframe,
    get_coordinate_stats,
    get_repo_root,
    load_boundaries,
    spatial_join_districts,
    spatial_join_tracts,
)

if TYPE_CHECKING:
    pass


class TestCleanCoordinates:
    """Tests for clean_coordinates function."""

    def test_filters_valid_philadelphia_coordinates(self):
        """Filters to valid Philadelphia coordinates only."""
        df = pd.DataFrame({
            "point_x": [-75.16, -100.0, -75.20],  # Middle invalid
            "point_y": [39.95, 40.0, 40.0],       # Middle invalid (lon out of bounds)
            "id": [1, 2, 3]
        })

        result = clean_coordinates(df)

        assert len(result) == 2
        assert result["id"].tolist() == [1, 3]

    def test_filters_out_nan_coordinates(self):
        """Filters out rows with NaN in point_x or point_y."""
        df = pd.DataFrame({
            "point_x": [-75.16, None, -75.20],
            "point_y": [39.95, 40.0, None],
            "id": [1, 2, 3]
        })

        result = clean_coordinates(df)

        # Only first row has both coordinates non-NaN
        assert len(result) == 1
        assert result["id"].iloc[0] == 1

    @pytest.mark.parametrize(
        "lon,should_pass",
        [
            (PHILLY_LON_MIN, True),   # At min boundary
            (PHILLY_LON_MAX, True),   # At max boundary
            (PHILLY_LON_MIN - 0.01, False),  # Just below min
            (PHILLY_LON_MAX + 0.01, False),  # Just above max
            (-100.0, False),          # Far out of bounds
        ]
    )
    def test_filters_out_out_of_bounds_lon(self, lon, should_pass):
        """Filters longitude values outside Philadelphia bounds."""
        df = pd.DataFrame({
            "point_x": [lon],
            "point_y": [40.0],  # Valid latitude
        })

        result = clean_coordinates(df)

        assert len(result) == (1 if should_pass else 0)

    @pytest.mark.parametrize(
        "lat,should_pass",
        [
            (PHILLY_LAT_MIN, True),   # At min boundary
            (PHILLY_LAT_MAX, True),   # At max boundary
            (PHILLY_LAT_MIN - 0.01, False),  # Just below min
            (PHILLY_LAT_MAX + 0.01, False),  # Just above max
            (50.0, False),            # Far out of bounds
        ]
    )
    def test_filters_out_out_of_bounds_lat(self, lat, should_pass):
        """Filters latitude values outside Philadelphia bounds."""
        df = pd.DataFrame({
            "point_x": [-75.16],  # Valid longitude
            "point_y": [lat],
        })

        result = clean_coordinates(df)

        assert len(result) == (1 if should_pass else 0)

    def test_custom_x_col_parameter(self):
        """Accepts custom column name for longitude."""
        df = pd.DataFrame({
            "custom_lon": [-75.16],
            "custom_lat": [39.95]
        })

        result = clean_coordinates(df, x_col="custom_lon", y_col="custom_lat")

        assert len(result) == 1

    def test_custom_y_col_parameter(self):
        """Accepts custom column name for latitude."""
        df = pd.DataFrame({
            "custom_lon": [-75.16],
            "custom_lat": [39.95]
        })

        result = clean_coordinates(df, x_col="custom_lon", y_col="custom_lat")

        assert len(result) == 1

    def test_missing_columns_raises_value_error(self):
        """Raises ValueError when coordinate columns missing."""
        df = pd.DataFrame({"other_column": [1, 2, 3]})

        with pytest.raises(ValueError, match="Columns .* not found in DataFrame"):
            clean_coordinates(df)

    def test_returns_copy_not_view(self):
        """Returns a copy, not a view."""
        df = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "id": [1]
        })

        result = clean_coordinates(df)

        # Modify result
        result.loc[result.index[0], "id"] = 999

        # Original DataFrame unchanged
        assert df["id"].iloc[0] == 1

    def test_preserves_original_columns(self):
        """Preserves all original columns in output."""
        df = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "col1": ["a"],
            "col2": [100],
        })

        result = clean_coordinates(df)

        assert list(result.columns) == list(df.columns)

    def test_handles_empty_dataframe(self):
        """Handles empty DataFrame."""
        df = pd.DataFrame({"point_x": [], "point_y": []})

        result = clean_coordinates(df)

        assert len(result) == 0
        assert list(result.columns) == ["point_x", "point_y"]

    def test_all_invalid_returns_empty(self):
        """All rows with invalid coordinates returns empty DataFrame."""
        df = pd.DataFrame({
            "point_x": [-100.0, -200.0],  # Outside Philly bounds
            "point_y": [50.0, 60.0],       # Outside Philly bounds
        })

        result = clean_coordinates(df)

        assert len(result) == 0


class TestCalculateSeverityScore:
    """Tests for calculate_severity_score function."""

    def test_ucr_100_band_returns_10_severity(self):
        """UCR 100-199 maps to severity 10.0."""
        df = pd.DataFrame({"ucr_general": [100]})

        scores = calculate_severity_score(df)

        assert scores.iloc[0] == 10.0

    def test_ucr_200_band_returns_8_severity(self):
        """UCR 200-299 maps to severity 8.0."""
        df = pd.DataFrame({"ucr_general": [250]})

        scores = calculate_severity_score(df)

        assert scores.iloc[0] == 8.0

    def test_ucr_300_band_returns_6_severity(self):
        """UCR 300-399 maps to severity 6.0."""
        df = pd.DataFrame({"ucr_general": [350]})

        scores = calculate_severity_score(df)

        assert scores.iloc[0] == 6.0

    def test_ucr_400_band_returns_5_severity(self):
        """UCR 400-499 maps to severity 5.0."""
        df = pd.DataFrame({"ucr_general": [450]})

        scores = calculate_severity_score(df)

        assert scores.iloc[0] == 5.0

    def test_ucr_500_band_returns_3_severity(self):
        """UCR 500-599 maps to severity 3.0."""
        df = pd.DataFrame({"ucr_general": [550]})

        scores = calculate_severity_score(df)

        assert scores.iloc[0] == 3.0

    def test_ucr_600_band_returns_1_severity(self):
        """UCR 600-699 maps to severity 1.0."""
        df = pd.DataFrame({"ucr_general": [650]})

        scores = calculate_severity_score(df)

        assert scores.iloc[0] == 1.0

    def test_ucr_700_band_returns_2_severity(self):
        """UCR 700-799 maps to severity 2.0."""
        df = pd.DataFrame({"ucr_general": [750]})

        scores = calculate_severity_score(df)

        assert scores.iloc[0] == 2.0

    def test_ucr_800_band_returns_4_severity(self):
        """UCR 800-899 maps to severity 4.0."""
        df = pd.DataFrame({"ucr_general": [850]})

        scores = calculate_severity_score(df)

        assert scores.iloc[0] == 4.0

    def test_unknown_ucr_defaults_to_0_5(self):
        """Unknown UCR codes default to 0.5 severity."""
        df = pd.DataFrame({"ucr_general": [9999]})

        scores = calculate_severity_score(df)

        assert scores.iloc[0] == 0.5

    def test_custom_weights_override_defaults(self):
        """Custom weights override default severity weights."""
        custom_weights = {
            100: 5.0,  # Override
            200: 3.0,
            300: 2.0,
        }

        df = pd.DataFrame({"ucr_general": [100, 600]})
        scores = calculate_severity_score(df, weights=custom_weights)

        # Custom weight used for 100
        assert scores.iloc[0] == 5.0
        # Unknown code defaults to 0.5
        assert scores.iloc[1] == 0.5

    def test_nan_ucr_code_defaults_to_0_5(self):
        """NaN UCR code defaults to 0.5 severity."""
        df = pd.DataFrame({
            "ucr_general": [None, 600]
        })

        scores = calculate_severity_score(df)

        # NaN UCR codes are filled with 0.5 default
        assert scores.iloc[0] == 0.5
        assert scores.iloc[1] == 1.0

    def test_custom_ucr_col_parameter(self):
        """Accepts custom UCR column name."""
        df = pd.DataFrame({
            "custom_ucr": [100, 600]
        })

        scores = calculate_severity_score(df, ucr_col="custom_ucr")

        assert scores.iloc[0] == 10.0
        assert scores.iloc[1] == 1.0

    def test_missing_ucr_col_raises_value_error(self):
        """Raises ValueError when UCR column missing."""
        df = pd.DataFrame({"other_column": [1, 2, 3]})

        with pytest.raises(ValueError, match="Column .* not found in DataFrame"):
            calculate_severity_score(df)

    def test_returns_series(self):
        """Returns pd.Series with same length as input DataFrame."""
        df = pd.DataFrame({"ucr_general": [100, 200, 300]})

        scores = calculate_severity_score(df)

        assert isinstance(scores, pd.Series)
        assert len(scores) == len(df)


class TestGetCoordinateStats:
    """Tests for get_coordinate_stats function."""

    def test_returns_dict_with_expected_keys(self):
        """Returns dictionary with expected keys."""
        df = pd.DataFrame({
            "point_x": [-75.16, -75.20],
            "point_y": [39.95, 40.0]
        })

        stats = get_coordinate_stats(df)

        expected_keys = [
            "total_records",
            "has_coordinates",
            "in_philadelphia_bounds",
            "coverage_rate",
            "in_bounds_rate",
            "lon_min",
            "lon_max",
            "lat_min",
            "lat_max",
        ]
        assert set(stats.keys()) == set(expected_keys)

    def test_total_records_matches_input_length(self):
        """total_records matches len(df)."""
        df = pd.DataFrame({
            "point_x": [-75.16, -75.20, -75.10],
            "point_y": [39.95, 40.0, 39.90]
        })

        stats = get_coordinate_stats(df)

        assert stats["total_records"] == len(df)

    def test_has_coordinates_counts_valid_coords(self):
        """has_coordinates counts rows with non-NaN coordinates."""
        df = pd.DataFrame({
            "point_x": [-75.16, None, -75.20],
            "point_y": [39.95, 40.0, None]
        })

        stats = get_coordinate_stats(df)

        # Only first row has both coordinates non-NaN
        assert stats["has_coordinates"] == 1

    def test_in_philadelphia_bounds_counts_valid_coords(self):
        """Counts coordinates in Philadelphia bounds."""
        df = pd.DataFrame({
            "point_x": [-75.16, -100.0, -75.20],  # Middle out of bounds
            "point_y": [39.95, 40.0, 50.0]
        })

        stats = get_coordinate_stats(df)

        # Only first row in Philly bounds
        assert stats["in_philadelphia_bounds"] == 1

    def test_coverage_rate_calculation(self):
        """coverage_rate = has_coordinates / total_records."""
        df = pd.DataFrame({
            "point_x": [-75.16, None, -75.20],
            "point_y": [39.95, 40.0, None]
        })

        stats = get_coordinate_stats(df)

        expected_rate = 1 / 3  # 1 out of 3 rows has coordinates
        assert stats["coverage_rate"] == pytest.approx(expected_rate)

    def test_in_bounds_rate_calculation(self):
        """in_bounds_rate = in_philadelphia_bounds / total_records."""
        df = pd.DataFrame({
            "point_x": [-75.16, -100.0, -75.20],  # Middle out of bounds
            "point_y": [39.95, 40.0, 50.0]
        })

        stats = get_coordinate_stats(df)

        expected_rate = 1 / 3  # 1 out of 3 rows in bounds
        assert stats["in_bounds_rate"] == pytest.approx(expected_rate)

    def test_lon_min_max_calculations(self):
        """Min/max longitude computed correctly."""
        df = pd.DataFrame({
            "point_x": [-75.16, -75.20, -75.10],
            "point_y": [39.95, 40.0, 39.90]
        })

        stats = get_coordinate_stats(df)

        assert stats["lon_min"] == pytest.approx(-75.20)
        assert stats["lon_max"] == pytest.approx(-75.10)

    def test_lat_min_max_calculations(self):
        """Min/max latitude computed correctly."""
        df = pd.DataFrame({
            "point_x": [-75.16, -75.20, -75.10],
            "point_y": [39.95, 40.0, 39.90]
        })

        stats = get_coordinate_stats(df)

        assert stats["lat_min"] == pytest.approx(39.90)
        assert stats["lat_max"] == pytest.approx(40.0)

    def test_empty_dataframe_returns_zero_stats(self):
        """Empty DataFrame has total_records=0, rates=0."""
        df = pd.DataFrame({"point_x": [], "point_y": []})

        stats = get_coordinate_stats(df)

        assert stats["total_records"] == 0
        assert stats["has_coordinates"] == 0
        assert stats["in_philadelphia_bounds"] == 0
        assert stats["coverage_rate"] == 0
        assert stats["in_bounds_rate"] == 0

    def test_custom_x_col_y_col_parameters(self):
        """Custom column names work."""
        df = pd.DataFrame({
            "custom_lon": [-75.16],
            "custom_lat": [39.95]
        })

        stats = get_coordinate_stats(df, x_col="custom_lon", y_col="custom_lat")

        assert stats["total_records"] == 1
        assert stats["has_coordinates"] == 1
        assert stats["in_philadelphia_bounds"] == 1

    def test_all_nan_coordinates_returns_zero_coverage(self):
        """All-NaN coordinates give coverage_rate=0."""
        df = pd.DataFrame({
            "point_x": [None, None],
            "point_y": [None, None]
        })

        stats = get_coordinate_stats(df)

        assert stats["has_coordinates"] == 0
        assert stats["coverage_rate"] == 0


class TestDfToGeodataframe:
    """Tests for df_to_geodataframe function."""

    def test_returns_geodataframe(self):
        """Returns gpd.GeoDataFrame."""
        df = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        result = df_to_geodataframe(df)

        assert isinstance(result, gpd.GeoDataFrame)

    def test_geometry_column_created(self):
        """Creates 'geometry' column with Point objects."""
        df = pd.DataFrame({
            "point_x": [-75.16, -75.20],
            "point_y": [39.95, 40.0]
        })

        result = df_to_geodataframe(df)

        assert "geometry" in result.columns
        assert all(isinstance(geom, Point) for geom in result["geometry"] if geom is not None)

    def test_default_crs_is_epsg_4326(self):
        """Default CRS is EPSG:4326 (WGS84)."""
        df = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        result = df_to_geodataframe(df)

        assert result.crs == "EPSG:4326"

    def test_custom_crs_parameter(self):
        """Custom CRS parameter works."""
        df = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        result = df_to_geodataframe(df, crs="EPSG:3857")

        assert result.crs == "EPSG:3857"

    def test_nan_coordinates_create_none_geometry(self):
        """NaN coordinates result in None geometry."""
        df = pd.DataFrame({
            "point_x": [-75.16, None, -75.20],
            "point_y": [39.95, 40.0, None]
        })

        result = df_to_geodataframe(df)

        # First row has valid geometry
        assert result["geometry"].iloc[0] is not None
        # Second and third rows have None geometry
        assert result["geometry"].iloc[1] is None
        assert result["geometry"].iloc[2] is None

    def test_custom_x_col_y_col_parameters(self):
        """Custom column names work."""
        df = pd.DataFrame({
            "custom_lon": [-75.16],
            "custom_lat": [39.95]
        })

        result = df_to_geodataframe(df, x_col="custom_lon", y_col="custom_lat")

        assert isinstance(result, gpd.GeoDataFrame)
        assert "geometry" in result.columns

    def test_preserves_original_columns(self):
        """Preserves all original columns in output."""
        df = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "col1": ["a"],
            "col2": [100],
        })

        result = df_to_geodataframe(df)

        assert "col1" in result.columns
        assert "col2" in result.columns
        assert result["col1"].iloc[0] == "a"
        assert result["col2"].iloc[0] == 100


class TestLoadBoundaries:
    """Tests for load_boundaries function."""

    @patch("analysis.utils.spatial.gpd.read_file")
    @patch("pathlib.Path.exists")
    def test_load_police_districts_returns_geodataframe(self, mock_exists, mock_read):
        """Returns gpd.GeoDataFrame for police districts."""
        # Mock file exists
        mock_exists.return_value = True

        # Mock GeoDataFrame
        mock_gdf = MagicMock(spec=gpd.GeoDataFrame)
        mock_read.return_value = mock_gdf

        result = load_boundaries("police_districts")

        assert result == mock_gdf
        mock_read.assert_called_once()

    @patch("analysis.utils.spatial.gpd.read_file")
    @patch("pathlib.Path.exists")
    def test_load_census_tracts_returns_geodataframe(self, mock_exists, mock_read):
        """Returns gpd.GeoDataFrame for census tracts."""
        # Mock file exists
        mock_exists.return_value = True

        # Mock GeoDataFrame
        mock_gdf = MagicMock(spec=gpd.GeoDataFrame)
        mock_read.return_value = mock_gdf

        result = load_boundaries("census_tracts")

        assert result == mock_gdf
        mock_read.assert_called_once()

    @patch("analysis.utils.spatial.gpd.read_file")
    @patch("pathlib.Path.exists")
    def test_load_census_tracts_pop_alias(self, mock_exists, mock_read):
        """'census_tracts_pop' alias works."""
        # Mock file exists
        mock_exists.return_value = True

        # Mock GeoDataFrame
        mock_gdf = MagicMock(spec=gpd.GeoDataFrame)
        mock_read.return_value = mock_gdf

        result = load_boundaries("census_tracts_pop")

        assert result == mock_gdf

    def test_unknown_boundary_raises_value_error(self):
        """Raises ValueError for unknown boundary name."""
        with pytest.raises(ValueError, match="Unknown boundary name"):
            load_boundaries("unknown_boundary")

    @patch("pathlib.Path.exists")
    def test_file_not_found_raises_file_not_found_error(self, mock_exists):
        """Raises FileNotFoundError when boundary file missing."""
        # Mock file not exists
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError, match="Boundary file not found"):
            load_boundaries("police_districts")

    @patch("analysis.utils.spatial.gpd.read_file")
    @patch("pathlib.Path.exists")
    def test_mock_file_path_uses_repo_root(self, mock_exists, mock_read):
        """File path constructed from repo root."""
        # Mock file exists
        mock_exists.return_value = True

        # Mock GeoDataFrame
        mock_gdf = MagicMock(spec=gpd.GeoDataFrame)
        mock_read.return_value = mock_gdf

        load_boundaries("police_districts")

        # Get the call arguments
        call_args = mock_read.call_args
        file_path = call_args[0][0]

        # Verify path contains expected components
        assert "police_districts.geojson" in str(file_path)


class TestSpatialJoinDistricts:
    """Tests for spatial_join_districts function."""

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_returns_dataframe_with_joined_dist_num(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Returns DataFrame with 'joined_dist_num' column."""
        # Setup mocks
        mock_clean.return_value = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "id": [1]
        })

        mock_gdf = MagicMock()
        mock_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = mock_gdf

        mock_joined = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "id": [1],
            "dist_num": [1],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "id": [1]
        })

        result = spatial_join_districts(crime_df, district_gdf=None)

        assert "joined_dist_num" in result.columns
        assert result["joined_dist_num"].iloc[0] == 1

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_calls_clean_coordinates_internally(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Calls coordinate cleaning before join."""
        mock_clean.return_value = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        mock_gdf = MagicMock()
        mock_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = mock_gdf

        mock_joined = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "dist_num": [1],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({"point_x": [-75.16], "point_y": [39.95]})

        spatial_join_districts(crime_df, district_gdf=None)

        mock_clean.assert_called_once()

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_calls_df_to_geodataframe_internally(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Calls conversion to GeoDataFrame."""
        mock_clean.return_value = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        mock_gdf = MagicMock()
        mock_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = mock_gdf

        mock_joined = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "dist_num": [1],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({"point_x": [-75.16], "point_y": [39.95]})

        spatial_join_districts(crime_df, district_gdf=None)

        mock_to_gdf.assert_called_once()

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_drops_index_right_column(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Drops 'index_right' cleanup column."""
        mock_clean.return_value = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        mock_gdf = MagicMock()
        mock_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = mock_gdf

        mock_joined = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "dist_num": [1],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({"point_x": [-75.16], "point_y": [39.95]})

        result = spatial_join_districts(crime_df, district_gdf=None)

        assert "index_right" not in result.columns

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_drops_geometry_column(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Drops 'geometry' column from output."""
        mock_clean.return_value = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        mock_gdf = MagicMock()
        mock_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = mock_gdf

        mock_joined = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "dist_num": [1],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({"point_x": [-75.16], "point_y": [39.95]})

        result = spatial_join_districts(crime_df, district_gdf=None)

        assert "geometry" not in result.columns

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_custom_x_col_y_col_parameters(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Custom column names work."""
        mock_clean.return_value = pd.DataFrame({
            "custom_lon": [-75.16],
            "custom_lat": [39.95]
        })

        mock_gdf = MagicMock()
        mock_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = mock_gdf

        mock_joined = pd.DataFrame({
            "custom_lon": [-75.16],
            "custom_lat": [39.95],
            "dist_num": [1],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({
            "custom_lon": [-75.16],
            "custom_lat": [39.95]
        })

        result = spatial_join_districts(
            crime_df,
            district_gdf=None,
            x_col="custom_lon",
            y_col="custom_lat"
        )

        # Verify clean_coordinates was called with custom columns (positional args)
        mock_clean.assert_called_once()
        call_args = mock_clean.call_args[0]
        assert call_args[1] == "custom_lon"  # x_col is second positional arg
        assert call_args[2] == "custom_lat"  # y_col is third positional arg

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_provided_district_gdf_used(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Custom district_gdf parameter used when provided."""
        mock_clean.return_value = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        crime_gdf = MagicMock()
        crime_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = crime_gdf

        # Create custom district gdf
        custom_district_gdf = MagicMock()
        custom_district_gdf.crs = "EPSG:4326"
        custom_district_gdf.__getitem__ = lambda self, key: custom_district_gdf
        custom_district_gdf.columns = ["dist_num", "geometry"]

        mock_joined = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "dist_num": [5],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({"point_x": [-75.16], "point_y": [39.95]})

        result = spatial_join_districts(crime_df, district_gdf=custom_district_gdf)

        assert "joined_dist_num" in result.columns

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_handles_crs_mismatch(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Handles CRS conversion when district_gdf.crs != crime_gdf.crs."""
        mock_clean.return_value = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        crime_gdf = MagicMock()
        crime_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = crime_gdf

        # Create district gdf with different CRS
        district_gdf = MagicMock()
        district_gdf.crs = "EPSG:3857"
        district_gdf.__getitem__ = lambda self, key: district_gdf
        district_gdf.columns = ["dist_num", "geometry"]

        # Mock to_crs to return self
        district_gdf.to_crs = lambda crs: district_gdf

        mock_joined = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "dist_num": [1],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({"point_x": [-75.16], "point_y": [39.95]})

        result = spatial_join_districts(crime_df, district_gdf=district_gdf)

        assert "joined_dist_num" in result.columns


class TestSpatialJoinTracts:
    """Tests for spatial_join_tracts function."""

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_returns_dataframe_with_tract_columns(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Returns DataFrame with GEOID and/or total_pop columns."""
        mock_clean.return_value = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        mock_gdf = MagicMock()
        mock_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = mock_gdf

        mock_joined = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "GEOID": ["42101010100"],
            "total_pop": [1000],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({"point_x": [-75.16], "point_y": [39.95]})

        result = spatial_join_tracts(crime_df, tract_gdf=None)

        assert "GEOID" in result.columns
        assert "total_pop" in result.columns

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_calls_clean_coordinates_internally(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Calls coordinate cleaning before join."""
        mock_clean.return_value = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        mock_gdf = MagicMock()
        mock_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = mock_gdf

        mock_joined = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "GEOID": ["42101010100"],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({"point_x": [-75.16], "point_y": [39.95]})

        spatial_join_tracts(crime_df, tract_gdf=None)

        mock_clean.assert_called_once()

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_calls_df_to_geodataframe_internally(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Calls conversion to GeoDataFrame."""
        mock_clean.return_value = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        mock_gdf = MagicMock()
        mock_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = mock_gdf

        mock_joined = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "GEOID": ["42101010100"],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({"point_x": [-75.16], "point_y": [39.95]})

        spatial_join_tracts(crime_df, tract_gdf=None)

        mock_to_gdf.assert_called_once()

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_drops_index_right_column(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Drops 'index_right' cleanup column."""
        mock_clean.return_value = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        mock_gdf = MagicMock()
        mock_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = mock_gdf

        mock_joined = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "GEOID": ["42101010100"],
            "total_pop": [1000],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({"point_x": [-75.16], "point_y": [39.95]})

        result = spatial_join_tracts(crime_df, tract_gdf=None)

        assert "index_right" not in result.columns

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_drops_geometry_column(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Drops 'geometry' column from output."""
        mock_clean.return_value = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        mock_gdf = MagicMock()
        mock_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = mock_gdf

        mock_joined = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "GEOID": ["42101010100"],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({"point_x": [-75.16], "point_y": [39.95]})

        result = spatial_join_tracts(crime_df, tract_gdf=None)

        assert "geometry" not in result.columns

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_custom_x_col_y_col_parameters(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Custom column names work."""
        mock_clean.return_value = pd.DataFrame({
            "custom_lon": [-75.16],
            "custom_lat": [39.95]
        })

        mock_gdf = MagicMock()
        mock_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = mock_gdf

        mock_joined = pd.DataFrame({
            "custom_lon": [-75.16],
            "custom_lat": [39.95],
            "GEOID": ["42101010100"],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({
            "custom_lon": [-75.16],
            "custom_lat": [39.95]
        })

        result = spatial_join_tracts(
            crime_df,
            tract_gdf=None,
            x_col="custom_lon",
            y_col="custom_lat"
        )

        # Verify clean_coordinates was called with custom columns (positional args)
        mock_clean.assert_called_once()
        call_args = mock_clean.call_args[0]
        assert call_args[1] == "custom_lon"  # x_col is second positional arg
        assert call_args[2] == "custom_lat"  # y_col is third positional arg

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_provided_tract_gdf_used(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Custom tract_gdf parameter used when provided."""
        mock_clean.return_value = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        crime_gdf = MagicMock()
        crime_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = crime_gdf

        # Create custom tract gdf
        custom_tract_gdf = MagicMock()
        custom_tract_gdf.crs = "EPSG:4326"
        custom_tract_gdf.__getitem__ = lambda self, key: custom_tract_gdf
        custom_tract_gdf.columns = ["GEOID", "total_pop", "geometry"]

        mock_joined = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "GEOID": ["42101019999"],
            "total_pop": [500],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({"point_x": [-75.16], "point_y": [39.95]})

        result = spatial_join_tracts(crime_df, tract_gdf=custom_tract_gdf)

        assert "GEOID" in result.columns

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_handles_crs_mismatch(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Handles CRS conversion when tract_gdf.crs != crime_gdf.crs."""
        mock_clean.return_value = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        crime_gdf = MagicMock()
        crime_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = crime_gdf

        # Create tract gdf with different CRS
        tract_gdf = MagicMock()
        tract_gdf.crs = "EPSG:3857"
        tract_gdf.__getitem__ = lambda self, key: tract_gdf
        tract_gdf.columns = ["GEOID", "total_pop", "geometry"]

        # Mock to_crs to return self
        tract_gdf.to_crs = lambda crs: tract_gdf

        mock_joined = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "GEOID": ["42101010100"],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({"point_x": [-75.16], "point_y": [39.95]})

        result = spatial_join_tracts(crime_df, tract_gdf=tract_gdf)

        assert "GEOID" in result.columns

    @patch("analysis.utils.spatial.gpd.sjoin")
    @patch("analysis.utils.spatial.df_to_geodataframe")
    @patch("analysis.utils.spatial.clean_coordinates")
    def test_handles_missing_tract_columns(self, mock_clean, mock_to_gdf, mock_sjoin):
        """Only available columns selected from tract_gdf."""
        mock_clean.return_value = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95]
        })

        crime_gdf = MagicMock()
        crime_gdf.crs = "EPSG:4326"
        mock_to_gdf.return_value = crime_gdf

        # Create tract gdf without total_pop column
        tract_gdf = MagicMock()
        tract_gdf.crs = "EPSG:4326"
        tract_gdf.__getitem__ = lambda self, key: tract_gdf
        tract_gdf.columns = ["GEOID", "geometry"]

        mock_joined = pd.DataFrame({
            "point_x": [-75.16],
            "point_y": [39.95],
            "GEOID": ["42101010100"],
            "index_right": [0],
            "geometry": [Point(-75.16, 39.95)]
        })
        mock_sjoin.return_value = mock_joined

        crime_df = pd.DataFrame({"point_x": [-75.16], "point_y": [39.95]})

        result = spatial_join_tracts(crime_df, tract_gdf=tract_gdf)

        # Should have GEOID but not total_pop
        assert "GEOID" in result.columns
        assert "total_pop" not in result.columns
