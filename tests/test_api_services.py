"""Unit tests for API service layer (api/services/data_loader.py).

This module tests the data loading service layer with mocked file I/O for fast
execution. Tests use monkeypatch to replace file system operations and tmp_path
for isolated test directories.

Test strategy:
- Mock file I/O to avoid loading real data files
- Use tmp_path for isolated test directories
- Test all code paths including error handling
- Validate cache management, data contract validation, and environment variable handling
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from api.services import data_loader


class TestLoadAllData:
    """Tests for load_all_data() function."""

    def test_load_all_data_populates_cache(self, tmp_path: Path) -> None:
        """Test load_all_data() populates _DATA_CACHE with JSON and GeoJSON files."""
        # Create required exports first
        for export in data_loader.REQUIRED_EXPORTS:
            file_path = tmp_path / export
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(f'{{"source": "{export}"}}', encoding="utf-8")

        # Create test JSON file
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}', encoding="utf-8")

        # Create test GeoJSON file in subdirectory
        geo_dir = tmp_path / "geo"
        geo_dir.mkdir(exist_ok=True)
        geojson_file = geo_dir / "test.geojson"
        geojson_file.write_text(
            '{"type": "FeatureCollection", "features": []}', encoding="utf-8"
        )

        # Load data
        cache = data_loader.load_all_data(data_dir=tmp_path)

        # Verify cache is populated
        assert "test.json" in cache
        assert "geo/test.geojson" in cache

        # Verify cache contains parsed JSON (not strings)
        assert cache["test.json"] == {"key": "value"}
        assert cache["geo/test.geojson"] == {
            "type": "FeatureCollection",
            "features": [],
        }

    def test_load_all_data_clears_existing_cache(self, tmp_path: Path) -> None:
        """Test load_all_data() clears existing cache before loading new data."""
        # Create required exports first
        for export in data_loader.REQUIRED_EXPORTS:
            file_path = tmp_path / export
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(f'{{"source": "{export}"}}', encoding="utf-8")

        # Pre-populate cache with old data
        data_loader._DATA_CACHE["old_key.json"] = {"old": "data"}

        # Create new test file
        new_file = tmp_path / "new.json"
        new_file.write_text('{"new": "data"}', encoding="utf-8")

        # Load new data
        cache = data_loader.load_all_data(data_dir=tmp_path)

        # Verify old cache keys are removed
        assert "old_key.json" not in cache
        assert "old_key.json" not in data_loader._DATA_CACHE

        # Verify only new data is in cache
        assert "new.json" in cache
        assert cache["new.json"] == {"new": "data"}

    def test_load_all_data_only_json_and_geojson(self, tmp_path: Path) -> None:
        """Test load_all_data() only loads .json and .geojson files."""
        # Create required exports first
        for export in data_loader.REQUIRED_EXPORTS:
            file_path = tmp_path / export
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(f'{{"source": "{export}"}}', encoding="utf-8")

        # Create files with different extensions
        (tmp_path / "data.json").write_text('{"type": "json"}', encoding="utf-8")
        (tmp_path / "data.geojson").write_text(
            '{"type": "FeatureCollection"}', encoding="utf-8"
        )
        (tmp_path / "data.txt").write_text("text file", encoding="utf-8")
        (tmp_path / "data.csv").write_text("a,b,c\n1,2,3", encoding="utf-8")

        # Load data
        cache = data_loader.load_all_data(data_dir=tmp_path)

        # Verify only JSON and GeoJSON files are loaded
        assert "data.json" in cache
        assert "data.geojson" in cache
        assert "data.txt" not in cache
        assert "data.csv" not in cache

    def test_load_all_data_validates_contract(self, tmp_path: Path) -> None:
        """Test load_all_data() raises RuntimeError for missing required exports."""
        # Create directory with only some required files
        (tmp_path / "annual_trends.json").write_text('{"data": []}', encoding="utf-8")

        # Should raise RuntimeError for missing exports
        with pytest.raises(RuntimeError, match="Missing required pipeline exports"):
            data_loader.load_all_data(data_dir=tmp_path)

    def test_load_all_data_with_nested_directories(self, tmp_path: Path) -> None:
        """Test load_all_data() loads files from nested directories."""
        # Create required exports first
        for export in data_loader.REQUIRED_EXPORTS:
            file_path = tmp_path / export
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(f'{{"source": "{export}"}}', encoding="utf-8")

        # Create nested directory structure
        (tmp_path / "level1").mkdir(exist_ok=True)
        (tmp_path / "level1" / "level2").mkdir(exist_ok=True)

        # Create files at different levels
        (tmp_path / "root.json").write_text('{"level": "root"}', encoding="utf-8")
        (tmp_path / "level1" / "mid.json").write_text(
            '{"level": "mid"}', encoding="utf-8"
        )
        (tmp_path / "level1" / "level2" / "deep.json").write_text(
            '{"level": "deep"}', encoding="utf-8"
        )

        # Load data
        cache = data_loader.load_all_data(data_dir=tmp_path)

        # Verify all files are loaded with correct relative paths
        assert cache["root.json"] == {"level": "root"}
        assert cache["level1/mid.json"] == {"level": "mid"}
        assert cache["level1/level2/deep.json"] == {"level": "deep"}


class TestGetData:
    """Tests for get_data() function."""

    def test_get_data_returns_cached_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test get_data() returns data from cache."""
        # Pre-populate cache with test data
        test_data = {"key": "value", "number": 42}
        monkeypatch.setattr(
            data_loader, "_DATA_CACHE", {"test.json": test_data}
        )

        # Fetch data
        result = data_loader.get_data("test.json")

        # Verify correct data is returned
        assert result == test_data

    def test_get_data_raises_key_error_for_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_data() raises KeyError for missing cache key."""
        # Set cache to empty
        monkeypatch.setattr(data_loader, "_DATA_CACHE", {})

        # Should raise KeyError with specific message
        with pytest.raises(KeyError, match="Data key not loaded"):
            data_loader.get_data("nonexistent.json")

    def test_get_data_with_geojson_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test get_data() returns GeoJSON data structure."""
        # Pre-populate cache with GeoJSON
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-75.16, 39.95]},
                    "properties": {"name": "Test"},
                }
            ],
        }
        monkeypatch.setattr(
            data_loader, "_DATA_CACHE", {"geo/districts.geojson": geojson_data}
        )

        # Fetch data
        result = data_loader.get_data("geo/districts.geojson")

        # Verify GeoJSON structure is preserved
        assert result == geojson_data
        assert result["type"] == "FeatureCollection"
        assert len(result["features"]) == 1

    def test_get_data_with_nested_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test get_data() handles nested cache keys."""
        # Pre-populate cache with nested key
        test_data = {"nested": "value"}
        monkeypatch.setattr(
            data_loader,
            "_DATA_CACHE",
            {"level1/level2/data.json": test_data},
        )

        # Fetch data with nested key
        result = data_loader.get_data("level1/level2/data.json")

        # Verify correct data is returned
        assert result == test_data


class TestContractStatus:
    """Tests for contract_status() function."""

    def test_contract_status_ok_when_all_files_present(self, tmp_path: Path) -> None:
        """Test contract_status() returns ok=True when all required files exist."""
        # Create all required exports
        for export in data_loader.REQUIRED_EXPORTS:
            file_path = tmp_path / export
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text('{"data": true}', encoding="utf-8")

        # Check contract status
        status = data_loader.contract_status(data_dir=tmp_path)

        # Verify status
        assert status["ok"] is True
        assert status["missing_exports"] == []
        assert status["data_dir"] == str(tmp_path)

    def test_contract_status_not_ok_when_files_missing(self, tmp_path: Path) -> None:
        """Test contract_status() returns ok=False when required files are missing."""
        # Create only some required files
        (tmp_path / "annual_trends.json").write_text('{"data": []}', encoding="utf-8")
        (tmp_path / "metadata.json").write_text('{"version": "1.0"}', encoding="utf-8")

        # Check contract status
        status = data_loader.contract_status(data_dir=tmp_path)

        # Verify status
        assert status["ok"] is False
        assert len(status["missing_exports"]) > 0
        assert "annual_trends.json" not in status["missing_exports"]
        assert "covid_comparison.json" in status["missing_exports"]
        assert status["data_dir"] == str(tmp_path)

    def test_contract_status_nonexistent_directory(self) -> None:
        """Test contract_status() handles nonexistent directory gracefully."""
        nonexistent_path = Path("/nonexistent/path/that/does/not/exist")

        # Check contract status
        status = data_loader.contract_status(data_dir=nonexistent_path)

        # Verify status
        assert status["ok"] is False
        assert len(status["missing_exports"]) == len(data_loader.REQUIRED_EXPORTS)
        assert status["data_dir"] == str(nonexistent_path)

    def test_contract_status_includes_last_loaded_dir(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Test contract_status() includes last_loaded_dir in response."""
        # Set last loaded directory
        test_dir = Path("/test/data/dir")
        monkeypatch.setattr(data_loader, "_LAST_DATA_DIR", test_dir)

        # Check contract status
        status = data_loader.contract_status(data_dir=tmp_path)

        # Verify last_loaded_dir is included
        assert "last_loaded_dir" in status
        assert status["last_loaded_dir"] == str(test_dir)


class TestCacheKeys:
    """Tests for cache_keys() function."""

    def test_cache_keys_returns_sorted_list(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test cache_keys() returns alphabetically sorted list of keys."""
        # Pre-populate cache with unsorted keys
        test_cache = {
            "z_final.json": {},
            "a_first.json": {},
            "m_middle.json": {},
            "geo/districts.geojson": {},
            "geo/hotspots.geojson": {},
        }
        monkeypatch.setattr(data_loader, "_DATA_CACHE", test_cache)

        # Get cache keys
        keys = data_loader.cache_keys()

        # Verify result is a list
        assert isinstance(keys, list)

        # Verify result is sorted alphabetically
        assert keys == sorted(keys)

        # Verify all cache keys are present
        assert set(keys) == set(test_cache.keys())

    def test_cache_keys_empty_when_cache_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test cache_keys() returns empty list when cache is empty."""
        # Set cache to empty
        monkeypatch.setattr(data_loader, "_DATA_CACHE", {})

        # Get cache keys
        keys = data_loader.cache_keys()

        # Verify result is empty list
        assert keys == []

    def test_cache_keys_includes_nested_keys(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test cache_keys() includes nested directory keys."""
        # Pre-populate cache with nested keys
        test_cache = {
            "root.json": {},
            "geo/districts.geojson": {},
            "level1/level2/data.json": {},
        }
        monkeypatch.setattr(data_loader, "_DATA_CACHE", test_cache)

        # Get cache keys
        keys = data_loader.cache_keys()

        # Verify all keys including nested ones are present
        assert "root.json" in keys
        assert "geo/districts.geojson" in keys
        assert "level1/level2/data.json" in keys


class TestValidateDataContract:
    """Tests for _validate_data_contract() function."""

    def test_validate_data_contract_raises_on_missing_directory(self) -> None:
        """Test _validate_data_contract() raises RuntimeError for missing directory."""
        nonexistent_path = Path("/nonexistent/path")

        # Should raise RuntimeError
        with pytest.raises(
            RuntimeError, match="API data directory does not exist"
        ):
            data_loader._validate_data_contract(nonexistent_path)

    def test_validate_data_contract_raises_on_missing_exports(self, tmp_path: Path) -> None:
        """Test _validate_data_contract() raises RuntimeError for missing exports."""
        # Create directory without required exports

        # Should raise RuntimeError with missing exports list
        with pytest.raises(RuntimeError, match="Missing required pipeline exports"):
            data_loader._validate_data_contract(tmp_path)

    def test_validate_data_contract_passes_with_complete_exports(self, tmp_path: Path) -> None:
        """Test _validate_data_contract() passes with all required exports."""
        # Create all required exports
        for export in data_loader.REQUIRED_EXPORTS:
            file_path = tmp_path / export
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text('{"data": true}', encoding="utf-8")

        # Should not raise any exception
        data_loader._validate_data_contract(tmp_path)

    def test_validate_data_contract_includes_all_missing_in_error(
        self, tmp_path: Path
    ) -> None:
        """Test _validate_data_contract() error message lists all missing exports."""
        # Create only one required file
        (tmp_path / "annual_trends.json").write_text('{"data": []}', encoding="utf-8")

        # Should raise RuntimeError
        try:
            data_loader._validate_data_contract(tmp_path)
            pytest.fail("Expected RuntimeError")
        except RuntimeError as e:
            # Verify error message mentions missing exports
            error_msg = str(e)
            assert "Missing required pipeline exports" in error_msg
            # Verify it lists at least some missing files
            assert "covid_comparison.json" in error_msg


class TestResolveDataDir:
    """Tests for _resolve_data_dir() function."""

    def test_resolve_data_dir_uses_explicit_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test _resolve_data_dir() uses explicit path when provided."""
        explicit_path = Path("/explicit/data/path")

        # Resolve with explicit path
        result = data_loader._resolve_data_dir(data_dir=explicit_path)

        # Verify returns explicit path
        assert result == explicit_path

    def test_resolve_data_dir_uses_env_var_when_set(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test _resolve_data_dir() uses API_DATA_DIR environment variable when set."""
        env_path = "/env/data/path"
        monkeypatch.setenv("API_DATA_DIR", env_path)

        # Resolve without explicit path
        result = data_loader._resolve_data_dir(data_dir=None)

        # Verify returns environment variable path
        assert result == Path(env_path)

    def test_resolve_data_dir_uses_default_when_env_not_set(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test _resolve_data_dir() uses default DATA_DIR when env var not set."""
        # Ensure env var is not set
        monkeypatch.delenv("API_DATA_DIR", raising=False)

        # Resolve without explicit path
        result = data_loader._resolve_data_dir(data_dir=None)

        # Verify returns default DATA_DIR
        assert result == data_loader.DATA_DIR

    def test_resolve_data_dir_explicit_overrides_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test _resolve_data_dir() explicit path overrides environment variable."""
        env_path = "/env/data/path"
        explicit_path = Path("/explicit/data/path")
        monkeypatch.setenv("API_DATA_DIR", env_path)

        # Resolve with explicit path (should override env)
        result = data_loader._resolve_data_dir(data_dir=explicit_path)

        # Verify returns explicit path, not env path
        assert result == explicit_path
        assert result != Path(env_path)


class TestMissingRequiredExports:
    """Tests for _missing_required_exports() function."""

    def test_missing_required_exports_returns_empty_when_all_present(
        self, tmp_path: Path
    ) -> None:
        """Test _missing_required_exports() returns empty list when all files exist."""
        # Create all required exports
        for export in data_loader.REQUIRED_EXPORTS:
            file_path = tmp_path / export
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text('{"data": true}', encoding="utf-8")

        # Get missing exports
        missing = data_loader._missing_required_exports(tmp_path)

        # Verify returns empty list
        assert missing == []

    def test_missing_required_exports_lists_missing_files(self, tmp_path: Path) -> None:
        """Test _missing_required_exports() lists missing files."""
        # Create only some required files
        (tmp_path / "annual_trends.json").write_text('{"data": []}', encoding="utf-8")
        (tmp_path / "metadata.json").write_text('{"version": "1.0"}', encoding="utf-8")

        # Get missing exports
        missing = data_loader._missing_required_exports(tmp_path)

        # Verify returns list of missing files
        assert isinstance(missing, list)
        assert len(missing) > 0
        assert "covid_comparison.json" in missing
        assert "annual_trends.json" not in missing

    def test_missing_required_exports_checks_geo_files(self, tmp_path: Path) -> None:
        """Test _missing_required_exports() checks geo subdirectory files."""
        # Create no files

        # Get missing exports
        missing = data_loader._missing_required_exports(tmp_path)

        # Verify geo files are in missing list
        assert "geo/districts.geojson" in missing
        assert "geo/tracts.geojson" in missing


class TestEnvironmentVariableIntegration:
    """Tests for API_DATA_DIR environment variable integration."""

    def test_load_all_data_uses_data_dir_from_env(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Test load_all_data() uses API_DATA_DIR when set."""
        # Set environment variable
        monkeypatch.setenv("API_DATA_DIR", str(tmp_path))

        # Create all required exports in tmp_path
        for export in data_loader.REQUIRED_EXPORTS:
            file_path = tmp_path / export
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(f'{{"source": "{export}"}}', encoding="utf-8")

        # Load data (should use env var, not explicit path)
        cache = data_loader.load_all_data()

        # Verify files from tmp_path are loaded
        assert len(cache) > 0
        assert "annual_trends.json" in cache

    def test_contract_status_uses_data_dir_from_env(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Test contract_status() uses API_DATA_DIR when set."""
        # Set environment variable
        monkeypatch.setenv("API_DATA_DIR", str(tmp_path))

        # Create some required files
        (tmp_path / "annual_trends.json").write_text('{"data": []}', encoding="utf-8")

        # Check contract status (should use env var)
        status = data_loader.contract_status()

        # Verify status reflects tmp_path
        assert status["data_dir"] == str(tmp_path)
        assert status["ok"] is False  # Missing most required files
