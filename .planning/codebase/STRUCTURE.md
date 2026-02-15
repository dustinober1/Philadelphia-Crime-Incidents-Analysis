# Philadelphia Crime Incidents Analysis - Codebase Structure

## Directory Layout

```
philadelphia-crime-incidents-analysis/
├── analysis/                 # Python analysis engine and CLI
├── api/                      # FastAPI backend service
├── web/                      # Next.js frontend application
├── pipeline/                 # Data processing pipeline
├── config/                   # YAML configuration files
├── data/                     # Data files and external dependencies
├── tests/                    # Test suites and fixtures
├── scripts/                  # Utility and deployment scripts
├── .planning/                # Documentation and planning artifacts
├── CLAUDE.md                 # Development guidance and workflows
├── docker-compose.yml        # Local development orchestration
├── environment.yml           # Conda environment specification
├── Makefile                  # Build and development targets
├── pyproject.toml            # Python project configuration
├── requirements.txt          # Python dependencies
└── requirements-dev.txt      # Development dependencies
```

## Module Organization

### Analysis Engine (`analysis/`)

**Core Modules:**
- `__init__.py` - Package initialization
- `config.py` - Configuration loading and validation
- `config_loader.py` - Legacy configuration loader
- `phase2_config_loader.py` - Phase 2 configuration handling
- `phase3_config_loader.py` - Phase 3 configuration handling
- `artifact_manager.py` - Report artifact management
- `report_utils.py` - Report generation utilities
- `spatial_utils.py` - Spatial analysis utilities
- `event_utils.py` - Event data processing
- `validate_phase3.py` - Phase 3 validation logic

**Subdirectories:**
- `cli/` - Command-line interface implementation
- `config/` - Configuration schemas and settings
- `data/` - Data loading and preprocessing modules
- `models/` - Machine learning models and utilities
- `utils/` - General utility functions
- `visualization/` - Plotting and visualization code

### CLI Structure (`analysis/cli/`)

**Entry Points:**
- `__main__.py` - Module entry point (`python -m analysis.cli`)
- `main.py` - Main typer application with command groups

**Command Groups:**
- `chief.py` - Chief-level analyses (trends, seasonality, covid)
- `patrol.py` - Patrol operations (hotspots, robbery-heatmap, district-severity, census-rates)
- `policy.py` - Policy evaluation (retail-theft, vehicle-crimes, composition, events)
- `forecasting.py` - Predictions (time-series, classification)

### API Service (`api/`)

**Core Files:**
- `__init__.py` - Package initialization
- `main.py` - FastAPI application entrypoint with middleware and routers
- `Dockerfile` - Container build specification
- `requirements.txt` - Python dependencies

**Subdirectories:**
- `routers/` - API endpoint implementations
- `services/` - Business logic and data loading
- `models/` - Pydantic request/response models

**Routers (`api/routers/`):**
- `trends.py` - Temporal trend analysis endpoints
- `spatial.py` - Geographic and spatial analysis endpoints
- `policy.py` - Policy evaluation data endpoints
- `forecasting.py` - Forecasting and prediction endpoints
- `questions.py` - Q&A feature with Firestore integration
- `metadata.py` - Data metadata and schema endpoints

### Web Interface (`web/`)

**Configuration Files:**
- `package.json` - Node.js dependencies and scripts
- `next.config.ts` - Next.js configuration
- `tsconfig.json` - TypeScript configuration
- `eslint.config.mjs` - ESLint configuration
- `postcss.config.mjs` - PostCSS configuration
- `Dockerfile` - Container build specification

**Source Code (`web/src/`):**
- `app/` - Next.js App Router pages and layouts
- `components/` - React components (maps, charts, UI elements)
- `lib/` - Utility functions and API client code

### Data Pipeline (`pipeline/`)

**Core Modules:**
- `__init__.py` - Package initialization
- `export_data.py` - Main data export script with typer CLI
- `refresh_data.py` - Data refresh functionality
- `compose_entrypoint.sh` - Docker Compose entrypoint script
- `Dockerfile` - Container build specification

### Configuration System (`config/`)

**YAML Configuration Files:**
- `global.yaml` - Global settings (paths, performance, logging)
- `chief.yaml` - Chief analysis configurations
- `patrol.yaml` - Patrol analysis configurations
- `policy.yaml` - Policy analysis configurations
- `forecasting.yaml` - Forecasting model configurations
- `phase1_config.yaml` - Legacy phase 1 configurations
- `phase2_config.yaml` - Phase 2 configurations
- `phase3_config.yaml` - Phase 3 configurations
- `report_template.md.j2` - Jinja2 report template

### Data Organization (`data/`)

**Data Directories:**
- `boundaries/` - Geographic boundary files (GeoJSON, Shapefiles)
- `output/` - Generated analysis outputs (JSON exports)
- `raw/` - Raw source data (gitignored, contains PII)
- `processed/` - Cleaned and processed data
- `external/` - External datasets and cache

### Test Organization (`tests/`)

**Test Structure:**
- `conftest.py` - Shared test fixtures and configuration
- `test_api_*.py` - API endpoint and service tests
- `test_cli_*.py` - CLI command tests by analysis group
- `test_config_*.py` - Configuration loading and validation tests
- `test_data_*.py` - Data loading, preprocessing, and validation tests
- `test_models_*.py` - Machine learning model tests
- `test_pipeline_*.py` - Data pipeline export and refresh tests
- `integration/` - End-to-end integration tests

## Key Files and Their Purposes

### Entry Points
- `analysis/cli/__main__.py` - CLI module entry point
- `api/main.py` - FastAPI application entrypoint
- `web/src/app/page.tsx` - Next.js main page component
- `pipeline/export_data.py` - Data pipeline main script

### Configuration Loading
- `analysis/config/settings.py` - Main configuration loading logic
- `analysis/config/schemas/` - Pydantic schemas for config validation
- `api/services/data_loader.py` - API data loading at startup

### Core Business Logic
- `analysis/data/loading.py` - Crime data loading and preprocessing
- `analysis/data/preprocessing.py` - Data cleaning and feature engineering
- `analysis/utils/classification.py` - Crime category classification
- `analysis/utils/temporal.py` - Temporal feature extraction
- `analysis/visualization/*.py` - Plotting and chart generation

### API Implementation
- `api/routers/*.py` - Individual router implementations
- `api/services/data_loader.py` - Data loading service
- `api/models/*.py` - Request/response Pydantic models

### Web Components
- `web/src/lib/api.ts` - API client functions
- `web/src/components/Map.tsx` - Mapbox map component
- `web/src/components/Charts.tsx` - Data visualization components

## Configuration Management

### YAML-Based Configuration
The system uses YAML files for configuration with Pydantic validation:

```python
# analysis/config/settings.py
from pydantic import BaseSettings

class GlobalConfig(BaseSettings):
    crime_data_path: str = "data/crime_incidents_combined.parquet"
    boundaries_dir: str = "data/boundaries"
    output_dir: str = "reports"
    fast_sample_frac: float = 0.1
```

### Configuration Loading Priority
1. **Default Values**: Defined in Pydantic models
2. **YAML Files**: Loaded from `config/*.yaml`
3. **Environment Variables**: `CRIME_*` prefixed variables
4. **CLI Arguments**: Highest priority command-line options

### Environment-Specific Configs
- **Local Development**: `.env` file with service ports and resource limits
- **Production**: Environment variables and Secret Manager
- **Testing**: Test-specific fixtures and mock data

## Build and Deployment Structure

### Containerization
**Dockerfiles:**
- `api/Dockerfile` - Python slim image for API service
- `web/Dockerfile` - Node.js image for frontend build
- `pipeline/Dockerfile` - Python image with analysis dependencies

**Docker Compose:**
- `docker-compose.yml` - Multi-service orchestration
- Service dependencies and health checks
- Volume mounts for development
- Resource limits and environment variables

### Build System
**Makefile Targets:**
- `make dev-web` - Start Next.js development server
- `make dev-api` - Start FastAPI with auto-reload
- `make export-data` - Run data pipeline export
- `make deploy` - Deploy to Firebase and Cloud Run

**Python Packaging:**
- `pyproject.toml` - Project metadata and tool configuration
- `requirements.txt` - Runtime dependencies
- `requirements-dev.txt` - Development dependencies
- `environment.yml` - Conda environment specification

### Deployment Pipeline
**Local Development:**
```bash
docker compose up -d --build  # Start full stack
docker compose logs -f        # Monitor services
```

**Production Deployment:**
```bash
make deploy                   # Firebase + Cloud Run
gcloud builds submit ...      # Cloud Build pipeline
```

### Quality Gates
**Code Quality:**
- `ruff check .` - Linting and formatting
- `black .` - Code formatting
- `mypy .` - Type checking (analysis/ excluded)
- `pytest tests/` - Test execution

**Pre-deployment Validation:**
- `./scripts/validate_local_stack.py` - Local stack validation
- `./scripts/validate_runtime_guardrails.sh` - Resource limit checks
- Health checks for all services

## Development Workflow

### Local Development Setup
1. **Environment**: `conda env create -f environment.yml`
2. **Dependencies**: `pip install -r requirements-dev.txt`
3. **Services**: `docker compose up -d --build`
4. **Web Dev**: `cd web && npm install && npm run dev`

### CLI Usage Examples
```bash
# Run analysis commands
python -m analysis.cli chief trends --fast
python -m analysis.cli patrol hotspots --fast

# View help
python -m analysis.cli --help
python -m analysis.cli chief trends --help
```

### API Development
```bash
# Start API with auto-reload
make dev-api
# Access docs at http://localhost:8080/docs
```

### Testing
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=analysis --cov=api --cov=pipeline

# Run specific tests
pytest tests/test_cli_chief.py::test_trends_command
```</content>
<parameter name="filePath">/Users/dustinober/Projects/Philadelphia-Crime-Incidents-Analysis/.planning/codebase/STRUCTURE.md