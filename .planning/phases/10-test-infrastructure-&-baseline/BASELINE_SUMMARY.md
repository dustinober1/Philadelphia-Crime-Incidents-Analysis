# Phase 10 Coverage Baseline

**Measured:** 2026-02-07

## Overall Metrics

- Total Coverage: 0%
- Total Statements: 2528
- Covered Statements: 0
- Missed Statements: 2528
- Coverage Gap to Target: 95%

## Per-Module Breakdown

### Analysis Modules (36 modules, 2175 statements)

**CLI Commands (5 modules, 711 statements)**
- analysis/cli/chief.py: 0% (164 statements)
- analysis/cli/patrol.py: 0% (221 statements)
- analysis/cli/policy.py: 0% (165 statements)
- analysis/cli/forecasting.py: 0% (133 statements)
- analysis/cli/main.py: 0% (28 statements)

**Data Processing (4 modules, 159 statements)**
- analysis/data/loading.py: 0% (55 statements)
- analysis/data/validation.py: 0% (64 statements)
- analysis/data/preprocessing.py: 0% (25 statements)
- analysis/data/cache.py: 0% (15 statements)

**Models (3 modules, 178 statements)**
- analysis/models/classification.py: 0% (70 statements)
- analysis/models/validation.py: 0% (60 statements)
- analysis/models/time_series.py: 0% (48 statements)

**Visualization (4 modules, 212 statements)**
- analysis/visualization/forecast_plots.py: 0% (146 statements)
- analysis/visualization/plots.py: 0% (38 statements)
- analysis/visualization/spatial_plots.py: 0% (9 statements)
- analysis/visualization/style.py: 0% (19 statements)

**Utilities (3 modules, 96 statements)**
- analysis/spatial_utils.py: 0% (75 statements)
- analysis/utils/spatial.py: 0% (69 statements)
- analysis/utils/temporal.py: 0% (14 statements)
- analysis/utils/classification.py: 0% (13 statements)

**Configuration (7 modules, 253 statements)**
- analysis/phase2_config_loader.py: 0% (70 statements)
- analysis/config_loader.py: 0% (56 statements)
- analysis/phase3_config_loader.py: 0% (31 statements)
- analysis/config/settings.py: 0% (30 statements)
- analysis/config/schemas/patrol.py: 0% (32 statements)
- analysis/config/schemas/policy.py: 0% (30 statements)
- analysis/config/schemas/chief.py: 0% (20 statements)
- analysis/config/schemas/forecasting.py: 0% (15 statements)
- analysis/config.py: 0% (10 statements)

**Core Analysis (5 modules, 342 statements)**
- analysis/validate_phase3.py: 0% (106 statements)
- analysis/event_utils.py: 0% (66 statements)
- analysis/artifact_manager.py: 0% (28 statements)
- analysis/report_utils.py: 0% (47 statements)

### API Modules (7 modules, 307 statements)

**Main Application**
- api/main.py: 0% (61 statements)

**Routers (6 modules, 246 statements)**
- api/routers/questions.py: 0% (163 statements)
- api/routers/trends.py: 0% (30 statements)
- api/routers/policy.py: 0% (17 statements)
- api/routers/spatial.py: 0% (17 statements)
- api/routers/forecasting.py: 0% (11 statements)
- api/routers/metadata.py: 0% (8 statements)

### Pipeline Modules (2 modules, 249 statements)

- pipeline/export_data.py: 0% (197 statements)
- pipeline/refresh_data.py: 0% (52 statements)

## Testing Priorities

### Tier 1 (0% coverage): 46 modules requiring initial tests

**High Priority (frequently used, high impact)**
1. analysis/data/loading.py - Data loading is fundamental
2. analysis/data/validation.py - Validation prevents bugs
3. analysis/data/preprocessing.py - Data quality is critical
4. analysis/spatial_utils.py - Used across analysis
5. analysis/event_utils.py - Used across analysis

**Medium Priority (user-facing)**
6. api/main.py - API entry point
7. api/routers/questions.py - Largest API router
8. analysis/cli/main.py - CLI entry point
9. analysis/cli/policy.py - Policy commands
10. pipeline/export_data.py - Data export functionality

**Lower Priority (supporting code)**
11. analysis/config_loader.py - Configuration management
12. analysis/models/* - Classification and time series models
13. analysis/visualization/* - Plotting functions

### Tier 2 (1-50% coverage): 0 modules needing expansion

### Tier 3 (51-80% coverage): 0 modules near completion

## Progress Tracking

**Baseline established:** 2026-02-07
**Starting coverage:** 0%
**Target coverage:** 95%
**Gap to close:** 95 percentage points (2528 statements)

**Next steps:**
1. Phase 11: Write tests for core modules (data, utils, models)
2. Phase 12: Write tests for API & CLI
3. Phase 13: Write tests for pipeline & support modules

## Comparison Commands

To track progress against this baseline:

```bash
# Compare current coverage to baseline
coverage report > .planning/phases/10-test-infrastructure-&-baseline/coverage-current.txt
diff .planning/phases/10-test-infrastructure-&-baseline/coverage-modules.txt \
     .planning/phases/10-test-infrastructure-&-baseline/coverage-current.txt

# Generate diff coverage report
diff-cover coverage.xml --compare-branch=HEAD \
  --fail-under=95 \
  --coverage-report-format=xml
```

## Files Generated

- `.coverage.baseline` - Coverage data file snapshot
- `coverage.baseline.xml` - XML report for diff-cover
- `coverage-baseline.json` - Machine-readable coverage data
- `coverage-baseline.txt` - Full pytest coverage output
- `coverage-modules.txt` - Per-module breakdown sorted by coverage
- `uncovered-modules.txt` - Categorized list with testing priorities
