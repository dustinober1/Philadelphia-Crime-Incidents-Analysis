"""Tests for analysis/config/settings.py validating GlobalConfig and BaseConfig classes."""

from pathlib import Path

import pytest
import yaml
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


class TestBaseConfigDefaults:
    """Test BaseConfig default values."""

    def test_base_config_defaults_output_dir(self):
        """Verify output_dir defaults correctly."""
        config = BaseConfig()
        assert config.output_dir.name == "reports"

    def test_base_config_defaults_dpi(self):
        """Verify dpi defaults to 300."""
        config = BaseConfig()
        assert config.dpi == 300

    def test_base_config_defaults_output_format(self):
        """Verify output_format defaults to "png"."""
        config = BaseConfig()
        assert config.output_format == "png"

    def test_base_config_defaults_fast_sample_frac(self):
        """Verify fast_sample_frac defaults to 0.1."""
        config = BaseConfig()
        assert config.fast_sample_frac == 0.1

    def test_base_config_defaults_cache_enabled(self):
        """Verify cache_enabled defaults to True."""
        config = BaseConfig()
        assert config.cache_enabled is True

    def test_base_config_defaults_log_level(self):
        """Verify log_level defaults to "INFO"."""
        config = BaseConfig()
        assert config.log_level == "INFO"

    def test_base_config_defaults_version(self):
        """Verify version defaults to "v1.0"."""
        config = BaseConfig()
        assert config.version == "v1.0"


class TestGlobalConfigYamlLoading:
    """Test GlobalConfig loading from YAML files."""

    def test_global_config_loads_from_yaml(self, tmp_path, monkeypatch):
        """Verify GlobalConfig loads values from global.yaml."""
        # Create config directory and YAML file
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "global.yaml"

        config_data = {
            "output_dir": str(tmp_path / "custom_reports"),
            "dpi": 150,
            "output_format": "svg",
            "fast_sample_frac": 0.5,
            "cache_enabled": False,
            "log_level": "DEBUG",
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Change to tmp_path so config/global.yaml is found
        monkeypatch.chdir(tmp_path)

        config = GlobalConfig()
        assert config.dpi == 150
        assert config.output_format == "svg"
        assert config.fast_sample_frac == 0.5
        assert config.cache_enabled is False
        assert config.log_level == "DEBUG"

    def test_global_config_yaml_overrides_defaults(self, tmp_path, monkeypatch):
        """Verify YAML values override defaults."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "global.yaml"

        config_data = {"dpi": 200, "output_format": "pdf"}
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        monkeypatch.chdir(tmp_path)

        config = GlobalConfig()
        assert config.dpi == 200  # Overridden
        assert config.output_format == "pdf"  # Overridden
        assert config.fast_sample_frac == 0.1  # Default preserved

    def test_global_config_missing_yaml_uses_defaults(self, tmp_path, monkeypatch):
        """Verify no error when YAML missing (uses defaults)."""
        # Create empty tmp_path with no config directory
        monkeypatch.chdir(tmp_path)

        # Should not raise an error
        config = GlobalConfig()
        assert config.dpi == 300  # Default
        assert config.output_format == "png"  # Default

    def test_global_config_yaml_partial_config(self, tmp_path, monkeypatch):
        """Verify partial YAML uses defaults for unspecified fields."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "global.yaml"

        # Only specify one field
        config_data = {"dpi": 400}
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        monkeypatch.chdir(tmp_path)

        config = GlobalConfig()
        assert config.dpi == 400  # From YAML
        assert config.output_format == "png"  # Default
        assert config.fast_sample_frac == 0.1  # Default
        assert config.cache_enabled is True  # Default


class TestEnvironmentVariableOverrides:
    """Test environment variable configuration overrides."""

    def test_global_config_env_override_output_dir(self, tmp_path, monkeypatch):
        """Verify CRIME_OUTPUT_DIR overrides YAML and default."""
        custom_dir = str(tmp_path / "custom_output")
        monkeypatch.setenv("CRIME_OUTPUT_DIR", custom_dir)

        config = GlobalConfig()
        assert str(config.output_dir) == custom_dir

    def test_global_config_env_override_dpi(self, monkeypatch):
        """Verify CRIME_DPI overrides other sources."""
        monkeypatch.setenv("CRIME_DPI", "500")

        config = GlobalConfig()
        assert config.dpi == 500

    def test_global_config_env_override_output_format(self, monkeypatch):
        """Verify CRIME_OUTPUT_FORMAT overrides."""
        monkeypatch.setenv("CRIME_OUTPUT_FORMAT", "svg")

        config = GlobalConfig()
        assert config.output_format == "svg"

    def test_global_config_env_override_fast_sample_frac(self, monkeypatch):
        """Verify CRIME_FAST_SAMPLE_FRAC overrides."""
        monkeypatch.setenv("CRIME_FAST_SAMPLE_FRAC", "0.75")

        config = GlobalConfig()
        assert config.fast_sample_frac == 0.75

    def test_global_config_env_override_cache_enabled(self, monkeypatch):
        """Verify CRIME_CACHE_ENABLED overrides (boolean parsing)."""
        # Test "false" string
        monkeypatch.setenv("CRIME_CACHE_ENABLED", "false")

        config = GlobalConfig()
        assert config.cache_enabled is False

    def test_global_config_env_override_log_level(self, monkeypatch):
        """Verify CRIME_LOG_LEVEL overrides."""
        monkeypatch.setenv("CRIME_LOG_LEVEL", "ERROR")

        config = GlobalConfig()
        assert config.log_level == "ERROR"

    def test_base_config_env_overrides_work(self, monkeypatch):
        """Verify env vars work for BaseConfig too."""
        monkeypatch.setenv("CRIME_DPI", "250")
        monkeypatch.setenv("CRIME_OUTPUT_FORMAT", "pdf")

        config = BaseConfig()
        assert config.dpi == 250
        assert config.output_format == "pdf"
