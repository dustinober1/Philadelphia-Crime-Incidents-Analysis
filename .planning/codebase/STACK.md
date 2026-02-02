# Technology Stack

**Analysis Date:** 2026-02-02

## Languages

**Primary:**
- Python 3.14.2 - Project environment specified in `environment.yml` (`name: crime`, `python=3.14.2`) — used for analysis, notebooks, and any scripts.

**Secondary:**
- Shell/Bash (git, firebase CLI) - used in developer tooling and seen in `firebase-debug.log` at the repo root (`firebase-debug.log`).
- Jupyter Notebooks (ipynb) - interactive analysis files under `notebooks/`.

## Runtime

**Environment:**
- Conda environment named `crime` described in `environment.yml` (`/environment.yml`).

**Package Manager:**
- conda (primary): `environment.yml` is the authoritative environment specification (`environment.yml`).
- pip (secondary): a `requirements.txt` exists (`requirements.txt`) and contains a long list of packages; many are present for development, analysis and web components.
- Lockfile: No pinned Conda lockfile (e.g. `conda-lock.yml`) or Pipenv/poetry lockfile detected. `requirements.txt` is present and can be used for pip installs.

## Frameworks

**Core:**
- FastAPI (`fastapi` in `requirements.txt`) + Starlette (`starlette` in `requirements.txt`) + Uvicorn (`uvicorn` in `requirements.txt`) — indicates an async API stack is available if used. See `requirements.txt`.
- Flask (`Flask` in `requirements.txt`) — lightweight WSGI applications referenced in `README.md`, but no `dashboard/` directory detected in the repository root (see "Repository layout vs present files" below).
- Streamlit (`streamlit` in `environment.yml`) — interactive app tooling is present in environment spec.

**Data / Analysis frameworks:**
- pandas, pyarrow, geopandas, pyproj, shapely, geopandas-related stack (see `requirements.txt` and `environment.yml`) — geospatial and table processing.
- NumPy, SciPy, scikit-learn — numeric and ML tooling.
- Plotly, folium, altair, bokeh, seaborn, matplotlib — visualization libraries.

**Testing:**
- pytest appears in `requirements.txt` but no tests/ harness present in repo root (not detected).

**Build/Dev tooling:**
- linters and formatters: `black`, `flake8`, `ruff`, `isort` are present in `requirements.txt`/environment recommendations (see `README.md` and `requirements.txt`).

## Key Dependencies

**Critical (present in `requirements.txt` / `environment.yml`):**
- `pandas` / `pyarrow` - core data processing (`requirements.txt`, `environment.yml`).
- `geopandas`, `shapely`, `pyproj` - spatial processing (`requirements.txt`).
- `psycopg2-binary`, `SQLAlchemy` - Postgres DB client & ORM support (`requirements.txt`).
- `s3fs`, `botocore`, `aiobotocore` - S3 / AWS access libs (`requirements.txt`).
- `redis` - caching (`requirements.txt`).
- `fastapi`, `uvicorn`, `starlette`, `pydantic` - API server & validation (`requirements.txt`).
- `flask` - WSGI app framework referenced in README (`requirements.txt`).
- `streamlit` - interactive dashboard runtime (`environment.yml`).

**Infrastructure & tooling:**
- `python-dotenv` - environment variable loading from `.env` (`requirements.txt`).
- `prometheus_client` - metrics (present in `requirements.txt`).
- `pyjwt` / `python-jose` - JWT handling (present in `requirements.txt`).

## Configuration

**Environment configuration:**
- Example env file present at `.env.example` listing external API keys (FRED and CENSUS). See `.env.example`.
- `python-dotenv` is available, so code likely reads a `.env` file at runtime (`requirements.txt`).

**Build / Run:**
- No centralized `Makefile`, `pyproject.toml` or `tox.ini` detected for run orchestration. `README.md` documents example run commands (e.g. `python analysis/06_generate_report.py`, `python dashboard/app.py`) but corresponding `analysis/` and `dashboard/` packages are not detected in the repository (see notes below).

## Platform Requirements

**Development:**
- Conda (recommended) using `environment.yml` (`environment.yml`) — install with `conda env create -f environment.yml`.
- Jupyter for notebooks: `notebooks/` contains multiple `.ipynb` files.

**Production / Deployment:**
- Not explicitly documented. There are libraries for multiple deployment targets (`uvicorn`/`fastapi`, `flask`, `streamlit`) but no deployment manifests or CI/CD pipeline files were detected (e.g., no `.github/workflows/` entries).

## Repository layout (what is referenced vs what is present)

- `README.md` references `analysis/` and `dashboard/` and entry points such as `analysis/06_generate_report.py` and `dashboard/app.py` (see `README.md`) but the corresponding directories/files are not detected in this repository snapshot (not present under repo root). Confirm presence before relying on those entrypoints.
- Present artifacts: `notebooks/` (multiple notebooks), `data/` (contains `data/crime_incidents_combined.parquet` and `data/external/weather_philly_2006_2026.parquet`), `reports/` (PNG and CSV outputs), `firebase-debug.log`.

---

*Stack analysis: 2026-02-02*
