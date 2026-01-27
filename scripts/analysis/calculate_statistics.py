#!/usr/bin/env python3
"""
Statistical analysis script for Philadelphia crime incidents data.
Generates descriptive statistics, trends, and correlations.
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
from src.analysis.profiler import DataProfiler
from src.data.loader import load_crime_data


def main():
    """Main function to run statistical analysis on crime data."""
    print("=" * 80)
    print("PHILADELPHIA CRIME INCIDENTS - STATISTICAL ANALYSIS REPORT")
    print("=" * 80)

    try:
        # Load the crime data
        print("\nLoading crime data...")
        df = load_crime_data()

        # Ensure dispatch_date_time is converted to datetime if not already
        if "dispatch_date_time" in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df["dispatch_date_time"]):
                df["dispatch_date_time"] = pd.to_datetime(df["dispatch_date_time"])

        print(f"Data loaded successfully. Shape: {df.shape}")

        # Initialize the DataProfiler
        profiler = DataProfiler(df)

        # Continue to comprehensive reporting in next step
        return df, profiler

    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    df, profiler = main()
    print(f"Data shape: {df.shape}")
