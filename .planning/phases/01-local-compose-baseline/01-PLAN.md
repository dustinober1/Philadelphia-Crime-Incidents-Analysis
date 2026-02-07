---
wave: 1
depends_on: []
files_modified:
  - docker-compose.yml
  - api/Dockerfile
  - web/Dockerfile
  - pipeline/Dockerfile
  - pipeline/compose_entrypoint.sh
autonomous: true
---

# Plan 01: Compose Service Topology Baseline

## Objective
Create the baseline container topology so `docker compose up` starts `web`, `api`, and `pipeline` as distinct long-running services using local-only defaults.

<tasks>
  <task id="01.1" title="Add missing container assets for web and pipeline">
    <details>
      Create `web/Dockerfile` and `pipeline/Dockerfile` suitable for local development. Keep builds deterministic and compatible with compose volume mounts.
    </details>
  </task>
  <task id="01.2" title="Convert compose from single-service to full core stack">
    <details>
      Update `docker-compose.yml` to define `web`, `api`, and `pipeline` as separate services with explicit commands, ports, and mount strategy for local iteration.
    </details>
  </task>
  <task id="01.3" title="Ensure pipeline runs as a durable service">
    <details>
      Add a pipeline entrypoint (or command wrapper) that keeps pipeline alive, continuously refreshing exports on a configurable interval instead of exiting after one run.
    </details>
  </task>
</tasks>

## Verification Criteria
- `docker compose config` validates successfully.
- `docker compose up` starts three core services (`web`, `api`, `pipeline`) without requiring cloud credentials.
- `docker compose ps` shows all three core services running after initial warmup.

## must_haves
- Core service boundaries are explicit and independent (`web`, `api`, `pipeline`).
- Default startup path is one command from repository root.
- Pipeline is long-running in baseline startup.
