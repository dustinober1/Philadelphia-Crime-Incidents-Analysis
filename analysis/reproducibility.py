"""
Reproducibility infrastructure for Philadelphia Crime Incidents EDA.

This module provides data version tracking, random seed management, and analysis
parameter documentation to ensure all analyses can be reproduced exactly.

Key components:
- DataVersion: Track data versions via SHA256 hash and metadata snapshots
- set_global_seed: Set random seeds for all libraries (numpy, random)
- get_analysis_metadata: Capture analysis parameters for documentation
- format_metadata_markdown: Format metadata for markdown reports
"""

from __future__ import annotations

import hashlib
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from analysis.config import STAT_CONFIG


class DataVersion:
    """
    Track data version information for reproducibility.

    Computes SHA256 hash of data file and captures metadata including
    row count, column count, column names, and date range.

    Parameters
    ----------
    data_path : Path | str
        Path to the data file (parquet, csv, etc.)

    Attributes
    ----------
    path : Path
        Path to the data file
    sha256 : str
        SHA256 hash of the data file
    row_count : int
        Number of rows in the dataset
    column_count : int
        Number of columns in the dataset
    columns : list[str]
        List of column names
    date_range : tuple[str, str] | None
        Min and max dates if dispatch_date column exists, else None
    computed_at : str
        ISO timestamp of when version was computed

    Examples
    --------
    >>> dv = DataVersion("data/crime_incidents_combined.parquet")
    >>> print(dv)
    DataVersion(path=...crime_incidents_combined.parquet, rows=3496353, sha256=abc123...)
    >>> metadata = dv.to_dict()
    >>> metadata["sha256"]
    'abc123def456...'
    """

    def __init__(self, data_path: Path | str) -> None:
        self.path = Path(data_path)
        if not self.path.exists():
            raise FileNotFoundError(f"Data file not found: {self.path}")

        self._metadata = self._compute_metadata()
        self.sha256: str = self._metadata["sha256"]
        self.row_count: int = self._metadata["row_count"]
        self.column_count: int = self._metadata["column_count"]
        self.columns: list[str] = self._metadata["columns"]
        self.date_range: Optional[tuple[str, str]] = self._metadata.get("date_range")
        self.computed_at: str = self._metadata["computed_at"]

    def _compute_metadata(self) -> Dict[str, Any]:
        """
        Compute metadata including SHA256 hash and dataset statistics.

        Reads the file in chunks for efficient hashing of large files,
        then loads the dataset to extract row count, columns, and date range.

        Returns
        -------
        dict
            Dictionary with keys: sha256, row_count, column_count, columns,
            date_range, computed_at
        """
        # Compute SHA256 hash in chunks (4KB) to handle large files
        sha256_hash = hashlib.sha256()
        chunk_size = 4096

        with open(self.path, "rb") as f:
            while chunk := f.read(chunk_size):
                sha256_hash.update(chunk)

        # Load pandas for metadata snapshot
        try:
            df = pd.read_parquet(self.path)
        except Exception as e:
            raise ValueError(f"Failed to read parquet file: {e}") from e

        # Extract date range if dispatch_date column exists
        date_range = None
        if "dispatch_date" in df.columns:
            # Try to convert to datetime
            try:
                dates = pd.to_datetime(df["dispatch_date"], errors="coerce")
                valid_dates = dates.dropna()
                if len(valid_dates) > 0:
                    min_date = valid_dates.min().strftime("%Y-%m-%d")
                    max_date = valid_dates.max().strftime("%Y-%m-%d")
                    date_range = (min_date, max_date)
            except Exception:
                # Date parsing failed, leave date_range as None
                pass

        return {
            "sha256": sha256_hash.hexdigest(),
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "date_range": date_range,
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Return metadata as dictionary for report generation.

        Returns
        -------
        dict
            Dictionary containing all metadata fields.
        """
        return {
            "path": str(self.path),
            "sha256": self.sha256,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "columns": self.columns,
            "date_range": self.date_range,
            "computed_at": self.computed_at,
        }

    def __repr__(self) -> str:
        """Return human-readable version information."""
        sha_short = self.sha256[:16] if self.sha256 else "unknown"
        return (
            f"DataVersion(path={self.path.name}, rows={self.row_count:,}, "
            f"sha256={sha_short}...)"
        )


def set_global_seed(seed: Optional[int] = None) -> int:
    """
    Set global random seed for reproducibility.

    Sets seeds for numpy and Python's random module. If no seed is provided,
    uses the default from STAT_CONFIG["random_seed"].

    Parameters
    ----------
    seed : int | None, default=None
        Random seed to use. If None, uses STAT_CONFIG["random_seed"].

    Returns
    -------
    int
        The seed that was set.

    Examples
    --------
    >>> set_global_seed(123)
    123
    >>> set_global_seed()  # Uses default from STAT_CONFIG
    42
    """
    if seed is None:
        seed = STAT_CONFIG["random_seed"]

    np.random.seed(seed)
    random.seed(seed)

    return seed


def get_analysis_metadata(
    data_version: Optional[DataVersion] = None, **params: Any
) -> Dict[str, Any]:
    """
    Capture analysis parameters for documentation.

    Collects analysis parameters with a timestamp and optional data version
    information for inclusion in generated reports.

    Parameters
    ----------
    data_version : DataVersion | None, default=None
        DataVersion object if tracking data version, else None
    **params : Any
        Analysis parameters as keyword arguments (e.g., alpha=0.01, n_bootstrap=1000)

    Returns
    -------
    dict
        Dictionary with keys: timestamp, parameters, data_version

    Examples
    --------
    >>> metadata = get_analysis_metadata(alpha=0.01, n_samples=1000)
    >>> metadata["parameters"]["alpha"]
    0.01
    >>> dv = DataVersion("data/crime_incidents_combined.parquet")
    >>> metadata = get_analysis_metadata(data_version=dv, test="mann-whitney")
    >>> metadata["data_version"]["row_count"]
    3496353
    """
    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parameters": params.copy() if params else {},
        "data_version": data_version.to_dict() if data_version else None,
    }

    return metadata


def format_metadata_markdown(metadata: Dict[str, Any]) -> str:
    """
    Format metadata for markdown reports.

    Creates a formatted "Analysis Configuration" section suitable for
    inclusion in all generated reports.

    Parameters
    ----------
    metadata : dict
        Metadata dictionary from get_analysis_metadata()

    Returns
    -------
    str
        Formatted markdown string with analysis configuration.

    Examples
    --------
    >>> metadata = get_analysis_metadata(alpha=0.01, method="dbscan")
    >>> md = format_metadata_markdown(metadata)
    >>> print(md)
    <details>
    <summary>Analysis Configuration</summary>
    ...
    </details>
    """
    lines = [
        "<details>",
        "<summary>Analysis Configuration</summary>",
        "",
        "```yaml",
        f"# Analysis executed at: {metadata.get('timestamp', 'unknown')}",
    ]

    # Add parameters
    params = metadata.get("parameters", {})
    if params:
        lines.append("# Parameters")
        for key, value in sorted(params.items()):
            if isinstance(value, (str, int, float, bool)):
                lines.append(f"{key}: {value}")
            elif isinstance(value, list):
                lines.append(f"{key}: [{', '.join(map(str, value))}]")
            elif isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            else:
                lines.append(f"{key}: {str(value)}")

    # Add data version if available
    dv = metadata.get("data_version")
    if dv:
        lines.append("")
        lines.append("# Data Version")
        lines.append(f"path: {dv.get('path', 'unknown')}")
        lines.append(f"sha256: {dv.get('sha256', 'unknown')}")
        lines.append(f"row_count: {dv.get('row_count', 'unknown'):,}")
        lines.append(f"column_count: {dv.get('column_count', 'unknown')}")

        if dv.get("date_range"):
            min_date, max_date = dv["date_range"]
            lines.append(f"date_range: {min_date} to {max_date}")

        lines.append(f"version_computed_at: {dv.get('computed_at', 'unknown')}")

    lines.extend(["```", "", "</details>", ""])

    return "\n".join(lines)
