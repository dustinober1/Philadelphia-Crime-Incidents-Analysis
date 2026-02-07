# Feature Research

**Domain:** Local-first container orchestration for full-stack analytics app
**Researched:** February 7, 2026
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = local workflow feels broken.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Single-command startup (`docker compose up`) | Baseline expectation for local dev setup | LOW | Must start all required services without manual sequencing |
| Service separation (api/web/pipeline/supporting) | Easier debugging and restarts | MEDIUM | Distinct containers mirror existing architecture boundaries |
| Reproducible local config via `.env` | Team consistency | LOW | Avoid per-developer hidden config drift |
| Healthchecks and startup gating | Prevent boot race failures | MEDIUM | API should not start before required data/services are ready |
| Persistent local volumes for generated artifacts | Keep state across restarts | LOW | Required for fast iteration on exported data |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Aggressive image slimming strategy | Faster pull/build, lower disk use | MEDIUM | Multi-stage builds + slim bases + dependency pruning |
| Explicit CPU/memory limits per service | Predictable laptop performance | MEDIUM | Prevents runaway resource usage during local analysis runs |
| Compose profiles for optional workflows | Flexible workflows without multiple compose files | MEDIUM | Keep default path simple while enabling power-user flows |
| One-shot pipeline container with idempotent refresh | Clean data refresh UX | MEDIUM | `run --rm` or profile-triggered execution patterns |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Bundling all processes in one container | Feels simpler initially | Hard to restart/debug; poor image hygiene | Keep separate services and shared network |
| Adding cloud-only dependencies to local default flow | “Matches production” argument | Breaks local-only scope, introduces secret/config friction | Local stubs or optional profiles only |
| Auto-rebuild everything on every file change | Perceived convenience | Slow feedback loops and high CPU usage | Targeted bind mounts and selective rebuilds |

## Feature Dependencies

```text
Single-command startup
    └──requires──> Service separation
                       └──requires──> Shared network + env/volumes

Resource limits
    └──requires──> Service-level runtime tuning

Pipeline one-shot container
    └──requires──> Stable artifact volume contract
```

### Dependency Notes

- **Single-command startup requires service separation:** each component must have a clear runtime contract.
- **Resource limits require service-level tuning:** default limits must be realistic per workload.
- **Pipeline one-shot requires artifact volume contract:** API/frontend must read consistent output locations.

## MVP Definition

### Launch With (v1)

- [ ] Compose file starts API, web, pipeline/export job, and required supporting services with one command.
- [ ] Resource limits are configured per service and documented.
- [ ] Docker images are optimized using slim/multi-stage builds where practical.
- [ ] Local env/config path is documented and reproducible.

### Add After Validation (v1.x)

- [ ] Compose profiles for specialized workflows (e.g., heavy analysis vs dashboard-only).
- [ ] Build cache optimization and CI cache hints for faster rebuild loops.

### Future Consideration (v2+)

- [ ] Non-local deployment parity concerns.
- [ ] Managed service integrations beyond local scope.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Single-command full bring-up | HIGH | MEDIUM | P1 |
| Per-service resource limits | HIGH | MEDIUM | P1 |
| Multi-stage image slimming | HIGH | MEDIUM | P1 |
| Compose profiles | MEDIUM | MEDIUM | P2 |
| Advanced rebuild automation | LOW | MEDIUM | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Typical OSS data app pattern | Typical SaaS starter pattern | Our Approach |
|---------|------------------------------|------------------------------|--------------|
| Local startup | `docker compose up` with 2-5 services | Cloud-first with limited local tooling | Full local stack via compose as default |
| Resource control | Often missing or partial | Mostly tuned for cloud quotas | Explicit local CPU/memory limits |
| Pipeline execution | Manual host scripts | External managed jobs | Containerized local job service |

## Sources

- `.planning/PROJECT.md`
- `.planning/codebase/ARCHITECTURE.md`
- `docker-compose.yml`
- `README.md`

---
*Feature research for: local containerized orchestration*
*Researched: February 7, 2026*
