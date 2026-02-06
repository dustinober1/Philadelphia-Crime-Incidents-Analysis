"""Tests for pipeline exporter."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from typer.testing import CliRunner

from pipeline.export_data import app


runner = CliRunner()


def test_export_output_dir_option(tmp_path: Path) -> None:
    output_dir = tmp_path / "api_data"
    result = runner.invoke(app, ["--output-dir", str(output_dir)])
    assert result.exit_code == 0
    assert (output_dir / "metadata.json").exists()
    assert (output_dir / "annual_trends.json").exists()
