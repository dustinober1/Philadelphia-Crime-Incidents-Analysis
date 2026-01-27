# External Integrations

**Analysis Date:** 2026-01-27

## APIs & External Services

**Geospatial:**
- OpenStreetMap - Basemaps through contextily
  - Service: OpenStreetMap tile servers
  - Usage: Background maps in geospatial visualizations
- Geocoding services - Through geopy
  - Providers: Multiple (Nominatim, Google, etc.)
  - Usage: Address to coordinate conversion

## Data Storage

**Databases:**
- None detected - No explicit database connections found in requirements
- Local files only: CSV, shapefiles, and other local formats

**File Storage:**
- Local filesystem only - Data stored in ./data directory
- Jupyter notebooks - Analysis and results storage

**Caching:**
- None explicitly configured - Relying on Python memory management

## Authentication & Identity

**Auth Provider:**
- None - No authentication systems detected
- Project appears to be local analysis environment

## Monitoring & Observability

**Error Tracking:**
- None - No error tracking services configured

**Logs:**
- Standard output - Basic logging through notebook outputs

## CI/CD & Deployment

**Hosting:**
- Local only - No deployment targets identified
- Jupyter notebooks for development/exploration

**CI Pipeline:**
- None - No CI/CD pipeline detected

## Environment Configuration

**Required env vars:**
- None explicitly defined in requirements or config

**Secrets location:**
- Not applicable - No external services requiring secrets detected

## Webhooks & Callbacks

**Incoming:**
- None - No webhook endpoints detected

**Outgoing:**
- Geocoding API calls - Through geopy library
  - Endpoints: Various geocoding provider APIs

---

*Integration audit: 2026-01-27*