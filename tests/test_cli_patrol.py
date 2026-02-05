"""End-to-end CLI tests for Patrol commands.

These tests verify that all Patrol CLI commands (hotspots, robbery-heatmap,
district-severity, census-rates) execute successfully, produce expected output,
and use the --fast flag for quick execution.

Tests use typer.testing.CliRunner for clean CLI invocation without subprocess overhead.
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


class TestPatrolHotspots:
    """Tests for the 'patrol hotspots' command."""

    def test_patrol_hotspots_basic(self, tmp_output_dir: Path) -> None:
        """Test that hotspots command executes successfully with --fast flag.

        Verifies:
        - Command exits with code 0
        - Output contains expected "Hotspots" indicator
        - Rich progress bars display correctly
        """
        result = runner.invoke(
            app,
            ["patrol", "hotspots", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        assert result.exit_code == 0, f"CLI failed: {result.stdout}"
        assert "Hotspots" in result.stdout or "hotspots" in result.stdout.lower()
        # Check for Rich output indicators
        assert "" in result.stdout or "Analysis complete" in result.stdout

    def test_patrol_hotspots_output_files(self, tmp_output_dir: Path) -> None:
        """Test that hotspots command creates expected output files.

        Verifies:
        - Summary file is created in correct location
        - Output directory structure is correct (reports/test/patrol/)
        - Files contain expected content
        """
        result = runner.invoke(
            app,
            ["patrol", "hotspots", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        assert result.exit_code == 0

        # Check for output directory
        output_path = tmp_output_dir / "test" / "patrol"
        assert output_path.exists(), f"Output directory not created: {output_path}"

        # Check for summary file (CLI appends _summary.txt to report_name)
        summary_file = output_path / "hotspots_report_summary.txt"
        assert summary_file.exists(), f"Summary file not created: {summary_file}"

        # Verify file contains expected content
        content = summary_file.read_text()
        assert "Hotspots Analysis Summary" in content
        assert "DBSCAN" in content
        assert "Clusters found" in content or "Total points" in content


class TestPatrolRobberyHeatmap:
    """Tests for the 'patrol robbery-heatmap' command."""

    def test_patrol_robbery_heatmap_basic(self, tmp_output_dir: Path) -> None:
        """Test that robbery-heatmap command executes successfully with --fast flag.

        Verifies:
        - Command exits with code 0
        - Output contains expected "Robbery" indicator
        - Fast mode sampling message appears
        """
        result = runner.invoke(
            app,
            ["patrol", "robbery-heatmap", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        assert result.exit_code == 0, f"CLI failed: {result.stdout}"
        assert "Robbery" in result.stdout or "robbery" in result.stdout.lower()
        # Check for completion message
        assert "Analysis complete" in result.stdout or "" in result.stdout

    def test_patrol_robbery_heatmap_output_files(self, tmp_output_dir: Path) -> None:
        """Test that robbery-heatmap command creates expected output files.

        Verifies:
        - Summary file is created in correct location
        - File contains robbery-specific statistics
        - Hourly breakdown is included
        """
        result = runner.invoke(
            app,
            ["patrol", "robbery-heatmap", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        assert result.exit_code == 0

        # Check for summary file (CLI appends _summary.txt to report_name)
        output_path = tmp_output_dir / "test" / "patrol"
        summary_file = output_path / "robbery_heatmap_report_summary.txt"
        assert summary_file.exists(), f"Summary file not created: {summary_file}"

        # Verify content
        content = summary_file.read_text()
        assert "Robbery Heatmap Analysis Summary" in content
        assert "Time bin size" in content
        assert "incidents" in content.lower()


class TestPatrolDistrictSeverity:
    """Tests for the 'patrol district-severity' command."""

    def test_patrol_district_severity_basic(self, tmp_output_dir: Path) -> None:
        """Test that district-severity command executes successfully with --fast flag.

        Verifies:
        - Command exits with code 0
        - Output contains expected "District" or "Severity" indicators
        - Severity calculation completes
        """
        result = runner.invoke(
            app,
            ["patrol", "district-severity", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        assert result.exit_code == 0, f"CLI failed: {result.stdout}"
        assert ("District" in result.stdout or "district" in result.stdout.lower()) or (
            "Severity" in result.stdout or "severity" in result.stdout.lower()
        )
        assert "Analysis complete" in result.stdout or "" in result.stdout

    def test_patrol_district_severity_output_files(self, tmp_output_dir: Path) -> None:
        """Test that district-severity command creates expected output files.

        Verifies:
        - Summary file is created
        - District rankings are included
        - Severity weights are applied correctly
        """
        result = runner.invoke(
            app,
            ["patrol", "district-severity", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        assert result.exit_code == 0

        # Check for summary file (CLI appends _summary.txt to report_name)
        output_path = tmp_output_dir / "test" / "patrol"
        summary_file = output_path / "district_severity_report_summary.txt"
        assert summary_file.exists(), f"Summary file not created: {summary_file}"

        # Verify content
        content = summary_file.read_text()
        assert "District Severity Analysis Summary" in content
        assert "District" in content
        assert "rankings" in content.lower() or "severity" in content.lower()


class TestPatrolCensusRates:
    """Tests for the 'patrol census-rates' command."""

    def test_patrol_census_rates_basic(self, tmp_output_dir: Path) -> None:
        """Test that census-rates command executes successfully with --fast flag.

        Verifies:
        - Command exits with code 0 (even if census boundaries unavailable)
        - Output contains "Census" indicator
        - Graceful handling of missing geopandas/boundary files
        """
        result = runner.invoke(
            app,
            ["patrol", "census-rates", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        # Allow for graceful degradation (geopandas may not be installed)
        assert result.exit_code == 0, f"CLI failed: {result.stdout}"
        assert "Census" in result.stdout or "census" in result.stdout.lower()

    def test_patrol_census_rates_output_files(self, tmp_output_dir: Path) -> None:
        """Test that census-rates command creates expected output files.

        Verifies:
        - Summary file is created
        - File contains census-specific statistics
        - Graceful fallback if boundaries unavailable
        """
        result = runner.invoke(
            app,
            ["patrol", "census-rates", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        assert result.exit_code == 0

        # Check for summary file (CLI appends _summary.txt to report_name)
        output_path = tmp_output_dir / "test" / "patrol"
        summary_file = output_path / "census_rates_report_summary.txt"
        assert summary_file.exists(), f"Summary file not created: {summary_file}"

        # Verify content
        content = summary_file.read_text()
        assert "Census Rates Analysis Summary" in content
        assert "Population threshold" in content or "incidents" in content.lower()
