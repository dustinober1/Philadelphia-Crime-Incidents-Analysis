"""Tests for analysis/config/settings.py validating GlobalConfig and BaseConfig classes."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from analysis.config.settings import BaseConfig, GlobalConfig


class TestGlobalConfigDefaults:
    """Test GlobalConfig default values."""

    def test_global_config_defaults_output_dir(self, tmp_path):
        """Verify output_dir defaults to repo_root/"reports"."""
        config = GlobalConfig()
        # Get repo root from config's crime_data_path which is repo_root/data/...
        repo_root = config.crime_data_path.parent.parent
        assert config.output_dir == repo_root / "reports"

    def test_global_config_defaults_dpi(self):
        """Verify dpi defaults to 300."""
        config = GlobalConfig()
        assert config.dpi == 300

    def test_global_config_defaults_output_format(self):
        """Verify output_format defaults to "png"."""
        config = GlobalConfig()
        assert config.output_format == "png"

    def test_global_config_defaults_fast_sample_frac(self):
        """Verify fast_sample_frac defaults to 0.1."""
        config = GlobalConfig()
        assert config.fast_sample_frac == 0.1

    def test_global_config_defaults_cache_enabled(self):
        """Verify cache_enabled defaults to True."""
        config = GlobalConfig()
        assert config.cache_enabled is True

    def test_global_config_defaults_log_level(self):
        """Verify log_level defaults to "INFO"."""
        config = GlobalConfig()
        assert config.log_level == "INFO"

    def test_global_config_defaults_crime_data_path(self):
        """Verify crime_data_path points to data/crime_incidents_combined.parquet."""
        config = GlobalConfig()
        assert config.crime_data_path.name == "crime_incidents_combined.parquet"
        assert "data" in config.crime_data_path.parts

    def test_global_config_defaults_boundaries_dir(self):
        """Verify boundaries_dir points to data/boundaries."""
        config = GlobalConfig()
        assert config.boundaries_dir.name == "boundaries"
        assert "data" in config.boundaries_dir.parts
