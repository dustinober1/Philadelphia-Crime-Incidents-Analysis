"""Load and cache exported JSON/GeoJSON payloads for API handlers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_DATA_CACHE: dict[str, Any] = {}


def load_all_data(data_dir: Path | None = None) -> dict[str, Any]:
    """Load exported files from disk into in-memory cache."""
    root = data_dir or DATA_DIR
    payloads: dict[str, Any] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(root))
        if path.suffix in {".json", ".geojson"}:
            payloads[rel] = json.loads(path.read_text(encoding="utf-8"))
    _DATA_CACHE.clear()
    _DATA_CACHE.update(payloads)
    return _DATA_CACHE


def get_data(key: str) -> Any:
    """Fetch cached payload by relative path key."""
    if key not in _DATA_CACHE:
        raise KeyError(f"Data key not loaded: {key}")
    return _DATA_CACHE[key]


def cache_keys() -> list[str]:
    """Return loaded cache keys for diagnostics."""
    return sorted(_DATA_CACHE.keys())
