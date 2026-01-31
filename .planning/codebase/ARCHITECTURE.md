# Architecture

**Analysis Date:** 2026-01-30

## Pattern Overview

**Overall:** Modular Data Analysis Pipeline with Separation of Concerns

**Key Characteristics:**
- Separation between core analysis modules and report generators
- Centralized configuration management
- Standardized data preprocessing pipeline
- Base64-encoded plot embedding for self-contained reports
- Modular design allowing individual analysis execution

## Layers

**Configuration Layer:**
- Purpose: Centralized constants and settings management
- Location: `[analysis/config.py]`
- Contains: Paths, plot settings, dataset info, DBSCAN parameters, color schemes
- Depends on: Pathlib for path operations
- Used by: All analysis modules

**Utilities Layer:**
- Purpose: Common data loading, validation, and helper functions
- Location: `[analysis/utils.py]`
- Contains: Data loading, coordinate validation, temporal feature extraction, UCR classification, plot encoding helpers
- Depends on: pandas, numpy, pathlib
- Used by: All analysis modules and reports

**Analysis Layer:**
- Purpose: Core data analysis computation
- Location: `[analysis/*.py]` (excluding report files)
- Contains: Statistical analysis, clustering, temporal patterns, spatial analysis
- Depends on: Utilities layer, config layer, matplotlib, seaborn, scipy
- Used by: Report generators

**Report Generation Layer:**
- Purpose: Markdown report orchestration and generation
- Location: `[analysis/*_report.py]` and `[analysis/06_generate_report.py]`
- Contains: Analysis orchestration, markdown formatting, plot embedding
- Depends on: Analysis layer, config layer
- Used by: Manual execution and automation scripts

## Data Flow

**Analysis Module Execution Flow:**

1. **Data Loading**: `load_data()` from `utils.py` reads parquet file
2. **Data Validation**: `validate_coordinates()` filters valid Philadelphia coordinates
3. **Feature Engineering**: `extract_temporal_features()` adds datetime columns
4. **Analysis Execution**: Module-specific computations (e.g., temporal patterns, spatial clustering)
5. **Results Packaging**: Analysis results packaged with base64-encoded plots
6. **Report Generation**: Results converted to markdown with embedded images

**Comprehensive Report Flow:**
```python
1. 06_generate_report.py
   ↓ 2. Run all analysis modules
   ↓ 3. Collect results dictionary
   ↓ 4. Generate markdown with embedded plots
   ↓ 5. Save to reports/ directory
```

## Key Abstractions

**Analysis Module:**
- Purpose: Self-contained analysis with standardized interface
- Examples: `[analysis/temporal_analysis.py]`, `[analysis/spatial_analysis.py]`
- Pattern: `analyze_*()` function returns dict with stats and base64 plots
- Common structure:
  ```python
  def analyze_*() -> dict:
      df = load_data()
      df = validate_coordinates(df)
      df = extract_temporal_features(df)
      # ... analysis logic ...
      return {"stats": ..., "plot": create_image_tag(...)}
  ```

**Report Generator:**
- Purpose: Orchestrate analysis and generate markdown reports
- Examples: `[analysis/06_generate_report.py]`, `[analysis/07_report_safety_trend.py]`
- Pattern: Import analysis modules, execute functions, format results to markdown

**Configuration:**
- Purpose: Centralized settings management
- Examples: `[analysis/config.py]`
- Pattern: Constants imported by all modules, no runtime mutations

## Entry Points

**Single Comprehensive Report:**
- Location: `[analysis/06_generate_report.py]`
- Triggers: `python analysis/06_generate_report.py`
- Responsibilities: Runs all analysis phases, generates complete EDA report

**Focused Reports:**
- Location: `[analysis/*_report.py]`
- Triggers: Individual script execution
- Responsibilities: Run specific analysis modules for targeted insights

**Utility Functions:**
- Location: `[analysis/utils.py]`
- Triggers: Imported by analysis modules
- Responsibilities: Provide reusable data loading and validation functions

**Module Testing:**
- Location: Individual analysis files
- Triggers: Direct execution with `python`
- Responsibilities: Standalone analysis with hardcoded function calls

## Error Handling

**Strategy:** Graceful degradation with informative messages

**Patterns:**
- Coordinate validation filters invalid records silently
- Missing column handling with flexible column name patterns
- Incomplete year exclusion (2026) from trend analysis
- Large dataset sampling for memory-efficient visualization

## Cross-Cutting Concerns

**Data Loading:** Standardized through `load_data()` with coordinate validation
**Plot Generation:** Matplotlib with Agg backend for non-interactive use
**Report Formatting:** Consistent markdown generation with embedded base64 images
**Memory Management:** Sampling of large datasets for visualization operations

---

*Architecture analysis: 2026-01-30*