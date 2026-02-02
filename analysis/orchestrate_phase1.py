"""Orchestrate Phase 1 notebooks with papermill."""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List

import papermill as pm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from analysis.artifact_manager import create_version_manifest, save_manifest
from analysis.config_loader import Phase1Config

NOTEBOOKS = {
    "annual_trend": Path("notebooks") / "philadelphia_safety_trend_analysis.ipynb",
    "seasonality": Path("notebooks") / "summer_crime_spike_analysis.ipynb",
    "covid": Path("notebooks") / "covid_lockdown_crime_landscape.ipynb",
}


def setup_logger(log_path: Path) -> logging.Logger:
    """Configure console and file logging."""
    logger = logging.getLogger("phase1-orchestrator")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def run_notebook(notebook_path: Path, output_path: Path, params: Dict) -> float:
    """Execute a notebook and return its runtime in seconds."""
    start = time.time()
    pm.execute_notebook(
        str(notebook_path),
        str(output_path),
        parameters=params,
    )
    return time.time() - start


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Phase 1 notebooks")
    parser.add_argument("--version", default="v1.0", help="Artifact version label")
    parser.add_argument(
        "--config-path",
        type=Path,
        default=Path("config") / "phase1_config.yaml",
        help="Path to Phase 1 config",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Use fast sample fraction from config",
    )
    parser.add_argument(
        "--notebook",
        choices=sorted(NOTEBOOKS.keys()),
        help="Run a single notebook",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue executing notebooks after a failure",
    )

    args = parser.parse_args()

    config = Phase1Config(args.config_path)
    reports_dir = Path(config.data["environment"]["output_dir"])  # type: ignore[index]
    reports_dir.mkdir(parents=True, exist_ok=True)

    logger = setup_logger(reports_dir / "execution.log")
    logger.info("Starting Phase 1 orchestration")

    notebooks = [args.notebook] if args.notebook else list(NOTEBOOKS.keys())
    artifacts: List[Path] = []
    run_params: Dict[str, Dict] = {}
    total_runtime = 0.0

    for notebook in notebooks:
        notebook_path = NOTEBOOKS[notebook]
        output_path = reports_dir / f"{notebook}_executed_{args.version}.ipynb"
        params = config.get_notebook_params(notebook)
        if args.fast:
            params = dict(params)
            params["fast_sample_frac"] = config.data["environment"]["fast_sample_frac"]  # type: ignore[index]

        run_params[notebook] = params
        logger.info("Starting %s...", notebook)
        try:
            runtime = run_notebook(notebook_path, output_path, params)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Notebook %s failed: %s", notebook, exc)
            if not args.continue_on_error:
                raise
            continue

        logger.info("Completed %s in %.1fs", notebook, runtime)
        total_runtime += runtime
        artifacts.append(output_path)

    if artifacts:
        manifest = create_version_manifest(
            version=args.version,
            artifacts=artifacts,
            params=run_params,
            runtime_seconds=total_runtime,
        )
        manifest_path = reports_dir / f"phase1_manifest_{args.version}.json"
        save_manifest(manifest, manifest_path)
        logger.info("Saved manifest to %s", manifest_path)

    logger.info("Phase 1 orchestration complete")


if __name__ == "__main__":
    main()
