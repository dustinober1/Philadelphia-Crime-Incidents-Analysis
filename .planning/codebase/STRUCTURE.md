# Codebase Structure

**Analysis Date:** 2026-02-07

## Directory Layout

```
Crime Incidents Philadelphia/
├── analysis/            # Python analysis code, CLI commands, models, plotting
├── api/                 # FastAPI service and exported data payloads
├── pipeline/            # Export/refresh scripts that generate API artifacts
├── web/                 # Next.js frontend (App Router, static export)
├── tests/               # Pytest suites (unit, CLI, integration)
├── config/              # YAML configs and report template
├── data/                # Source and boundary datasets
├── docs/                # Migration and release documentation
├── reports/             # Generated analysis outputs and archived artifacts
├── pyproject.toml       # Python project/tooling configuration
├── cloudbuild.yaml      # Cloud Build + Cloud Run deployment pipeline
└── firebase.json        # Hosting config and API rewrite rules
```

## Directory Purposes

**`analysis/`:**
- Purpose: core analytics implementation and reusable utilities.
- Contains: CLI command modules, data loading/preprocessing, modeling helpers, visualization routines.
- Key files: `analysis/cli/main.py`, `analysis/data/loading.py`, `analysis/utils/spatial.py`, `analysis/models/*.py`.
- Subdirectories: `cli/`, `config/`, `data/`, `models/`, `utils/`, `visualization/`.

**`api/`:**
- Purpose: request-time service layer exposing precomputed metrics and Q&A endpoints.
- Contains: app bootstrap, routers, schemas, and generated payload files.
- Key files: `api/main.py`, `api/routers/questions.py`, `api/services/data_loader.py`.
- Subdirectories: `routers/`, `models/`, `services/`, `data/`, `data/geo/`.

**`pipeline/`:**
- Purpose: data artifact generation and verification for API consumption.
- Contains: `export_data.py` and `refresh_data.py` Typer apps.
- Key files: `pipeline/export_data.py`, `pipeline/refresh_data.py`.
- Subdirectories: none beyond package scaffolding.

**`web/`:**
- Purpose: client-facing dashboard and map application.
- Contains: Next.js app routes, reusable UI components, API hooks, config files.
- Key files: `web/src/app/layout.tsx`, `web/src/app/page.tsx`, `web/src/lib/api.ts`, `web/next.config.ts`.
- Subdirectories: `src/app/`, `src/components/`, `src/lib/`, plus generated `out/` and `.next/` (ignored).

**`tests/`:**
- Purpose: validation of analysis logic, CLI commands, API behavior, and integration outputs.
- Contains: `test_*.py` files with pytest fixtures, CLI runner tests, and integration markers.
- Key files: `tests/conftest.py`, `tests/test_cli_*.py`, `tests/test_api_endpoints.py`.
- Subdirectories: `tests/integration/` for migration/integration checks.

## Key File Locations

**Entry Points:**
- `analysis/cli/main.py`: top-level Typer command registry.
- `analysis/cli/__main__.py`: module execution entrypoint.
- `pipeline/export_data.py`: artifact export command entrypoint.
- `pipeline/refresh_data.py`: artifact validation/refresh entrypoint.
- `api/main.py`: FastAPI service entrypoint.
- `web/src/app/layout.tsx`: global app shell for frontend routes.

**Configuration:**
- `pyproject.toml`: Python deps/toolchain + pytest/ruff/black/mypy settings.
- `config/*.yaml`: analysis parameter defaults.
- `web/tsconfig.json`, `web/eslint.config.mjs`, `web/next.config.ts`: frontend config.
- `cloudbuild.yaml`, `firebase.json`, `docker-compose.yml`: deployment/runtime config.

**Core Logic:**
- `analysis/data/`, `analysis/utils/`, `analysis/models/`: analytics business logic.
- `api/routers/`: HTTP behavior by feature area.
- `pipeline/export_data.py`: transformation boundary between analysis and API.
- `web/src/app/*/page.tsx`: UI composition for each feature section.

**Testing:**
- `tests/`: unit/CLI/API tests.
- `tests/integration/`: integration and migration-verification tests.

**Documentation:**
- `README.md`: primary project guide and run/deploy instructions.
- `docs/`: migration, release notes, completion summaries.

## Naming Conventions

**Files:**
- Python modules: `snake_case.py` (`analysis/data/preprocessing.py`, `pipeline/refresh_data.py`).
- Test modules: `test_*.py` (`tests/test_cli_policy.py`).
- React components: `PascalCase.tsx` (`web/src/components/MapContainer.tsx`).
- Next route folders: lowercase path segments (`web/src/app/trends/page.tsx`).

**Directories:**
- Mostly lowercase and noun-based (`analysis/`, `pipeline/`, `reports/`).
- Frontend route directories map directly to URL segments (`web/src/app/map/`, `web/src/app/questions/`).

**Special Patterns:**
- CLI subcommands use Typer `@app.command()` names, with explicit kebab names where needed (for example `robbery-heatmap`).
- API endpoints follow versioned prefix `/api/v1/...` via router include in `api/main.py`.

## Where to Add New Code

**New Analysis Feature:**
- Primary code: appropriate domain module in `analysis/`.
- CLI command registration: `analysis/cli/{chief|patrol|policy|forecasting}.py`.
- Config schema/defaults: `analysis/config/schemas/*.py` and `config/*.yaml`.
- Tests: `tests/test_cli_*.py` and/or domain-specific `tests/test_*.py`.

**New API Endpoint:**
- Route handler: new or existing module in `api/routers/`.
- Shared payload/schema updates: `api/models/schemas.py` and `api/services/data_loader.py` if needed.
- Tests: `tests/test_api_endpoints.py` and integration tests.

**New Frontend Page/Module:**
- Route: `web/src/app/<route>/page.tsx`.
- Reusable UI: `web/src/components/`.
- Data hooks/types: `web/src/lib/api.ts`.

**Shared Utilities:**
- Python utilities: `analysis/utils/`.
- Frontend utilities: `web/src/lib/`.

## Special Directories

**`reports/`:**
- Purpose: generated analysis artifacts and historical outputs.
- Source: created by CLI commands and analysis workflows.
- Committed: yes (contains published/archived outputs in repo state).

**`api/data/`:**
- Purpose: generated API payload contracts consumed at runtime.
- Source: `pipeline/export_data.py` and `pipeline/refresh_data.py`.
- Committed: yes.

**`web/.next/` and `web/out/`:**
- Purpose: build artifacts.
- Source: Next.js build/export.
- Committed: no (ignored by `.gitignore`).

**`web/node_modules/`:**
- Purpose: frontend dependencies.
- Source: npm install.
- Committed: no (ignored by `.gitignore`).

---

*Structure analysis: 2026-02-07*
*Update when directory structure changes*
