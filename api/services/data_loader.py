"""Load and cache exported JSON/GeoJSON payloads for API handlers."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REQUIRED_EXPORTS = [
    "annual_trends.json",
    "annual_trends_district.json",  # District-scoped annual trends (03-06)
    "classification_features.json",
    "covid_comparison.json",
    "crime_composition.json",
    "event_impact.json",
    "forecast.json",
    "metadata.json",
    "monthly_trends.json",
    "monthly_trends_district.json",  # District-scoped monthly trends (03-06)
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

_DATA_CACHE: dict[str, Any] = {}
_LAST_DATA_DIR: Path = DATA_DIR


def _resolve_data_dir(data_dir: Path | None = None) -> Path:
    if data_dir is not None:
        return data_dir
    raw = os.getenv("API_DATA_DIR")
    return Path(raw) if raw else DATA_DIR


def _missing_required_exports(root: Path) -> list[str]:
    return [relative for relative in REQUIRED_EXPORTS if not (root / relative).exists()]


def _validate_data_contract(root: Path) -> None:
    if not root.exists() or not root.is_dir():
        raise RuntimeError(
            f"API data directory does not exist: {root}. "
            "Set API_DATA_DIR to the shared pipeline export location."
        )
    missing = _missing_required_exports(root)
    if missing:
        raise RuntimeError(
            "Missing required pipeline exports in API data directory: "
            + ", ".join(missing)
        )


def load_all_data(data_dir: Path | None = None) -> dict[str, Any]:
    """Load exported files from disk into in-memory cache."""
    root = _resolve_data_dir(data_dir)
    _validate_data_contract(root)

    payloads: dict[str, Any] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(root))
        if path.suffix in {".json", ".geojson"}:
            payloads[rel] = json.loads(path.read_text(encoding="utf-8"))
    _DATA_CACHE.clear()
    _DATA_CACHE.update(payloads)
    global _LAST_DATA_DIR
    _LAST_DATA_DIR = root
    return _DATA_CACHE


def get_data(key: str) -> Any:
    """Fetch cached payload by relative path key."""
    if key not in _DATA_CACHE:
        raise KeyError(f"Data key not loaded: {key}")
    return _DATA_CACHE[key]


def cache_keys() -> list[str]:
    """Return loaded cache keys for diagnostics."""
    return sorted(_DATA_CACHE.keys())


def contract_status(data_dir: Path | None = None) -> dict[str, Any]:
    """Return current contract health for API readiness checks."""
    root = _resolve_data_dir(data_dir)
    missing = _missing_required_exports(root) if root.exists() else REQUIRED_EXPORTS
    return {
        "ok": len(missing) == 0,
        "data_dir": str(root),
        "missing_exports": missing,
        "last_loaded_dir": str(_LAST_DATA_DIR),
    }
