# External Integrations

**Analysis Date:** 2026-02-07

## APIs & External Services

**Mapping & Geospatial Tiles:**
- Mapbox - Basemap tiles and map interaction in the web client.
  - SDK/Client: `mapbox-gl`, `react-map-gl` (`web/package.json`, `web/src/components/MapContainer.tsx`).
  - Auth: `NEXT_PUBLIC_MAPBOX_TOKEN` (`web/.env.example`).
  - Endpoints used: client-side Mapbox style URL (`mapbox://styles/mapbox/light-v11`).

**Cloud Platform Services:**
- Google Cloud Run - hosts FastAPI backend.
  - Deployment definition: `cloudbuild.yaml` and Firebase rewrite in `firebase.json`.
  - Auth/config: service env vars (`GOOGLE_CLOUD_PROJECT`, `CORS_ORIGINS`, etc.).

**Community Q&A Storage Backend:**
- Google Firestore (optional runtime dependency) - stores submitted/answered community questions.
  - SDK/Client: `firebase-admin` (`api/requirements.txt`, `api/routers/questions.py`).
  - Auth: application default credentials + server env config.
  - Fallback path: in-memory dictionary when Firestore init fails (`api/routers/questions.py`).

## Data Storage

**Databases:**
- Firestore collection for Q&A documents (`FIRESTORE_COLLECTION_QUESTIONS`).
  - Connection: Google ADC + project-scoped service account.
  - Client: `firebase_admin.firestore`.

**File Storage:**
- Local repository artifacts as source of truth for API responses:
  - Main data: `data/crime_incidents_combined.parquet`.
  - Boundaries: `data/boundaries/*.geojson`.
  - Exported API payloads: `api/data/*.json` and `api/data/geo/*.geojson`.

**Caching:**
- In-memory API cache at process startup for exported payloads (`api/services/data_loader.py`).
- Joblib disk cache for analysis data loading (`analysis/data/cache.py`, used by `analysis/data/loading.py`).

## Authentication & Identity

**Auth Provider:**
- Custom admin authentication for question moderation.
  - Implementation: password check + HMAC-signed bearer token (`api/routers/questions.py`).
  - Secrets: `ADMIN_PASSWORD`, `ADMIN_TOKEN_SECRET`.
  - Session model: stateless signed token with 1-hour TTL.

**OAuth Integrations:**
- Not detected.

## Monitoring & Observability

**Error Tracking:**
- Not detected (no Sentry/NewRelic integration in repo).

**Analytics:**
- Not detected.

**Logs:**
- API request/exception logging via Python `logging` middleware (`api/main.py`).
- Runtime destination is platform stdout/stderr (Cloud Run / local Uvicorn).

## CI/CD & Deployment

**Hosting:**
- Frontend: Firebase Hosting serving static export from `web/out` (`firebase.json`).
- Backend: Cloud Run service `philly-crime-api` (`cloudbuild.yaml`, `firebase.json` rewrite).

**CI Pipeline:**
- Google Cloud Build builds/pushes API image and deploys to Cloud Run (`cloudbuild.yaml`).
- Local deployment helper command in `Makefile` (`firebase deploy && gcloud run deploy ...`).

## Environment Configuration

**Development:**
- Required web vars: `NEXT_PUBLIC_MAPBOX_TOKEN`, optional `NEXT_PUBLIC_API_BASE` (`web/.env.example`).
- Required API vars for admin/Q&A behavior: `ADMIN_PASSWORD`, `ADMIN_TOKEN_SECRET`, `FIRESTORE_COLLECTION_QUESTIONS`, `GOOGLE_CLOUD_PROJECT` (`README.md`).
- Local fallback for questions exists when Firestore is unavailable.

**Staging:**
- No dedicated staging profile/config file detected in-repo.

**Production:**
- Cloud Run secrets injected via Secret Manager (`cloudbuild.yaml` `--set-secrets`).
- CORS origins configured via env var list (`api/main.py`, `cloudbuild.yaml`).

## Webhooks & Callbacks

**Incoming:**
- Not detected.

**Outgoing:**
- Not detected.

---

*Integration audit: 2026-02-07*
*Update when adding/removing external services*
