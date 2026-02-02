# Technology Stack

**Analysis Date:** 2026-02-02

## Languages

**Primary:**
- Python 3.14 (see `environment.yml` line 21)

**Secondary:**
- Not detected (repository contains Jupyter notebooks as primary artifacts)

## Runtime

**Environment:**
- Conda environment named `crime` (see `environment.yml` line 1)

**Package Manager:**
- conda (environment defined in `environment.yml`)
- pip/requirements file present: `requirements.txt` (lock-like list of packages)

## Frameworks

**Core:**
- FastAPI==0.128.0 referenced in `requirements.txt` (line 117) — not required by notebooks but present in dependencies
- Flask referenced in `requirements.txt` (line 122)
- Streamlit referenced in `environment.yml` (line 37) and `requirements.txt` (line 98)

**Testing:**
- pytest listed in `requirements.txt` (line 310)

**Build/Dev:**
- uvicorn (ASGI server) present in `requirements.txt` (line 35)

## Key Dependencies

**Critical data & analysis:**
- pandas (`environment.yml` line 109)
- numpy (`environment.yml` line 104)
- pyarrow (`environment.yml` line 117)
- geopandas (`requirements.txt` line 28)
- matplotlib / seaborn (`requirements.txt` lines 109, 60)

**Web / API / backend related:**
- fastapi (`requirements.txt` line 117)
- starlette (`requirements.txt` line 96)
- uvicorn (`requirements.txt` line 35)

**Cloud / Storage / Tools:**
- s3fs (`requirements.txt` line 55) — S3 access client
- boto/botocore (`requirements.txt` lines 53) — AWS SDK components

## Configuration

**Environment:**
- Example environment variables exposed in `.env.example` (FRED_API_KEY, CENSUS_API_KEY) — see `./.env.example`

**Build:**
- No build system detected. Notebooks are primary deliverables. `environment.yml` and `requirements.txt` are the authoritative dependency manifests.

## Platform Requirements

**Development:**
- Conda with ability to create environment from `environment.yml` (Python 3.14)
- Jupyter Notebook runtime (notebooks under `notebooks/`) — see `notebooks/philadelphia_safety_trend_analysis.ipynb`

**Production:**
- Not applicable / Not detected. No deployment scripts or CI/CD configs for application servers present in repository root.

---

*Stack analysis: 2026-02-02*
