---
wave: 1
depends_on: []
files_modified:
  - .dockerignore
  - api/Dockerfile
  - pipeline/Dockerfile
  - web/Dockerfile
autonomous: true
---

# Plan 01: Container Build Footprint Reduction

## Objective
Reduce image size and build context transfer for `api`, `pipeline`, and `web` by tightening Docker ignore rules and hardening Dockerfiles for cache-friendly, minimal builds.

<tasks>
  <task id="01.1" title="Add repository-level .dockerignore tuned to local workflow">
    <details>
      Create a root `.dockerignore` that excludes large generated artifacts and local-only directories (`web/node_modules`, `web/.next`, `web/out`, `.git`, `**/__pycache__`, local venvs, logs, temporary outputs) while keeping files required by `api`, `pipeline`, and `web` builds.
    </details>
  </task>
  <task id="01.2" title="Refactor API and pipeline Dockerfiles for smaller and more stable layers">
    <details>
      Reorder and tighten `api/Dockerfile` and `pipeline/Dockerfile` so dependency installation is isolated from source-copy layers. Remove unnecessary install duplication and ensure copied paths are only those needed at runtime.
    </details>
  </task>
  <task id="01.3" title="Align web image behavior with build-time dependency installation">
    <details>
      Update `web/Dockerfile` so dependencies are installed during image build and runtime startup does not perform a full package install on each container boot in the default flow.
    </details>
  </task>
</tasks>

## Verification Criteria
- `docker build -f api/Dockerfile .`, `docker build -f pipeline/Dockerfile .`, and `docker build -f web/Dockerfile .` all succeed.
- Build contexts are measurably smaller (visible in build output transfer size) after `.dockerignore` introduction.
- Rebuilding after a source-only code change reuses dependency layers for all three images.

## must_haves
- All three core service images use slim/cache-aware patterns.
- Build contexts exclude large generated local artifacts.
- Default runtime no longer depends on per-start full dependency installs.
