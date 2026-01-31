# Testing Patterns

**Analysis Date:** 2026-01-30

## Test Framework

**Runner:**
- Not detected - No test framework configuration found
- No pytest, unittest, or other testing framework files present

**Assertion Library:**
- Not detected - No explicit test assertions found
- Results validation done through print statements and data inspection

**Run Commands:**
```bash
# No test commands configured
# Manual execution of analysis scripts:
python analysis/data_quality.py
python analysis/temporal_analysis.py
# ... etc
```

## Test File Organization

**Location:**
- Not applicable - No dedicated test directory found
- No test files present in the codebase

**Naming:**
- Not applicable - No test naming convention found

**Structure:**
- Not applicable - No test structure implemented

## Test Structure

**Suite Organization:**
- Not detected - No formal test suites
- Each analysis module is a self-contained unit

**Patterns:**
- No unit tests found
- Integration testing done through manual execution
- No fixtures or test data setup

## Mocking

**Framework:**
- Not detected - No mocking framework in use

**Patterns:**
- No mocking patterns found
- All data loaded from actual Parquet files

**What to Mock:**
- Not applicable - No mocking implemented

**What NOT to Mock:**
- Data loading from real files
- File system operations
- External dependencies (pandas, matplotlib, etc.)

## Fixtures and Factories

**Test Data:**
- Not detected - No dedicated test data fixtures
- Uses actual crime data from `data/crime_incidents_combined.parquet`

**Location:**
- No test data directory
- Real data used for all analyses

## Coverage

**Requirements:**
- Not enforced - No code coverage tooling
- No coverage reports generated

**View Coverage:**
- Not available - No coverage commands configured

## Test Types

**Unit Tests:**
- Not implemented - No unit tests found
- Functions not tested in isolation

**Integration Tests:**
- Manual only - Run through script execution
- Data pipeline tested end-to-end

**E2E Tests:**
- Not implemented - No end-to-end tests
- Report generation not automated

## Common Patterns

**Async Testing:**
- Not applicable - No async functions in codebase

**Error Testing:**
- Manual validation through print statements
- No automated error condition testing

**Validation Patterns:**
- Results dictionaries contain validation keys
- Print statements show progress and results
- Data quality checks performed during analysis

**Manual Testing Approach:**
```python
# Manual validation pattern found in codebase
print("Loading data...")
df = load_data(clean=False)

print("Analyzing missing data...")
missing_summary = get_missing_summary(df)
print(f"Found {len(missing_summary)} columns with missing data")

# Results validation through dictionary structure
results = {
    "total_records": len(df),
    "total_columns": len(df.columns),
    "columns": list(df.columns),
    "missing_summary": missing_summary,
}
```

**Data Validation Patterns:**
- Coordinate validation before spatial analysis
- Temporal feature extraction consistency
- Missing data thresholds applied
- Sample sizes calculated for performance

---

*Testing analysis: 2026-01-30*
```