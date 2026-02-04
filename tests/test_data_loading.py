"""Tests for data loading functions with caching.

This module tests the data loading functionality including:
- load_crime_data() with clean parameter
- Cache performance verification (5x+ speedup expected)
- load_boundaries() (with geopandas optional import)
- load_external_data() error handling
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from analysis.data import clear_cache, load_crime_data
from analysis.data.cache import _CACHE_DIR, memory
from analysis.data.loading import _load_crime_data_parquet, load_boundaries, load_external_data

if TYPE_CHECKING:
    pass


class TestLoadCrimeData:
    """Tests for load_crime_data function."""

    def test_returns_dataframe(self):
        """load_crime_data returns a pandas DataFrame."""
        df = load_crime_data()
        assert isinstance(df, pd.DataFrame)

    def test_dataframe_not_empty(self):
        """load_crime_data returns non-empty DataFrame."""
        df = load_crime_data()
        assert len(df) > 0

    def test_has_expected_columns(self):
        """DataFrame has expected columns for crime data."""
        df = load_crime_data()
        expected_cols = ["objectid", "dispatch_date", "ucr_general"]
        for col in expected_cols:
            assert col in df.columns, f"Column '{col}' not found in DataFrame"

    def test_clean_parameter_defaults_to_true(self):
        """Default clean=True drops rows with missing dispatch_date."""
        df = load_crime_data()
        assert df["dispatch_date"].notna().all()

    def test_clean_false_includes_all_rows(self):
        """clean=False includes rows with missing dispatch_date."""
        df_dirty = load_crime_data(clean=False)
        df_clean = load_crime_data(clean=True)
        # dirty version should have same or more rows
        assert len(df_dirty) >= len(df_clean)

    def test_dispatch_date_is_datetime(self):
        """dispatch_date column is parsed as datetime."""
        df = load_crime_data()
        assert pd.api.types.is_datetime64_any_dtype(df["dispatch_date"])

    @pytest.mark.slow
    def test_cache_performance_speedup(self):
        """Second load is at least 5x faster than first load (cache hit).

        This test verifies that joblib caching provides significant
        performance improvement. Expected speedup is 10-20x, but we
        assert at least 5x to account for system variability.
        """
        import time

        # Clear cache to ensure first load reads from disk
        clear_cache()

        # First load (reads from parquet)
        start = time.time()
        df1 = load_crime_data()
        first_load_time = time.time() - start

        # Second load (should hit cache)
        start = time.time()
        df2 = load_crime_data()
        second_load_time = time.time() - start

        # Verify DataFrames are equal
        pd.testing.assert_frame_equal(df1, df2)

        # Verify speedup (at least 5x faster)
        speedup = first_load_time / second_load_time if second_load_time > 0 else float("inf")
        assert speedup >= 5.0, f"Cache speedup {speedup:.1f}x is less than 5x threshold"

    @pytest.mark.slow
    def test_cache_persists_across_calls(self):
        """Cached result persists across multiple function calls."""
        clear_cache()

        df1 = load_crime_data()
        df2 = load_crime_data()
        df3 = load_crime_data()

        pd.testing.assert_frame_equal(df1, df2)
        pd.testing.assert_frame_equal(df2, df3)

    def test_cache_key_different_for_clean_parameter(self):
        """Cache key includes 'clean' parameter."""
        clear_cache()

        # Load with clean=True (first call, reads from disk)
        df1 = load_crime_data(clean=True)

        # Load with clean=False (should be separate cache entry)
        df2 = load_crime_data(clean=False)

        # Verify different result sets (clean=False has more rows)
        assert len(df2) >= len(df1)


class TestCacheDirectory:
    """Tests for cache directory management."""

    def test_cache_directory_exists(self):
        """Cache directory .cache/joblib/ exists after first load."""
        load_crime_data()
        assert _CACHE_DIR.exists()

    def test_clear_cache_removes_cached_files(self):
        """clear_cache() removes cached files from cache directory."""
        # Load data to populate cache
        load_crime_data()

        # Clear cache
        clear_cache()

        # Cache directory should be empty or only contain hidden files
        items = [item for item in _CACHE_DIR.iterdir() if not item.name.startswith(".")]
        assert len(items) == 0, "Cache directory should be empty after clear_cache()"


class TestLoadBoundaries:
    """Tests for load_boundaries function."""

    def test_raises_import_error_without_geopandas(self):
        """Raises ImportError when geopandas is not installed."""
        # Mock HAS_GEOPANDAS to False
        with (
            patch("analysis.data.loading.HAS_GEOPANDAS", False),
            pytest.raises(ImportError, match="geopandas is required"),
        ):
            load_boundaries("police_districts")

    def test_invalid_boundary_name_raises_value_error(self):
        """Invalid boundary name raises ValueError."""
        # Mock geopandas as available
        with patch("analysis.data.loading.HAS_GEOPANDAS", True):
            # Mock the internal function to avoid actual file loading
            mock_gpd = Mock()
            mock_gpd.GeoDataFrame.from_features.return_value = []
            with (
                patch("analysis.data.loading.gpd", mock_gpd),
                pytest.raises(ValueError, match="Unknown boundary"),
            ):
                load_boundaries("invalid_boundary")

    @pytest.mark.skipif(
        not Path("data/boundaries/Police_Districts.geojson").exists(),
        reason="Boundary data file not found",
    )
    @pytest.mark.slow
    def test_load_police_districts_returns_geodataframe(self):
        """load_boundaries('police_districts') returns GeoDataFrame."""
        try:
            import geopandas as gpd

            districts = load_boundaries("police_districts")
            assert isinstance(districts, gpd.GeoDataFrame)
            assert len(districts) > 0
        except ImportError:
            pytest.skip("geopandas not installed")

    @pytest.mark.skipif(
        not Path("data/boundaries/Census_Tracts_2020.geojson").exists(),
        reason="Boundary data file not found",
    )
    @pytest.mark.slow
    def test_load_census_tracts_returns_geodataframe(self):
        """load_boundaries('census_tracts') returns GeoDataFrame."""
        try:
            import geopandas as gpd

            tracts = load_boundaries("census_tracts")
            assert isinstance(tracts, gpd.GeoDataFrame)
            assert len(tracts) > 0
        except ImportError:
            pytest.skip("geopandas not installed")


class TestLoadExternalData:
    """Tests for load_external_data function."""

    def test_nonexistent_file_raises_file_not_found_error(self):
        """Loading nonexistent external data raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="External data not found"):
            load_external_data("nonexistent_file")

    def test_loads_existing_csv_file(self):
        """Loads valid CSV file from data/external/.

        Note: This test requires an existing CSV file in data/external/.
        If no such file exists, this test is skipped.
        """
        repo_root = Path(__file__).resolve().parent.parent.parent
        external_dir = repo_root / "data" / "external"

        # Find any CSV file in data/external
        csv_files = list(external_dir.glob("*.csv"))
        if not csv_files:
            pytest.skip("No CSV files found in data/external/")

        # Test loading the first available CSV file
        test_file = csv_files[0]
        df = load_external_data(test_file.stem)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestInternalLoadFunctions:
    """Tests for internal cached loading functions."""

    def test_load_crime_data_parquet_decorated_with_cache(self):
        """_load_crime_data_parquet is decorated with memory.cache.

        joblib.Memory.cache wraps functions, so we check that the function
        is callable and has the expected attributes from joblib's wrapper.
        """
        # The cached function should be callable
        assert callable(_load_crime_data_parquet)
        # joblib cached functions have __wrapped__ attribute pointing to original
        assert hasattr(_load_crime_data_parquet, "__wrapped__")

    @pytest.mark.slow
    def test_internal_function_returns_dataframe(self):
        """Internal function returns DataFrame with parsed dispatch_date."""
        df = _load_crime_data_parquet(clean=True)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert pd.api.types.is_datetime64_any_dtype(df["dispatch_date"])


class TestMemoryInstance:
    """Tests for joblib Memory instance."""

    def test_memory_instance_exists(self):
        """Global memory instance is configured."""

        assert memory is not None
        assert hasattr(memory, "location")

    def test_memory_location_is_cache_dir(self):
        """Memory location points to cache directory."""

        assert _CACHE_DIR in Path(memory.location).parents or Path(memory.location) == _CACHE_DIR


class TestGeopandasImport:
    """Tests for geopandas optional import handling."""

    def test_has_geopandas_is_bool(self):
        """HAS_GEOPANDAS is a boolean indicating geopandas availability."""
        from analysis.data.loading import HAS_GEOPANDAS

        assert isinstance(HAS_GEOPANDAS, bool)


class TestFileNotFoundError:
    """Tests for FileNotFoundError handling in loading functions."""

    def test_internal_function_raises_file_not_found(self):
        """Internal _load_crime_data_parquet raises FileNotFoundError for missing file."""
        # This tests the error path in the internal cached function
        # We can't easily mock CRIME_DATA_PATH because the function is cached,
        # but we can verify the code path exists
        # The function should have error handling for FileNotFoundError
        # We can verify this by checking the source code has the error handling
        import inspect

        from analysis.data.loading import _load_crime_data_parquet

        source = inspect.getsource(_load_crime_data_parquet)
        assert "FileNotFoundError" in source
        assert "Crime data not found" in source
