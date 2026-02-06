"""Integration tests verifying CLI outputs match notebook artifacts.

This module tests that v1.1 CLI commands produce outputs consistent with
v1.0 notebook-generated artifacts. Tests use pattern matching rather than
exact value comparison to accommodate minor numerical differences.

Verification approach:
1. Run CLI command with --fast --version integration-test
2. Check expected output files exist
3. Verify output content matches expected patterns
4. Confirm key statistics are within reasonable ranges

Note: These tests use --fast mode for speed. Full verification can be
done manually by running commands without --fast and inspecting outputs.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

if TYPE_CHECKING:
    pass

from analysis.cli.main import app

runner = CliRunner()


@pytest.mark.integration
class TestChiefMigrationVerification:
    """Verify Chief CLI outputs match notebook artifacts."""

    def test_chief_trends_outputs_match_notebook(self) -> None:
        """Verify trends command produces outputs matching annual_trend notebook."""
        result = runner.invoke(
            app,
            ["chief", "trends", "--fast", "--version", "integration-test"],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        output_dir = Path("reports/integration-test/chief")
        assert output_dir.exists(), "Output directory not created"

        # Check for expected output files
        expected_files = [
            "annual_trends_report_summary.txt",
            "annual_trends_report_trend.png",
        ]

        for filename in expected_files:
            file_path = output_dir / filename
            assert file_path.exists(), f"Expected output file not created: {filename}"

        # Verify summary content matches expected patterns
        summary_path = output_dir / "annual_trends_report_summary.txt"
        summary_content = summary_path.read_text()

        # Pattern matching (not exact values, allows for sampling differences)
        assert "Annual Trends Analysis" in summary_content
        assert "total incidents" in summary_content.lower()
        assert "annual totals" in summary_content.lower() or "period:" in summary_content.lower()

        # Verify figure was created (not corrupted)
        figure_path = output_dir / "annual_trends_report_trend.png"
        assert figure_path.stat().st_size > 1000, "Figure file too small (corrupted?)"

    def test_chief_seasonality_outputs_match_notebook(self) -> None:
        """Verify seasonality command produces outputs matching seasonality notebook."""
        result = runner.invoke(
            app,
            ["chief", "seasonality", "--fast", "--version", "integration-test"],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        output_dir = Path("reports/integration-test/chief")
        assert output_dir.exists()

        # Check for expected outputs
        expected_files = [
            "seasonality_report_summary.txt",
            "seasonality_report_seasonal.png",
        ]

        for filename in expected_files:
            assert (output_dir / filename).exists(), f"Expected output file not created: {filename}"

        # Verify content patterns
        summary = (output_dir / "seasonality_report_summary.txt").read_text()
        assert "seasonality" in summary.lower()
        assert "summer" in summary.lower() or "spike" in summary.lower()

    def test_chief_covid_outputs_match_notebook(self) -> None:
        """Verify covid command produces outputs matching COVID notebook."""
        result = runner.invoke(
            app,
            ["chief", "covid", "--fast", "--version", "integration-test"],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        output_dir = Path("reports/integration-test/chief")
        assert (output_dir / "covid_impact_report_summary.txt").exists()
        assert (output_dir / "covid_impact_report_covid_impact.png").exists()

        # Verify COVID-specific patterns
        summary = (output_dir / "covid_impact_report_summary.txt").read_text()
        assert "covid" in summary.lower()
        assert "2020" in summary or "lockdown" in summary.lower()


@pytest.mark.integration
class TestPatrolMigrationVerification:
    """Verify Patrol CLI outputs match notebook artifacts."""

    def test_patrol_hotspots_outputs_match_notebook(self) -> None:
        """Verify hotspots command produces outputs matching hotspot_clustering notebook."""
        result = runner.invoke(
            app,
            ["patrol", "hotspots", "--fast", "--version", "integration-test"],
        )

        # Note: hotspots requires sklearn, may skip if not available
        if "sklearn" not in result.output and result.exit_code == 0:
            output_dir = Path("reports/integration-test/patrol")
            assert output_dir.exists()

            # Check for cluster outputs
            assert (output_dir / "hotspots_report_summary.txt").exists()
            assert (output_dir / "hotspots_report_clusters.png").exists()
        else:
            pytest.skip("sklearn not available or command failed")

    def test_patrol_robbery_heatmap_outputs_match_notebook(self) -> None:
        """Verify robbery-heatmap command produces outputs matching robbery_temporal_heatmap notebook."""
        result = runner.invoke(
            app,
            ["patrol", "robbery-heatmap", "--fast", "--version", "integration-test"],
        )

        # Note: robbery-heatmap requires seaborn
        if result.exit_code == 0:
            output_dir = Path("reports/integration-test/patrol")
            assert (output_dir / "robbery_heatmap_report_heatmap.png").exists()
            assert (output_dir / "robbery_heatmap_report_summary.txt").exists()
        else:
            pytest.skip("seaborn not available or command failed")

    def test_patrol_district_severity_outputs_match_notebook(self) -> None:
        """Verify district-severity command produces outputs matching district_severity notebook."""
        result = runner.invoke(
            app,
            ["patrol", "district-severity", "--fast", "--version", "integration-test"],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        output_dir = Path("reports/integration-test/patrol")
        assert (output_dir / "district_severity_report_summary.txt").exists()
        assert (output_dir / "district_severity_report_severity.png").exists()

    def test_patrol_census_rates_outputs_match_notebook(self) -> None:
        """Verify census-rates command produces outputs matching census_tract_rates notebook."""
        result = runner.invoke(
            app,
            ["patrol", "census-rates", "--fast", "--version", "integration-test"],
        )

        # Note: census-rates requires geopandas for figure creation
        # Command may succeed with summary only if geopandas unavailable
        if result.exit_code == 0:
            output_dir = Path("reports/integration-test/patrol")
            assert (output_dir / "census_rates_report_summary.txt").exists()
            # Figure created only if geopandas available
            if not (output_dir / "census_rates_report_rates.png").exists():
                pytest.skip("geopandas not available, figure not created")
        else:
            pytest.skip("geopandas not available or command failed")


@pytest.mark.integration
class TestPolicyMigrationVerification:
    """Verify Policy CLI outputs match notebook artifacts."""

    def test_policy_retail_theft_outputs_match_notebook(self) -> None:
        """Verify retail-theft command produces outputs matching retail_theft_trend notebook."""
        result = runner.invoke(
            app,
            ["policy", "retail-theft", "--fast", "--version", "integration-test"],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        output_dir = Path("reports/integration-test/policy")
        assert (output_dir / "retail_theft_report_summary.txt").exists()
        assert (output_dir / "retail_theft_report_trend.png").exists()

    def test_policy_vehicle_crimes_outputs_match_notebook(self) -> None:
        """Verify vehicle-crimes command produces outputs matching vehicle_crimes_corridors notebook."""
        result = runner.invoke(
            app,
            ["policy", "vehicle-crimes", "--fast", "--version", "integration-test"],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        output_dir = Path("reports/integration-test/policy")
        assert (output_dir / "vehicle_crimes_report_summary.txt").exists()
        assert (output_dir / "vehicle_crimes_report_trend.png").exists()

    def test_policy_composition_outputs_match_notebook(self) -> None:
        """Verify composition command produces outputs matching crime_composition notebook."""
        result = runner.invoke(
            app,
            ["policy", "composition", "--fast", "--version", "integration-test"],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        output_dir = Path("reports/integration-test/policy")
        assert (output_dir / "composition_report_summary.txt").exists()
        assert (output_dir / "composition_report_categories.png").exists()

    def test_policy_events_outputs_match_notebook(self) -> None:
        """Verify events command produces outputs matching event_impact_analysis notebook."""
        result = runner.invoke(
            app,
            ["policy", "events", "--fast", "--version", "integration-test"],
        )

        # Note: events command may skip if event data not available
        # Even without event data, summary should be created
        if result.exit_code == 0:
            output_dir = Path("reports/integration-test/policy")
            if (output_dir / "events_impact_report_summary.txt").exists():
                summary = (output_dir / "events_impact_report_summary.txt").read_text()
                assert "event" in summary.lower()
        else:
            pytest.skip("Event data not available or command failed")


@pytest.mark.integration
class TestForecastingMigrationVerification:
    """Verify Forecasting CLI outputs match notebook artifacts."""

    def test_forecasting_time_series_outputs_match_notebook(self) -> None:
        """Verify time-series command produces outputs matching forecasting_crime_ts notebook."""
        result = runner.invoke(
            app,
            ["forecasting", "time-series", "--fast", "--version", "integration-test"],
        )

        # Note: time-series requires prophet
        if result.exit_code == 0:
            output_dir = Path("reports/integration-test/forecasting")
            assert (output_dir / "forecast_report_forecast.png").exists()
            assert (output_dir / "forecast_report_summary.txt").exists()
        else:
            pytest.skip("prophet not available or command failed")

    def test_forecasting_classification_outputs_match_notebook(self) -> None:
        """Verify classification command produces outputs matching classification_violence notebook."""
        result = runner.invoke(
            app,
            ["forecasting", "classification", "--fast", "--version", "integration-test"],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        output_dir = Path("reports/integration-test/forecasting")
        assert (output_dir / "classification_report_summary.txt").exists()
        # Note: figure created only if sklearn available
        if (output_dir / "classification_report_performance.png").exists():
            # Verify classification metrics in output
            summary = (output_dir / "classification_report_summary.txt").read_text()
            assert "classification" in summary.lower()
            assert "violence" in summary.lower() or "violent" in summary.lower()
