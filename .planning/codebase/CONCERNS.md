# Codebase Concerns

**Analysis Date:** 2026-01-30

## Tech Debt

**Hardcoded Configuration Values:**
- Issue: Critical parameters scattered across `config.py` with no validation
- Files: `/Users/dustinober/Projects/Crime Incidents Philadelphia/analysis/config.py`, `/Users/dustinober/Projects/Crime Incidents Philadelphia/analysis/weighted_severity_analysis.py`
- Impact: Difficult to tune parameters; no way to experiment with different values without code changes
- Fix approach: Create parameter configuration system with validation and defaults

**Missing Dependency Management:**
- Issue: No `requirements.txt` file; virtual environment lacks version pinning
- Files: Entire project
- Impact: Dependency version changes could break analysis; difficult to reproduce exact results
- Fix approach: Generate `requirements.txt` with pinned versions; implement CI/CD dependency checks

**Code Duplication in Weighted Severity Analysis:**
- Issue: Similar normalization functions duplicated in `weighted_severity_analysis.py`
- Files: `/Users/dustinober/Projects/Crime Incidents Philadelphia/analysis/weighted_severity_analysis.py` (lines 83-100, 147-195)
- Impact: Maintenance burden; inconsistent normalization possible
- Fix approach: Extract to shared utility functions in `utils.py`

## Known Bugs

**DBSCAN Clustering Instability:**
- Symptoms: Warning message "No clusters found. Trying with lower min_samples..." appears in output
- Files: `/Users/dustinober/Projects/Crime Incidents Philadelphia/analysis/red_zones.py` (line 393)
- Trigger: Occurs when default clustering parameters don't find meaningful clusters
- Workaround: Automatically falls back to `min_samples=25`, but this may not be optimal for all datasets

**Coordinate Validation Edge Cases:**
- Symptoms: Records with coordinates outside Philadelphia bbox are filtered silently
- Files: `/Users/dustinober/Projects/Crime Incidents Philadelphia/analysis/utils.py` (lines 97-125)
- Trigger: ~25% of records lack valid coordinates but no warning is shown to user
- Workaround: Analysis scripts should report validation statistics to users

**Column Name Variations Not Handled Consistently:**
- Symptoms: Some analysis scripts fail when dataset column names change
- Files: Multiple scripts use hard-coded column names without fallback patterns
- Trigger: Dataset structure changes break specific analysis modules
- Workaround: Implement robust column detection as shown in CLAUDE.md guidelines

## Security Considerations

**No Input Validation on File Paths:**
- Risk: Path traversal attacks if untrusted data is loaded
- Files: `/Users/dustinober/Projects/Crime Incidents Philadelphia/analysis/utils.py` (load_data function)
- Current mitigation: Uses Path object which provides some protection
- Recommendations: Add input validation and restrict data directory access

**Environment Variables Not Secured:**
- Risk: Potential exposure of configuration in logs or error messages
- Files: Analysis scripts print paths and configuration details
- Current mitigation: None specific
- Recommendations: Sanitize log messages to avoid exposing system paths

## Performance Bottlenecks

**Large Dataset Memory Issues:**
- Problem: Full dataset (3.5M records) loaded into memory without pagination
- Files: Multiple analysis scripts
- Cause: Pandas DataFrames load entire datasets at once
- Improvement path: Implement chunked processing for memory-constrained environments

**Inefficient Sampling for Visualizations:**
- Problem: Random sampling without stratification can bias results
- Files: `/Users/dustinober/Projects/Crime Incidents Philadelphia/analysis/spatial_analysis.py`, `/Users/dustinober/Projects/Crime Incidents Philadelphia/analysis/red_zones.py`
- Cause: Simple random sampling may not preserve important distributions
- Improvement path: Implement stratified sampling by crime type, district, or time period

**DBSCAN Performance with Haversine Distance:**
- Problem: Clustering large geographic dataset is computationally expensive
- Files: `/Users/dustinober/Projects/Crime Incidents Philadelphia/analysis/utils.py` (dbscan_clustering function)
- Cause: Haversine distance calculation is O(n²) for pairwise distances
- Improvement path: Consider approximate nearest neighbor algorithms or spatial indexing

## Fragile Areas

**Dataset Schema Dependencies:**
- Files: All analysis modules
- Why fragile: Direct column name dependencies without robust fallback
- Safe modification: Use the column detection pattern from CLAUDE.md
- Test coverage: High - used in all analyses, but no validation tests

**Color Scheme Management:**
- Files: `/Users/dustinober/Projects/Crime Incidents Philadelphia/analysis/config.py`
- Why fragile: Hard-coded color strings with no validation
- Safe modification: Create color palette class with validation
- Test coverage: Low - only referenced in plots

## Scaling Limits

**Processing Time for Full Dataset:**
- Current capacity: ~5-10 minutes per analysis on modern hardware
- Limit: DBSCAN clustering becomes impractical beyond ~500K records
- Scaling path: Implement distributed processing with Dask or PySpark

**Memory Usage:**
- Current capacity: ~8GB RAM for full dataset processing
- Limit: Analysis fails on systems with <4GB available RAM
- Scaling path: Implement out-of-core processing for large datasets

## Dependencies at Risk

**Outdated Visualization Libraries:**
- Risk: Matplotlib/seaborn updates could break custom plot styling
- Impact: All visualizations may need redesign
- Migration plan: Create plotting abstraction layer with version tolerance

**Pandas Version Dependency:**
- Risk: Future pandas versions may change DataFrame behavior
- Impact: All data processing could break
- Migration plan: Pin pandas version and create compatibility layer

## Missing Critical Features

**Error Handling and Recovery:**
- Problem: No graceful handling of missing or corrupted data files
- Blocks: Automated pipeline execution
- Priority: High

**Progress Indicators for Large Operations:**
- Problem: Long-running operations (DBSCAN, large aggregations) provide no feedback
- Blocks: User experience during large analyses
- Priority: Medium

## Test Coverage Gaps

**Input Validation Tests:**
- What's not tested: Edge cases in coordinate validation, malformed datetime parsing
- Files: `/Users/dustinober/Projects/Crime Incidents Philadelphia/analysis/utils.py`
- Risk: Invalid data could cause silent failures or incorrect results
- Priority: High

**Statistical Accuracy Tests:**
- What's not tested: Statistical significance of trends, proper handling of small sample sizes
- Files: All analysis modules
- Risk: May report statistically insignificant findings as significant
- Priority: Medium

---

*Concerns audit: 2026-01-30*