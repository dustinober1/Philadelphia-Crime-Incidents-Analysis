"""
Convert all CSV files in data/raw/philly_crime_data to a single parquet file.

This script:
1. Discovers all CSV files in the philly_crime_data directory
2. Reads and concatenates them into a single DataFrame
3. Performs basic data type optimization
4. Saves as parquet for efficient storage and querying
"""

import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path
import time
import sys

# Configuration
CSV_DIR = Path(__file__).parent / "raw" / "philly_crime_data"
OUTPUT_FILE = Path(__file__).parent / "processed" / "crime_incidents_combined.parquet"
CHUNK_SIZE = 20  # Process CSVs in chunks to manage memory

def get_csv_files():
    """Get all CSV files sorted by filename."""
    csv_files = sorted(CSV_DIR.glob("incidents_*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {CSV_DIR}")
    return csv_files

def infer_dtypes(df):
    """Optimize data types for better storage and performance."""
    for col in df.columns:
        if df[col].dtype == 'object':
            # Try to convert to category for string columns with many duplicates
            if df[col].nunique() / len(df) < 0.5:
                df[col] = df[col].astype('category')
        elif df[col].dtype == 'int64':
            # Downcast integers to smaller types if possible
            max_val = df[col].max()
            min_val = df[col].min()
            if min_val >= 0 and max_val < 256:
                df[col] = df[col].astype('uint8')
            elif min_val >= -128 and max_val < 127:
                df[col] = df[col].astype('int8')
            elif min_val >= 0 and max_val < 65536:
                df[col] = df[col].astype('uint16')
            elif min_val >= -32768 and max_val < 32767:
                df[col] = df[col].astype('int16')
    return df

def convert_csv_to_parquet():
    """Convert all CSV files to a single parquet file."""
    print("=" * 80)
    print("CSV to Parquet Conversion")
    print("=" * 80)
    
    csv_files = get_csv_files()
    total_files = len(csv_files)
    
    print(f"\nFound {total_files} CSV files to process")
    print(f"CSV Directory: {CSV_DIR}")
    print(f"Output File: {OUTPUT_FILE}\n")
    
    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    start_time = time.time()
    dfs = []
    
    print("Reading CSV files...")
    for i, csv_file in enumerate(csv_files, 1):
        try:
            # Display progress
            if (i - 1) % 10 == 0:
                print(f"  [{i}/{total_files}] Processing: {csv_file.name}")
            
            # Read CSV with date parsing
            df = pd.read_csv(
                csv_file,
                parse_dates=['dispatch_date_time'],
                low_memory=False
            )
            dfs.append(df)
            
            # Process in chunks to manage memory
            if len(dfs) >= CHUNK_SIZE:
                print(f"  Chunk complete: {len(dfs)} files read, combining...")
        except Exception as e:
            print(f"  ✗ Error reading {csv_file.name}: {e}")
            continue
    
    print(f"\n  [✓] All files read. Total files: {len(dfs)}")
    
    # Combine all dataframes
    print(f"\nCombining {len(dfs)} dataframes...")
    combined_df = pd.concat(dfs, ignore_index=True)
    
    print(f"Combined shape: {combined_df.shape}")
    print(f"Memory usage before optimization: {combined_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Display data type info
    print(f"\nDataFrame Info:")
    print(f"  Columns: {len(combined_df.columns)}")
    print(f"  Rows: {len(combined_df):,}")
    print(f"  Date range: {combined_df['dispatch_date_time'].min()} to {combined_df['dispatch_date_time'].max()}")
    
    # Optimize data types
    print(f"\nOptimizing data types...")
    combined_df = infer_dtypes(combined_df)
    
    optimized_memory = combined_df.memory_usage(deep=True).sum() / 1024**2
    print(f"Memory usage after optimization: {optimized_memory:.2f} MB")
    
    # Save to parquet
    print(f"\nWriting to parquet: {OUTPUT_FILE}")
    combined_df.to_parquet(
        OUTPUT_FILE,
        engine='pyarrow',
        compression='snappy',
        index=False
    )
    
    # Verify the output
    parquet_size = OUTPUT_FILE.stat().st_size / 1024**2
    print(f"Parquet file size: {parquet_size:.2f} MB")
    
    # Read back to verify
    verified_df = pd.read_parquet(OUTPUT_FILE)
    print(f"\nVerification:")
    print(f"  Rows read back: {len(verified_df):,}")
    print(f"  Columns read back: {len(verified_df.columns)}")
    print(f"  ✓ File integrity verified")
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"\n" + "=" * 80)
    print(f"Conversion Complete!")
    print(f"Time elapsed: {elapsed:.2f} seconds")
    print(f"Processing rate: {total_files / elapsed:.2f} files/second")
    print("=" * 80)
    
    return OUTPUT_FILE

if __name__ == "__main__":
    try:
        output_path = convert_csv_to_parquet()
        print(f"\n✓ Success! Output saved to: {output_path}")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error during conversion: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
