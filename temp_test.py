#!/usr/bin/env python3
"""Test script to verify data loading and notebook dependencies."""

import pandas as pd
from pathlib import Path

# Define the same paths as the notebook
PROJECT_ROOT = Path(".").resolve()
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

print(f"Looking for data in: {PROCESSED_DATA_DIR}")

# Check if the file exists
data_file = PROCESSED_DATA_DIR / "crime_incidents_cleaned.parquet"
print(f"Data file path: {data_file}")
print(f"File exists: {data_file.exists()}")

if data_file.exists():
    print("Attempting to load data...")
    try:
        df = pd.read_parquet(data_file)
        print(f"Successfully loaded {len(df):,} records")
        print(f"Columns: {list(df.columns)}")
    except Exception as e:
        print(f"Error loading data: {e}")
else:
    print("Data file does not exist!")

    # Look for similar files
    print("\nLooking for other parquet files in data directory:")
    for file in (DATA_DIR / "processed").glob("*.parquet"):
        print(f"  - {file}")

    for file in DATA_DIR.glob("*.parquet"):
        print(f"  - {file}")
