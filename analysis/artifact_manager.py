"""Artifact versioning utilities for Phase 1 outputs."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path


def get_versioned_path(template: str, version: str) -> Path:
    """Return a versioned Path from a template.

    Parameters
    ----------
    template : str
        Template string containing ``{version}`` placeholder.
    version : str
        Version identifier to inject.

    Returns
    -------
    pathlib.Path
        Path with version substituted.
    """
    return Path(template.format(version=version))


def compute_file_hash(filepath: Path) -> str:
    """Compute the SHA256 hash for a file.

    Parameters
    ----------
    filepath : pathlib.Path
        File to hash.

    Returns
    -------
    str
        Hex digest of the SHA256 hash.
    """
    sha256 = hashlib.sha256()
    with filepath.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_git_commit() -> str | None:
    """Return the current git commit hash, if available.

    Returns
    -------
    str or None
        Short commit hash, or None if unavailable.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def create_version_manifest(
    version: str,
    artifacts: list[Path],
    params: dict,
    runtime_seconds: float,
) -> dict:
    """Create a version manifest for generated artifacts.

    Parameters
    ----------
    version : str
        Version identifier for the run.
    artifacts : list of pathlib.Path
        Paths to generated artifacts.
    params : dict
        Parameters used for the run.
    runtime_seconds : float
        Runtime in seconds.

    Returns
    -------
    dict
        Manifest dictionary including hashes and metadata.
    """
    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    artifact_entries = [
        {"path": str(path), "sha256": compute_file_hash(path)} for path in artifacts
    ]

    return {
        "version": version,
        "timestamp": timestamp,
        "git_commit": get_git_commit(),
        "runtime_seconds": runtime_seconds,
        "parameters": params,
        "artifacts": artifact_entries,
    }


def save_manifest(manifest: dict, output_path: Path) -> None:
    """Save manifest JSON to disk.

    Parameters
    ----------
    manifest : dict
        Manifest payload.
    output_path : pathlib.Path
        Destination file path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
