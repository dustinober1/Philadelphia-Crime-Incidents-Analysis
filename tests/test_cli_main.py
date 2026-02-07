"""Integration tests for main CLI commands (version, info).

These tests use typer.testing.CliRunner to invoke CLI commands programmatically
and verify they execute successfully, produce expected output, and have correct
exit codes. These are the only main app commands not yet tested.

Usage:
    pytest tests/test_cli_main.py -v

Test classes:
    TestVersionCommand: Tests for the 'version' command
    TestInfoCommand: Tests for the 'info' command
    TestRichFormatting: Tests for Rich output formatting
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from typer.testing import CliRunner

if TYPE_CHECKING:
    pass

# Import the main CLI app
from analysis.cli.main import app

# Create CliRunner instance for all tests
runner = CliRunner()


class TestVersionCommand:
    """Tests for the 'version' command."""

    def test_version_command_basic(self) -> None:
        """Test basic execution of version command."""
        result = runner.invoke(app, ["version"])

        # Verify command executed successfully
        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify expected output content
        assert "CLI Version" in result.stdout
        assert "typer" in result.stdout
        assert "Python" in result.stdout

    def test_version_command_table_structure(self) -> None:
        """Test version command output has table-like structure."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify table-like output format
        # Look for version numbers (e.g., "v1.1", "3.14+")
        assert "v1.1" in result.stdout or "v1" in result.stdout
        # Verify "Component" or similar column indicator
        assert "CLI" in result.stdout or "Component" in result.stdout

    def test_version_command_no_arguments_required(self) -> None:
        """Test that version command requires no parameters."""
        result = runner.invoke(app, ["version"])

        # Verify command executes successfully without additional arguments
        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Should not complain about missing arguments
        assert "Missing" not in result.stdout
        assert "required" not in result.stdout.lower()


class TestInfoCommand:
    """Tests for the 'info' command."""

    def test_info_command_basic(self) -> None:
        """Test basic execution of info command."""
        result = runner.invoke(app, ["info"])

        # Verify command executed successfully
        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify expected output content
        assert "Data sources:" in result.stdout
        assert "Analysis areas:" in result.stdout
        assert "Reports directory:" in result.stdout

    def test_info_command_data_sources_listed(self) -> None:
        """Test that info command lists all data sources."""
        result = runner.invoke(app, ["info"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify data sources are mentioned
        assert "Philadelphia Police Department" in result.stdout
        assert "U.S. Census Bureau" in result.stdout
        assert "City event schedules" in result.stdout

    def test_info_command_analysis_areas_listed(self) -> None:
        """Test that info command lists all analysis areas."""
        result = runner.invoke(app, ["info"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify analysis areas are mentioned
        assert "Chief:" in result.stdout
        assert "Patrol:" in result.stdout
        assert "Policy:" in result.stdout
        assert "Forecasting:" in result.stdout

    def test_info_command_resolved_reports_path(self) -> None:
        """Test that info command shows resolved reports path."""
        result = runner.invoke(app, ["info"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify path is displayed
        assert "Resolved path:" in result.stdout
        assert "reports/" in result.stdout


class TestRichFormatting:
    """Tests for Rich output formatting in version and info commands."""

    def test_version_uses_rich_table(self) -> None:
        """Test version command uses Rich table formatting."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify output contains table structure (columnar output)
        # Look for multiple lines with structured content
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 3, "Table output should have multiple lines"

        # Check for version numbers in the output
        assert any("v" in line or "Version" in line for line in lines), \
            "Table should contain version information"

    def test_info_uses_rich_panel(self) -> None:
        """Test info command uses Rich panel formatting."""
        result = runner.invoke(app, ["info"])

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify panel title is in output
        assert "Philadelphia Crime Incidents Analysis" in result.stdout

        # Verify structured content (bold markers or similar)
        assert "Data sources:" in result.stdout or "Data sources" in result.stdout
        assert "Analysis areas:" in result.stdout or "Analysis areas" in result.stdout

    def test_both_commands_no_error_output(self) -> None:
        """Test both commands execute without errors."""
        # Test version command
        version_result = runner.invoke(app, ["version"])
        assert version_result.exit_code == 0, f"Version command failed: {version_result.output}"

        # Verify no error messages in output
        assert "Error" not in version_result.stdout
        assert "Exception" not in version_result.stdout
        assert "Traceback" not in version_result.stdout

        # Test info command
        info_result = runner.invoke(app, ["info"])
        assert info_result.exit_code == 0, f"Info command failed: {info_result.output}"

        # Verify no error messages in output
        assert "Error" not in info_result.stdout
        assert "Exception" not in info_result.stdout
        assert "Traceback" not in info_result.stdout
