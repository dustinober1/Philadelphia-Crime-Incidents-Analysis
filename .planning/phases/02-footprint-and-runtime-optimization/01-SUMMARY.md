# Plan 01 Summary: Container Build Footprint Reduction

## Status
Completed

## Work Completed
- Added repository-level `.dockerignore` to exclude large local artifacts and generated outputs from build context transfer.
- Refactored `api/Dockerfile` dependency install step to isolate requirement installation before source copy and remove redundant install layers.
- Refactored `pipeline/Dockerfile` to keep dependency installation cacheable and copy only required `data/boundaries` and `data/external` datasets rather than all local data/report outputs.
- Updated `web/Dockerfile` to install dependencies during image build.
- Removed runtime `npm install` from `web` compose startup command so default boot uses prebuilt dependency layers.

## Verification
- `docker build -f api/Dockerfile -t phase2-check-api .`
- `docker build -f pipeline/Dockerfile -t phase2-check-pipeline .`
- `docker build -f web/Dockerfile -t phase2-check-web .`
- Warm rebuild cache checks:
  - `docker build -f api/Dockerfile . | rg "CACHED"`
  - `docker build -f pipeline/Dockerfile . | rg "CACHED"`
  - `docker build -f web/Dockerfile . | rg "CACHED"`

## Commits
- `8c984a5` `feat(02-01): reduce container build footprint`
