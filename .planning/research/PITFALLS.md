# Pitfalls Research

**Domain:** Local-only Dockerized full-stack analytics applications
**Researched:** February 7, 2026
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: "One Command" That Still Needs Manual Steps

**What goes wrong:** `docker compose up` starts containers, but developers still must manually run pipeline/export commands.

**Why it happens:** Pipeline jobs are treated as separate ad hoc scripts, not part of compose contracts.

**How to avoid:** Define pipeline as a compose service/job with clear dependency/trigger behavior and shared artifact output.

**Warning signs:** Fresh clone cannot serve complete data without extra undocumented commands.

**Phase to address:** Phase 1 (compose orchestration baseline).

---

### Pitfall 2: Bloated Images and Slow Rebuild Loops

**What goes wrong:** Iteration speed collapses because images are large and rebuild on small code changes.

**Why it happens:** Single-stage Dockerfiles, broad copy contexts, and mixed build/runtime dependencies.

**How to avoid:** Multi-stage builds, slim runtime images, pinned dependency layers, and targeted `COPY` ordering.

**Warning signs:** Rebuilds consistently take minutes for small changes; local disk usage spikes.

**Phase to address:** Phase 2 (image and runtime optimization).

---

### Pitfall 3: Resource Limits Break Legitimate Workloads

**What goes wrong:** Containers OOM or throttle heavily during normal data refresh jobs.

**Why it happens:** Limits chosen without profiling or workload awareness.

**How to avoid:** Start with conservative defaults plus documented override profiles for heavier runs.

**Warning signs:** Frequent OOM kills, partial artifact writes, flaky local startup.

**Phase to address:** Phase 2 (resource tuning and validation).

---

### Pitfall 4: Hidden Cloud Coupling in "Local-Only" Scope

**What goes wrong:** Local startup silently depends on cloud credentials/services.

**Why it happens:** Existing code paths assume production integration defaults.

**How to avoid:** Provide local fallback paths (in-memory/emulator/stubs) and disable cloud-only dependencies by default.

**Warning signs:** `docker compose up` fails on machines without cloud credentials.

**Phase to address:** Phase 1 (local-default configuration hardening).

---

### Pitfall 5: Volume Contract Drift Between Pipeline and API

**What goes wrong:** Pipeline writes artifacts to locations API does not read, causing stale/missing data.

**Why it happens:** Path conventions are implicit and untested.

**How to avoid:** Establish explicit artifact path contract and validate in integration checks.

**Warning signs:** API boots but returns outdated/empty datasets after pipeline run.

**Phase to address:** Phase 3 (verification and developer UX hardening).

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Reusing one Dockerfile for all services | Faster initial setup | Oversized images and poor cache locality | Temporary prototype only |
| Skipping healthchecks | Less compose config | Flaky startup ordering | Never for default flow |
| Hardcoding env vars in compose | Quick local bring-up | Config drift and secret leakage | Never; use `.env` contracts |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Mapbox token | Assume token always present | Graceful no-token behavior for local dev |
| Firestore-backed questions | Require cloud auth in default path | In-memory fallback/emulator as local default |
| Exported data files | Bind mount wrong host path | Explicit named volume/path contract |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Reinstalling deps every rebuild | Long build times | Cache dependency layers before source copy | Every code iteration |
| Running heavy pipeline on API container | API latency spikes/crashes | Isolate pipeline into dedicated service | Moderate dataset growth |
| Unbounded frontend dev watchers | High CPU fan noise | Tune watch paths and resource limits | On lower-power laptops |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Committing real secrets in compose/env files | Credential exposure | Use `.env.example` + ignored local `.env` |
| Keeping admin defaults in shipped config | Unauthorized local access | Require explicit override and safe defaults |
| Exposing all ports by default | Unnecessary attack surface | Publish only required local ports |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Ambiguous startup status | Developers don't know when stack is ready | Healthcheck-based readiness + clear logs |
| Too many startup variants | Confusion about "correct" path | One canonical default command |
| Missing recovery guidance | Slow troubleshooting | Document reset flows (`down -v`, rebuild, rerun pipeline) |

## "Looks Done But Isn't" Checklist

- [ ] **Compose bring-up:** All required services start with `docker compose up` from clean clone.
- [ ] **Pipeline integration:** Fresh startup produces/loads current artifacts without manual shell steps.
- [ ] **Resource controls:** CPU/memory limits are active and tested under expected local workloads.
- [ ] **Docs:** README local-run section reflects actual command path and recovery steps.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Manual hidden startup steps | MEDIUM | Integrate missing task into compose, update docs/tests |
| Bloated images | MEDIUM | Refactor Dockerfiles to multi-stage and optimize build context |
| Volume drift | HIGH | Standardize artifact paths, add startup validation, re-export data |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| One command still manual | Phase 1 | Clean-clone startup succeeds with one command |
| Image bloat and rebuild drag | Phase 2 | Image size + rebuild time regression checks |
| Resource limits mis-tuned | Phase 2 | Pipeline/API runs complete within capped resources |
| Cloud coupling in local default | Phase 1 | No cloud credentials required for baseline run |
| Volume contract drift | Phase 3 | Integration check validates fresh artifacts visible via API |

## Sources

- `.planning/PROJECT.md`
- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/CONCERNS.md`
- `docker-compose.yml`
- `README.md`

---
*Pitfalls research for: local-only containerized stack*
*Researched: February 7, 2026*
