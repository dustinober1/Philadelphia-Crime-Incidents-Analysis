"""Integration tests for CLI output verification.

These tests verify that CLI command outputs are structurally correct and contain
expected patterns. They validate that generated reports and figures have the
expected format without requiring exact pixel-perfect matches or exact data values.

Tests use the --version integration-test flag to isolate outputs from test runs
and avoid cluttering production reports directories.

Usage:
    pytest tests/test_integration_output_verification.py -v -m integration
    pytest tests/ -v -m integration

Test patterns:
    - Verify output directory structure exists
    - Verify expected files are created (not exact content)
    - Verify files contain expected headers/keywords (pattern matching)
    - Use tolerance for numeric values, not exact matches
    - Handle optional dependencies gracefully with pytest.importorskip
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from analysis.cli.main import app

if TYPE_CHECKING:
    pass

# Create CliRunner instance for all tests
runner = CliRunner()


@pytest.mark.integration
class TestChiefTrendsOutput:
    """Integration tests for 'chief trends' output structure."""

    def test_chief_trends_output_structure(self) -> None:
        """Verify chief trends command creates expected output structure.

        Checks:
        - Output directory exists: reports/integration-test/chief/
        - Summary file exists: annual_trends_report_summary.txt
        - Summary file contains expected headers and keywords

        Does NOT check:
        - Exact data values (may vary with sample size)
        - Pixel-perfect image comparison
        """
        result = runner.invoke(
            app,
            ["chief", "trends", "--fast", "--version", "integration-test"],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify output directory exists
        output_dir = Path("reports/integration-test/chief")
        assert output_dir.exists(), f"Output directory not created: {output_dir}"

        # Verify summary file exists
        summary_file = output_dir / "annual_trends_report_summary.txt"
        assert summary_file.exists(), f"Summary file not created: {summary_file}"

        # Verify file contains expected patterns (not exact content)
        content = summary_file.read_text()
        assert "Annual Trends" in content or "Annual Crime Trends" in content
        assert "Total incidents" in content or "incidents" in content.lower()
        assert "2015" in content or "2024" in content  # Verify period is included


@pytest.mark.integration
class TestPatrolHotspotsOutput:
    """Integration tests for 'patrol hotspots' output structure."""

    def test_patrol_hotspots_output_structure(self) -> None:
        """Verify patrol hotspots command creates expected output structure.

        Checks:
        - Output directory exists: reports/integration-test/patrol/
        - At least one output file exists (PNG or TXT)
        - Summary contains expected keywords

        Does NOT check:
        - Exact cluster counts (may vary with algorithm parameters)
        - Exact coordinate values
        """
        result = runner.invoke(
            app,
            ["patrol", "hotspots", "--fast", "--version", "integration-test"],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify output directory exists
        output_dir = Path("reports/integration-test/patrol")
        assert output_dir.exists(), f"Output directory not created: {output_dir}"

        # Verify at least one output file exists
        summary_file = output_dir / "hotspots_report_summary.txt"
        assert summary_file.exists(), f"Summary file not created: {summary_file}"

        # Verify file contains expected patterns
        content = summary_file.read_text()
        assert "Hotspots" in content or "hotspots" in content.lower() or "Cluster" in content
        assert "incidents" in content.lower() or "points" in content.lower()


@pytest.mark.integration
class TestPolicyRetailTheftOutput:
    """Integration tests for 'policy retail-theft' output structure."""

    def test_policy_retail_theft_output_structure(self) -> None:
        """Verify policy retail-theft command creates expected output structure.

        Checks:
        - Output directory exists: reports/integration-test/policy/
        - Summary file exists
        - Summary contains retail theft specific keywords

        Does NOT check:
        - Exact incident counts
        - Exact percentage changes
        """
        result = runner.invoke(
            app,
            ["policy", "retail-theft", "--fast", "--version", "integration-test"],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify output directory exists
        output_dir = Path("reports/integration-test/policy")
        assert output_dir.exists(), f"Output directory not created: {output_dir}"

        # Verify summary file exists
        summary_file = output_dir / "retail_theft_report_summary.txt"
        assert summary_file.exists(), f"Summary file not created: {summary_file}"

        # Verify file contains expected patterns
        content = summary_file.read_text()
        assert "Retail Theft" in content or "retail" in content.lower()
        assert "Baseline" in content or "period" in content.lower()
        assert "incidents" in content.lower()


@pytest.mark.integration
class TestForecastingClassificationOutput:
    """Integration tests for 'forecasting classification' output structure."""

    def test_forecasting_classification_output_structure(self) -> None:
        """Verify forecasting classification command creates expected output structure.

        Checks:
        - Output directory exists: reports/integration-test/forecasting/
        - Model metrics file exists
        - Metrics file contains model evaluation keywords

        Does NOT check:
        - Exact accuracy/precision/f1 scores (may vary with sampling)
        - Exact feature importance values

        Note: Skips if sklearn is not available (handled gracefully by CLI).
        """
        # Check if sklearn is available
        pytest.importorskip("sklearn", reason="sklearn not installed, skipping classification test")

        result = runner.invoke(
            app,
            ["forecasting", "classification", "--fast", "--version", "integration-test"],
        )

        # CLI may exit with 0 even if sklearn issues a warning
        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify output directory exists
        output_dir = Path("reports/integration-test/forecasting")
        assert output_dir.exists(), f"Output directory not created: {output_dir}"

        # Verify model metrics file exists
        # CLI appends _summary.txt to report_name
        metrics_file = output_dir / "classification_report_summary.txt"
        assert metrics_file.exists(), f"Metrics file not created: {metrics_file}"

        # Verify file contains expected patterns
        content = metrics_file.read_text()
        assert (
            "classification" in content.lower()
            or "violence" in content.lower()
            or "model" in content.lower()
        )


@pytest.mark.integration
class TestCLIOutputIsolation:
    """Integration tests verifying output isolation via --version flag."""

    def test_version_flag_creates_separate_directories(self) -> None:
        """Verify --version flag creates isolated output directories.

        Checks:
        - Different version values create different directories
        - Integration-test outputs are separate from production outputs
        """
        # Run with integration-test version
        result1 = runner.invoke(
            app,
            ["chief", "seasonality", "--fast", "--version", "integration-test"],
        )
        assert result1.exit_code == 0

        # Run with a different version
        result2 = runner.invoke(
            app,
            ["chief", "seasonality", "--fast", "--version", "isolation-test"],
        )
        assert result2.exit_code == 0

        # Verify both directories exist separately
        dir1 = Path("reports/integration-test/chief")
        dir2 = Path("reports/isolation-test/chief")
        assert dir1.exists(), f"Integration-test directory not created: {dir1}"
        assert dir2.exists(), f"Isolation-test directory not created: {dir2}"

        # Verify each has its own output file
        file1 = dir1 / "seasonality_report_summary.txt"
        file2 = dir2 / "seasonality_report_summary.txt"
        assert file1.exists(), f"Integration-test summary not created: {file1}"
        assert file2.exists(), f"Isolation-test summary not created: {file2}"
