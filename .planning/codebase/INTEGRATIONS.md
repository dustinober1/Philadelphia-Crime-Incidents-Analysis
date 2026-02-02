# External Integrations

**Analysis Date:** 2026-02-02

## APIs & External Services

**Federal Reserve (FRED):**
- Purpose: Unemployment rate and economic indicators (used by analysis)
- Auth: `FRED_API_KEY` in `.env.example` (file: `./.env.example` lines 8-16)

**U.S. Census (ACS):**
- Purpose: Demographic / economic variables (median income, poverty rate)
- Auth: `CENSUS_API_KEY` in `.env.example` (file: `./.env.example` line 27)

**AWS / S3:**
- S3 client libraries present: `s3fs` (`requirements.txt` line 55), `botocore` (`requirements.txt` line 53)
- Purpose: Not explicitly used in repository code; libraries indicate possible S3 read/write capabilities when running notebooks or scripts

**Other External Data Sources:**
- Not directly detected by code, but notebooks reference `data/crime_incidents_combined.parquet` (see `docs/NOTEBOOK_QUICK_REFERENCE.md` line 90 and `docs/NOTEBOOK_COMPLETION_REPORT.md` lines 22-23)

## Data Storage

**Databases:**
- Not detected. No direct DB connection strings or ORM configuration found. `psycopg2-binary` appears in `requirements.txt` (line 269) indicating potential PostgreSQL usage, but no connection code detected in repository root.

**File Storage:**
- Local data files in `data/`:
  - `data/crime_incidents_combined.parquet` (used by notebooks) — referenced in `docs/NOTEBOOK_QUICK_REFERENCE.md` line 90
  - `data/external/weather_philly_2006_2026.parquet` (present in repository)
  - `data/external/.cache/weather_cache.sqlite` (present)

**Caching:**
- Redis client present in `requirements.txt` (`redis==6.4.0`, line 37) but no active usage discovered in repository code.

## Authentication & Identity

**API Keys:**
- `FRED_API_KEY` — `.env.example` (line 16)
- `CENSUS_API_KEY` — `.env.example` (line 27)

**Auth Providers:**
- No OAuth providers, Supabase, Firebase, or Auth0 usage detected in repository. No auth code paths found.

## Monitoring & Observability

**Error Tracking:**
- Not detected. No Sentry or logging service integration files found. `python-json-logger` exists in `requirements.txt` (line 15) which supports structured logging.

**Logs:**
- Not applicable — notebooks output to console and saved artifacts under `reports/` when executed.

## CI/CD & Deployment

**Hosting:**
- Not detected. No `Procfile`, `Dockerfile`, or cloud deployment manifests present in repository root.

**CI Pipeline:**
- Not detected. No `.github/workflows` found in repository root (search truncated), so assume CI is not configured here.

## Environment Configuration

**Required env vars (from `.env.example`):**
- `FRED_API_KEY` — Federal Reserve API
- `CENSUS_API_KEY` — U.S. Census API

**Secrets location:**
- Not detected. `.env.example` shows required variables; actual `.env` should be created by the operator. No vault or secrets manager integration detected.

## Webhooks & Callbacks

**Incoming:**
- Not detected.

**Outgoing:**
- Not detected.

---

*Integration audit: 2026-02-02*
