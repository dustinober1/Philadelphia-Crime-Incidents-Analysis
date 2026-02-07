"""Tests for pipeline refresh operations (pipeline/refresh_data.py)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from pipeline.refresh_data import (
    _REQUIRED_FILES,
    _assert_reproducible,
    _canonical_json,
    _load_json,
    _validate_artifacts,
    app,
)

runner = CliRunner()


def _create_minimal_valid_files(output_dir: Path) -> None:
    """Create minimal valid files for all required exports."""
    valid_metadata = {
        "total_incidents": 100000,
        "date_start": "2006-01-01",
        "date_end": "2024-12-31",
        "last_updated": "2025-01-15T10:30:00Z",
        "source": "Philadelphia Police Department",
        "colors": {"crime": "#FF5733"},
    }
    valid_annual_trends = [{"year": 2020, "incidents": 10000}]
    valid_forecast = {"historical": [{"date": "2023-01-01", "value": 100}], "forecast": [{"date": "2024-01-01", "value": 110}]}

    for file_path in _REQUIRED_FILES:
        full_path = output_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path == "metadata.json":
            full_path.write_text(json.dumps(valid_metadata))
        elif file_path == "annual_trends.json":
            full_path.write_text(json.dumps(valid_annual_trends))
        elif file_path == "forecast.json":
            full_path.write_text(json.dumps(valid_forecast))
        else:
            full_path.write_text("{}")


class TestValidateArtifactsSuccess:
    """Tests for _validate_artifacts success cases."""

    def test_validate_artifacts_passes_with_complete_exports(self, tmp_path: Path) -> None:
        """Should pass when all required export files exist."""
        # Create minimal valid files
        _create_minimal_valid_files(tmp_path)

        # Should not raise any exception
        _validate_artifacts(tmp_path)

    def test_validate_artifacts_passes_with_valid_metadata(self, tmp_path: Path) -> None:
        """Should pass when metadata.json has all required keys."""
        # Create all required files with valid metadata
        _create_minimal_valid_files(tmp_path)

        # Should not raise any exception
        _validate_artifacts(tmp_path)

    def test_validate_artifacts_passes_with_valid_annual_trends(self, tmp_path: Path) -> None:
        """Should pass when annual_trends.json is a non-empty list."""
        # Create all required files with valid annual trends
        _create_minimal_valid_files(tmp_path)

        # Should not raise any exception
        _validate_artifacts(tmp_path)

    def test_validate_artifacts_passes_with_valid_forecast(self, tmp_path: Path) -> None:
        """Should pass when forecast.json contains historical and forecast keys."""
        # Create all required files with valid forecast
        _create_minimal_valid_files(tmp_path)

        # Should not raise any exception
        _validate_artifacts(tmp_path)


class TestValidateArtifactsFailure:
    """Tests for _validate_artifacts failure cases."""

    def test_validate_artifacts_raises_missing_files(self, tmp_path: Path) -> None:
        """Should raise RuntimeError when required files are missing."""
        # Create only metadata.json to trigger missing file error
        (tmp_path / "metadata.json").write_text(json.dumps({
            "total_incidents": 100000,
            "date_start": "2006-01-01",
            "date_end": "2024-12-31",
            "last_updated": "2025-01-15T10:30:00Z",
            "source": "Philadelphia Police Department",
            "colors": {"crime": "#FF5733"},
        }))

        with pytest.raises(RuntimeError, match="Missing required export files"):
            _validate_artifacts(tmp_path)

    def test_validate_artifacts_raises_invalid_metadata_keys(self, tmp_path: Path) -> None:
        """Should raise RuntimeError when metadata.json missing required keys."""
        # Create all files with invalid metadata
        for file_path in _REQUIRED_FILES:
            full_path = tmp_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if file_path == "metadata.json":
                full_path.write_text(json.dumps({"total_incidents": 100000}))  # Missing required keys
            elif file_path == "annual_trends.json":
                full_path.write_text(json.dumps([{"year": 2020, "incidents": 10000}]))
            elif file_path == "forecast.json":
                full_path.write_text(json.dumps({
                    "historical": [{"date": "2023-01-01", "value": 100}],
                    "forecast": [{"date": "2024-01-01", "value": 110}],
                }))
            else:
                full_path.write_text("{}")

        with pytest.raises(RuntimeError, match="metadata.json is missing required keys"):
            _validate_artifacts(tmp_path)

    def test_validate_artifacts_raises_invalid_annual_trends(self, tmp_path: Path) -> None:
        """Should raise RuntimeError when annual_trends.json is not a list."""
        # Create all files with invalid annual_trends
        for file_path in _REQUIRED_FILES:
            full_path = tmp_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if file_path == "metadata.json":
                full_path.write_text(json.dumps({
                    "total_incidents": 100000,
                    "date_start": "2006-01-01",
                    "date_end": "2024-12-31",
                    "last_updated": "2025-01-15T10:30:00Z",
                    "source": "Philadelphia Police Department",
                    "colors": {"crime": "#FF5733"},
                }))
            elif file_path == "annual_trends.json":
                full_path.write_text(json.dumps({"not": "a list"}))  # Not a list
            elif file_path == "forecast.json":
                full_path.write_text(json.dumps({
                    "historical": [{"date": "2023-01-01", "value": 100}],
                    "forecast": [{"date": "2024-01-01", "value": 110}],
                }))
            else:
                full_path.write_text("{}")

        with pytest.raises(RuntimeError, match="annual_trends.json must be a non-empty list"):
            _validate_artifacts(tmp_path)

    def test_validate_artifacts_raises_empty_annual_trends(self, tmp_path: Path) -> None:
        """Should raise RuntimeError when annual_trends.json is empty list."""
        # Create all files with empty annual_trends
        for file_path in _REQUIRED_FILES:
            full_path = tmp_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if file_path == "metadata.json":
                full_path.write_text(json.dumps({
                    "total_incidents": 100000,
                    "date_start": "2006-01-01",
                    "date_end": "2024-12-31",
                    "last_updated": "2025-01-15T10:30:00Z",
                    "source": "Philadelphia Police Department",
                    "colors": {"crime": "#FF5733"},
                }))
            elif file_path == "annual_trends.json":
                full_path.write_text(json.dumps([]))  # Empty list
            elif file_path == "forecast.json":
                full_path.write_text(json.dumps({
                    "historical": [{"date": "2023-01-01", "value": 100}],
                    "forecast": [{"date": "2024-01-01", "value": 110}],
                }))
            else:
                full_path.write_text("{}")

        with pytest.raises(RuntimeError, match="annual_trends.json must be a non-empty list"):
            _validate_artifacts(tmp_path)

    def test_validate_artifacts_raises_invalid_forecast_structure(self, tmp_path: Path) -> None:
        """Should raise RuntimeError when forecast.json missing historical/forecast."""
        # Create all files with invalid forecast structure
        for file_path in _REQUIRED_FILES:
            full_path = tmp_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if file_path == "metadata.json":
                full_path.write_text(json.dumps({
                    "total_incidents": 100000,
                    "date_start": "2006-01-01",
                    "date_end": "2024-12-31",
                    "last_updated": "2025-01-15T10:30:00Z",
                    "source": "Philadelphia Police Department",
                    "colors": {"crime": "#FF5733"},
                }))
            elif file_path == "annual_trends.json":
                full_path.write_text(json.dumps([{"year": 2020, "incidents": 10000}]))
            elif file_path == "forecast.json":
                full_path.write_text(json.dumps({"only": "historical"}))  # Missing forecast key
            else:
                full_path.write_text("{}")

        with pytest.raises(RuntimeError, match="forecast.json must contain historical and forecast fields"):
            _validate_artifacts(tmp_path)
