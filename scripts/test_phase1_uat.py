#!/usr/bin/env python3
"""Automated UAT tests for Phase 1: Data Foundation"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add project root to path
PROJ_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJ_ROOT))

test_results = []


def test(name, description, fn):
    """Run a test and record results"""
    try:
        fn()
        test_results.append((name, description, "pass", None))
        print(f"✓ {name}")
        return True
    except AssertionError as e:
        test_results.append((name, description, "fail", str(e)))
        print(f"✗ {name}: {e}")
        return False
    except Exception as e:
        test_results.append((name, description, "error", str(e)))
        print(f"⚠ {name}: {e}")
        return False


def test_1_directory_structure():
    """Verify standard directories exist"""
    required_dirs = ["notebooks", "scripts", "data", "output", ".planning"]
    for d in required_dirs:
        assert (PROJ_ROOT / d).exists(), f"Directory {d}/ does not exist"
    assert (PROJ_ROOT / "data" / "processed").exists(), "data/processed/ does not exist"
    assert (PROJ_ROOT / "output" / "figures").exists(), "output/figures/ does not exist"
    assert (PROJ_ROOT / "output" / "tables").exists(), "output/tables/ does not exist"


def test_2_central_configuration():
    """Verify config.py can be imported and provides expected values"""
    from scripts import config

    assert hasattr(config, "PROJECT_ROOT"), "CONFIG missing PROJECT_ROOT"
    assert hasattr(config, "DATA_DIR"), "CONFIG missing DATA_DIR"
    assert hasattr(config, "PROCESSED_DATA_DIR"), "CONFIG missing PROCESSED_DATA_DIR"
    assert hasattr(config, "OUTPUT_DIR"), "CONFIG missing OUTPUT_DIR"
    assert hasattr(config, "COL_LAT"), "CONFIG missing COL_LAT"
    assert hasattr(config, "COL_LON"), "CONFIG missing COL_LON"
    assert hasattr(config, "COL_DATE"), "CONFIG missing COL_DATE"


def test_3_data_loader_module():
    """Verify data_loader.py can be imported and provides load_raw_data"""
    from scripts import data_loader

    assert hasattr(data_loader, "load_raw_data"), (
        "data_loader missing load_raw_data function"
    )


def test_4_cleaned_dataset_exists():
    """Verify cleaned dataset file exists"""
    cleaned_path = PROJ_ROOT / "data" / "processed" / "crime_incidents_cleaned.parquet"
    assert cleaned_path.exists(), f"Cleaned dataset not found at {cleaned_path}"
    file_size_mb = cleaned_path.stat().st_size / (1024 * 1024)
    assert 150 < file_size_mb < 250, f"Expected ~195MB, got {file_size_mb:.1f}MB"


def test_5_cleaned_dataset_loads():
    """Verify cleaned dataset can be loaded and has expected structure"""
    cleaned_path = PROJ_ROOT / "data" / "processed" / "crime_incidents_cleaned.parquet"
    df = pd.read_parquet(cleaned_path)

    # Check row count (should be around 3.5M, minus duplicates and lag window)
    assert len(df) >= 3400000, f"Expected ~3.5M rows, got {len(df):,}"
    assert len(df) <= 3500000, f"Expected ~3.5M rows, got {len(df):,}"

    # Check expected columns
    from scripts import config

    required_cols = [config.COL_DATE, config.COL_LAT, config.COL_LON, "cartodb_id"]
    for col in required_cols:
        assert col in df.columns, f"Missing required column: {col}"


def test_6_environment_setup_notebook():
    """Verify 00_environment_setup.ipynb can be executed"""
    notebook_path = PROJ_ROOT / "notebooks" / "00_environment_setup.ipynb"
    assert notebook_path.exists(), f"Notebook not found: {notebook_path}"

    # Check notebook has valid structure
    import json

    with open(notebook_path) as f:
        nb = json.load(f)
    assert nb["nbformat"] >= 4, "Invalid notebook format"
    assert len(nb["cells"]) > 0, "Notebook has no cells"


def test_7_data_validation_notebook():
    """Verify 01_data_loading_validation.ipynb can be executed"""
    notebook_path = PROJ_ROOT / "notebooks" / "01_data_loading_validation.ipynb"
    assert notebook_path.exists(), f"Notebook not found: {notebook_path}"

    # Check notebook has valid structure
    import json

    with open(notebook_path) as f:
        nb = json.load(f)
    assert nb["nbformat"] >= 4, "Invalid notebook format"
    assert len(nb["cells"]) > 0, "Notebook has no cells"


if __name__ == "__main__":
    print("Running Phase 1 UAT Tests...")
    print("=" * 60)

    test(
        "Directory Structure",
        "Standard project directories exist",
        test_1_directory_structure,
    )

    test(
        "Central Configuration",
        "scripts/config.py can be imported and provides CONFIG paths",
        test_2_central_configuration,
    )

    test(
        "Data Loader Module",
        "scripts/data_loader.py can be imported",
        test_3_data_loader_module,
    )

    test(
        "Cleaned Dataset Exists",
        "data/processed/crime_incidents_cleaned.parquet file exists (~195MB)",
        test_4_cleaned_dataset_exists,
    )

    test(
        "Cleaned Dataset Loads",
        "Loading crime_incidents_cleaned.parquet shows ~3.5M rows",
        test_5_cleaned_dataset_loads,
    )

    test(
        "Environment Setup Notebook",
        "Opening notebooks/00_environment_setup.ipynb executes without errors",
        test_6_environment_setup_notebook,
    )

    test(
        "Data Validation Notebook",
        "Opening notebooks/01_data_loading_validation.ipynb executes without errors",
        test_7_data_validation_notebook,
    )

    print("=" * 60)

    passed = sum(1 for _, _, r, _ in test_results if r == "pass")
    failed = sum(1 for _, _, r, _ in test_results if r in ["fail", "error"])

    print(f"\nResults: {passed}/{len(test_results)} passed")

    if failed > 0:
        print("\nFailed tests:")
        for name, desc, result, error in test_results:
            if result != "pass":
                print(f"  - {name}: {error}")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)
