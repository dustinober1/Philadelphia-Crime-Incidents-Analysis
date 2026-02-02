# External Integrations

**Analysis Date:** 2026-02-02

## APIs & External Services

**FRED (Federal Reserve Economic Data)**
- Purpose: Unemployment rate data (PAPHIL5URN for Philadelphia County) referenced in `.env.example`.
- SDK/Client: No dedicated SDK required; project likely uses `requests` or `pandas-datareader` (not detected). `requests` is in `environment.yml`/`requirements.txt`.
- Auth: `FRED_API_KEY` environment variable (`.env.example`).
- Files referencing: `.env.example` (lines pointing to `FRED_API_KEY`).

**U.S. Census / ACS**
- Purpose: ACS economic indicators (median income, poverty rates) referenced in `.env.example`.
- SDK/Client: Typically `requests`/`census`/`censusdata` packages; these specific libs are not explicitly present in `requirements.txt` but `requests` is available.
- Auth: `CENSUS_API_KEY` environment variable (`.env.example`).
- Files referencing: `.env.example`.

**Firebase / Google Cloud CLI (observed usage)**
- Purpose: Seen by presence of `firebase-debug.log` at repo root which implies firebase CLI operations were run locally.
- SDK/Client: `firebase-tools` (not in Python deps); `firebase-debug.log` is present. No code-level Firebase SDK imports were detected in Python notebook text search, but the log exists at `firebase-debug.log`.
- Auth: Uses Google OAuth / service account credentials when deploying — no service account files included.
- Files referencing: `firebase-debug.log` (repo root).

**AWS / S3**
- Purpose: S3 access appears supported via packages: `s3fs`, `botocore`, `aiobotocore` present in `requirements.txt` and `aws-*` client libs listed in `environment.yml`.
- SDK/Client: `s3fs` and `botocore` / `aiobotocore` (`requirements.txt`). Native AWS C SDK packages present in `environment.yml` (e.g., `aws-sdk-cpp`, `aws-c-s3`).
- Auth: Standard AWS credentials (environment variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`) — not enumerated in `.env.example` but implied by AWS libraries.
- Files referencing: `requirements.txt`, `environment.yml`.

**Redis**
- Purpose: caching/backing store — `redis==6.4.0` in `requirements.txt`.
- Client: `redis` Python package.
- Auth/Connection: No connection URL in `.env.example`; typical env var would be `REDIS_URL` or `REDIS_HOST`.

## Data Storage

**Local Files / Parquet**
- Primary data files live in `data/`:
  - `data/crime_incidents_combined.parquet`
  - `data/external/weather_philly_2006_2026.parquet`
  - `data/external/.cache/weather_cache.sqlite`
- Parquet + pyarrow used: `pyarrow` present in `environment.yml` / `requirements.txt`.

**Databases**
- PostgreSQL (client support): `psycopg2-binary==2.9.11` and `SQLAlchemy` present in `requirements.txt` — the repo references database tooling but no live `database` config or `docker-compose` found.
- Connection config: Not present; no `DATABASE_URL` or `PGHOST` in `.env.example`. If used, typical env var would be `DATABASE_URL`.

**Object Storage**
- S3-compatible storage supported via `s3fs` (present). No S3 bucket names or env vars (e.g., S3_BUCKET) are included in `.env.example`.

## Authentication & Identity

**JWT / Token handling**
- Libraries: `pyjwt` and `python-jose` present in `requirements.txt` — project has tools for JWT creation/validation if needed.
- No explicit auth provider config detected (Auth0, Okta, Firebase Auth SDK imports not found in repo files). `.env.example` does not include OAuth client IDs/secrets.

**Environment secrets**
- `.env.example` lists only `FRED_API_KEY` and `CENSUS_API_KEY`.
- Repo does not commit any service account keys or secrets — good practice.

## Monitoring & Observability

**Prometheus**
- `prometheus_client` is present in `requirements.txt`, so code can expose metrics endpoints if implemented. No explicit instrumented endpoints or `prometheus.yml` were detected.

**Logging / Error tracking**
- No error tracking packages (Sentry/Datadog) detected in `requirements.txt` or code search.

## CI/CD & Deployment

**Hosting / CI**
- No CI pipeline or GitHub Actions detected (no `.github/workflows/` entries). No Dockerfiles or deployment manifests detected.

**Firebase traces**
- `firebase-debug.log` implies deployment or hosting via Firebase CLI at some point — examine project owner workflows if planning to use Firebase hosting. File path: `firebase-debug.log`.

## Environment Configuration

**Required env vars (explicit in repo):**
- `FRED_API_KEY` — seen in `.env.example`.
- `CENSUS_API_KEY` — seen in `.env.example`.

**Likely required env vars (implied by dependencies):**
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` — required for S3/aws usage via `s3fs`/`botocore`.
- `DATABASE_URL` or `PGHOST`/`PGPORT`/`PGUSER`/`PGPASSWORD` — for PostgreSQL connections if used.
- `REDIS_URL` — for Redis caching if used.

## Webhooks & Callbacks

**Incoming or Outgoing Webhooks:**
- Not detected: no explicit webhook endpoints or webhook handlers found in notebooks or README. No mention of webhooks in `README.md` or `.env.example`.

---

*Integration audit: 2026-02-02*
