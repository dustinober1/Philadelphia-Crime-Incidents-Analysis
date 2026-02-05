"""Shared pytest fixtures for fast unit tests.

This module provides common fixtures used across test files to avoid
repetitive setup and enable fast test execution. Fixtures provide small,
representative sample datasets instead of loading the full 3.4M-row crime
dataset, ensuring tests run in seconds rather than minutes.

Usage:
    def test_something(sample_crime_df):
        # sample_crime_df is a 100-row DataFrame with representative crime data
        assert len(sample_crime_df) == 100

    def test_output(tmp_output_dir):
        # tmp_output_dir is a temporary directory for test outputs
        output_file = tmp_output_dir / "output.csv"
        # ... write test outputs ...
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest

if TYPE_CHECKING:
    pass


@pytest.fixture
def sample_crime_df() -> pd.DataFrame:
    """Provide a small sample DataFrame with representative crime data.

    Creates a 100-row DataFrame with the same schema as the production crime
    dataset, using random values within realistic bounds for Philadelphia.

    Uses np.random.seed(42) for reproducibility across test runs.

    Returns:
        DataFrame with columns:
            - objectid: Sequential IDs 1-100
            - dispatch_date: Daily dates from 2020-01-01
            - ucr_general: UCR codes from [100, 200, 300, 500, 600, 700, 800]
            - point_x: Longitude coordinates in Philadelphia bounds (-75.3, -74.95)
            - point_y: Latitude coordinates in Philadelphia bounds (39.85, 40.15)
            - dc_dist: Police district codes 1-23

    Examples:
        >>> df = sample_crime_df()
        >>> len(df)
        100
        >>> "objectid" in df.columns
        True
    """
    np.random.seed(42)

    n_rows = 100

    df = pd.DataFrame(
        {
            "objectid": range(1, n_rows + 1),
            "dispatch_date": pd.date_range("2020-01-01", periods=n_rows, freq="D"),
            "ucr_general": np.random.choice([100, 200, 300, 500, 600, 700, 800], n_rows),
            "point_x": np.random.uniform(-75.3, -74.95, n_rows),
            "point_y": np.random.uniform(39.85, 40.15, n_rows),
            "dc_dist": np.random.choice(range(1, 24), n_rows),
        }
    )

    return df


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Provide a temporary output directory for test artifacts.

    Creates an 'output' subdirectory under pytest's tmp_path fixture
    for tests that need to write temporary files during execution.
    The directory is automatically cleaned up after each test.

    Args:
        tmp_path: pytest's built-in temporary directory fixture

    Returns:
        Path object pointing to the output directory

    Examples:
        >>> def test_generate_report(tmp_output_dir):
        ...     output_file = tmp_output_dir / "report.csv"
        ...     output_file.write_text("data")
        ...     assert output_file.exists()
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir
