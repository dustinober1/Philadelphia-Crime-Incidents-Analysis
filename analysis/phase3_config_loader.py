"""Configuration loader for Phase 3 analyses."""

from pathlib import Path
from typing import Any

import yaml


class Phase3Config:
    """Load and access Phase 3 configuration parameters."""

    def __init__(self, config_path: Path = None):
        if config_path is None:
            repo_root = Path(__file__).resolve().parent.parent
            config_path = repo_root / "config" / "phase3_config.yaml"

        with open(config_path) as f:
            self._config = yaml.safe_load(f)

    @property
    def retail_theft(self) -> dict[str, Any]:
        """Get retail theft analysis configuration."""
        return self._config.get("retail_theft", {})

    @property
    def vehicle_crimes(self) -> dict[str, Any]:
        """Get vehicle crimes analysis configuration."""
        return self._config.get("vehicle_crimes", {})

    @property
    def crime_composition(self) -> dict[str, Any]:
        """Get crime composition analysis configuration."""
        return self._config.get("crime_composition", {})

    @property
    def events(self) -> dict[str, Any]:
        """Get event impact analysis configuration."""
        return self._config.get("events", {})

    @property
    def corridors(self) -> dict[str, Any]:
        """Get corridor overlay configuration."""
        return self._config.get("corridors", {})

    @property
    def coordinate_bounds(self) -> dict[str, float]:
        """Get Philadelphia coordinate bounds."""
        return self._config.get("coordinate_bounds", {})

    @property
    def version(self) -> str:
        """Get config version."""
        return self._config.get("version", "unknown")
