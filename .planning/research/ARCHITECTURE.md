# Architecture Research

**Domain:** Local container architecture for analytics API + dashboard platform
**Researched:** February 7, 2026
**Confidence:** HIGH

## Standard Architecture

### System Overview

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                         Docker Compose Project                             │
├────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐   ┌─────────────┐   ┌──────────────────┐                 │
│  │ Web Service │   │ API Service │   │ Pipeline Service │                 │
│  │ (Next.js)   │   │ (FastAPI)   │   │ (refresh/export) │                 │
│  └──────┬──────┘   └──────┬──────┘   └────────┬─────────┘                 │
│         │                 │                   │                           │
├─────────┴─────────────────┴───────────────────┴───────────────────────────┤
│                    Shared Internal Network + Env                           │
├────────────────────────────────────────────────────────────────────────────┤
│      ┌──────────────────────┐      ┌──────────────────────────────────┐    │
│      │ Artifacts Volume     │      │ Optional Supporting Services     │    │
│      │ (api/data outputs)   │      │ (e.g., local emulators/stubs)    │    │
│      └──────────────────────┘      └──────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| `web` | Serve local UI and call local API | Next.js dev/prod container with API base URL wiring |
| `api` | Serve precomputed payloads and app endpoints | FastAPI container with artifact volume mount |
| `pipeline` | Generate/refresh API data artifacts | Python one-shot job container or profile service |
| `supporting` | Local stand-ins for external systems | Optional containers enabled by profile |

## Recommended Project Structure

```text
./
├── docker-compose.yml             # Primary local orchestration
├── docker/
│   ├── api.Dockerfile             # API runtime image (or existing api/Dockerfile)
│   ├── web.Dockerfile             # Frontend image
│   └── pipeline.Dockerfile        # Pipeline job image
├── .env.example                   # Local config contract
├── api/
├── web/
└── pipeline/
```

### Structure Rationale

- **Service-specific Dockerfiles:** better image-size optimization and cache behavior.
- **Single compose entrypoint:** keeps one-command startup aligned with core value.
- **Shared artifact volume:** preserves contract between data export and API serving.

## Architectural Patterns

### Pattern 1: Service-per-boundary Containers

**What:** One container per runtime concern (web, api, pipeline).
**When to use:** Always for this project; boundaries already exist in code.
**Trade-offs:** More compose config, much better isolation and observability.

### Pattern 2: One-shot Data Job Container

**What:** Pipeline executes as idempotent job, writing artifacts to shared volume.
**When to use:** Data refresh/export workflows.
**Trade-offs:** Adds ordering concerns, but keeps API runtime light.

### Pattern 3: Local Resource Budgeting

**What:** CPU/memory caps per service.
**When to use:** Default local setup to avoid laptop exhaustion.
**Trade-offs:** Needs tuning for heavy analysis runs.

## Data Flow

### Request Flow

```text
Browser
  -> web container (Next.js)
  -> api container (FastAPI)
  -> reads exported artifacts from shared data volume
```

### State Management

```text
Pipeline container writes artifacts -> shared volume -> API reads on startup/request -> web fetches API
```

### Key Data Flows

1. **Artifact publication flow:** `pipeline` writes JSON/GeoJSON artifacts consumed by `api`.
2. **Dashboard read flow:** `web` queries `api` endpoints and renders maps/charts locally.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 1 developer | Default compose with conservative limits |
| Small team local use | Add profile variants and volume conventions |
| CI-local parity | Introduce deterministic build cache + pinned image tags |

### Scaling Priorities

1. **First bottleneck:** pipeline runtime/memory pressure; mitigate with tuned limits and staged jobs.
2. **Second bottleneck:** frontend rebuild latency; mitigate with bind mounts and dependency caching.

## Anti-Patterns

### Anti-Pattern 1: API Builds Artifacts at Startup

**What people do:** Move heavy data prep into API boot.
**Why it's wrong:** Slow/fragile startup, violates separation of concerns.
**Do this instead:** Keep explicit pipeline service/job for exports.

### Anti-Pattern 2: Global Unlimited Resource Usage

**What people do:** No limits on CPU/memory.
**Why it's wrong:** Local instability and non-reproducible performance.
**Do this instead:** Define per-service caps and document override path.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Mapbox | Frontend env token | Keep optional for local, provide fallback behavior |
| Firestore path | Optional/emulated or in-memory fallback | Maintain local-only execution path without cloud dependency |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `pipeline` -> `api` | Shared artifacts (volume/path contract) | Most critical contract for deterministic local runs |
| `web` <-> `api` | HTTP on compose network | Keep base URL configurable via env |

## Sources

- `.planning/codebase/ARCHITECTURE.md`
- `docker-compose.yml`
- `api/Dockerfile`
- `.planning/PROJECT.md`

---
*Architecture research for: local compose-first analytics stack*
*Researched: February 7, 2026*
