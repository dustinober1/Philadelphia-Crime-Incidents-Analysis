"""Refresh and validate API export artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import typer

from pipeline.export_data import export_all

app = typer.Typer(help="Refresh API data exports and validate artifact integrity.")

_REQUIRED_FILES = [
    "annual_trends.json",
    "classification_features.json",
    "covid_comparison.json",
    "crime_composition.json",
    "event_impact.json",
    "forecast.json",
    "metadata.json",
    "monthly_trends.json",
    "retail_theft_trend.json",
    "robbery_heatmap.json",
    "seasonality.json",
    "spatial_summary.json",
    "vehicle_crime_trend.json",
    "geo/corridors.geojson",
    "geo/districts.geojson",
    "geo/hotspot_centroids.geojson",
    "geo/tracts.geojson",
]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_json(path: Path) -> str:
    payload = _load_json(path)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _validate_artifacts(output_dir: Path) -> None:
    missing = [relative for relative in _REQUIRED_FILES if not (output_dir / relative).exists()]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing required export files: {joined}")

    metadata = _load_json(output_dir / "metadata.json")
    required_metadata_keys = {
        "total_incidents",
        "date_start",
        "date_end",
        "last_updated",
        "source",
        "colors",
    }
    if not required_metadata_keys.issubset(set(metadata.keys())):
        raise RuntimeError("metadata.json is missing required keys")

    annual = _load_json(output_dir / "annual_trends.json")
    if not isinstance(annual, list) or not annual:
        raise RuntimeError("annual_trends.json must be a non-empty list")

    forecast = _load_json(output_dir / "forecast.json")
    if not isinstance(forecast, dict) or "historical" not in forecast or "forecast" not in forecast:
        raise RuntimeError("forecast.json must contain historical and forecast fields")


def _assert_reproducible() -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        run_a = export_all(root / "run_a")
        run_b = export_all(root / "run_b")

        mismatches: list[str] = []
        for relative in _REQUIRED_FILES:
            path_a = run_a / relative
            path_b = run_b / relative
            if _canonical_json(path_a) != _canonical_json(path_b):
                mismatches.append(relative)
        if mismatches:
            joined = ", ".join(mismatches)
            raise RuntimeError(f"Reproducibility check failed for: {joined}")


@app.command()
def run(
    output_dir: Path = typer.Option(Path("api/data"), help="Output directory for exports"),
    verify_reproducibility: bool = typer.Option(
        False,
        "--verify-reproducibility",
        help="Run export twice and assert deterministic outputs",
    ),
) -> None:
    """Refresh API data and validate exported artifacts."""
    resolved = export_all(output_dir)
    _validate_artifacts(resolved)
    typer.echo(f"Validated exports: {resolved}")

    if verify_reproducibility:
        _assert_reproducible()
        typer.echo("Reproducibility check passed")


if __name__ == "__main__":
    app()
