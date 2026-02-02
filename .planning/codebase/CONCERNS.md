# Codebase Concerns

**Analysis Date:** 2026-02-02

## Tech Debt

1. Large, monolithic notebooks with embedded outputs
   - Issue: Project contains multiple large notebooks under `notebooks/` (e.g. `notebooks/philadelphia_safety_trend_analysis.ipynb`, `notebooks/covid_lockdown_crime_landscape.ipynb`, `notebooks/summer_crime_spike_analysis.ipynb`, `notebooks/data_quality_audit_notebook.ipynb`) with embedded binary outputs and large base64 PNG blocks.
   - Files: `notebooks/philadelphia_safety_trend_analysis.ipynb`, `notebooks/covid_lockdown_crime_landscape.ipynb`, `notebooks/summer_crime_spike_analysis.ipynb`, `notebooks/data_quality_audit_notebook.ipynb`
   - Impact: Repository size inflation, noisy diffs, slow cloning, and poor CI performance when notebooks are executed or diffed.
   - Fix approach: Split heavy processing into `analysis/` Python modules (e.g., `analysis/data_processing.py`, `analysis/aggregation.py`) and keep notebooks as lightweight orchestrators. Strip large outputs from committed notebooks (use `nbstripout`) and move generated images to `reports/` (already partially done).

2. Missing `analysis/` and `dashboard/` directories referenced in README
   - Issue: README documents `analysis/` scripts and `dashboard/` entry points (e.g., `analysis/06_generate_report.py`, `dashboard/app.py`) but the tree lacks those directories.
   - Files referenced: `analysis/06_generate_report.py`, `analysis/summer_spike.py`, `dashboard/app.py` (not present)
   - Impact: Onboarding confusion; documentation drift; automated scripts referenced in README fail if followed.
   - Fix approach: Either add the missing modules or update documentation to match current layout. Create minimal `analysis/__init__.py` with referenced entrypoints or remove stale README references.

3. Overly broad and outdated `requirements.txt`
   - Issue: `requirements.txt` (463 lines) contains many pinned or local-build references and packages not required for core functionality.
   - File: `requirements.txt`
   - Impact: Difficult environment reproducibility, heavy install footprint, and risk of incompatible pins across platforms.
   - Fix approach: Create a minimal `requirements-minimal.txt` for core runtime (pandas, pyarrow, geopandas, matplotlib, jupyter) and keep the large list in `environment.yml`. Prefer `environment.yml` for conda-based reproducibility (project already documents `crime` conda env).

## Known Bugs

1. Notebook outputs claimed cleared but still contain images
   - Symptom: Notebooks claim "Outputs cleared" in docs but `.ipynb` files include large embedded PNG base64 blobs (several hundred lines each).
   - Files: `notebooks/*.ipynb` (multiple)
   - Trigger: Committing notebooks with outputs preserved.
   - Workaround: Re-run `nbstripout --install` locally and strip outputs before committing; keep generated images in `reports/`.

## Security Considerations

1. Potential secrets and API key patterns
   - Issue: `.env.example` exposes environment variable names (`FRED_API_KEY`, `CENSUS_API_KEY`) and repository contains Firebase debug logs `firebase-debug.log` under project root.
   - Files: `.env.example`, `firebase-debug.log`
   - Risk: Accidental commit of secrets or logs; debug logs may reveal tokens or identifiers in other contexts.
   - Recommendations: Ensure `.env` is gitignored (already listed in `.gitignore`), remove `firebase-debug.log` from repo if it contains sensitive data and add it to `.gitignore` (already present). Scan repository for accidental secrets using a secret scanner prior to publishing.

2. No credential / secret handling guidance beyond `.env.example`
   - Issue: No centralized secret management documentation or CI secret policy.
   - Impact: Contributors may commit keys or misuse environment variables.
   - Recommendations: Add `SECURITY.md` or extend README with secret handling instructions and CI secret usage examples.

## Performance Bottlenecks

1. Single large Parquet data file
   - Issue: `data/crime_incidents_combined.parquet` and `data/external/weather_philly_2006_2026.parquet` are large and committed/checked-in (or referenced in `.gitignore` partially). The data directory contains large binary artifacts.
   - Files: `data/crime_incidents_combined.parquet`, `data/external/weather_philly_2006_2026.parquet`
   - Impact: Slow cloning, memory pressure when notebooks load entire dataset, and makes CI runs heavy.
   - Fix approach: Keep large datasets out of Git (use external storage or Git LFS) and provide sample datasets for CI (e.g., `data/sample/crime_sample.parquet`). Implement streaming or chunked reads in `analysis/` modules.

2. Heavy environment and many dependencies
   - Issue: `environment.yml` pins many packages and Python 3.14 - creating environment takes long and may fail on some platforms.
   - File: `environment.yml`
   - Impact: Slows onboarding and CI setup.
   - Fix approach: Provide lightweight `environment-dev.yml` and a `requirements.txt` for pip-based installs; document optional extras.

## Fragile Areas

1. Divergence between notebooks and (missing) analysis code
   - Files: `notebooks/*.ipynb`, README references `analysis/` scripts that are not present
   - Why fragile: Notebooks may contain ad-hoc data-transforms that are not unit-tested or reusable; missing programmatic entrypoints make automation brittle.
   - Safe modification: Extract transformation logic into `analysis/` modules and add unit tests under `tests/` before updating notebooks.
   - Test coverage: No tests present in repo (no `tests/` directory detected).

2. Inconsistent CI/automation artifacts
   - Files: `.github/` not present; `AGENTS.md` refers to CI workflow `.github/workflows/run-notebooks.yml` which is not found.
   - Why fragile: Expectations for automated notebook execution in CI are not backed by configuration, causing failed assumptions for contributors.
   - Safe modification: Add a minimal `.github/workflows/run-notebooks.yml` or update `AGENTS.md` to reflect current CI configuration.

## Dependencies at Risk

1. Use of geopandas and rtree/shapely pinned versions
   - Files: `requirements.txt`, `environment.yml` (geopandas, rtree, shapely)
   - Risk: Platform-specific binary dependencies can be hard to build (rtree, GEOS) and break on CI macOS/linux differences.
   - Migration plan: Add clear install notes in README, ship a trimmed `requirements-minimal.txt`, and consider using Docker for reproducible runtime.

## Missing Critical Features

1. No tests or CI harness
   - Files: project root (no `tests/`, no `.github/workflows/`)
   - Problem: No automated tests for core logic, making refactors risky.
   - Priority: High — add a small test harness for `analysis/` helpers and a CI workflow to run notebooks in fast mode.

2. No LICENSE file
   - Files: project root (missing `LICENSE`)
   - Problem: Unclear IP/usage terms for contributors/users.
   - Priority: Medium — add an appropriate license file.

## Test Coverage Gaps

1. Untested notebook transformations
   - Files: `notebooks/*.ipynb`
   - What's not tested: core data cleaning, classification (violent vs property), aggregation and peak detection logic.
   - Risk: Silent regressions when refactoring.
   - Priority: High — extract logic to `analysis/` modules and write unit tests under `tests/`.

---

*Concise remediation plan (next steps):*
- Add `analysis/` modules for reusable logic and create `tests/` with pytest for core functions.
- Strip notebook outputs and move generated images to `reports/` (use `nbstripout`).
- Create minimal `requirements-minimal.txt` and document environment setup in README.
- Remove large data files from Git or migrate them to Git LFS / cloud storage and provide small sample datasets for CI.
- Add CI workflow (GitHub Actions) to run tests and execute notebooks in headless fast mode.
- Add `LICENSE` and `SECURITY.md` and run a secret-scan to ensure no credentials are committed.

---

*Audit complete: 2026-02-02*
