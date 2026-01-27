# Codebase Concerns

**Analysis Date:** 2026-01-27

## Tech Debt

**Hardcoded Configuration:**
- Issue: Key parameters are hardcoded in scripts instead of external configuration.
- Files:
  - `scripts/helper/scrape.py`: `START_YEAR`, `END_YEAR`, `BASE_URL`.
  - `scripts/helper/csv_to_parquet.py`: `CSV_DIR`, `OUTPUT_FILE`.
- Impact: Modifying parameters (e.g., updating the year range) requires code changes.
- Fix approach: Move configuration to `config.ini` or environment variables.

**Missing Test Suite:**
- Issue: No automated tests exist.
- Files: `N/A` (No `tests/` directory)
- Impact: High risk of regressions when refactoring or adding features.
- Fix approach: Initialize `pytest` and add unit tests for helper scripts.

## Known Bugs

**Ineffective Memory Management (Fake Chunking):**
- Symptoms: `csv_to_parquet.py` claims to process in chunks but accumulates all data in memory.
- Files: `scripts/helper/csv_to_parquet.py`
- Trigger: Running the script on a large dataset (many CSVs).
- Defect:
  ```python
  # Process in chunks to manage memory
  if len(dfs) >= CHUNK_SIZE:
      print(f"  Chunk complete: {len(dfs)} files read, combining...")
      # BUG: No actual processing or clearing of 'dfs' happens here!
  ```
- Workaround: None (script works only if RAM > Total Dataset Size).

## Performance Bottlenecks

**Memory-Intensive Concatenation:**
- Problem: `pd.concat(dfs)` creates a full copy of the dataset in memory.
- Files: `scripts/helper/csv_to_parquet.py`
- Cause: Loading all CSVs into a list before combining.
- Improvement path: Implement true incremental processing: read chunk -> append to parquet file -> clear memory.

**Sequential Scraping:**
- Problem: Downloads happen one by one.
- Files: `scripts/helper/scrape.py`
- Cause: Single-threaded loop `for year in range(...)`.
- Improvement path: Use `concurrent.futures` or `asyncio` to parallelize downloads.

## Fragile Areas

**External API Dependency:**
- Files: `scripts/helper/scrape.py`
- Why fragile: Depends on hardcoded SQL query structure (`incidents_part1_part2`) and Carto API availability.
- Safe modification: Abstract API client and add retries/circuit breakers (partially implemented).

**Schema Evolution:**
- Files: `scripts/helper/csv_to_parquet.py`
- Why fragile: Assumes all CSVs from 2006-2025 have identical columns. `pd.concat` will introduce NaNs or mixed types if schemas drift.
- Safe modification: Add schema validation before concatenation.

## Test Coverage Gaps

**Entire Codebase:**
- What's not tested: Everything.
- Files: `scripts/helper/scrape.py`, `scripts/helper/csv_to_parquet.py`
- Risk: Critical ETL scripts are unverified.
- Priority: High

---

*Concerns audit: 2026-01-27*
