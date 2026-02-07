# Architecture

**Analysis Date:** 2026-02-07

## Pattern Overview

**Overall:** Monorepo with offline analytics pipeline + precomputed data API + static Next.js client.

**Key Characteristics:**
- Batch-first data preparation: heavy analysis runs in CLI/pipeline code, not request-time API handlers.
- Read-optimized API: FastAPI serves cached JSON/GeoJSON artifacts from `api/data/`.
- Static-first frontend: Next.js app is exported (`output: "export"`) and consumes API endpoints via SWR.
- Separate operational paths: analytical CLI (`analysis/cli/`) and user-facing web stack (`api/`, `web/`).

## Layers

**Analysis Layer:**
- Purpose: compute trends, spatial metrics, policy signals, and forecasts.
- Contains: CLI command groups, data cleaning, modeling, plotting (`analysis/cli/`, `analysis/data/`, `analysis/models/`, `analysis/utils/`, `analysis/visualization/`).
- Depends on: parquet/boundary files, pandas/geopandas/sklearn/prophet ecosystem.
- Used by: researchers/operators and export pipeline.

**Export Pipeline Layer:**
- Purpose: transform analysis outputs and source data into API-ready payloads.
- Contains: deterministic exporters and artifact validators (`pipeline/export_data.py`, `pipeline/refresh_data.py`).
- Depends on: analysis layer + source data + optional geospatial/model libs.
- Used by: API runtime, deployment workflows.

**API Layer:**
- Purpose: expose versioned REST endpoints and Q&A moderation endpoints.
- Contains: app lifecycle and middleware (`api/main.py`), routers (`api/routers/*.py`), schema models (`api/models/schemas.py`), in-memory payload cache (`api/services/data_loader.py`).
- Depends on: exported files in `api/data/`, optional Firestore.
- Used by: frontend and external API consumers.

**Frontend Layer:**
- Purpose: render dashboards, maps, policy views, forecasts, and Q&A UI.
- Contains: app routes (`web/src/app/*`), reusable components (`web/src/components/*`), API hooks (`web/src/lib/api.ts`).
- Depends on: API endpoints under `/api/v1/*`, Mapbox token for map rendering.
- Used by: end users through Firebase-hosted static site.

## Data Flow

**Primary Data Publication Flow:**
1. Source dataset and boundaries are loaded from repository data files (`data/`).
2. CLI analysis modules compute derived metrics (`analysis/cli/*.py`, `analysis/*`).
3. Export pipeline writes normalized JSON/GeoJSON payloads (`pipeline/export_data.py` -> `api/data/`).
4. FastAPI startup loads all artifacts into `_DATA_CACHE` (`api/main.py`, `api/services/data_loader.py`).
5. Routers return cached payloads, with lightweight filtering where needed (`api/routers/*.py`).
6. Next.js frontend fetches endpoints through SWR hooks and renders charts/maps (`web/src/lib/api.ts`, `web/src/app/*.tsx`).

**Community Q&A Flow:**
1. User submits question from `web/src/components/QuestionForm.tsx`.
2. API validates/rate-limits input in `api/routers/questions.py`.
3. Record persists to Firestore if available, else in-memory fallback.
4. Admin authenticates with password, receives signed bearer token, and moderates pending items.
5. Public questions page only reads answered items.

**State Management:**
- Analytics/pipeline is file-based and batch-oriented.
- API uses in-memory caches (`_DATA_CACHE`, `_RATE_LIMIT`, `_IN_MEMORY`) per process.
- Frontend uses SWR client-side cache with stateless page components.

## Key Abstractions

**Command Group Abstraction:**
- Purpose: isolate analysis domains with consistent CLI ergonomics.
- Examples: `analysis/cli/chief.py`, `analysis/cli/patrol.py`, `analysis/cli/policy.py`, `analysis/cli/forecasting.py`.
- Pattern: Typer sub-apps registered by `analysis/cli/main.py`.

**Config Schema Abstraction:**
- Purpose: unify defaults + YAML + env + CLI overrides.
- Examples: `analysis/config/settings.py`, `analysis/config/schemas/*.py`.
- Pattern: Pydantic settings and typed config objects per domain.

**Data Artifact Abstraction:**
- Purpose: enforce fixed contract between pipeline/API/frontend.
- Examples: `api/data/*.json`, `api/data/geo/*.geojson`, routers consuming specific keys.
- Pattern: precomputation + static payload serving.

**API Router Abstraction:**
- Purpose: separate feature areas into endpoint modules.
- Examples: `api/routers/trends.py`, `api/routers/spatial.py`, `api/routers/policy.py`, `api/routers/forecasting.py`, `api/routers/questions.py`.
- Pattern: one APIRouter per domain under `/api/v1` prefix.

## Entry Points

**CLI Entry Point:**
- Location: `analysis/cli/main.py` and `analysis/cli/__main__.py`.
- Triggers: `python -m analysis.cli ...` commands.
- Responsibilities: register groups, route execution, print Rich status output.

**Pipeline Entry Points:**
- Location: `pipeline/export_data.py`, `pipeline/refresh_data.py`.
- Triggers: `python -m pipeline.export_data` / `python -m pipeline.refresh_data`.
- Responsibilities: produce and validate API payload artifacts.

**API Entry Point:**
- Location: `api/main.py`.
- Triggers: Uvicorn/Cloud Run process startup.
- Responsibilities: preload data cache, install middleware/handlers, mount routers.

**Frontend Entry Point:**
- Location: `web/src/app/layout.tsx` plus route pages in `web/src/app/*/page.tsx`.
- Triggers: static app navigation and client-side data fetches.
- Responsibilities: compose UI shell and domain views.

## Error Handling

**Strategy:** Boundary-level handling with explicit HTTP payloads for API and fail-soft fallbacks for optional analytics dependencies.

**Patterns:**
- API defines global exception handlers for `HTTPException`, validation errors, and unhandled exceptions (`api/main.py`).
- Q&A endpoints return clear status codes/messages and guard admin routes with bearer token checks (`api/routers/questions.py`).
- Analysis commands catch optional dependency import errors and continue with degraded outputs in some flows (`analysis/cli/patrol.py`, `analysis/cli/forecasting.py`, `pipeline/export_data.py`).

## Cross-Cutting Concerns

**Logging:**
- Structured request timing/log lines in API middleware (`api/main.py`).
- Rich console progress/status for CLI commands (`analysis/cli/*.py`).

**Validation:**
- Typed request/response models for API (`api/models/schemas.py`).
- Pydantic data validation utilities in analysis domain (`analysis/data/validation.py`).
- Export artifact validation in refresh command (`pipeline/refresh_data.py`).

**Authentication:**
- Admin-only actions use password bootstrap + signed bearer token (`api/routers/questions.py`).
- Public read endpoints remain unauthenticated.

---

*Architecture analysis: 2026-02-07*
*Update when major patterns change*
