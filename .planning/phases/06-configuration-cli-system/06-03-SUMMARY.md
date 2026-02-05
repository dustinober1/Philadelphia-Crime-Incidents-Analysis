---
phase: 06-configuration-cli-system
plan: 03
subsystem: cli
tags: typer, rich, cli-architecture, command-groups

# Dependency graph
requires:
  - phase: 06-configuration-cli-system
    plan: 02
    provides: Configuration schemas (TrendsConfig, SeasonalityConfig, etc.)
provides:
  - CLI package structure with 4 command groups
  - 13 placeholder commands with argument parsing
  - Entry point for python -m analysis.cli
affects:
  - Phase 06-04 through 06-07 (command implementation plans)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Typer command groups using app.add_typer()"
    - "Kebab-case command names for multi-word commands"
    - "Rich console for formatted output"

key-files:
  created:
    - analysis/cli/__init__.py
    - analysis/cli/__main__.py
    - analysis/cli/main.py
    - analysis/cli/chief.py
    - analysis/cli/patrol.py
    - analysis/cli/policy.py
    - analysis/cli/forecasting.py
  modified: []

key-decisions:
  - "Use fast flag as CLI-only parameter, not stored in config (BaseConfig has fast_sample_frac instead)"
  - "Kebab-case command names (robbery-heatmap, district-severity, retail-theft) for CLI consistency"
  - "Placeholder commands with TODO comments indicating implementation plan"

patterns-established:
  - "Pattern 1: Each command group is a separate typer.Typer() app"
  - "Pattern 2: Commands use config schemas for validation, fast flag is CLI-only"
  - "Pattern 3: Rich console with colored output for better UX"

# Metrics
duration: 11min
completed: 2026-02-05
---

# Phase 6 Plan 3: Modular CLI Structure Summary

**Typer-based CLI with 4 command groups and 13 placeholder commands using Rich console for formatted output**

## Performance

- **Duration:** 11 min
- **Started:** 2026-02-05T00:46:23Z
- **Completed:** 2026-02-05T00:57:25Z
- **Tasks:** 4
- **Files modified:** 7 files created

## Accomplishments
- Created complete CLI package structure with python -m analysis.cli entry point
- Implemented 4 command groups (chief, patrol, policy, forecasting) with proper typer apps
- Added 13 placeholder commands with CLI argument parsing and config validation
- Established kebab-case naming convention for multi-word commands

## Task Commits

Each task was committed atomically:

1. **Task 1: Create CLI package structure and main app** - `c24f05e` (feat)
2. **Task 2: Create Chief command group with 3 commands** - `2400cd0` (feat)
3. **Task 3: Create Patrol command group with 4 commands** - `19255f6` (feat)
4. **Task 4: Create Policy and Forecasting command groups** - `92a79c1` (feat)

**Plan metadata:** TBD (docs: complete plan)

## Files Created/Modified
- `analysis/cli/__init__.py` - Package exports with app
- `analysis/cli/__main__.py` - Module entry point for `python -m analysis.cli`
- `analysis/cli/main.py` - Main typer app with command groups, version/info commands
- `analysis/cli/chief.py` - Chief command group (trends, seasonality, covid)
- `analysis/cli/patrol.py` - Patrol command group (hotspots, robbery-heatmap, district-severity, census-rates)
- `analysis/cli/policy.py` - Policy command group (retail-theft, vehicle-crimes, composition, events)
- `analysis/cli/forecasting.py` - Forecasting command group (time-series, classification)

## Command Structure

### Chief (3 commands)
- `trends` - Annual crime trends with start_year, end_year, version, fast options
- `seasonality` - Seasonal patterns with summer_months, winter_months, version, fast options
- `covid` - COVID impact with lockdown_date, before_years, version, fast options

### Patrol (4 commands)
- `hotspots` - Spatial clustering with eps, min_samples, version, fast options
- `robbery-heatmap` - Temporal heatmap with time_bin, grid_size, version, fast options
- `district-severity` - Severity scores with districts, version, fast options
- `census-rates` - Census tract rates with population_threshold, version, fast options

### Policy (4 commands)
- `retail-theft` - Retail theft trends with baseline_start, baseline_end, version, fast options
- `vehicle-crimes` - Vehicle crime analysis with ucr_codes, start_date, end_date, version, fast options
- `composition` - Crime composition with top_n, version, fast options
- `events` - Event impact with days_before, days_after, version, fast options

### Forecasting (2 commands)
- `time-series` - Forecasting with horizon, model_type, version, fast options
- `classification` - Violence classification with test_size, random_state, version, fast options

## Decisions Made

### Decision 1: Fast flag is CLI-only, not stored in config
The plan specified passing `fast_mode` to config, but BaseConfig doesn't have that field - it has `fast_sample_frac` instead. The `fast` boolean flag is now a CLI-only parameter that controls behavior without modifying the config object.

**Rationale:** Config schemas don't have a `fast_mode` boolean field. The `fast` flag is better handled as a runtime flag that doesn't need persistence.

### Decision 2: Kebab-case command names for multi-word commands
Commands with multiple words use kebab-case (e.g., `robbery-heatmap`, `district-severity`, `retail-theft`) via typer's `name` parameter.

**Rationale:** Kebab-case is standard CLI convention for multi-word commands, better UX than snake_case or camelCase.

### Decision 3: Placeholder commands indicate implementation plan
Each command prints a yellow message indicating which plan will implement the logic (06-04 for chief, 06-05 for patrol, 06-06 for policy, 06-07 for forecasting).

**Rationale:** Clear communication to users about current implementation status.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed AttributeError: TrendsConfig has no attribute 'fast_mode'**
- **Found during:** Task 2 (Chief command group implementation)
- **Issue:** Plan specified passing `fast_mode=fast` to TrendsConfig, but BaseConfig doesn't have a `fast_mode` field (only `fast_sample_frac`)
- **Fix:** Removed `fast_mode` parameter from config initialization, kept `fast` as a CLI-only parameter that controls behavior at runtime
- **Files modified:** analysis/cli/chief.py
- **Verification:** Commands now execute without AttributeError, fast flag prints correctly
- **Committed in:** 2400cd0 (Task 2 commit)

**2. [Rule 1 - Bug] Applied same fix to seasonality and covid commands**
- **Found during:** Task 2 (same issue in other commands)
- **Issue:** Same `fast_mode` issue in seasonality and covid commands
- **Fix:** Removed `fast_mode` from config initialization in both commands
- **Files modified:** analysis/cli/chief.py
- **Verification:** All three chief commands work correctly
- **Committed in:** 2400cd0 (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 - bug fixes for same issue)
**Impact on plan:** Fixes were necessary for correct operation. The fast flag now works as a CLI-only parameter, which is actually cleaner than storing it in config.

## Issues Encountered

**Issue 1: Import order warnings from ruff**
- During commits, ruff reordered imports in main.py (chief, forecasting, patrol, policy alphabetically)
- Resolved: Pre-commit hook fixed automatically, no manual intervention needed

**Issue 2: Black formatting**
- During commits, black reformatted f-strings (removed f prefix where unnecessary)
- Resolved: Pre-commit hook fixed automatically

## Next Phase Readiness

**Ready for next phase:**
- CLI structure is complete and functional
- All 13 commands have proper argument parsing and help text
- Config integration is working (each command loads its respective config schema)
- Kebab-case naming convention established for multi-word commands

**Implementation plans ready:**
- 06-04: Chief command implementation (trends, seasonality, covid)
- 06-05: Patrol command implementation (hotspots, robbery-heatmap, district-severity, census-rates)
- 06-06: Policy command implementation (retail-theft, vehicle-crimes, composition, events)
- 06-07: Forecasting command implementation (time-series, classification)

**No blockers or concerns.**

---
*Phase: 06-configuration-cli-system*
*Completed: 2026-02-05*
