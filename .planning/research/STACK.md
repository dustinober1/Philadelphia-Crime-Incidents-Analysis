# Stack Research

**Domain:** Local-first containerized data platform (analysis + API + web)
**Researched:** February 7, 2026
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Docker Engine + Compose Spec | Compose v2 | Local multi-service orchestration | One-command startup, explicit service dependencies, standardized local workflow |
| Python (analysis/pipeline/API images) | 3.12-slim for runtime, 3.14-compatible code | Runs analysis CLI, export pipeline, FastAPI backend | Existing repo already uses Python-first backend/pipeline and has an API Dockerfile |
| FastAPI + Uvicorn | FastAPI from `api/requirements.txt` | Serves precomputed data and question endpoints | Current backend architecture is already FastAPI and read-optimized |
| Next.js + React | Next 15.5.2 / React 19.1.1 | Frontend dashboard container | Existing frontend already uses this stack and can run in a dedicated service |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| GNU Make (or npm scripts) | latest | Wrap common compose tasks | Use for stable `make up`, `make down`, `make rebuild` commands |
| `docker buildx` | v0.2x+ | Build cache and multi-stage optimization | Use when image-size and build-time tuning matter |
| `tini` | stable | PID 1 signal handling in containers | Use for long-running services to avoid zombie processes |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `docker compose` profiles | Service grouping | Keep optional jobs (one-shot pipeline) separate from always-on services |
| Healthchecks | Reliable startup ordering | Gate frontend/API dependency readiness with `depends_on` + health checks |
| `.env` file | Local config injection | Keep local secrets/config centralized and reproducible |

## Installation

```bash
# Core runtime
brew install docker

# Verify compose
docker compose version

# Start full local stack
docker compose up --build
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Multiple focused service images | Single monolithic image | Only for throwaway prototypes where build speed matters more than clarity |
| Compose-managed local services | Host-installed runtime dependencies | Only when Docker is unavailable on developer machines |
| Multi-stage builds | Single-stage builds | Single-stage is acceptable for very small scripts with zero native deps |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| One giant container for API+web+pipeline | Poor isolation, harder debugging, oversized images | Separate containers per service boundary |
| Unbounded resource usage | Local machine thrash and inconsistent dev behavior | Compose CPU/memory limits and sane defaults |
| Production cloud coupling in local flow | Breaks local-only scope and adds fragile dependencies | Local stubs/volumes for dev-only dependencies |

## Stack Patterns by Variant

**If iterative feature development is the priority:**
- Run API + web continuously, keep pipeline as one-shot job service.
- Because it minimizes rebuild/restart cycle time.

**If reproducible data snapshots are the priority:**
- Add a dedicated scheduled/triggered refresh container profile.
- Because it keeps exported artifacts deterministic across machines.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Next.js 15.5.2 | React 19.1.1 | Matches existing `web/package.json` |
| API container `python:3.12-slim` | FastAPI/Uvicorn app | Matches existing `api/Dockerfile` runtime |
| Compose v2 | Current Docker Desktop/Engine | Needed for modern `docker compose` UX |

## Sources

- `.planning/PROJECT.md` — scope and constraints
- `.planning/codebase/STACK.md` — existing stack and deployment context
- `docker-compose.yml` — current local orchestration baseline
- `api/Dockerfile` — current API container pattern
- `web/package.json` — frontend runtime/dependency versions

---
*Stack research for: local containerized crime analytics platform*
*Researched: February 7, 2026*
