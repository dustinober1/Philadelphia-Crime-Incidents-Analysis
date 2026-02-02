"""Configuration loader for Phase 1 analyses."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import yaml

DEFAULT_CONFIG_PATH = Path("config") / "phase1_config.yaml"
NOTEBOOKS = {"annual_trend", "seasonality", "covid"}


@dataclass(frozen=True)
class Phase1Config:
    """Load and validate Phase 1 configuration."""

    config_path: Path = DEFAULT_CONFIG_PATH
    data: Dict[str, Any] | None = None

    def __post_init__(self) -> None:
        config_path = self.config_path
        if not config_path.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")

        with config_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        self._validate(data)
        object.__setattr__(self, "data", data)

    def get_notebook_params(self, notebook_name: str) -> Dict[str, Any]:
        """Return parameters for a configured notebook.

        Parameters
        ----------
        notebook_name : str
            Notebook identifier (annual_trend, seasonality, covid).

        Returns
        -------
        dict
            Parameters for the requested notebook.
        """
        self._ensure_notebook(notebook_name)
        return dict(self.data[notebook_name]["params"])  # type: ignore[index]

    def get_output_path(
        self, notebook_name: str, artifact_type: str, version: str | None = None
    ) -> Path:
        """Return output path for a notebook artifact.

        Parameters
        ----------
        notebook_name : str
            Notebook identifier.
        artifact_type : str
            Artifact type key in the outputs section (png, report, etc.).
        version : str, optional
            Override version used for formatting.

        Returns
        -------
        pathlib.Path
            Path to the formatted output file.
        """
        self._ensure_notebook(notebook_name)
        outputs = self.data[notebook_name]["outputs"]  # type: ignore[index]
        if artifact_type not in outputs:
            raise KeyError(
                f"Artifact type '{artifact_type}' not defined for {notebook_name}"
            )

        version_value = version or self.data["version"]  # type: ignore[index]
        output_dir = Path(self.data["environment"]["output_dir"])  # type: ignore[index]
        filename = outputs[artifact_type].format(version=version_value)
        return output_dir / filename

    def _ensure_notebook(self, notebook_name: str) -> None:
        if notebook_name not in NOTEBOOKS:
            raise KeyError(f"Unknown notebook: {notebook_name}")

    def _validate(self, data: Dict[str, Any]) -> None:
        required_top = {"version", "environment"} | NOTEBOOKS
        missing = required_top - data.keys()
        if missing:
            raise ValueError(f"Missing required config keys: {sorted(missing)}")

        for notebook in NOTEBOOKS:
            section = data.get(notebook, {})
            if "params" not in section or "outputs" not in section:
                raise ValueError(f"{notebook} must define params and outputs")

        self._validate_dates(data)

    def _validate_dates(self, data: Dict[str, Any]) -> None:
        covid_params = data.get("covid", {}).get("params", {})
        lockdown_date = covid_params.get("lockdown_date")
        if lockdown_date:
            try:
                datetime.strptime(lockdown_date, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError(
                    "covid.params.lockdown_date must be YYYY-MM-DD"
                ) from exc
