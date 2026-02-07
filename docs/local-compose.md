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

## Data contract

- Pipeline writes exports to shared volume path `/shared/api-data`.
- API reads exports from `/app/api/data` (same named volume).
- API fails fast at startup when required export files are missing.

## Refresh behavior

- Pipeline runs `pipeline.refresh_data` on a loop.
- Interval controlled by `PIPELINE_REFRESH_INTERVAL_SECONDS` (default `900`).
- On refresh failure, pipeline keeps prior artifacts and retries on the next interval.

## Troubleshooting

- Stream logs:

```bash
docker compose logs -f pipeline api web
```

- Validate stack contract end-to-end:

```bash
python scripts/validate_local_stack.py
```

- Benchmark cold vs warm image builds:

```bash
./scripts/benchmark_container_builds.sh
```

## Reset / clean start

Remove all running services and local volumes:

```bash
docker compose down -v
```

Then bring the stack back:

```bash
docker compose up -d --build
```
