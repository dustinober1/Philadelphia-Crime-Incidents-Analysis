"""End-to-end CLI tests for Chief commands.

These tests use typer.testing.CliRunner to invoke CLI commands programmatically
and verify they execute successfully, produce expected output, and create correct
output files. All tests use the --fast flag to avoid loading the full dataset.

Usage:
    pytest tests/test_cli_chief.py -v

Test classes:
    TestChiefTrends: Tests for the 'chief trends' command
    TestChiefSeasonality: Tests for the 'chief seasonality' command
    TestChiefCovid: Tests for the 'chief covid' command
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from typer.testing import CliRunner

if TYPE_CHECKING:
    pass

# Import the main CLI app
from analysis.cli.main import app

# Create CliRunner instance for all tests
runner = CliRunner()


class TestChiefTrends:
    """Tests for the 'chief trends' command."""

    def test_chief_trends_basic(self, tmp_output_dir: Path) -> None:
        """Test basic execution of trends command with --fast flag."""
        result = runner.invoke(
            app,
            ["chief", "trends", "--fast", "--version", "test"],
        )

        # Verify command executed successfully
        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify expected output content
        assert "Annual Trends Analysis" in result.stdout
        assert "Analysis complete" in result.stdout
        assert "Total incidents analyzed:" in result.stdout

    def test_chief_trends_output_files(self, tmp_output_dir: Path) -> None:
        """Test that trends command creates expected output files."""
        result = runner.invoke(
            app,
            ["chief", "trends", "--fast", "--version", "test"],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check that output directory exists
        output_dir = Path("reports/test/chief")
        assert output_dir.exists(), f"Output directory not created: {output_dir}"

        # Check for expected output files
        expected_files = [
            "annual_trends_report_summary.txt",
            "annual_trends_report_trend.png",
        ]

        for filename in expected_files:
            file_path = output_dir / filename
            assert file_path.exists(), f"Expected output file not created: {file_path}"

    def test_chief_trends_output_format(self, tmp_output_dir: Path) -> None:
        """Test trends command with different output formats."""
        for fmt in ["png", "svg"]:
            result = runner.invoke(
                app,
                ["chief", "trends", "--output-format", fmt, "--fast", "--version", "test"],
            )
            assert result.exit_code == 0, f"Command failed for format {fmt}: {result.output}"

            # Check that figure file with correct extension exists
            figure_path = Path("reports/test/chief") / f"annual_trends_report_trend.{fmt}"
            assert figure_path.exists(), f"Figure not created for format {fmt}: {figure_path}"

    def test_chief_trends_date_range(self, tmp_output_dir: Path) -> None:
        """Test trends command with custom date range."""
        result = runner.invoke(
            app,
            [
                "chief",
                "trends",
                "--fast",
                "--start-year",
                "2018",
                "--end-year",
                "2020",
                "--version",
                "test",
            ],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify the period is reflected in output
        assert "2018" in result.stdout or "2020" in result.stdout


class TestChiefSeasonality:
    """Tests for the 'chief seasonality' command."""

    def test_chief_seasonality_basic(self, tmp_output_dir: Path) -> None:
        """Test basic execution of seasonality command with --fast flag."""
        result = runner.invoke(
            app,
            ["chief", "seasonality", "--fast", "--version", "test"],
        )

        # Verify command executed successfully
        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify expected output content
        assert "Seasonality Analysis" in result.stdout
        assert "Analysis complete" in result.stdout

    def test_chief_seasonality_output_files(self, tmp_output_dir: Path) -> None:
        """Test that seasonality command creates expected output files."""
        result = runner.invoke(
            app,
            ["chief", "seasonality", "--fast", "--version", "test"],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check that output directory exists
        output_dir = Path("reports/test/chief")
        assert output_dir.exists(), f"Output directory not created: {output_dir}"

        # Check for expected output files
        expected_files = [
            "seasonality_report_summary.txt",
            "seasonality_report_seasonal.png",
        ]

        for filename in expected_files:
            file_path = output_dir / filename
            assert file_path.exists(), f"Expected output file not created: {file_path}"


class TestChiefCovid:
    """Tests for the 'chief covid' command."""

    def test_chief_covid_basic(self, tmp_output_dir: Path) -> None:
        """Test basic execution of covid command with --fast flag."""
        result = runner.invoke(
            app,
            ["chief", "covid", "--fast", "--version", "test"],
        )

        # Verify command executed successfully
        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify expected output content
        assert "COVID Impact Analysis" in result.stdout
        assert "Analysis complete" in result.stdout

    def test_chief_covid_output_files(self, tmp_output_dir: Path) -> None:
        """Test that covid command creates expected output files."""
        result = runner.invoke(
            app,
            ["chief", "covid", "--fast", "--version", "test"],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check that output directory exists
        output_dir = Path("reports/test/chief")
        assert output_dir.exists(), f"Output directory not created: {output_dir}"

        # Check for expected output files
        expected_files = [
            "covid_impact_report_summary.txt",
            "covid_impact_report_covid_impact.png",
        ]

        for filename in expected_files:
            file_path = output_dir / filename
            assert file_path.exists(), f"Expected output file not created: {file_path}"
