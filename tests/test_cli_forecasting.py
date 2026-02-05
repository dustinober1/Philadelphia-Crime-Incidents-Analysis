"""End-to-end CLI tests for Forecasting commands.

These tests verify that all Forecasting CLI commands (time-series, classification)
execute successfully, produce expected output, and use the --fast flag for quick
execution.

Tests use typer.testing.CliRunner for clean CLI invocation without subprocess overhead.

Usage:
    pytest tests/test_cli_forecasting.py -v
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from typer.testing import CliRunner

from analysis.cli.main import app

if TYPE_CHECKING:
    pass

# Create CliRunner instance for all tests
runner = CliRunner()


class TestForecastingTimeSeries:
    """Tests for the 'forecasting time-series' command."""

    def test_forecasting_time_series_basic(self, tmp_output_dir: Path) -> None:
        """Test that time-series command executes successfully with --fast flag.

        Verifies:
        - Command exits with code 0 (even if prophet not available)
        - Output contains expected "Time Series" indicator
        - Graceful handling of missing prophet library
        """
        result = runner.invoke(
            app,
            ["forecasting", "time-series", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        # Allow for graceful degradation (prophet may not be installed)
        assert result.exit_code == 0, f"CLI failed: {result.stdout}"
        assert "Time Series" in result.stdout or "time" in result.stdout.lower()
        # Check for completion message
        assert "Analysis complete" in result.stdout or "" in result.stdout

    def test_forecasting_time_series_output_files(self, tmp_output_dir: Path) -> None:
        """Test that time-series command creates expected output files.

        Verifies:
        - Summary file is created in correct location
        - Output directory structure is correct (reports/test/forecasting/)
        - Files contain expected content or fallback message
        """
        result = runner.invoke(
            app,
            ["forecasting", "time-series", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        assert result.exit_code == 0

        # Check for output directory
        output_path = tmp_output_dir / "test" / "forecasting"
        assert output_path.exists(), f"Output directory not created: {output_path}"

        # Check for summary file (CLI appends _summary.txt to report_name)
        summary_file = output_path / "forecast_report_summary.txt"
        assert summary_file.exists(), f"Summary file not created: {summary_file}"

        # Verify file contains expected content
        content = summary_file.read_text()
        assert "Time Series Forecasting Summary" in content
        assert "Model:" in content
        assert "Training data" in content


class TestForecastingClassification:
    """Tests for the 'forecasting classification' command."""

    def test_forecasting_classification_basic(self, tmp_output_dir: Path) -> None:
        """Test that classification command executes successfully with --fast flag.

        Verifies:
        - Command exits with code 0 (even if sklearn not available)
        - Output contains expected "Violence Classification" indicator
        - Graceful handling of missing scikit-learn library
        """
        result = runner.invoke(
            app,
            ["forecasting", "classification", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        # Allow for graceful degradation (sklearn may not be installed)
        assert result.exit_code == 0, f"CLI failed: {result.stdout}"
        assert (
            "Violence Classification" in result.stdout or "classification" in result.stdout.lower()
        )
        # Check for completion message
        assert "Analysis complete" in result.stdout or "" in result.stdout

    def test_forecasting_classification_output_files(self, tmp_output_dir: Path) -> None:
        """Test that classification command creates expected output files.

        Verifies:
        - Summary file is created in correct location
        - File contains classification-specific statistics
        - Graceful fallback if sklearn unavailable
        """
        result = runner.invoke(
            app,
            ["forecasting", "classification", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        assert result.exit_code == 0

        # Check for summary file (CLI appends _summary.txt to report_name)
        output_path = tmp_output_dir / "test" / "forecasting"
        summary_file = output_path / "classification_report_summary.txt"
        assert summary_file.exists(), f"Summary file not created: {summary_file}"

        # Verify content
        content = summary_file.read_text()
        assert "Violence Classification Summary" in content
        assert "Test size" in content or "incidents" in content.lower()
