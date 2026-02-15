# Technology Stack Documentation

## Programming Languages

- **Python 3.14+** (primary backend language)
  - Minimum version: 3.13 (pyproject.toml)
  - Conda environment: Python 3.14.2
  - TypeScript 5.9.2 (frontend)

## Frameworks and Libraries

### Backend (Python)

#### Core Data Processing
- **Pandas 2.0+** - Data manipulation and analysis
- **GeoPandas 0.14+** - Spatial data processing
- **PyArrow 21.0+** - High-performance data serialization
- **Scikit-learn 1.3+** - Machine learning algorithms
- **Statsmodels 0.14+** - Statistical modeling

#### Visualization
- **Matplotlib 3.8+** - Plotting and charting
- **Seaborn 0.13+** - Statistical data visualization
- **Folium** - Interactive maps (via conda)

#### API Framework
- **FastAPI 0.116.1** - REST API framework
- **Uvicorn 0.35.0** - ASGI server
- **Pydantic 2.11.7** - Data validation and serialization

#### CLI and Configuration
- **Typer 0.12+** - Command-line interface framework
- **Rich 13.0+** - Terminal formatting and progress bars
- **Pydantic-settings 2.0+** - Configuration management

#### Machine Learning and Forecasting
- **Prophet** - Time series forecasting (Facebook Prophet)
- **Joblib 1.4+** - Model serialization and caching

### Frontend (JavaScript/TypeScript)

#### Core Framework
- **Next.js 15.5.2** - React framework with App Router
- **React 19.1.1** - UI library
- **React DOM 19.1.1** - React rendering

#### Mapping and Visualization
- **Mapbox GL 3.14.0** - Interactive maps
- **React Map GL 8.0.4** - React wrapper for Mapbox
- **Recharts 3.1.2** - Data visualization charts

#### Data Fetching
- **SWR 2.3.6** - React data fetching library

#### UI Components and Styling
- **Headless UI 2.2.7** - Unstyled UI components
- **Lucide React 0.544.0** - Icon library
- **Tailwind CSS 4.1.12** - Utility-first CSS framework
- **clsx 2.1.1** - Conditional CSS classes

### Development and Testing

#### Testing
- **Pytest 8.0+** - Testing framework
- **pytest-cov 7.0+** - Coverage reporting
- **pytest-xdist 3.0+** - Parallel test execution

#### Code Quality
- **Ruff 0.9+** - Fast Python linter and formatter
- **Black 25.0+** - Python code formatter
- **MyPy 1.15+** - Static type checker
- **ESLint 9.33.0** - JavaScript/TypeScript linting
- **Pre-commit 4.0+** - Git hooks

#### Type Stubs
- **Pandas-stubs 2.0+** - Type stubs for pandas
- **Types-requests 2.32+** - Type stubs for requests
- **Types-PyYAML 6.0+** - Type stubs for PyYAML
- **@types/mapbox-gl 3.4.1** - TypeScript types for Mapbox
- **@types/node 22.17.2** - Node.js type definitions
- **@types/react 19.1.10** - React type definitions

## Build Tools and Package Managers

### Python
- **Conda** - Environment and package management
  - Environment file: `environment.yml`
  - Python version: 3.14.2
- **pip** - Python package installer
  - Requirements files: `requirements.txt`, `requirements-dev.txt`, `api/requirements.txt`
- **pyproject.toml** - PEP 621 project metadata and build configuration

### JavaScript/Node.js
- **npm** - Node package manager
  - Package file: `web/package.json`
- **ESLint** - JavaScript linting
- **TypeScript Compiler** - Type checking and compilation

### Build Automation
- **Makefile** - Build and development tasks
  - Commands: `make dev-web`, `make dev-api`, `make deploy`, etc.

## Deployment and Containerization

### Containerization
- **Docker** - Container platform
  - Dockerfiles: `api/Dockerfile`, `pipeline/Dockerfile`, `web/Dockerfile`
- **Docker Compose** - Multi-container orchestration
  - Configuration: `docker-compose.yml`
  - Services: pipeline, api, web

### Cloud Deployment
- **Google Cloud Run** - Serverless container execution
  - API deployment via Cloud Build
- **Firebase Hosting** - Static web hosting
  - Web frontend deployment
- **Google Cloud Build** - CI/CD pipeline
  - Configuration: `cloudbuild.yaml`

## Development Environment Setup

### Local Development
1. **Conda Environment**
   ```bash
   conda env create -f environment.yml
   conda activate crime
   ```

2. **Install Development Dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Web Dependencies**
   ```bash
   cd web && npm install
   ```

4. **Docker Compose**
   ```bash
   docker compose up -d --build
   ```

### Environment Variables
- **API**: `ADMIN_PASSWORD`, `ADMIN_TOKEN_SECRET`, `FIRESTORE_COLLECTION_QUESTIONS`, `GOOGLE_CLOUD_PROJECT`
- **Web**: `NEXT_PUBLIC_API_BASE`
- **Pipeline**: `PIPELINE_OUTPUT_DIR`, `PIPELINE_REFRESH_INTERVAL_SECONDS`

## Version Constraints and Requirements

### Python Version Requirements
- **Minimum**: Python 3.13
- **Target**: Python 3.14+
- **Conda**: Python 3.14.2

### Key Package Versions
- **FastAPI**: 0.116.1
- **Next.js**: 15.5.2
- **React**: 19.1.1
- **Pandas**: 2.0+
- **GeoPandas**: 0.14+
- **Scikit-learn**: 1.3+

### Node.js Requirements
- **TypeScript**: 5.9.2
- **ESLint**: 9.33.0
- **Tailwind CSS**: 4.1.12

### System Requirements
- **Docker**: For containerized development
- **Conda**: For Python environment management
- **Node.js/npm**: For frontend development
- **Git**: Version control

## Code Quality Tools Configuration

### Python
- **Ruff**: Linting and formatting (line length: 100)
- **Black**: Code formatting (line length: 100)
- **MyPy**: Type checking with strict settings
  - Excludes analysis/ directory
  - Requires type hints for API and pipeline code

### JavaScript/TypeScript
- **ESLint**: Configured via Next.js
- **TypeScript**: Strict type checking
- **Pre-commit**: Git hooks for code quality

### Testing
- **Pytest**: 90%+ coverage target
- **Coverage.py**: HTML and terminal reporting
- **Parallel execution**: Via pytest-xdist