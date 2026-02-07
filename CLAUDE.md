# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Philadelphia Crime Incidents is a reproducible crime analysis system with three main components:

1. **Analysis Engine** (`analysis/`) - Python-based CLI with 13 analysis commands across 4 domains (chief, patrol, policy, forecasting)
2. **API Service** (`api/`) - FastAPI backend serving crime data endpoints to the web UI
3. **Web Interface** (`web/`) - Next.js frontend for interactive data visualization
4. **Data Pipeline** (`pipeline/`) - Automated data processing and export that powers the API

### Data Flow Architecture

```
Data Sources (PPD, Census) → Pipeline → API Data (shared volume) → FastAPI → Next.js Web UI
                                        ↓
                                    Analysis CLI
                                        ↓
                                    Reports (versioned outputs)
```

The pipeline service fetches and processes crime data, exporting it to `/api/data/`. The API loads this data at startup via `api/services/data_loader.py` and serves it through routers. The web UI consumes API endpoints for visualization.

### Technology Stack

- **Python 3.14+** (via conda env `crime`)
- **FastAPI** for REST API (uvicorn server)
- **Next.js 15.5.2** with React 19 for frontend
- **Docker Compose** for local development orchestration
- **GeoPandas/Pandas** for spatial and data processing
- **Pytest** with 90%+ coverage target

## Common Development Commands

### Local Development (Docker Compose - Primary Workflow)

```bash
# Initialize environment files
cp .env.example .env
cp web/.env.example web/.env.local

# Start full stack (pipeline + API + web)
docker compose up -d --build

# Verify services are healthy
docker compose ps
curl http://localhost:8080/api/health
python scripts/validate_local_stack.py --skip-startup

# View logs
docker compose logs -f pipeline api web

# Reset stack (clear volumes and rebuild)
./scripts/reset_local_stack.sh
docker compose up -d --build
```

**Service Endpoints:**
- Web UI: `http://localhost:3001` (or `${WEB_PORT:-3001}`)
- API docs: `http://localhost:8080/docs`
- API health: `http://localhost:8080/api/health`

### Analysis CLI (Conda Workflow - Secondary)

The CLI requires the `crime` conda environment (defined in `environment.yml`):

```bash
# Create/activate conda environment
conda env create -f environment.yml
conda activate crime

# Install dev dependencies for testing
pip install -r requirements-dev.txt

# Run any of the 13 analysis commands
python -m analysis.cli chief trends --fast
python -m analysis.cli chief seasonality --fast
python -m analysis.cli chief covid --fast
python -m analysis.cli patrol hotspots --fast
python -m analysis.cli patrol robbery-heatmap --fast
python -m analysis.cli patrol district-severity --fast
python -m analysis.cli patrol census-rates --fast
python -m analysis.cli policy retail-theft --fast
python -m analysis.cli policy vehicle-crimes --fast
python -m analysis.cli policy composition --fast
python -m analysis.cli policy events --fast
python -m analysis.cli forecasting time-series --fast
python -m analysis.cli forecasting classification --fast

# CLI help
python -m analysis.cli --help
python -m analysis.cli chief trends --help
```

**CLI Command Options:**
- `--fast`: Use 10% data sample (for testing/development)
- `--version`: Set output version tag (default: v1.0)
- `--output-format`: Figure format (png, svg, pdf)

**Output:** All artifacts saved to `reports/{version}/{group}/` with figures and markdown summaries.

### Web Frontend Development

```bash
cd web

# Install dependencies
npm install

# Local development server
npm run dev

# Production build (static export)
npm run build

# Type checking
npm run typecheck

# Linting
npm run lint
```

### Makefile Commands

```bash
# Development servers
make dev-web          # Next.js dev server
make dev-api          # FastAPI with uvicorn --reload

# Data pipeline
make export-data      # python -m pipeline.export_data --output-dir api/data
make refresh-data     # python -m pipeline.refresh_data --output-dir api/data

# Deployment
make deploy           # firebase deploy && gcloud run deploy

# Cleanup
make clean-all        # Remove all caches, build artifacts, reports
make clean-unused-files    # Remove DS_Store, empty dirs, backups, caches

# Quality gates
make check-clean      # Run safety checks (git status, imports, tests)
make check-runtime-guardrails  # Validate runtime resource settings
make scan-dead-code   # Run vulture dead code scanner (read-only)
```

### Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=analysis --cov=api --cov=pipeline --cov-report=term-missing

# Run specific test file
pytest tests/test_cli_chief.py

# Run specific test function
pytest tests/test_cli_chief.py::test_trends_command

# Skip slow tests
pytest tests/ -m "not slow"

# Run tests in parallel (auto-detect CPUs)
pytest tests/ -nauto

# Run integration tests only
pytest tests/integration/ -m integration
```

### Code Quality

```bash
# Python linting and formatting
ruff check .                    # Lint with ruff
ruff check . --fix             # Auto-fix lint issues
black --check .                # Check formatting
black .                        # Format code
mypy .                         # Type checking (note: excludes analysis/)

# Web quality gates
cd web && npm run lint && npm run typecheck && npm run build

# Full quality gate (all checks)
ruff check . && black --check . && mypy . && python -m pytest -q
```

## Architecture Details

### CLI Structure (Analysis Engine)

The CLI uses **typer** for command registration and **Rich** for console output:

```
analysis/cli/
├── __main__.py       # Module entry point: python -m analysis.cli
├── main.py           # Main typer app with command groups
├── chief.py          # Chief-level analyses (trends, seasonality, covid)
├── patrol.py         # Patrol operations (hotspots, robbery, severity, census)
├── policy.py         # Policy evaluation (retail, vehicles, composition, events)
└── forecasting.py    # Predictions (time-series, classification)
```

**Command Pattern:**
Each analysis module is a typer app with functions decorated as commands. Options like `--fast`, `--version`, `--output-format` are defined at the function level using typer decorators.

**Testing Pattern:**
CLI tests use `typer.testing.CliRunner` to invoke commands programmatically. See `tests/test_cli_*.py` for examples.

### API Architecture

```
api/
├── main.py              # FastAPI app entrypoint with CORS, middleware, lifespan
├── routers/             # API endpoint groups
│   ├── trends.py       # /api/trends/* endpoints
│   ├── spatial.py      # /api/spatial/* endpoints
│   ├── policy.py       # /api/policy/* endpoints
│   ├── forecasting.py  # /api/forecasting/* endpoints
│   ├── metadata.py     # /api/metadata endpoint
│   └── questions.py    # /api/questions/* (Q&A feature with Firestore)
├── services/
│   └── data_loader.py  # Loads all data from api/data/ at startup
├── models/             # Pydantic models for request/response validation
└── data/               # Generated data exports (not in version control)
```

**Data Loading:**
The API loads all required data files at startup via `load_all_data()` in `api/services/data_loader.py`. Data is cached in module-level dictionaries and accessed via `cache_keys` constants. This ensures the API fails fast if data is missing.

**Router Pattern:**
Each router module handles a specific domain (trends, spatial, policy, forecasting). Routers are registered in `api/main.py` with prefix paths.

### Configuration System

Analysis commands use YAML configuration files with Pydantic validation:

```
config/
├── global.yaml         # Global settings (paths, version, defaults)
├── chief.yaml          # Chief analysis configs (years, seasons, COVID dates)
├── patrol.yaml         # Patrol configs (districts, thresholds)
├── policy.yaml         # Policy configs (crime types, event dates)
└── forecasting.yaml    # Forecasting configs (prophet params, features)
```

**Config Loading:**
Configs are loaded by `analysis/config/settings.py` and validated against Pydantic schemas in `analysis/config/schemas/`. CLI commands can override config values via command-line arguments.

### Data Pipeline

```
pipeline/
├── export_data.py      # One-time export: processes and writes to api/data/
├── refresh_data.py     # Periodic refresh: runs on interval in Docker Compose
└── compose_entrypoint.sh  # Entrypoint for pipeline service in compose
```

**Pipeline Outputs (api/data/):**
- `metadata.json` - Data metadata and refresh timestamp
- `trends_summary.json` - Aggregated trends data
- `spatial_hotspots.json` - Hotspot analysis results
- `policy_*.json` - Policy analysis exports
- `forecasting_*.json` - Forecast predictions
- `districts.geojson` - District boundaries for mapping

These files are loaded by the API at startup and served via endpoints.

### Test Organization

```
tests/
├── conftest.py                 # Shared fixtures and test configuration
├── test_cli_*.py              # CLI command tests (by group)
├── test_api_*.py              # API endpoint and service tests
├── test_data_*.py             # Data loading, validation, preprocessing
├── test_models_*.py           # Model tests (classification, time-series)
├── test_config_*.py           # Configuration schema tests
├── test_pipeline_*.py         # Pipeline export/refresh tests
└── integration/               # Integration tests (marked with @pytest.mark.integration)
```

**Test Fixtures:**
Key fixtures in `conftest.py`:
- `sample_df` - Minimal sample DataFrame for testing
- `mock_geo_data` - Mock GeoDataFrame for spatial tests
- `clean_test_dir` - Temp directory cleanup
- `skip_slow_tests` - Marker for slow tests

**Test Markers:**
- `slow`: Tests that take >5 seconds or require full datasets (deselected with `-m "not slow"`)
- `integration`: End-to-end integration tests

### Web Frontend Structure

```
web/
├── app/                # Next.js app directory (App Router)
├── components/         # React components (maps, charts, UI)
├── lib/               # API client functions
├── public/            # Static assets
└── package.json       # Dependencies and scripts
```

**Key Dependencies:**
- `next` 15.5.2 with React 19
- `mapbox-gl` + `react-map-gl` for interactive maps
- `recharts` for data visualization
- `swr` for data fetching

## Important Conventions

### Versioned Outputs

All analysis outputs are versioned by the `--version` flag (default: v1.0):

```
reports/
└── v1.0/
    ├── chief/         # Chief analysis outputs
    ├── patrol/        # Patrol analysis outputs
    ├── policy/        # Policy analysis outputs
    └── forecasting/   # Forecasting outputs
```

Each output directory contains:
- PNG/SVG/PDF figures
- `summary.md` - Text summary of findings
- `manifest.json` - Metadata about the analysis run

### Data Privacy

**Critical:** Never commit raw data with PII to version control.
- Raw data with PII goes in `data/raw/` (gitignored)
- Processed/cleaned data in `data/processed/` should have PII removed
- External cache in `data/external/.cache/` is gitignored

### Error Handling in CLI

CLI commands use Rich console output for errors and warnings:
- Use `console.error()` for error messages
- Use `console.warning()` for warnings
- Use Rich progress bars for long-running operations
- Exit with `raise typer.Exit(code=1)` on errors

### API Data Requirements

The API requires specific files in `api/data/` to start successfully. These are generated by the pipeline:
- `metadata.json` (required for health check)
- All JSON and GeoJSON files referenced in `api/services/data_loader.py`

If files are missing, the API will log errors and may fail startup.

### Python Type Hints

The project uses strict mypy configuration for API code, but type checking is currently disabled for `analysis/` (see `pyproject.toml` mypy overrides). When adding new code to `api/` or `pipeline/`, follow these patterns:
- Use `from __future__ import annotations` for forward references
- Avoid generic `Any` types
- Use Pydantic models for API request/response validation

## Deployment

### Cloud Run Deployment (API)

```bash
# Authenticate
gcloud auth login
gcloud config set project <GCP_PROJECT_ID>

# Ensure secrets exist
echo -n "<admin-password>" | gcloud secrets create ADMIN_PASSWORD --data-file=-
echo -n "<random-token-secret>" | gcloud secrets create ADMIN_TOKEN_SECRET --data-file=-

# Deploy via Cloud Build
gcloud builds submit --project <GCP_PROJECT_ID> --config cloudbuild.yaml .
```

### Firebase Hosting (Web)

```bash
# Build static export
cd web && npm ci && npm run build && cd ..

# Deploy to Firebase
firebase deploy --only hosting --project <FIREBASE_PROJECT_ID>
```

### Required Environment Variables (Cloud Run)

- `GOOGLE_CLOUD_PROJECT` - GCP project ID
- `FIRESTORE_COLLECTION_QUESTIONS` - Firestore collection name (default: `questions`)
- `CORS_ORIGINS` - Comma-separated allowed origins
- `ADMIN_PASSWORD` - Secret Manager secret for admin auth
- `ADMIN_TOKEN_SECRET` - Secret Manager secret for JWT tokens

## Troubleshooting

### Docker Compose Issues

**API health check failing:**
- Check if pipeline exports are complete: `docker compose logs pipeline`
- Verify shared volume has data: `docker compose exec api ls -la /app/api/data/`
- Restart API after pipeline is healthy: `docker compose restart api`

**Web service unreachable:**
- Check web logs: `docker compose logs web`
- Verify WEB_PORT in `.env`
- Ensure port 3001 is not in use

### Pipeline Not Refreshing

Check pipeline health file and logs:
```bash
docker compose exec pipeline cat /tmp/pipeline-refresh.ok
docker compose logs --tail=100 pipeline
```

### Import Errors in CLI

Ensure conda environment is activated:
```bash
conda activate crime
python -c "import analysis; print('OK')"
```

If imports fail, recreate the environment:
```bash
conda env remove -n crime
conda env create -f environment.yml
```

### Test Failures

**ImportError in tests:**
- Ensure you're in the project root directory
- Try running with PYTHONPATH: `PYTHONPATH=. pytest tests/`

**Missing data fixtures:**
- Run `pytest tests/ -k "test_" --co` to list all tests
- Check `conftest.py` for fixture definitions
- Some tests may require full datasets (marked with `@pytest.mark.slow`)

## Documentation References

- **README.md** - User-facing project overview
- **AGENTS.md** - Contribution guidelines (note: may not exist in current repo)
- **docs/MIGRATION.md** - v1.0 notebook to v1.1 CLI migration guide
- **docs/local-compose.md** - Local Compose troubleshooting
- **config/*.yaml** - Analysis configuration documentation
