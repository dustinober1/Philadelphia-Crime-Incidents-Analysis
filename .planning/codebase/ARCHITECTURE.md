# Architecture

**Analysis Date:** 2026-01-27

## Pattern Overview

**Overall:** Script-based ETL (Extract, Transform, Load) Pipeline

**Key Characteristics:**
- **Sequential Execution:** Standalone scripts intended to be run in sequence.
- **File-Centric State:** State is maintained via the file system (CSV checking, Parquet existence).
- **Minimal Abstraction:** Logic is contained within scripts rather than a shared library (currently).

## Layers

**Data Acquisition:**
- Purpose: Downloads raw crime data from the Carto API.
- Location: `scripts/helper/scrape.py`
- Contains: API request logic, retry mechanisms, monthly chunking.
- Depends on: `requests`
- Used by: Manual execution / Scheduler

**Data Transformation:**
- Purpose: Cleans, types, and compresses raw data into analytical format.
- Location: `scripts/helper/csv_to_parquet.py`
- Contains: CSV parsing, type optimization (downcasting), Parquet serialization.
- Depends on: `pandas`, `pyarrow`
- Used by: Downstream analysis (future)

**Configuration:**
- Purpose: Centralizes file paths and environment settings.
- Location: `config.ini`
- Contains: Paths for raw/processed data, model outputs, visualization settings.

## Data Flow

**Primary Pipeline:**

1. **Ingest**: `scripts/helper/scrape.py` fetches data year-by-month from Carto API.
   - Output: `data/raw/philly_crime_data/incidents_YYYY_MM.csv`
2. **Process**: `scripts/helper/csv_to_parquet.py` reads all raw CSVs.
   - Action: Concatenates, optimizes types (e.g., `object` -> `category`, `int64` -> `int8/16`), and writes to Parquet.
   - Output: `data/processed/crime_incidents_combined.parquet`

**State Management:**
- **Idempotency**: Scraper checks if `incidents_YYYY_MM.csv` exists before downloading.
- **Storage**: Data persists on the local filesystem (`data/`).

## Key Abstractions

**Batch Processing:**
- Purpose: Handles data in manageable chunks (months for download, file batches for processing).
- Examples: `scripts/helper/scrape.py`, `scripts/helper/csv_to_parquet.py`
- Pattern: Iterative processing with retry logic.

## Entry Points

**Data Scraper:**
- Location: `scripts/helper/scrape.py`
- Triggers: Manual execution (`python scripts/helper/scrape.py`)
- Responsibilities: Fetching historical and new data.

**Data Converter:**
- Location: `scripts/helper/csv_to_parquet.py`
- Triggers: Manual execution (`python scripts/helper/csv_to_parquet.py`)
- Responsibilities: aggregating CSVs into a single optimized Parquet file.

## Error Handling

**Strategy:** Retries and Logging

**Patterns:**
- **Retry Logic:** Scraper uses a loop with `time.sleep` and `MAX_RETRIES` for network requests.
- **Graceful Failure:** Scripts catch exceptions, print error messages to stderr, and often continue processing other chunks if possible (or exit cleanly).

## Cross-Cutting Concerns

**Logging:** Console output (`print`) with simple status messages.
**Configuration:** `config.ini` provides a single source of truth for paths, though scripts currently hardcode some defaults or calculate paths relative to `__file__`.

---

*Architecture analysis: 2026-01-27*
