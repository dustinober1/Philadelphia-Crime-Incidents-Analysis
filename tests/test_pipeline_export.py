"""Tests for pipeline exporter."""

from pathlib import Path

from typer.testing import CliRunner

from pipeline.export_data import app
from pipeline.refresh_data import app as refresh_app

runner = CliRunner()


def test_export_output_dir_option(tmp_path: Path) -> None:
    output_dir = tmp_path / "api_data"
    result = runner.invoke(app, ["--output-dir", str(output_dir)])
    assert result.exit_code == 0
    assert (output_dir / "metadata.json").exists()
    assert (output_dir / "annual_trends.json").exists()


def test_refresh_and_validate_command(tmp_path: Path) -> None:
    output_dir = tmp_path / "api_data"
    result = runner.invoke(refresh_app, ["--output-dir", str(output_dir)])
    assert result.exit_code == 0
    assert "Validated exports" in result.stdout
    assert (output_dir / "forecast.json").exists()
