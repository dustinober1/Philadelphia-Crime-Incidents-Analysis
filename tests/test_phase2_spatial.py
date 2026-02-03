"""Tests for Phase 2 spatial utilities and configuration."""

import pandas as pd
import pytest

from analysis.phase2_config_loader import (
    ClusteringConfig,
    CoordinateBounds,
    Phase2Config,
    load_phase2_config,
)
from analysis.spatial_utils import (
    calculate_severity_score,
    clean_coordinates,
    get_coordinate_stats,
    load_boundaries,
)


class TestPhase2Config:
    """Tests for Phase 2 configuration loading."""

    def test_load_config_success(self):
        """Config loads without error."""
        config = load_phase2_config()
        assert config.version == "1.0"
        assert isinstance(config.clustering, ClusteringConfig)

    def test_clustering_defaults(self):
        """Clustering config has expected defaults."""
        config = load_phase2_config()
        assert config.clustering.eps_degrees == 0.002
        assert config.clustering.min_samples == 50
        assert config.clustering.algorithm == "DBSCAN"

    def test_severity_weights_loaded(self):
        """Severity weights are loaded correctly."""
        config = load_phase2_config()
        assert 100 in config.severity_weights
        assert config.severity_weights[100] == 10.0  # Homicide
        assert config.severity_weights[600] == 1.0  # Theft

    def test_census_config(self):
        """Census config has expected values."""
        config = load_phase2_config()
        assert config.census.population_column == "total_pop"
        assert config.census.rate_per == 100000
        assert config.census.min_population == 100


class TestCleanCoordinates:
    """Tests for coordinate cleaning function."""

    def test_filters_out_of_bounds_lat(self):
        """Filters coordinates outside Philadelphia latitude bounds."""
        df = pd.DataFrame(
            {
                "point_x": [-75.1, -75.1, -75.1],
                "point_y": [39.9, 41.0, 38.0],  # in, too high, too low
            }
        )
        result = clean_coordinates(df)
        assert len(result) == 1
        assert result.iloc[0]["point_y"] == 39.9

    def test_filters_out_of_bounds_lon(self):
        """Filters coordinates outside Philadelphia longitude bounds."""
        df = pd.DataFrame(
            {
                "point_x": [-75.1, -74.5, -76.0],  # in, too east, too west
                "point_y": [39.95, 39.95, 39.95],
            }
        )
        result = clean_coordinates(df)
        assert len(result) == 1
        assert result.iloc[0]["point_x"] == -75.1

    def test_filters_null_coordinates(self):
        """Filters records with null coordinates."""
        df = pd.DataFrame(
            {
                "point_x": [-75.1, None, -75.1],
                "point_y": [39.95, 39.95, None],
            }
        )
        result = clean_coordinates(df)
        assert len(result) == 1

    def test_preserves_other_columns(self):
        """Preserves non-coordinate columns."""
        df = pd.DataFrame(
            {
                "point_x": [-75.1],
                "point_y": [39.95],
                "incident_id": ["ABC123"],
                "ucr_general": [100],
            }
        )
        result = clean_coordinates(df)
        assert "incident_id" in result.columns
        assert result.iloc[0]["incident_id"] == "ABC123"

    def test_returns_copy(self):
        """Returns a copy, not a view."""
        df = pd.DataFrame(
            {
                "point_x": [-75.1],
                "point_y": [39.95],
            }
        )
        result = clean_coordinates(df)
        result.loc[result.index[0], "point_x"] = -999
        assert df.iloc[0]["point_x"] == -75.1  # Original unchanged

    def test_custom_column_names(self):
        """Works with custom coordinate column names."""
        df = pd.DataFrame(
            {
                "lon": [-75.1],
                "lat": [39.95],
            }
        )
        result = clean_coordinates(df, x_col="lon", y_col="lat")
        assert len(result) == 1


class TestCalculateSeverityScore:
    """Tests for severity score calculation."""

    def test_homicide_highest_severity(self):
        """Homicide (100) has highest severity."""
        df = pd.DataFrame({"ucr_general": [100]})
        scores = calculate_severity_score(df)
        assert scores.iloc[0] == 10.0

    def test_theft_low_severity(self):
        """Theft (600) has low severity."""
        df = pd.DataFrame({"ucr_general": [600]})
        scores = calculate_severity_score(df)
        assert scores.iloc[0] == 1.0

    def test_unknown_code_defaults(self):
        """Unknown codes default to 0.5."""
        df = pd.DataFrame({"ucr_general": [999]})
        scores = calculate_severity_score(df)
        assert scores.iloc[0] == 0.5

    def test_multiple_records(self):
        """Handles multiple records correctly."""
        df = pd.DataFrame({"ucr_general": [100, 200, 300, 600, 900]})
        scores = calculate_severity_score(df)
        assert list(scores) == [10.0, 8.0, 6.0, 1.0, 0.5]

    def test_maps_to_hundred_band(self):
        """Maps specific codes to hundred-band correctly."""
        # UCR codes like 306 should map to 300 band
        df = pd.DataFrame({"ucr_general": [306, 615, 418]})
        scores = calculate_severity_score(df)
        assert scores.iloc[0] == 6.0  # 306 -> 300 -> Robbery
        assert scores.iloc[1] == 1.0  # 615 -> 600 -> Theft
        assert scores.iloc[2] == 5.0  # 418 -> 400 -> Aggravated Assault


class TestLoadBoundaries:
    """Tests for boundary loading function."""

    def test_load_police_districts(self):
        """Loads police districts successfully."""
        gdf = load_boundaries("police_districts")
        assert len(gdf) == 21
        assert "geometry" in gdf.columns
        assert "dist_num" in gdf.columns

    def test_load_census_tracts(self):
        """Loads census tracts successfully."""
        gdf = load_boundaries("census_tracts")
        assert len(gdf) >= 350
        assert "geometry" in gdf.columns
        assert "total_pop" in gdf.columns

    def test_invalid_name_raises(self):
        """Raises ValueError for unknown boundary name."""
        with pytest.raises(ValueError, match="Unknown boundary name"):
            load_boundaries("invalid_name")


class TestGetCoordinateStats:
    """Tests for coordinate statistics function."""

    def test_basic_stats(self):
        """Returns expected statistics structure."""
        df = pd.DataFrame(
            {
                "point_x": [-75.1, -75.1, None],
                "point_y": [39.95, 39.95, 39.95],
            }
        )
        stats = get_coordinate_stats(df)
        assert "total_records" in stats
        assert "coverage_rate" in stats
        assert stats["total_records"] == 3
        assert stats["has_coordinates"] == 2

    def test_coverage_rate_calculation(self):
        """Coverage rate calculated correctly."""
        df = pd.DataFrame(
            {
                "point_x": [-75.1, -75.1],
                "point_y": [39.95, 39.95],
            }
        )
        stats = get_coordinate_stats(df)
        assert stats["coverage_rate"] == 1.0

    def test_empty_dataframe(self):
        """Handles empty DataFrame."""
        df = pd.DataFrame({"point_x": [], "point_y": []})
        stats = get_coordinate_stats(df)
        assert stats["total_records"] == 0
        assert stats["coverage_rate"] == 0
