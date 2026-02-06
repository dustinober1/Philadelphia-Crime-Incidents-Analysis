# Requirements: Crime Incidents Philadelphia

**Defined:** 2026-02-04
**Core Value:** Provide clear, reproducible, evidence-based answers to policy and operations questions about crime in Philadelphia

## v1.1 Requirements

### Architecture (ARCH)

- [ ] **ARCH-01**: Create module-based structure under `analysis/` with separate submodules for each analysis category (trends, spatial, policy, forecasting)
- [ ] **ARCH-02**: Extract reusable utility functions from notebooks into dedicated modules (data, visualization, validation, metrics)
- [ ] **ARCH-03**: Implement new data layer (`analysis/data/`) to replace `analysis.utils.load_data()` with cleaner API
- [ ] **ARCH-04**: Create CLI entry points for each analysis using typer (13 scripts matching notebook count)
- [ ] **ARCH-05**: Implement Rich/typer progress bars and console output for long-running operations
- [ ] **ARCH-06**: Design configuration system with CLI args for runtime and YAML files for defaults

### Configuration (CONFIG)

- [ ] **CONFIG-01**: Create `config/` directory with separate YAML files for each analysis (trends.yaml, hotspots.yaml, etc.)
- [ ] **CONFIG-02**: Define schema for all config files using pydantic for validation
- [ ] **CONFIG-03**: Implement CLI argument parsing with typer, overriding YAML defaults
- [ ] **CONFIG-04**: Create global config file for shared parameters (data paths, output directories, logging level)
- [ ] **CONFIG-05**: Implement environment variable support for sensitive parameters (API keys, paths)

### Data Layer (DATA)

- [ ] **DATA-01**: Create `analysis/data/` module with functions for loading crime data, external data, and boundary data
- [ ] **DATA-02**: Implement data validation functions to check for missingness, date ranges, coordinate validity
- [ ] **DATA-03**: Create data preprocessing utilities (filtering, aggregation, merging)
- [ ] **DATA-04**: Implement caching layer for expensive data operations
- [ ] **DATA-05**: Create test fixtures for sample data in `tests/fixtures/`

### Visualization (VIZ)

- [ ] **VIZ-01**: Extract visualization utilities into `analysis/visualization/` module
- [ ] **VIZ-02**: Support multiple output formats (PNG, SVG, HTML, JSON) via CLI argument
- [ ] **VIZ-03**: Implement consistent styling using existing color palettes from `analysis.config.COLORS`
- [ ] **VIZ-04**: Create publication-quality output (300 DPI) for all figures
- [ ] **VIZ-05**: Save figures to `reports/` with configurable naming conventions

### Testing (TEST)

- [ ] **TEST-01**: Set up pytest framework with 90%+ coverage target
- [ ] **TEST-02**: Write unit tests for all utility functions in `analysis/utils/`
- [ ] **TEST-03**: Write unit tests for data layer functions (loading, validation, preprocessing)
- [ ] **TEST-04**: Write end-to-end tests for each CLI script (13 scripts)
- [ ] **TEST-05**: Create test fixtures for sample data and expected outputs
- [ ] **TEST-06**: Implement pytest-cov for coverage reporting
- [ ] **TEST-07**: Create integration tests that validate outputs against notebook-generated artifacts
- [ ] **TEST-08**: Add pre-commit hooks for linting and testing

### Documentation (DOCS)

- [ ] **DOCS-01**: Update AGENTS.md to reflect script-based workflow (replace notebook rules with script rules)
- [ ] **DOCS-02**: Create CLI help documentation (typer auto-generates)
- [ ] **DOCS-03**: Write module docstrings for all new modules
- [ ] **DOCS-04**: Create migration guide for converting notebooks to scripts
- [ ] **DOCS-05**: Update README.md with script-based examples

### Migration (MIGRATE)

- [ ] **MIGRATE-01**: Convert Chief (3 notebooks): trends, seasonality, COVID → CLI scripts
- [ ] **MIGRATE-02**: Convert Patrol (4 notebooks): hotspots, robbery heatmap, district severity, census rates → CLI scripts
- [ ] **MIGRATE-03**: Convert Policy (4 notebooks): retail theft, vehicle crimes, composition, events → CLI scripts
- [ ] **MIGRATE-04**: Convert Forecasting (2 notebooks): time series, classification, heat-crime → CLI scripts
- [ ] **MIGRATE-05**: Verify all converted scripts produce identical outputs to notebooks (within tolerance)
- [ ] **MIGRATE-06**: Delete notebooks after successful conversion and verification
- [ ] **MIGRATE-07**: Update PROJECT.md to reflect script-based architecture
- [ ] **MIGRATE-08**: Update ROADMAP.md to remove notebook-based workflow references

### Quality & Standards (QUAL)

- [x] **QUAL-01**: Add type hints to all functions (mypy compatible)
- [x] **QUAL-02**: Follow PEP 8 code style with black formatter
- [x] **QUAL-03**: Add docstrings to all functions following Google or NumPy style
- [x] **QUAL-04**: Add ruff/flake8 for linting
- [x] **QUAL-05**: Create requirements-dev.txt for development dependencies (pytest, black, ruff, mypy, typer, rich, pydantic)
- [x] **QUAL-06**: Add pre-commit configuration (black, ruff, mypy, pytest)

## v2 Requirements

- (deferred items such as interactive dashboards, real-time alerts, additional ML models)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Keeping notebooks as production tools | Milestone goal is script-based architecture |
| Notebooks as development documentation | Delete after conversion |
| Rewriting algorithms | Existing analysis logic is preserved, only structure changes |
| New analysis capabilities | Focus on conversion, not new features |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ARCH-01 | Phase 5 | ✅ Complete |
| ARCH-02 | Phase 5 | ✅ Complete |
| ARCH-03 | Phase 5 | ✅ Complete |
| ARCH-04 | Phase 6 | ✅ Complete |
| ARCH-05 | Phase 6 | ✅ Complete |
| ARCH-06 | Phase 6 | ✅ Complete |
| CONFIG-01 | Phase 6 | ✅ Complete |
| CONFIG-02 | Phase 6 | ✅ Complete |
| CONFIG-03 | Phase 6 | ✅ Complete |
| CONFIG-04 | Phase 6 | ✅ Complete |
| CONFIG-05 | Phase 6 | ✅ Complete |
| DATA-01 | Phase 5 | ✅ Complete |
| DATA-02 | Phase 5 | ✅ Complete |
| DATA-03 | Phase 5 | ✅ Complete |
| DATA-04 | Phase 5 | ✅ Complete |
| DATA-05 | Phase 7 | ✅ Complete |
| VIZ-01 | Phase 7 | ✅ Complete |
| VIZ-02 | Phase 7 | ✅ Complete |
| VIZ-03 | Phase 7 | ✅ Complete |
| VIZ-04 | Phase 7 | ✅ Complete |
| VIZ-05 | Phase 7 | ✅ Complete |
| TEST-01 | Phase 7 | ✅ Complete |
| TEST-02 | Phase 7 | ✅ Complete |
| TEST-03 | Phase 7 | ✅ Complete |
| TEST-04 | Phase 7 | ✅ Complete |
| TEST-05 | Phase 7 | ✅ Complete |
| TEST-06 | Phase 7 | ✅ Complete |
| TEST-07 | Phase 7 | ✅ Complete |
| TEST-08 | Phase 7 | ✅ Complete |
| DOCS-01 | Phase 8 | ✅ Complete | |
| DOCS-02 | Phase 8 | ✅ Complete | |
| DOCS-03 | Phase 8 | ✅ Complete | |
| DOCS-04 | Phase 8 | ✅ Complete | |
| DOCS-05 | Phase 8 | ✅ Complete | |
| MIGRATE-01 | Phase 8 | ✅ Complete | |
| MIGRATE-02 | Phase 8 | ✅ Complete | |
| MIGRATE-03 | Phase 8 | ✅ Complete | |
| MIGRATE-04 | Phase 8 | ✅ Complete | |
| MIGRATE-05 | Phase 8 | ✅ Complete | |
| MIGRATE-06 | Phase 8 | ✅ Complete | |
| MIGRATE-07 | Phase 8 | ✅ Complete | |
| MIGRATE-08 | Phase 8 | ✅ Complete | |

**Coverage:**
- v1.1 requirements: 46 total
- Mapped to phases: 46 ✓
- Unmapped: 0

---
*Requirements defined: 2026-02-04*
