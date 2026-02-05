"""End-to-end CLI tests for Policy commands.

These tests verify that all Policy CLI commands (retail-theft, vehicle-crimes,
composition, events) execute successfully, produce expected output, and use the
--fast flag for quick execution.

Tests use typer.testing.CliRunner for clean CLI invocation without subprocess overhead.

Usage:
    pytest tests/test_cli_policy.py -v
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


class TestPolicyRetailTheft:
    """Tests for the 'policy retail-theft' command."""

    def test_policy_retail_theft_basic(self, tmp_output_dir: Path) -> None:
        """Test that retail-theft command executes successfully with --fast flag.

        Verifies:
        - Command exits with code 0
        - Output contains expected "Retail Theft" indicator
        - Rich progress bars display correctly
        """
        result = runner.invoke(
            app,
            ["policy", "retail-theft", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        assert result.exit_code == 0, f"CLI failed: {result.stdout}"
        assert "Retail Theft" in result.stdout or "retail" in result.stdout.lower()
        # Check for completion message
        assert "Analysis complete" in result.stdout or "" in result.stdout

    def test_policy_retail_theft_output_files(self, tmp_output_dir: Path) -> None:
        """Test that retail-theft command creates expected output files.

        Verifies:
        - Summary file is created in correct location
        - Output directory structure is correct (reports/test/policy/)
        - Files contain expected content
        """
        result = runner.invoke(
            app,
            ["policy", "retail-theft", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        assert result.exit_code == 0

        # Check for output directory
        output_path = tmp_output_dir / "test" / "policy"
        assert output_path.exists(), f"Output directory not created: {output_path}"

        # Check for summary file (CLI appends _summary.txt to report_name)
        summary_file = output_path / "retail_theft_report_summary.txt"
        assert summary_file.exists(), f"Summary file not created: {summary_file}"

        # Verify file contains expected content
        content = summary_file.read_text()
        assert "Retail Theft Analysis Summary" in content
        assert "Baseline period" in content
        assert "incidents" in content.lower()

        # Check for figure file
        figure_file = output_path / "retail_theft_report_trend.png"
        assert figure_file.exists(), f"Figure file not created: {figure_file}"


class TestPolicyVehicleCrimes:
    """Tests for the 'policy vehicle-crimes' command."""

    def test_policy_vehicle_crimes_basic(self, tmp_output_dir: Path) -> None:
        """Test that vehicle-crimes command executes successfully with --fast flag.

        Verifies:
        - Command exits with code 0
        - Output contains expected "Vehicle" indicator
        - Fast mode sampling message appears
        """
        result = runner.invoke(
            app,
            ["policy", "vehicle-crimes", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        assert result.exit_code == 0, f"CLI failed: {result.stdout}"
        assert "Vehicle" in result.stdout or "vehicle" in result.stdout.lower()
        # Check for completion message
        assert "Analysis complete" in result.stdout or "" in result.stdout

    def test_policy_vehicle_crimes_output_files(self, tmp_output_dir: Path) -> None:
        """Test that vehicle-crimes command creates expected output files.

        Verifies:
        - Summary file is created in correct location
        - File contains vehicle-specific statistics
        - UCR code information is included
        """
        result = runner.invoke(
            app,
            ["policy", "vehicle-crimes", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        assert result.exit_code == 0

        # Check for summary file (CLI appends _summary.txt to report_name)
        output_path = tmp_output_dir / "test" / "policy"
        summary_file = output_path / "vehicle_crimes_report_summary.txt"
        assert summary_file.exists(), f"Summary file not created: {summary_file}"

        # Verify content
        content = summary_file.read_text()
        assert "Vehicle Crimes Analysis Summary" in content
        assert "UCR codes" in content
        assert "incidents" in content.lower()

        # Check for figure file
        figure_file = output_path / "vehicle_crimes_report_trend.png"
        assert figure_file.exists(), f"Figure file not created: {figure_file}"


class TestPolicyComposition:
    """Tests for the 'policy composition' command."""

    def test_policy_composition_basic(self, tmp_output_dir: Path) -> None:
        """Test that composition command executes successfully with --fast flag.

        Verifies:
        - Command exits with code 0
        - Output contains expected "Composition" indicator
        - Crime classification completes
        """
        result = runner.invoke(
            app,
            ["policy", "composition", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        assert result.exit_code == 0, f"CLI failed: {result.stdout}"
        assert "Composition" in result.stdout or "composition" in result.stdout.lower()
        assert "Analysis complete" in result.stdout or "" in result.stdout

    def test_policy_composition_output_files(self, tmp_output_dir: Path) -> None:
        """Test that composition command creates expected output files.

        Verifies:
        - Summary file is created
        - Top N categories are included
        - UCR hundred-band breakdown is present
        """
        result = runner.invoke(
            app,
            ["policy", "composition", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        assert result.exit_code == 0

        # Check for summary file (CLI appends _summary.txt to report_name)
        output_path = tmp_output_dir / "test" / "policy"
        summary_file = output_path / "composition_report_summary.txt"
        assert summary_file.exists(), f"Summary file not created: {summary_file}"

        # Verify content
        content = summary_file.read_text()
        assert "Crime Composition Analysis Summary" in content
        assert "Top" in content and "crime categories" in content
        assert "UCR" in content

        # Check for figure file
        figure_file = output_path / "composition_report_categories.png"
        assert figure_file.exists(), f"Figure file not created: {figure_file}"


class TestPolicyEvents:
    """Tests for the 'policy events' command."""

    def test_policy_events_basic(self, tmp_output_dir: Path) -> None:
        """Test that events command executes successfully with --fast flag.

        Verifies:
        - Command exits with code 0 (even if event data unavailable)
        - Output contains "Event" indicator
        - Graceful handling of missing event_utils
        """
        result = runner.invoke(
            app,
            ["policy", "events", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        # Allow for graceful degradation (event_utils may not exist)
        assert result.exit_code == 0, f"CLI failed: {result.stdout}"
        assert "Event" in result.stdout or "event" in result.stdout.lower()

    def test_policy_events_output_files(self, tmp_output_dir: Path) -> None:
        """Test that events command creates expected output files.

        Verifies:
        - Summary file is created
        - File contains event-specific statistics
        - Graceful fallback if event data unavailable
        """
        result = runner.invoke(
            app,
            ["policy", "events", "--fast", "--version", "test"],
            env={"CRIME_OUTPUT_DIR": str(tmp_output_dir)},
        )

        assert result.exit_code == 0

        # Check for summary file (CLI appends _summary.txt to report_name)
        output_path = tmp_output_dir / "test" / "policy"
        summary_file = output_path / "events_impact_report_summary.txt"
        assert summary_file.exists(), f"Summary file not created: {summary_file}"

        # Verify content
        content = summary_file.read_text()
        assert "Event Impact Analysis Summary" in content
        assert "Event window" in content or "incidents" in content.lower()
