# Technology Stack

**Analysis Date:** 2026-02-07

## Languages

**Primary:**
- Python 3.14+ - Core analysis, CLI, data pipeline, and backend code in `analysis/`, `pipeline/`, and `api/`.
- TypeScript 5.x - Frontend application code in `web/src/`.

**Secondary:**
- YAML - Runtime configuration in `config/*.yaml`.
- JSON/GeoJSON - API payload artifacts in `api/data/`.
- CSS (Tailwind v4) - Styling in `web/src/app/globals.css`.

## Runtime

**Environment:**
- Python 3.14+ for analysis and pipeline workflows (`pyproject.toml`, `README.md`).
- Python 3.12 container runtime for API deployment (`api/Dockerfile`).
- Node.js runtime for Next.js frontend build and local dev (`web/package.json`); version is not pinned in-repo.

**Package Manager:**
- Python: Conda + pip (`environment.yml`, `requirements-dev.txt`, `pyproject.toml`).
- Frontend: npm with lockfile.
- Lockfile: `web/package-lock.json` present.

## Frameworks

**Core:**
- Typer - CLI command system (`analysis/cli/main.py`).
- FastAPI - HTTP API service (`api/main.py`).
- Next.js 15 (App Router) + React 19 - Frontend app (`web/src/app/`).

**Testing:**
- pytest - Primary Python test runner (`pyproject.toml`, `tests/`).
- FastAPI TestClient - API endpoint tests (`tests/test_api_endpoints.py`).
- Typer CliRunner - CLI integration tests (`tests/test_cli_*.py`).

**Build/Dev:**
- Ruff, Black, mypy - Python lint/format/type checks (`pyproject.toml`).
- ESLint + TypeScript compiler - Frontend checks (`web/package.json`, `web/eslint.config.mjs`, `web/tsconfig.json`).
- Uvicorn - API app server (`Makefile`, `api/Dockerfile`).
- Cloud Build + Firebase Hosting/Cloud Run - deployment pipeline (`cloudbuild.yaml`, `firebase.json`).

## Key Dependencies

**Critical:**
- pandas / geopandas / pyarrow - primary data processing and geospatial workflows (`pyproject.toml`, `analysis/data/`, `pipeline/export_data.py`).
- scikit-learn - clustering and classification in analytics and export routines (`analysis/cli/patrol.py`, `analysis/models/classification.py`, `pipeline/export_data.py`).
- prophet - time-series forecasting where available (`analysis/cli/forecasting.py`, `pipeline/export_data.py`).
- fastapi + pydantic - API layer and request/response validation (`api/main.py`, `api/models/schemas.py`).
- next + react-map-gl + recharts + swr - map and chart UI rendering (`web/src/components/MapContainer.tsx`, `web/src/app/*.tsx`).

**Infrastructure:**
- firebase-admin - Firestore-backed question workflow (`api/routers/questions.py`, `api/requirements.txt`).
- mapbox-gl / react-map-gl - external map tiles and map interaction (`web/src/components/MapContainer.tsx`).

## Configuration

**Environment:**
- Python analysis config uses layered settings from CLI args, env vars, and YAML files (`analysis/config/settings.py`, `config/*.yaml`).
- API runtime env vars include `CORS_ORIGINS`, `ADMIN_PASSWORD`, `ADMIN_TOKEN_SECRET`, `GOOGLE_CLOUD_PROJECT`, and `FIRESTORE_COLLECTION_QUESTIONS` (`api/main.py`, `api/routers/questions.py`, `README.md`).
- Frontend env vars include `NEXT_PUBLIC_API_BASE` and `NEXT_PUBLIC_MAPBOX_TOKEN` (`web/.env.example`, `web/src/lib/api.ts`).

**Build:**
- Python tooling/config in `pyproject.toml`.
- Frontend build config in `web/next.config.ts`, `web/postcss.config.mjs`, and `web/tsconfig.json`.
- Deployment config in `cloudbuild.yaml`, `firebase.json`, and `docker-compose.yml`.

## Platform Requirements

**Development:**
- Conda environment named `crime` recommended (`README.md`, `environment.yml`).
- Python tooling plus Node/npm for frontend workflows.
- Optional Docker for local API container (`docker-compose.yml`).

**Production:**
- API deploys to Google Cloud Run (`cloudbuild.yaml`, `firebase.json` rewrite).
- Frontend ships as static export (`web/out`) hosted on Firebase Hosting (`web/next.config.ts`, `firebase.json`).
- Data artifacts are precomputed and served from `api/data/`.

---

*Stack analysis: 2026-02-07*
*Update after major dependency changes*
