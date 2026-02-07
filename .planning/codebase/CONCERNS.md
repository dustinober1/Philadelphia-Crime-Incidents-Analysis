# Codebase Concerns

**Analysis Date:** 2026-02-07

## Tech Debt

**Duplicate spatial/config utility stacks (`analysis/utils/*` vs legacy `analysis/spatial_utils.py`, `analysis/phase2_config_loader.py`):**
- Issue: overlapping functionality exists in parallel modules.
- Why: migration from notebook-era/phase files to newer package layout appears incremental.
- Impact: higher maintenance risk and potential divergence in behavior depending on import path.
- Fix approach: consolidate to a single spatial/config API surface and deprecate old modules with explicit shim windows.

**Large orchestration functions in CLI modules (`analysis/cli/chief.py`, `analysis/cli/patrol.py`, `analysis/cli/policy.py`):**
- Issue: command handlers mix data loading, transformation, visualization, and file I/O in long functions.
- Why: convenience during script-first migration.
- Impact: harder targeted unit testing and higher regression risk when modifying one step.
- Fix approach: extract reusable service-layer helpers per command stage and keep CLI handlers thin.

## Known Bugs

**Potential boundary loader defect in `analysis/data/loading.py`:**
- Symptoms: `load_boundaries()` may fail depending on geopandas expectations.
- Trigger: calling `load_boundaries()` code path that passes raw bytes to `gpd.GeoDataFrame.from_file(...)`.
- Workaround: use `analysis/utils/spatial.py` or `analysis/spatial_utils.py` loaders that call `gpd.read_file(path)` directly.
- Root cause: likely wrong input type for geopandas file loader API.

**In-memory admin/session state is process-local (`api/routers/questions.py`):**
- Symptoms: rate-limit/session/question fallback data resets on restart or differs across instances.
- Trigger: Cloud Run scale-out/restart or Firestore unavailability.
- Workaround: rely on Firestore path and avoid depending on in-memory fallback for persistent behavior.
- Root cause: `_RATE_LIMIT`, `_IN_MEMORY`, and token validation rely on single-process memory.

## Security Considerations

**Admin auth uses password + bearer token without login throttling:**
- Risk: brute-force attempts on `/api/v1/questions/admin/session` are not explicitly rate-limited.
- Current mitigation: constant-time compare and secret-based token signing.
- Recommendations: add per-IP and per-account login throttles plus structured audit logging for failed attempts.

**Frontend-admin access control is client-routed only (`web/src/app/admin/page.tsx`):**
- Risk: admin page is publicly reachable as a route (auth enforced only when API calls run).
- Current mitigation: backend endpoints require valid bearer token.
- Recommendations: add route-level UX guard and explicit unauthorized state handling to reduce accidental exposure/scraping.

## Performance Bottlenecks

**API startup eagerly loads all exported payloads into memory (`api/services/data_loader.py`):**
- Problem: all JSON/GeoJSON files are read at process start.
- Measurement: no in-repo benchmark, but cost scales with artifact size and instance count.
- Cause: eager `load_all_data()` in FastAPI lifespan.
- Improvement path: lazy-load rarely used payloads and cache per-key on first request.

**Frontend map/data pages issue multiple client-side fetches per route:**
- Problem: map and trend views pull several datasets independently (`web/src/app/map/page.tsx`, `web/src/app/trends/page.tsx`).
- Measurement: no p95 metrics in repo; pattern implies multi-request waterfall risk on slow networks.
- Cause: independent SWR hooks and lack of server-side prefetch/bundling.
- Improvement path: aggregate key datasets server-side or provide bundled API endpoints for high-traffic views.

## Fragile Areas

**Optional dependency branching in analytics/export paths (`pipeline/export_data.py`, `analysis/cli/patrol.py`, `analysis/cli/forecasting.py`):**
- Why fragile: behavior changes by environment depending on geopandas/prophet/sklearn availability.
- Common failures: missing figures or reduced outputs without hard failure in some flows.
- Safe modification: treat dependency matrix as explicit test matrix and assert expected degraded outputs.
- Test coverage: present for many CLI flows, but optional dependency combinations are only partially covered.

**Dual Python version expectations (`pyproject.toml` vs `api/Dockerfile`):**
- Why fragile: analysis targets Python 3.14+, API container runs Python 3.12.
- Common failures: subtle version-specific behavior differences and dependency resolution drift.
- Safe modification: unify or explicitly pin compatibility matrix and run CI across both versions.
- Test coverage: no dedicated multi-version matrix config detected in repository.

## Scaling Limits

**Q&A moderation/session model:**
- Current capacity: bounded by in-memory dictionaries if Firestore is unavailable.
- Limit: state does not synchronize across multiple API instances.
- Symptoms at limit: inconsistent rate limiting, missing pending items, token/session confusion across restarts.
- Scaling path: enforce Firestore as required backend and move rate-limit/session state to shared storage.

**Artifact-driven API growth:**
- Current capacity: tied to artifact size loaded per process.
- Limit: memory footprint increases with richer geo layers/historical slices.
- Symptoms at limit: slower cold starts and higher memory pressure per Cloud Run instance.
- Scaling path: chunk artifacts, compress responses, and add selective/lazy loading.

## Dependencies at Risk

**Prophet / geopandas optional availability:**
- Risk: export and CLI outputs vary when these packages are missing.
- Impact: forecast/geospatial outputs may be absent or downgraded.
- Migration plan: standardize environment provisioning and make capability status explicit in generated reports.

**Custom admin token implementation:**
- Risk: homegrown auth can drift from best practices (rotation, revocation, lockouts).
- Impact: admin endpoints are security-sensitive.
- Migration plan: move to managed identity/auth provider or hardened JWT/session middleware.

## Missing Critical Features

**Frontend automated test suite:**
- Problem: no Jest/Vitest/Playwright tests detected for `web/src/`.
- Current workaround: rely on lint/typecheck/build as quality gate.
- Blocks: confident refactors in UI interactions (map toggles, admin moderation UX, chart transformations).
- Implementation complexity: medium.

**Explicit staging environment profile:**
- Problem: config/deploy files focus on local + production values.
- Current workaround: manual variable overrides.
- Blocks: safe pre-production validation and reproducible release promotion.
- Implementation complexity: medium.

## Test Coverage Gaps

**Cross-service deployment behavior:**
- What's not tested: end-to-end Firebase rewrite to Cloud Run, CORS edge cases, secret injection failures.
- Risk: integration issues only discovered during deployment.
- Priority: High.
- Difficulty to test: Medium (requires environment-integrated tests).

**Frontend runtime behavior under API failures:**
- What's not tested: degraded UI states when `/api/v1/*` endpoints error or time out.
- Risk: user-facing blank/error states can regress unnoticed.
- Priority: Medium.
- Difficulty to test: Medium.

---

*Concerns audit: 2026-02-07*
*Update as issues are fixed or new ones discovered*
