# Local Compose Runbook

This project supports a compose-first local workflow.

## One-command startup

1. Copy local env defaults:

```bash
cp .env.example .env
cp web/.env.example web/.env.local
```

2. Start the full local stack:

```bash
docker compose up -d --build
```

3. Verify health:

```bash
docker compose ps
curl http://localhost:8080/api/health
```

Expected services:
- `pipeline` (healthy)
- `api` (healthy)
- `web` (running; health transitions to healthy)

## Local URLs

- Web UI: `http://localhost:${WEB_PORT:-3001}`
- API health: `http://localhost:8080/api/health`

## First-run env contract

Copy `.env.example` to `.env` and keep these local defaults set for first run:

- `WEB_PORT=3001`
- `PIPELINE_REFRESH_INTERVAL_SECONDS=900`
- `ADMIN_PASSWORD=change-me`
- `ADMIN_TOKEN_SECRET=change-me-token-secret`
- `FIRESTORE_COLLECTION_QUESTIONS=questions`
- `GOOGLE_CLOUD_PROJECT=local-dev`
- `CORS_ORIGINS=http://localhost:3001,http://localhost:3000,https://philly-crime-explorer.web.app,https://philly-crime-explorer.firebaseapp.com`

The compose stack starts locally with these values and does not require cloud credentials.
External analysis API keys in `.env.example` are optional and not required for compose startup.

## Runtime budgets

Default compose startup enforces resource caps:

- `pipeline`: `${PIPELINE_CPU_LIMIT:-1.00}` CPU, `${PIPELINE_MEM_LIMIT:-1536m}` memory
- `api`: `${API_CPU_LIMIT:-1.00}` CPU, `${API_MEM_LIMIT:-1024m}` memory
- `web`: `${WEB_CPU_LIMIT:-1.00}` CPU, `${WEB_MEM_LIMIT:-1024m}` memory

To tune locally, edit `.env` and validate rendered limits:

```bash
docker compose config | rg -n "cpus|mem_limit"
./scripts/validate_compose_runtime_budget.sh
```

## Optional compose profiles

Default startup behavior remains:

```bash
docker compose up -d --build
```

Profile-gated workflow available for advanced local use:

- `refresh` profile: one-shot pipeline export refresh

```bash
docker compose --profile refresh config
docker compose --profile refresh run --rm pipeline-refresh-once
```

Profiles are opt-in overlays and should not be required for routine development startup.

## Data contract

- Pipeline writes exports to shared volume path `/shared/api-data`.
- API reads exports from `/app/api/data` (same named volume).
- API fails fast at startup when required export files are missing.

## Refresh behavior

- Pipeline runs `pipeline.refresh_data` on a loop.
- Interval controlled by `PIPELINE_REFRESH_INTERVAL_SECONDS` (default `900`).
- On refresh failure, pipeline keeps prior artifacts and retries on the next interval.

## Recovery playbooks

### Failure mode: API never becomes healthy after startup

Symptom:
- `docker compose ps` shows `pipeline` unhealthy or `api` waiting/restarting.

Recovery steps:

```bash
docker compose logs --tail=200 pipeline api
docker compose restart pipeline api
docker compose ps
```

Expected recovery signal:
- `pipeline` and `api` both report `healthy`.

### Failure mode: stale shared-volume exports break API data contract

Symptom:
- `curl http://localhost:8080/api/health` reports missing exports or stale metadata.

Recovery steps:

```bash
./scripts/reset_local_stack.sh
docker compose up -d --build
```

Expected recovery signal:
- API health returns `{\"ok\": true}` and no missing exports.

### Failure mode: dependency or Docker cache drift after local code changes

Symptom:
- Service starts but behavior does not reflect recent dependency or image changes.

Recovery steps:

```bash
docker compose down
docker compose build --no-cache pipeline api web
docker compose up -d
```

Expected recovery signal:
- Rebuilt images start cleanly and health checks pass.

## Post-recovery validation checklist

Run these after any recovery flow:

```bash
docker compose ps
curl http://localhost:8080/api/health
python scripts/validate_local_stack.py --skip-startup
```

Expected signals:
- `pipeline` and `api` are `healthy`; `web` is `running` or `healthy`.
- API health payload includes `"ok": true`.
- Validator reports endpoint and export checks passed.

## Troubleshooting and diagnostics

- Stream logs:

```bash
docker compose logs -f pipeline api web
```

- Validate stack contract end-to-end (startup + readiness checks):

```bash
python scripts/validate_local_stack.py
```

- Benchmark cold vs warm image builds:

```bash
./scripts/benchmark_container_builds.sh
```

## Reset / clean start

Preferred scripted reset:

```bash
./scripts/reset_local_stack.sh
```

Optional deeper reset with dangling image prune:

```bash
./scripts/reset_local_stack.sh --prune-images
```
