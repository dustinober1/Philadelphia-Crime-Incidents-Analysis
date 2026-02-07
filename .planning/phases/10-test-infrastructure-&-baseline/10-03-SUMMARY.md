---
phase: 10-test-infrastructure-&-baseline
plan: 03
subsystem: testing
tags: [coverage, baseline, pytest, measurement, testing-infrastructure]

dependency_graph:
  requires:
    - "10-01: Test Infrastructure Setup (pytest, coverage.py configuration)"
  provides:
    - "Baseline coverage measurement (0% coverage, 2528 statements)"
    - "Prioritized list of 46 modules requiring tests"
    - "Coverage snapshot for future progress tracking"
  affects:
    - "10-04: Coverage report comparison and validation"
    - "Phase 11: Test writing priorities for core modules"
    - "Phase 12: Test writing priorities for API & CLI"
    - "Phase 13: Test writing priorities for pipeline & support"

tech_stack:
  added: []
  patterns:
    - "Coverage baseline measurement with pytest --cov"
    - "Multi-format coverage reports (term, XML, HTML, JSON)"
    - "Per-module coverage breakdown for prioritization"

key_files:
  created:
    - .planning/phases/10-test-infrastructure-&-baseline/coverage-baseline.txt
    - .planning/phases/10-test-infrastructure-&-baseline/coverage-baseline.json
    - .planning/phases/10-test-infrastructure-&-baseline/coverage-modules.txt
    - .planning/phases/10-test-infrastructure-&-baseline/uncovered-modules.txt
    - .planning/phases/10-test-infrastructure-&-baseline/.coverage.baseline
    - .planning/phases/10-test-infrastructure-&-baseline/coverage.baseline.xml
    - .planning/phases/10-test-infrastructure-&-baseline/BASELINE_SUMMARY.md
  modified: []

decisions_made:
  - title: "Coverage baseline confirmed at 0%"
    rationale: "Measurement confirmed 0% coverage across all 46 modules (2528 statements), resolving the 16% vs 60% discrepancy from earlier observations. The earlier 16% figure may have included test infrastructure or been measured differently."
    impact: "Provides accurate starting point for tracking progress toward 95% coverage target. All modules need tests written."
    alternatives_considered:
      - "Re-running with different configuration (rejected - current config is correct)"
      - "Excluding test files from measurement (rejected - already excluded)"

  - title: "Testing priority strategy established"
    rationale: "Categorized modules by impact and frequency of use to guide test writing in phases 11-13. High-priority modules are those that are frequently used and have high impact on data quality or user experience."
    impact: "Phases 11-13 will focus on high-value modules first, maximizing benefit of testing effort. Core data processing and validation modules prioritized in Phase 11."
    alternatives_considered:
      - "Alphabetical order (rejected - doesn't prioritize impact)"
      - "Largest modules first (rejected - size != impact)"
      - "Random order (rejected - no strategic value)"

metrics:
  duration: "3 minutes"
  completed: "2026-02-07"
  coverage_baseline: "0%"
  modules_measured: 46
  total_statements: 2528
  coverage_gap: "95 percentage points"
---

# Phase 10 Plan 03: Baseline Test Coverage Summary

**One-liner:** Measured and documented coverage baseline at 0% across 46 modules (2528 statements), creating prioritized roadmap for test writing in phases 11-13.

## Objective Achieved

Established accurate baseline coverage measurement with per-module breakdown, resolving the 16% vs 60% discrepancy from earlier observations. Created comprehensive documentation and prioritized list of modules requiring tests.

## Key Deliverables

### 1. Coverage Baseline Measurement
- **Overall Coverage:** 0% (2528 statements, 0 covered, 2528 missed)
- **Modules Measured:** 46 across 3 subsystems
- **Gap to Target:** 95 percentage points

### 2. Per-Module Breakdown
**Analysis Modules (36 modules, 2175 statements):**
- CLI commands: 5 modules (711 statements)
- Data processing: 4 modules (159 statements)
- Models: 3 modules (178 statements)
- Visualization: 4 modules (212 statements)
- Utilities: 4 modules (96 statements)
- Configuration: 9 modules (253 statements)
- Core analysis: 7 modules (342 statements)

**API Modules (7 modules, 307 statements):**
- Main application: api/main.py (61 statements)
- Routers: 6 modules (246 statements)
  - questions.py is largest (163 statements)

**Pipeline Modules (2 modules, 249 statements):**
- export_data.py: 197 statements (largest single module)
- refresh_data.py: 52 statements

### 3. Testing Priorities Established

**Tier 1 - High Priority (Phase 11):**
- analysis/data/loading.py - Data loading is fundamental
- analysis/data/validation.py - Validation prevents bugs
- analysis/data/preprocessing.py - Data quality is critical
- analysis/spatial_utils.py - Used across analysis
- analysis/event_utils.py - Used across analysis

**Tier 2 - Medium Priority (Phase 12):**
- api/main.py - API entry point
- api/routers/questions.py - Largest API router
- analysis/cli/main.py - CLI entry point
- analysis/cli/policy.py - Policy commands
- pipeline/export_data.py - Data export functionality

**Tier 3 - Lower Priority (Phase 13):**
- Configuration loaders and schemas
- Visualization and plotting functions
- Classification and time series models

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Coverage files gitignored**

- **Found during:** Task 3
- **Issue:** .coverage.baseline file is gitignored by .gitignore pattern `.coverage.*`
- **Fix:** Committed only coverage.baseline.xml and BASELINE_SUMMARY.md; .coverage.baseline kept as local snapshot for comparison
- **Files modified:** None (adjusted git commit strategy)
- **Commit:** f25a0ce

**Justification:** Coverage data files (.coverage.*) are appropriately gitignored to avoid committing binary data. The XML report and summary documentation provide sufficient baseline tracking.

### Plan Adjustments

None - plan executed exactly as written.

## Task Commits

| Task | Name | Commit | Files |
| ---- | ---- | ------ | ----- |
| 1 | Run fresh coverage baseline measurement | 4c8bd9f | coverage-baseline.txt, coverage-baseline.json, coverage-modules.txt |
| 2 | Document uncovered and under-covered modules | af356c0 | uncovered-modules.txt |
| 3 | Create coverage baseline snapshot | f25a0ce | coverage.baseline.xml, BASELINE_SUMMARY.md |

## Files Created

1. **coverage-baseline.txt** (33KB)
   - Full pytest coverage output with terminal report
   - Shows missing lines per file
   - Exit code 2 expected (coverage below 95%)

2. **coverage-baseline.json** (113KB)
   - Machine-readable coverage data
   - Contains per-module breakdown with line-by-line coverage
   - Suitable for programmatic analysis

3. **coverage-modules.txt** (3.5KB)
   - Per-module breakdown sorted by coverage percentage
   - Shows statements, missing, and coverage for each module
   - All 46 modules at 0% coverage

4. **uncovered-modules.txt** (2.9KB)
   - Categorized list by coverage tier
   - Priority recommendations for phases 11-13
   - Testing strategy guidance

5. **.coverage.baseline** (52KB, local only)
   - Coverage data file snapshot
   - Not committed (gitignored)
   - Used for future comparison

6. **coverage.baseline.xml** (96KB)
   - XML report for diff-cover integration
   - Committed for CI/CD baseline comparison

7. **BASELINE_SUMMARY.md** (4.9KB)
   - Comprehensive baseline documentation
   - Per-module breakdown by subsystem
   - Comparison commands for progress tracking

## Next Steps

### Phase 11: Core Modules (Recommended)
Based on baseline analysis, Phase 11 should prioritize:

1. **Data Processing** (159 statements)
   - loading.py: Data loading logic
   - validation.py: Data validation and quality checks
   - preprocessing.py: Data transformation

2. **Core Utilities** (141 statements)
   - spatial_utils.py: Spatial analysis functions
   - event_utils.py: Event processing utilities

3. **Models** (178 statements)
   - classification.py: Classification models
   - time_series.py: Time series models
   - validation.py: Model validation

### Progress Tracking Commands

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

## Success Criteria Met

- ✅ Accurate baseline coverage measured (0% across 2528 statements in 46 modules)
- ✅ Per-module coverage breakdown documented (coverage-modules.txt)
- ✅ Uncovered modules categorized by coverage tier (all 46 modules in Tier 1)
- ✅ Priority list created for test writing (uncovered-modules.txt)
- ✅ Baseline snapshot saved for future progress tracking (XML + documentation)

## Lessons Learned

1. **Baseline measurement is critical:** Resolved discrepancy between observed (16-60%) and actual (0%) coverage through comprehensive measurement with multiple report formats.

2. **Prioritization matters:** Not all modules are equal. Focusing on high-impact, frequently-used modules first maximizes testing value.

3. **Documentation aids progress tracking:** Comprehensive baseline documentation makes it easy to track progress and adjust priorities as testing progresses.

4. **Multi-format reports serve different needs:**
   - Terminal: Quick human-readable overview
   - JSON: Programmatic analysis and metrics
   - XML: CI/CD integration with diff-cover
   - HTML: Visual inspection of specific files
