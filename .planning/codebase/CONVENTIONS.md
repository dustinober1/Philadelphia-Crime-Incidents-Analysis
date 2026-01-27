# Coding Conventions

**Analysis Date:** 2026-01-27

## Naming Patterns

**Files:**
- `snake_case.py`: `scripts/helper/csv_to_parquet.py`, `scripts/helper/scrape.py`

**Functions:**
- `snake_case`: `convert_csv_to_parquet()`, `get_csv_files()`

**Variables:**
- `snake_case`: `csv_files`, `combined_df`

**Classes:**
- `PascalCase` (Recommended in `AGENTS.md`, though no classes observed in inspected scripts)

**Constants:**
- `UPPER_CASE`: `CSV_DIR`, `OUTPUT_FILE`, `CHUNK_SIZE`

## Code Style

**Formatting:**
- `black` or `ruff format` (Recommended)
- Indentation: 4 spaces
- Line length: 88-100 characters

**Linting:**
- `flake8` or `ruff` (Recommended)
- No explicit config file detected in root

## Import Organization

**Order:**
1. Standard Library (`os`, `sys`, `time`, `pathlib`)
2. Third-Party (`pandas`, `requests`)
3. Local Application (`src`)

**Path Aliases:**
- Not detected

## Error Handling

**Patterns:**
- Specific `try...except` blocks for I/O and network operations.
- `response.raise_for_status()` for HTTP errors.
- `sys.exit(1)` on critical failure in scripts.

## Logging

**Framework:** `print` statements used in scripts for progress and errors.

**Patterns:**
- Progress indicators in loops (e.g., `Processing: {filename}`).
- Error messages prefixed with `✗`.
- Success messages prefixed with `✓`.

## Comments

**When to Comment:**
- Docstrings at module level explaining purpose and steps.
- Docstrings for functions.
- Inline comments for complex steps (e.g., memory management chunking).

**JSDoc/TSDoc:**
- Python Docstrings (Google/NumPy style recommended).

## Function Design

**Size:**
- Functions tend to be focused (e.g., `infer_dtypes`, `download_month`).

**Parameters:**
- Explicit typing not strictly enforced (no type hints observed in `scrape.py` or `csv_to_parquet.py`).

**Return Values:**
- Functions return status (boolean) or data artifacts (paths, dataframes).

## Module Design

**Exports:**
- Scripts use `if __name__ == "__main__":` block for execution.

**Barrel Files:**
- `__init__.py` files exist in `src/utils` but are empty.

---

*Convention analysis: 2026-01-27*
