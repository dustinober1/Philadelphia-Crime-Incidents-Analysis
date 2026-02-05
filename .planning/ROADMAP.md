# ROADMAP: Crime Incidents Philadelphia

**v1.0 (Complete):** Phases 1-4 | **v1.1 (Active):** Phases 5-8

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | High-Level Trends & Seasonality | Establish baseline city-wide trends and seasonal patterns | CHIEF-01, CHIEF-02, CHIEF-03 | 4 | ✅ COMPLETE |
| 2 | Spatial & Socioeconomic Analysis | Identify where and why crimes concentrate | PATROL-01, PATROL-02, PATROL-03, HYP-SOCIO | 4 | ✅ COMPLETE |
| 3 | Policy Deep Dives & Event Impacts | Validate specific narratives and measure event impacts | POLICY-01, POLICY-02, POLICY-03, HYP-EVENTS | 4 | ✅ COMPLETE |
| 4 | Forecasting & Predictive Modeling | Build forecasts and classification models | FORECAST-01, FORECAST-02, HYP-HEAT | 4 | ✅ COMPLETE |
| 5 | Foundation Architecture | Establish module structure, data layer, and quality standards | ARCH-01, ARCH-02, ARCH-03, DATA-01, DATA-02, DATA-03, DATA-04, QUAL-01, QUAL-02, QUAL-03, QUAL-04, QUAL-05, QUAL-06 | 3 | ✅ COMPLETE |
| 6 | Configuration & CLI System | Build configuration system and CLI entry points | CONFIG-01, CONFIG-02, CONFIG-03, CONFIG-04, CONFIG-05, ARCH-04, ARCH-05, ARCH-06 | 5 | ✅ COMPLETE |
| 7 | Visualization & Testing | Implement visualization utilities and comprehensive testing | VIZ-01, VIZ-02, VIZ-03, VIZ-04, VIZ-05, TEST-01, TEST-02, TEST-03, TEST-04, TEST-05, TEST-06, TEST-07, TEST-08 | 5 | ⏸️ PENDING |
| 8 | Documentation & Migration | Document new workflow and migrate notebooks to scripts | DOCS-01, DOCS-02, DOCS-03, DOCS-04, DOCS-05, MIGRATE-01, MIGRATE-02, MIGRATE-03, MIGRATE-04, MIGRATE-05, MIGRATE-06, MIGRATE-07, MIGRATE-08 | 5 | ⏸️ PENDING |

---

## v1.0 Phases (Complete)

### Phase 1 — High-Level Trends & Seasonality ✅ COMPLETE
Goal: Produce audited, reproducible answers to: Is Philadelphia getting safer? Is there a summer spike? How did COVID change the landscape?
Requirements covered: CHIEF-01, CHIEF-02, CHIEF-03

### Phase 2 — Spatial & Socioeconomic Analysis ✅ COMPLETE
Goal: Identify hotspots, temporal hotspots for robbery, and per-tract crime rates normalized by population.
Requirements covered: PATROL-01, PATROL-02, PATROL-03, HYP-SOCIO

### Phase 3 — Policy Deep Dives & Event Impacts ✅ COMPLETE
Goal: Provide focused evidence on retail theft, vehicle crimes, and event-day effects to inform policy decisions.
Requirements covered: POLICY-01, POLICY-02, POLICY-03, HYP-EVENTS

### Phase 4 — Forecasting & Predictive Modeling ✅ COMPLETE
Goal: Deliver short-term forecasts and a violence-classification model with interpretable importances to support operational alerts and deeper research.
Requirements covered: FORECAST-01, FORECAST-02, HYP-HEAT

---

## v1.1 Phases (Active)

### Phase 5 — Foundation Architecture ✅ COMPLETE
**Goal:** Establish a robust module-based structure with data layer and quality standards to support script-based analysis
**Completed:** 2026-02-04

**Dependencies:** None (new infrastructure)

**Requirements covered:**
- Architecture: ARCH-01, ARCH-02, ARCH-03
- Data Layer: DATA-01, DATA-02, DATA-03, DATA-04
- Quality & Standards: QUAL-01, QUAL-02, QUAL-03, QUAL-04, QUAL-05, QUAL-06

**Success criteria:**
1. Developer can import utilities from `analysis.data` and `analysis.utils` to load and validate crime data with proper type hints
2. Developer can run all existing tests (pytest) and see 90%+ code coverage report for utility functions
3. Developer can use black, ruff, and mypy on codebase with zero violations in new modules
4. Developer can load cached data after first load using the new caching layer, with cache invalidated on data changes
5. Developer can write new modules that follow PEP 8 with docstrings and type hints, passing all pre-commit hooks

**Plans:**
- [x] 05-01-PLAN.md — Extract utilities into modular structure with type hints and docstrings
- [x] 05-02-PLAN.md — Implement data layer with loading, validation, preprocessing, and caching
- [x] 05-03-PLAN.md — Set up quality tools (pytest, mypy, black, ruff, pre-commit)
- [x] 05-04-PLAN.md — Fix mypy errors in data layer (gap closure)
- [x] 05-05-PLAN.md — Install dev dependencies and verify quality tools (gap closure)
- [x] 05-06-PLAN.md — Create tests for utils modules (gap closure)
- [x] 05-07-PLAN.md — Create tests for data layer modules (gap closure)

### Phase 6 — Configuration & CLI System ✅ COMPLETE
**Goal:** Build a flexible configuration system and CLI entry points for all 13 analyses with rich user feedback
**Completed:** 2026-02-04

**Dependencies:** Phase 5 (module structure must exist)

**Requirements covered:**
- Configuration: CONFIG-01, CONFIG-02, CONFIG-03, CONFIG-04, CONFIG-05
- Architecture: ARCH-04, ARCH-05, ARCH-06

**Success criteria:**
1. User can run `python -m analysis.cli --help` and see clear CLI arguments and documentation
2. User can override YAML config defaults with CLI arguments (e.g., `--output-format svg`)
3. User can see progress bars and status messages for long-running operations using Rich output
4. Developer can add a new analysis by creating a YAML config file and CLI script with pydantic validation
5. Developer can configure sensitive parameters via environment variables without committing them to code

**Plans:**
- [x] 06-01-PLAN.md — Install CLI dependencies (typer, rich, pydantic-settings)
- [x] 06-02-PLAN.md — Create configuration system with schemas and YAML files
- [x] 06-03-PLAN.md — Build CLI entry point structure with 4 command groups
- [x] 06-04-PLAN.md — Implement Chief commands (trends, seasonality, covid)
- [x] 06-05-PLAN.md — Implement Patrol commands (hotspots, robbery, district, census)
- [x] 06-06-PLAN.md — Implement Policy and Forecasting commands (6 commands)
- [x] 06-07-PLAN.md — Integrate Rich progress bars across all commands

### Phase 7 — Visualization & Testing ✅ COMPLETE
**Goal:** Implement comprehensive visualization utilities with multi-format output and complete testing coverage for all analysis scripts

**Completed:** 2026-02-05

**Dependencies:** Phase 5 (module structure) and Phase 6 (CLI configuration)

**Requirements covered:**
- Visualization: VIZ-01, VIZ-02, VIZ-03, VIZ-04, VIZ-05
- Testing: TEST-01, TEST-02, TEST-03, TEST-04, TEST-05, TEST-06, TEST-07, TEST-08

**Success criteria:**
1. ✅ User can generate figures in PNG, SVG, or PDF formats via CLI argument (`--output-format`)
2. ✅ User can see consistent styling across all figures using project color palettes
3. ✅ Developer can run `pytest` and see 90%+ coverage for all analysis code including CLI scripts
4. ✅ Developer can verify outputs match notebook-generated artifacts using integration tests
5. ✅ Developer can commit changes and have pre-commit hooks automatically run linting and tests

**Plans:**
- [x] 07-01-PLAN.md — Create visualization module (style, helpers, plots)
- [x] 07-02-PLAN.md — Create test fixtures (sample data, conftest.py)
- [x] 07-03-PLAN.md — Create CLI tests for Chief commands (3 commands)
- [x] 07-04-PLAN.md — Create CLI tests for Patrol commands (4 commands)
- [x] 07-05-PLAN.md — Create CLI tests for Policy and Forecasting commands (6 commands)
- [x] 07-06-PLAN.md — Create integration tests and verify coverage
- [x] 07-07-PLAN.md — Update pre-commit hooks with pytest
- [x] 07-08-PLAN.md — Add --output-format to Chief and Forecasting CLI commands (gap closure)
- [x] 07-09-PLAN.md — Add --output-format to Patrol and Policy CLI commands (gap closure)
- [x] 07-10-PLAN.md — Wire figure generation to all CLI commands and update tests (gap closure)

### Phase 8 — Documentation & Migration
**Goal:** Document the new script-based workflow, migrate all notebooks to scripts, verify outputs, and update project documentation

**Dependencies:** Phase 6 (CLI system ready to receive migrated scripts) and Phase 7 (testing infrastructure for verification)

**Requirements covered:**
- Documentation: DOCS-01, DOCS-02, DOCS-03, DOCS-04, DOCS-05
- Migration: MIGRATE-01, MIGRATE-02, MIGRATE-03, MIGRATE-04, MIGRATE-05, MIGRATE-06, MIGRATE-07, MIGRATE-08

**Success criteria:**
1. User can run any analysis as a CLI script (e.g., `python -m analysis.cli.trends`) and get identical output to the original notebook
2. Developer can read migration guide and understand how to convert a notebook to a CLI script
3. Developer can see updated AGENTS.md and README.md reflecting script-based workflow with examples
4. All 13 notebooks are deleted after successful conversion and verification
5. PROJECT.md and ROADMAP.md reference only script-based architecture, not notebooks

---

## Traceability

### v1.0 Coverage (Complete)
- All CHIEF-* requirements in Phase 1 ✅
- All PATROL-* and HYP-SOCIO in Phase 2 ✅
- All POLICY-* and HYP-EVENTS in Phase 3 ✅
- All FORECAST-* and HYP-HEAT in Phase 4 ✅

### v1.1 Coverage
| Requirement | Phase | Status |
|-------------|-------|--------|
| ARCH-01 | Phase 5 | Pending |
| ARCH-02 | Phase 5 | Pending |
| ARCH-03 | Phase 5 | Pending |
| ARCH-04 | Phase 6 | Complete |
| ARCH-05 | Phase 6 | Complete |
| ARCH-06 | Phase 6 | Complete |
| CONFIG-01 | Phase 6 | Complete |
| CONFIG-02 | Phase 6 | Complete |
| CONFIG-03 | Phase 6 | Complete |
| CONFIG-04 | Phase 6 | Complete |
| CONFIG-05 | Phase 6 | Complete |
| DATA-01 | Phase 5 | Pending |
| DATA-02 | Phase 5 | Pending |
| DATA-03 | Phase 5 | Pending |
| DATA-04 | Phase 5 | Pending |
| DATA-05 | Phase 7 | Pending |
| VIZ-01 | Phase 7 | Pending |
| VIZ-02 | Phase 7 | Pending |
| VIZ-03 | Phase 7 | Pending |
| VIZ-04 | Phase 7 | Pending |
| VIZ-05 | Phase 7 | Pending |
| TEST-01 | Phase 7 | Pending |
| TEST-02 | Phase 7 | Pending |
| TEST-03 | Phase 7 | Pending |
| TEST-04 | Phase 7 | Pending |
| TEST-05 | Phase 7 | Pending |
| TEST-06 | Phase 7 | Pending |
| TEST-07 | Phase 7 | Pending |
| TEST-08 | Phase 7 | Pending |
| DOCS-01 | Phase 8 | Pending |
| DOCS-02 | Phase 8 | Pending |
| DOCS-03 | Phase 8 | Pending |
| DOCS-04 | Phase 8 | Pending |
| DOCS-05 | Phase 8 | Pending |
| MIGRATE-01 | Phase 8 | Pending |
| MIGRATE-02 | Phase 8 | Pending |
| MIGRATE-03 | Phase 8 | Pending |
| MIGRATE-04 | Phase 8 | Pending |
| MIGRATE-05 | Phase 8 | Pending |
| MIGRATE-06 | Phase 8 | Pending |
| MIGRATE-07 | Phase 8 | Pending |
| MIGRATE-08 | Phase 8 | Pending |

**Coverage:** 46/46 v1.1 requirements mapped ✓

---

## Progress

| Phase | Status | Plans | Complete |
|-------|--------|-------|----------|
| 1 - High-Level Trends | ✅ Complete | 5 | 5/5 |
| 2 - Spatial & Socioeconomic | ✅ Complete | 6 | 6/6 |
| 3 - Policy Deep Dives | ✅ Complete | 6 | 6/6 |
| 4 - Forecasting & Modeling | ✅ Complete | 7 | 7/7 |
| 5 - Foundation Architecture | ✅ Complete | 7 | 7/7 |
| 6 - Configuration & CLI | ✅ Complete | 7 | 7/7 |
| 7 - Visualization & Testing | ✅ Complete | 10 | 10/10 |
| 8 - Documentation & Migration | ⏸️ Pending | 0 | 0/0 |

**Overall:** 24/24 v1.0 plans complete | 7/7 plans complete in Phase 5 | 7/7 plans complete in Phase 6 | 10/10 plans complete in Phase 7

---

## Next Steps

1. ~~Approve this roadmap~~ ✅ Complete
2. ~~`/gsd-discuss-phase 1`~~ ✅ Complete
3. ~~`/gsd-plan-phase 1`~~ ✅ Complete
4. ~~`/gsd-execute-phase 1`~~ ✅ Complete
5. ~~`/gsd-plan-phase 2`~~ ✅ Complete
6. ~~`/gsd-execute-phase 2`~~ ✅ Complete
7. ~~`/gsd-plan-phase 3`~~ ✅ Complete
8. ~~`/gsd-execute-phase 3`~~ ✅ Complete
9. ~~`/gsd-plan-phase 4`~~ ✅ Complete
10. ~~`/gsd-execute-phase 4`~~ ✅ Complete
11. ~~Approve v1.1 roadmap~~ ✅ Complete
12. ~~`/gsd-plan-phase 5`~~ ✅ Complete
13. ~~`/gsd-execute-phase 5`~~ ✅ Complete
14. ~~`/gsd-plan-phase 6`~~ ✅ Complete
15. ~~`/gsd:execute-phase 6`~~ ✅ Complete
16. ~~`/gsd:plan-phase 7`~~ ✅ Complete
17. ~~`/gsd:execute-phase 7`~~ ✅ Complete
18. **Next:** `/gsd:plan-phase 8`
