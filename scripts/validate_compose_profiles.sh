#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required" >&2
  exit 1
fi

default_cfg="$(mktemp)"
profile_cfg="$(mktemp)"
trap 'rm -f "$default_cfg" "$profile_cfg"' EXIT

docker compose config >"$default_cfg"
docker compose --profile refresh config >"$profile_cfg"

if rg -q "pipeline-refresh-once:" "$default_cfg"; then
  echo "profile service leaked into default compose config" >&2
  exit 1
fi

rg -q "pipeline:" "$default_cfg"
rg -q "api:" "$default_cfg"
rg -q "web:" "$default_cfg"

rg -q "pipeline-refresh-once:" "$profile_cfg"
rg -q "profiles:" "$profile_cfg"
rg -q -- "- refresh" "$profile_cfg"

rg -q "docker compose --profile refresh config" README.md
rg -q "docker compose --profile refresh run --rm pipeline-refresh-once" README.md
rg -q "docker compose --profile refresh run --rm pipeline-refresh-once" docs/local-compose.md

echo "compose profile validation passed"
