# Crime Incidents - Philadelphia

A reproducible analysis project for Philadelphia crime incidents. This repository contains data loading and cleaning utilities, domain-specific analyses (chief, patrol, policy, forecasting), automated report generation, and a script-first CLI workflow for reproducible outputs.

## Highlights
- Script-based CLI architecture with 13 analysis commands.
- Reproducible data processing and validation pipelines.
- Automated report generation into `reports/{version}/{group}/`.
- Comprehensive pytest coverage for CLI commands and core analysis modules.

## Requirements
- Docker Desktop (or Docker Engine + Compose plugin)
- Python 3.14+ (for analysis CLI workflows)
- Conda environment `crime` (for analysis CLI workflows, see `environment.yml`)

## Quickstart

### Local Compose Startup (Default)

1. Initialize local env files:

```bash
cp .env.example .env
cp web/.env.example web/.env.local
```

2. Start the full stack (pipeline + API + web):

```bash
docker compose up -d --build
```

3. Verify readiness:

```bash
docker compose ps
curl http://localhost:8080/api/health
python scripts/validate_local_stack.py --skip-startup
```

Expected smoke-check pass signal:
- `Local compose smoke check passed`

Common smoke-check failures:
- `API health check failed ... ok!=true` -> API not ready yet; wait briefly, then rerun.
- `API health missing required exports ...` -> pipeline exports are incomplete; check `docker compose logs pipeline api`.
- `Web endpoint check failed ...` -> web service is unreachable; check `docker compose logs web`.

### Machine-Readable Output for Automation

The validation script now supports machine-readable output formats for CI/CD integration:

```bash
# JSON output (for CI parsing)
python scripts/validate_local_stack.py --format json

# YAML output (for configuration management)
python scripts/validate_local_stack.py --format yaml

# Human-readable output (default)
python scripts/validate_local_stack.py --format human
```

The script returns appropriate exit codes:
- `0` when validation succeeds
- `1` when validation fails

The machine-readable output includes timing information for performance monitoring.

### Extended API Endpoint Validation

The validation script now includes extended validation for high-value API endpoints:

```bash
# Run extended validation on additional API endpoints
python scripts/validate_local_stack.py --extended

# Run extended validation with JSON output
python scripts/validate_local_stack.py --extended --format json

# Specify a different API base URL if needed
python scripts/validate_local_stack.py --extended --api-base-url http://localhost:8080
```

Extended validation includes:
- Validation of trends, spatial, policy, forecasting, and metadata endpoints
- Data integrity checks to ensure responses have expected structure
- Performance threshold checks with warnings for slow responses
- Detailed reporting of validation results for each endpoint

4. Open local endpoints:

- Web UI: `http://localhost:${WEB_PORT:-3001}`
- API health: `http://localhost:8080/api/health`

No cloud credentials are required for this local baseline.
For troubleshooting and reset playbooks, see `docs/local-compose.md`.

### Analysis CLI Setup (Optional / Secondary Workflow)

```bash
# Create conda environment
conda env create -f environment.yml
conda activate crime

# Install dev dependencies (for testing)
pip install -r requirements-dev.txt
```

### Running Analyses

**v1.1 CLI (Recommended):**

All analyses are available as CLI commands:

```bash
# Chief-level analyses (trends, seasonality, COVID)
python -m analysis.cli chief trends --fast
python -m analysis.cli chief seasonality --fast
python -m analysis.cli chief covid --fast

# Patrol analyses (hotspots, robbery, district severity, census rates)
python -m analysis.cli patrol hotspots --fast
python -m analysis.cli patrol robbery-heatmap --fast
python -m analysis.cli patrol district-severity --fast
python -m analysis.cli patrol census-rates --fast

# Policy analyses (retail theft, vehicle crimes, composition, events)
python -m analysis.cli policy retail-theft --fast
python -m analysis.cli policy vehicle-crimes --fast
python -m analysis.cli policy composition --fast
python -m analysis.cli policy events --fast

# Forecasting (time series, classification)
python -m analysis.cli forecasting time-series --fast
python -m analysis.cli forecasting classification --fast

# See all available commands
python -m analysis.cli --help
```

**Command options:**
- `--fast`: Fast mode with 10% sample (for testing)
- `--version`: Output version tag (default: v1.0)
- `--output-format`: Figure format (png, svg, pdf)

**Output:** All artifacts saved to `reports/{version}/{group}/` with PNG/SVG/PDF figures and text summaries.

**Note:** The v1.0 notebook-based workflow has been migrated to CLI scripts. See [docs/MIGRATION.md](docs/MIGRATION.md) for the complete mapping of notebooks to CLI commands.

## Repository Layout

- `analysis/` - Analysis modules and CLI commands
  - `cli/` - CLI entry points using typer (chief, patrol, policy, forecasting)
  - `data/` - Data layer with loading, validation, preprocessing
  - `utils/` - Utility functions (classification, temporal, spatial)
  - `visualization/` - Publication-quality visualization utilities
  - `config/` - Configuration management with YAML schemas
- `tests/` - Pytest tests for all modules and CLI commands
- `data/` - Data storage (cleaned parquet, boundaries, external)
- `reports/` - Analysis outputs (figures, markdown reports, manifests)
- `config/` - YAML configuration files for each analysis group
- `docs/` - Additional documentation (migration guide, summaries)

## Development Guidelines

This project follows script-based development with CLI commands. See `AGENTS.md` for complete contribution guidelines including:

- Script structure using typer and Rich
- Testing with pytest and CliRunner
- Code quality standards (black, ruff, mypy)
- Pre-commit hooks for automated checks
- Documentation patterns

For the v1.0 -> v1.1 migration guide, see [docs/MIGRATION.md](docs/MIGRATION.md).

## Data & Privacy
- Keep raw datasets with personally-identifiable information (PII) out of version control.
- Store local raw inputs under `data/raw/` and document external data provenance.

## Common Workflows

**Run all tests:**
```bash
pytest tests/
```

**Run tests with coverage:**
```bash
pytest tests/ --cov=analysis --cov-report=term-missing
```

**Run specific analysis:**
```bash
python -m analysis.cli chief trends --output-format svg
```

**Check CLI help:**
```bash
python -m analysis.cli --help
python -m analysis.cli chief trends --help
```

## v1.1 Release Notes

The v1.1 release introduces a script-based architecture replacing the
notebook-based workflow from v1.0. Key improvements:

- **CLI Commands:** All 13 analyses available as `python -m analysis.cli` commands
- **Testing:** Comprehensive pytest tests with 90%+ coverage
- **Configuration:** YAML configs with CLI argument overrides
- **Quality:** Automated linting, formatting, type checking
- **Visualization:** Multi-format output (PNG, SVG, PDF) with consistent styling
- **Performance:** Faster execution without Jupyter overhead

See [docs/MIGRATION.md](docs/MIGRATION.md) for the complete notebook-to-CLI mapping.

## Quick Reference: All 13 Commands

### Chief (3 commands)
- `trends`: Annual crime trends analysis
- `seasonality`: Seasonal patterns and summer spike
- `covid`: Pre/during/post COVID comparison

### Patrol (4 commands)
- `hotspots`: Spatial clustering analysis
- `robbery-heatmap`: Temporal heatmap for robbery
- `district-severity`: Per-district severity scoring
- `census-rates`: Population-normalized crime rates

### Policy (4 commands)
- `retail-theft`: Retail theft trend analysis
- `vehicle-crimes`: Vehicle crime corridor analysis
- `composition`: Crime composition breakdown
- `events`: Event-day impact analysis

### Forecasting (2 commands)
- `time-series`: Prophet-based time series forecasting
- `classification`: Violence classification with feature importance

## Legacy Notebooks

Original v1.0 notebooks have been archived to `reports/v1.0/notebooks/`.
They are no longer maintained but preserved for historical reference.

## Philadelphia Crime Explorer Web Stack

This repository now includes:

- Frontend: `web/` (Next.js static export)
- Backend: `api/` (FastAPI on Cloud Run)
- Data pipeline: `pipeline/export_data.py` and `pipeline/refresh_data.py`

### Local Run (Compose-First)

1. Initialize local env files:

```bash
cp .env.example .env
cp web/.env.example web/.env.local
```

2. Start the full stack (pipeline + API + web):

```bash
docker compose up -d --build
```

3. Verify readiness:

```bash
docker compose ps
curl http://localhost:8080/api/health
python scripts/validate_local_stack.py --skip-startup
```

Expected smoke-check pass signal:
- `Local compose smoke check passed`

Common smoke-check failures:
- `API health check failed ... ok!=true` -> API not ready yet; wait briefly, then rerun.
- `API health missing required exports ...` -> pipeline exports are incomplete; check `docker compose logs pipeline api`.
- `Web endpoint check failed ...` -> web service is unreachable; check `docker compose logs web`.

### Machine-Readable Output for Automation

The validation script now supports machine-readable output formats for CI/CD integration:

```bash
# JSON output (for CI parsing)
python scripts/validate_local_stack.py --format json

# YAML output (for configuration management)
python scripts/validate_local_stack.py --format yaml

# Human-readable output (default)
python scripts/validate_local_stack.py --format human
```

The script returns appropriate exit codes:
- `0` when validation succeeds
- `1` when validation fails

The machine-readable output includes timing information for performance monitoring.

### Extended API Endpoint Validation

The validation script now includes extended validation for high-value API endpoints:

```bash
# Run extended validation on additional API endpoints
python scripts/validate_local_stack.py --extended

# Run extended validation with JSON output
python scripts/validate_local_stack.py --extended --format json

# Specify a different API base URL if needed
python scripts/validate_local_stack.py --extended --api-base-url http://localhost:8080
```

Extended validation includes:
- Validation of trends, spatial, policy, forecasting, and metadata endpoints
- Data integrity checks to ensure responses have expected structure
- Performance threshold checks with warnings for slow responses
- Detailed reporting of validation results for each endpoint

4. Open the app:

- Web UI: `http://localhost:${WEB_PORT:-3001}`
- API health: `http://localhost:8080/api/health`

No cloud credentials are required for this local baseline.

### Default Runtime Budgets

The default compose profile applies explicit CPU and memory caps to the long-running services:

- `pipeline`: `PIPELINE_CPU_LIMIT=1.00`, `PIPELINE_MEM_LIMIT=1536m`
- `api`: `API_CPU_LIMIT=1.00`, `API_MEM_LIMIT=1024m`
- `web`: `WEB_CPU_LIMIT=1.00`, `WEB_MEM_LIMIT=1024m`

Adjust limits in your local `.env` if your machine is constrained or if services restart under load:

```bash
cp .env.example .env
# then edit API_MEM_LIMIT/WEB_MEM_LIMIT/PIPELINE_MEM_LIMIT as needed
docker compose up -d --build
docker compose config | rg -n "cpus|mem_limit"
```

### Runtime Mode Presets (Optional)

Default startup remains the primary path:

```bash
docker compose up -d --build
```

When machine constraints or local workload demands change, use the runtime mode helper:

- `default`: normal day-to-day local development and baseline behavior checks.
- `low-power`: reduce container CPU/memory pressure on constrained laptops.
- `high-performance`: increase container limits for heavier local workloads.
- `auto`: detect host CPU/RAM and choose a recommended preset before startup.

```bash
./scripts/compose_with_runtime_mode.sh --mode low-power up -d --build
./scripts/compose_with_runtime_mode.sh --mode high-performance up -d --build
./scripts/compose_with_runtime_mode.sh --mode auto up -d --build
./scripts/compose_with_runtime_mode.sh --recommend
./scripts/validate_runtime_guardrails.sh
# or
make check-runtime-guardrails
```

Resource detection details: `docs/resource-detection.md`

### Optional Compose Profiles (Advanced)

Default startup remains unchanged:

```bash
docker compose up -d --build
```

Advanced users can run a one-shot pipeline refresh with the `refresh` profile:

```bash
docker compose --profile refresh config
docker compose --profile refresh run --rm pipeline-refresh-once
```

Use profile workflows only when needed; they are opt-in overlays and not required for normal local bring-up.

For troubleshooting, reset, and contract details, see `docs/local-compose.md`.

### Recovery and Reset (Local Compose)

Common recovery commands:

```bash
docker compose logs --tail=200 pipeline api web
./scripts/reset_local_stack.sh
docker compose up -d --build
```

Post-recovery validation checklist:

```bash
docker compose ps
curl http://localhost:8080/api/health
python scripts/validate_local_stack.py --skip-startup
```

For scenario-specific playbooks, see `docs/local-compose.md`.

### Required Server Env (Cloud Run)

Set these on the API service:

- `GOOGLE_CLOUD_PROJECT`
- `FIRESTORE_COLLECTION_QUESTIONS` (default: `questions`)
- `CORS_ORIGINS`
- `ADMIN_PASSWORD` (Secret Manager-backed)
- `ADMIN_TOKEN_SECRET` (Secret Manager-backed)

Admin auth secrets are server-only. Do not use `NEXT_PUBLIC_*` for admin credentials.

### Quality Gates (Local)

```bash
ruff check .
black --check .
mypy .
python -m pytest -q
cd web && npm install && npm run lint && npm run typecheck && npm run build
```

### Deploy (Exact Commands)

1. Authenticate CLI tools:

```bash
gcloud auth login
gcloud config set project <GCP_PROJECT_ID>
firebase login
```

2. Ensure Cloud Run secrets exist:

```bash
echo -n "<admin-password>" | gcloud secrets create ADMIN_PASSWORD --data-file=-
echo -n "<random-token-secret>" | gcloud secrets create ADMIN_TOKEN_SECRET --data-file=-
```

If the secrets already exist, add versions instead:

```bash
echo -n "<admin-password>" | gcloud secrets versions add ADMIN_PASSWORD --data-file=-
echo -n "<random-token-secret>" | gcloud secrets versions add ADMIN_TOKEN_SECRET --data-file=-
```

3. Build static web output:

```bash
cd web && npm ci && npm run build && cd ..
```

4. Refresh/validate API data:

```bash
python -m pipeline.refresh_data --output-dir api/data
```

5. Deploy hosting:

```bash
firebase deploy --only hosting --project <FIREBASE_PROJECT_ID>
```

6. Deploy API via Cloud Build + Cloud Run:

```bash
gcloud builds submit --project <GCP_PROJECT_ID> --config cloudbuild.yaml .
```

### Rollback

1. Roll back API traffic to a previous Cloud Run revision:

```bash
gcloud run revisions list --service philly-crime-api --region us-east1
gcloud run services update-traffic philly-crime-api --region us-east1 --to-revisions <REVISION_NAME>=100
```

2. Roll back hosting by redeploying a previous commit:

```bash
git checkout <PREVIOUS_GOOD_COMMIT>
cd web && npm ci && npm run build && cd ..
firebase deploy --only hosting --project <FIREBASE_PROJECT_ID>
```

### Known Limitations

- Forecast output quality depends on historical reporting consistency and may drift when data schema changes.
- Spatial exports require boundary and corridor files in `data/boundaries/`; missing files reduce map fidelity.
- Q&A admin auth uses bearer tokens without MFA; deploy behind stronger IAM controls for higher-security environments.
