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


class TestLoadJson:
    """Tests for _load_json helper."""

    def test_load_json_parses_valid_file(self, tmp_path: Path) -> None:
        """Should parse valid JSON file and return dict."""
        test_data = {"key": "value", "number": 42, "nested": {"a": 1}}
        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        result = _load_json(test_file)
        assert result == test_data
        assert result["key"] == "value"
        assert result["number"] == 42
        assert result["nested"]["a"] == 1

    def test_load_json_handles_unicode(self, tmp_path: Path) -> None:
        """Should handle Unicode characters in JSON."""
        test_data = {
            "emoji": "🚨 Crime Data",
            "international": "犯罪事件",
            "special_chars": "©®™£€¢¥",
        }
        test_file = tmp_path / "unicode.json"
        test_file.write_text(json.dumps(test_data), encoding="utf-8")

        result = _load_json(test_file)
        assert result["emoji"] == "🚨 Crime Data"
        assert result["international"] == "犯罪事件"
        assert result["special_chars"] == "©®™£€¢¥"


class TestCanonicalJson:
    """Tests for _canonical_json helper."""

    def test_canonical_json_sorts_keys(self, tmp_path: Path) -> None:
        """Should return JSON with sorted keys for comparison."""
        test_file = tmp_path / "test.json"
        # Create JSON with keys in random order
        test_file.write_text(json.dumps({"z": 1, "a": 2, "m": 3}))

        result = _canonical_json(test_file)
        # Keys should be sorted alphabetically
        assert result == '{"a":2,"m":3,"z":1}'

    def test_canonical_json_removes_whitespace(self, tmp_path: Path) -> None:
        """Should return compact JSON with no extra whitespace."""
        test_file = tmp_path / "test.json"
        # Create JSON with formatting
        test_data = {"key": "value", "nested": {"a": 1, "b": 2}}
        test_file.write_text(json.dumps(test_data, indent=2))

        result = _canonical_json(test_file)
        # Should have no extra whitespace
        assert "  " not in result  # No indentation spaces
        assert "\n" not in result  # No newlines


class TestAssertReproducible:
    """Tests for _assert_reproducible reproducibility verification."""

    @patch("pipeline.refresh_data.export_all")
    def test_assert_reproducible_passes_deterministic_exports(self, mock_export: patch, tmp_path: Path) -> None:
        """Should pass when export_all returns same data twice."""
        # Create deterministic export directory with same content
        run_dir = tmp_path / "run"
        run_dir.mkdir(parents=True, exist_ok=True)

        # Create identical files for both runs
        def mock_export_func(output_dir: Path) -> Path:
            for file_path in _REQUIRED_FILES:
                full_path = output_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                # Write deterministic content
                full_path.write_text('{"same":"data"}')
            return output_dir

        mock_export.side_effect = mock_export_func

        # Should not raise any exception
        _assert_reproducible()

        assert mock_export.call_count == 2

    @patch("pipeline.refresh_data.export_all")
    def test_assert_reproducible_detects_differences(self, mock_export: patch, tmp_path: Path) -> None:
        """Should raise RuntimeError when exports differ."""
        call_count = [0]

        def mock_export_func(output_dir: Path) -> Path:
            call_count[0] += 1
            for file_path in _REQUIRED_FILES:
                full_path = output_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                # Write different content on each call
                full_path.write_text(f'{{"run":{call_count[0]}}}')
            return output_dir

        mock_export.side_effect = mock_export_func

        with pytest.raises(RuntimeError, match="Reproducibility check failed"):
            _assert_reproducible()

        assert mock_export.call_count == 2

    @patch("pipeline.refresh_data.export_all")
    def test_assert_reproducible_compares_all_required_files(self, mock_export: patch, tmp_path: Path) -> None:
        """Should compare each file in _REQUIRED_FILES."""
        def mock_export_func(output_dir: Path) -> Path:
            # Create all required files
            for file_path in _REQUIRED_FILES:
                full_path = output_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text('{"data":"value"}')
            return output_dir

        mock_export.side_effect = mock_export_func

        # Should not raise when all files match
        _assert_reproducible()

        # Verify export_all was called twice
        assert mock_export.call_count == 2
