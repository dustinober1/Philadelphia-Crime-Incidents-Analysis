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

## Reset / clean start

Remove all running services and local volumes:

```bash
docker compose down -v
```

Then bring the stack back:

```bash
docker compose up -d --build
```
