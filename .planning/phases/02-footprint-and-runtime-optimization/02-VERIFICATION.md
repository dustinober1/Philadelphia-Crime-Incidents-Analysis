# Phase 02 Verification Report

status: passed
phase: 02
phase_name: Footprint and Runtime Optimization
score: 9/9 must-haves verified

## Must-have Verification

1. Build contexts exclude large local artifacts - PASS  
Evidence: root `.dockerignore` excludes `.git`, cache dirs, node artifacts, reports, and large local data outputs.

2. API image uses cache-aware dependency layering - PASS  
Evidence: `api/Dockerfile` copies requirements and installs dependencies before source copy.

3. Pipeline image uses cache-aware dependency layering and reduced copied datasets - PASS  
Evidence: `pipeline/Dockerfile` installs dependencies before source copy and only includes required `data/boundaries` and `data/external` subsets.

4. Web image installs dependencies at build time - PASS  
Evidence: `web/Dockerfile` runs `npm ci --no-audit --no-fund` during build.

5. Default runtime no longer performs per-boot full dependency install - PASS  
Evidence: `docker-compose.yml` web command now runs `npm run dev ...` without `npm install` pre-step.

6. Runtime budgets are explicitly enforced for pipeline/api/web - PASS  
Evidence: `docker-compose.yml` defines `cpus` and `mem_limit` for all three long-running services.

7. Runtime budgets are configurable via env defaults - PASS  
Evidence: `.env.example` includes six budget variables used by compose interpolation.

8. Optimization claims are guarded by repeatable scripts/tests - PASS  
Evidence: `scripts/benchmark_container_builds.sh`, `scripts/validate_compose_runtime_budget.sh`, and `tests/integration/test_phase2_footprint_runtime.py` added and passing.

9. Phase 1 startup behavior remains intact after optimizations - PASS  
Evidence: `python scripts/validate_local_stack.py` passes with health-gated compose startup and service readiness.

## Verification Commands Run

- `docker build -f api/Dockerfile -t phase2-check-api .`
- `docker build -f pipeline/Dockerfile -t phase2-check-pipeline .`
- `docker build -f web/Dockerfile -t phase2-check-web .`
- `docker build -f api/Dockerfile . | rg "CACHED"`
- `docker build -f pipeline/Dockerfile . | rg "CACHED"`
- `docker build -f web/Dockerfile . | rg "CACHED"`
- `docker compose config`
- `./scripts/validate_compose_runtime_budget.sh`
- `pytest -q tests/integration/test_phase2_footprint_runtime.py`
- `./scripts/benchmark_container_builds.sh`
- `python scripts/validate_local_stack.py`
