# Phase 1 Plan: Infrastructure & Configuration
**Wave:** 1  
**Depends on:** None  
**Files modified:** `analysis/`, `config/`, `pyproject.toml`  
**Autonomous:** Yes  

---

## Goal
Create the foundational infrastructure needed for Phase 1: external configuration system, analysis module, and orchestration framework. This wave establishes the scaffolding that all three notebooks will use.

---

## Tasks

### TASK-1.1: Create Analysis Module Structure
**Objective:** Scaffold the `analysis/` Python package with shared utilities for data loading and crime classification.

<requirements>
- Create `analysis/__init__.py` to make it a package
- Create `analysis/config.py` with data paths and color palette constants
- Create `analysis/utils.py` with core functions: `load_data()`, `classify_crime_category()`, `extract_temporal_features()`
- Ensure functions match the import signatures used in existing notebooks
- Add docstrings following NumPy style
</requirements>

<acceptance>
- `analysis/` directory exists with all three files
- Can successfully import: `from analysis.config import CRIME_DATA_PATH, COLORS`
- Can successfully import: `from analysis.utils import load_data, classify_crime_category, extract_temporal_features`
- All functions have type hints and docstrings
- `load_data()` successfully loads the parquet file and returns a DataFrame
</acceptance>

<files>
- CREATE: `analysis/__init__.py`
- CREATE: `analysis/config.py`
- CREATE: `analysis/utils.py`
</files>

---

### TASK-1.2: Create External Configuration System
**Objective:** Build YAML-based configuration system with parameters for all three notebooks, supporting versioning and artifact management.

<requirements>
- Create `config/` directory structure
- Create `config/phase1_config.yaml` with sections for: environment, notebooks (annual_trend, seasonality, covid), each with params and output definitions
- Include parameters for: date ranges, statistical thresholds, COVID period definitions, output paths
- Support version interpolation in artifact names (e.g., `{version}`)
- Create `analysis/config_loader.py` with `Phase1Config` class to parse YAML and provide helper methods
- Add schema validation (basic checks: required keys present, valid date formats)
</requirements>

<acceptance>
- `config/phase1_config.yaml` exists with all three notebook configurations
- `analysis/config_loader.py` can parse the YAML without errors
- `Phase1Config.get_notebook_params('annual_trend')` returns dict with expected keys
- `Phase1Config.get_output_path('annual_trend', 'png', version='v1.0')` returns correctly formatted path
- Config includes all parameters currently hardcoded in notebooks (start_year, end_year, summer_months, lockdown_date, etc.)
</acceptance>

<files>
- CREATE: `config/phase1_config.yaml`
- CREATE: `analysis/config_loader.py`
</files>

<context>
Key parameters to externalize (from research):
- Annual Trend: start_year=2015, end_year=2024 (exclude 2026), min_complete_months=12
- Seasonality: summer_months=[6,7,8], winter_months=[1,2,3], significance_level=0.05
- COVID: lockdown_date="2020-03-01", before_years=[2018,2019], during_years=[2020,2021], after_start_year=2023
</context>

---

### TASK-1.3: Implement Artifact Versioning System
**Objective:** Create artifact management utilities to handle versioned outputs and manifest generation.

<requirements>
- Create `analysis/artifact_manager.py` with functions for versioning and manifest creation
- Implement `create_version_manifest()` that generates JSON manifest with: version, timestamp, git commit, artifact list (with SHA256), parameters used, runtime stats
- Implement `get_versioned_path()` helper for consistent path generation
- Add git commit hash extraction (fallback gracefully if not in git repo)
- Support both semantic versioning (v1.0) and timestamp versioning
</requirements>

<acceptance>
- `analysis/artifact_manager.py` exists with documented functions
- `create_version_manifest()` generates valid JSON matching schema in research doc
- Manifest includes git commit hash when available
- `get_versioned_path('reports/trend_{version}.png', 'v1.0')` returns `reports/trend_v1.0.png`
- Can compute SHA256 hashes for generated files
</acceptance>

<files>
- CREATE: `analysis/artifact_manager.py`
</files>

---

### TASK-1.4: Build Orchestration Script
**Objective:** Create Python orchestrator that executes all three notebooks headlessly using papermill, with error handling and logging.

<requirements>
- Create `analysis/orchestrate_phase1.py` as main execution script
- Use papermill to execute each notebook with parameter injection
- Support command-line arguments: --version, --config-path, --fast (sample mode), --notebook (run specific notebook only)
- Implement logging to both console and file (`reports/execution.log`)
- Add error handling with descriptive messages
- Track execution time per notebook
- Generate execution manifest at completion
- Create `reports/` directory if it doesn't exist
</requirements>

<acceptance>
- `analysis/orchestrate_phase1.py` exists and is executable
- Running `python analysis/orchestrate_phase1.py` executes all three notebooks successfully
- Logs show clear progress: "Starting annual_trend...", "Completed in 15.2s", etc.
- `--notebook annual_trend` runs only that notebook
- `--fast` flag passes sample parameter to notebooks
- Execution manifest JSON is generated in `reports/`
- Script exits with code 0 on success, non-zero on failure
</acceptance>

<files>
- CREATE: `analysis/orchestrate_phase1.py`
</files>

<context>
Notebook paths (from research):
- notebooks/philadelphia_safety_trend_analysis.ipynb (annual_trend)
- notebooks/summer_crime_spike_analysis.ipynb (seasonality)
- notebooks/covid_lockdown_crime_landscape.ipynb (covid)
</context>

---

### TASK-1.5: Create Report Template System
**Objective:** Build Jinja2-based markdown report template for consistent academic-style output format across all analyses.

<requirements>
- Create `config/report_template.md.j2` Jinja2 template
- Include sections: Summary, Methods, Findings, Data Quality Summary, Limitations, Technical Details
- Support variable injection: timestamp, version, data_range, n_records, findings_content
- Create `analysis/report_utils.py` with helper functions: `generate_data_quality_summary()`, `render_report_template()`
- Add data quality table generator that checks for: missing dates, duplicates, partial year data
</requirements>

<acceptance>
- `config/report_template.md.j2` exists with all required sections
- Template renders correctly with sample data
- `generate_data_quality_summary(df)` returns dict with quality metrics
- `render_report_template(template_path, context)` returns formatted markdown string
- Generated report includes generation timestamp in header
- Report format matches academic style from research doc
</acceptance>

<files>
- CREATE: `config/report_template.md.j2`
- CREATE: `analysis/report_utils.py`
</files>

---

### TASK-1.6: Update Project Dependencies
**Objective:** Ensure all required dependencies are documented and installation is reproducible.

<requirements>
- Verify papermill, pyyaml, jinja2 are in requirements.txt (already installed per research)
- Create `pyproject.toml` for modern Python dependency management (optional but recommended)
- Document Phase 1 execution in README.md with usage examples
- Add section "Running Phase 1 Analyses" with orchestrator usage
</requirements>

<acceptance>
- `requirements.txt` includes papermill, pyyaml, jinja2 with version pins
- README.md has "Running Phase 1 Analyses" section with clear examples
- Documentation shows how to run: all notebooks, single notebook, with custom config
- Installation instructions are accurate
</acceptance>

<files>
- UPDATE: `requirements.txt` (if needed)
- UPDATE: `README.md`
- CREATE: `pyproject.toml` (optional)
</files>

---

## Verification Criteria

### Must-Have Outcomes
1. **Functional analysis module**: Can import all shared utilities without errors
2. **External configuration**: All notebook parameters are in `config/phase1_config.yaml`, not hardcoded
3. **Headless execution**: `python analysis/orchestrate_phase1.py` runs successfully and generates artifacts
4. **Artifact versioning**: Manifests are generated with version, timestamp, git hash, and file hashes
5. **Report templates**: Jinja2 template exists and can render markdown reports

### Success Metrics
- Zero import errors when loading analysis module
- Orchestrator completes all three notebooks in < 5 minutes
- All artifacts saved to `reports/` with versioned names
- Execution log contains clear progress indicators
- Manifest JSON is valid and contains all required fields

### Quality Checks
- [ ] All Python modules have `__init__.py`
- [ ] All functions have type hints and docstrings
- [ ] YAML config is valid and parseable
- [ ] Orchestrator has proper error handling (try/except with logging)
- [ ] File paths use `pathlib.Path` (not string concatenation)
- [ ] Colorblind-safe palette is defined in config.py
- [ ] Git commit hash extraction fails gracefully if not in repo

---

## Dependencies
- **External**: papermill, pyyaml, jinja2 (already installed)
- **Data**: `data/crime_incidents_combined.parquet` (already exists)
- **Blocks**: None (Wave 1 - can proceed immediately)

---

## Estimated Effort
**Time:** 4-6 hours  
**Complexity:** Medium (scaffolding, no complex algorithms)

---

## Notes
- This infrastructure wave is foundational; subsequent waves (notebook refactoring) depend on it
- Focus on clean interfaces: notebooks should only need to import and call functions
- Error messages should be descriptive (e.g., "Config file not found at config/phase1_config.yaml")
- The orchestrator should handle partial failures gracefully (log error, continue with next notebook if --continue flag is set)
