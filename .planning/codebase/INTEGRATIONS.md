# External Integrations

**Analysis Date:** 2026-01-27

## APIs & External Services

**Public Data:**
- **Philadelphia Crime Data (Carto)** - Source of crime incident data
  - Endpoint: `https://phl.carto.com/api/v2/sql`
  - Implementation: `scripts/helper/scrape.py`
  - Auth: Public (No authentication required)
  - Method: SQL queries via GET requests (table: `incidents_part1_part2`)

## Data Storage

**Databases:**
- None - File-based storage only

**File Storage:**
- **Local Filesystem**
  - Raw Data: `data/raw/` (CSV format)
  - Processed Data: `data/processed/` (Parquet format)
  - Managed by: `scripts/helper/scrape.py` and `scripts/helper/csv_to_parquet.py`

**Caching:**
- **Simple File Check**
  - Mechanism: Checks if file exists before downloading in `scrape.py`

## Authentication & Identity

**Auth Provider:**
- None - No user authentication system

## Monitoring & Observability

**Error Tracking:**
- None - Print statements and exception handling in scripts

**Logs:**
- Console output only (print statements)

## CI/CD & Deployment

**Hosting:**
- Local execution

**CI Pipeline:**
- None

## Environment Configuration

**Required env vars:**
- None detected

**Secrets location:**
- No secrets detected (Public API)

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

---

*Integration audit: 2026-01-27*
