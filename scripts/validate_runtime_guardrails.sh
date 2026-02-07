#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

run_stage() {
  local label="$1"
  shift

  echo "[guardrails] running: $label"
  if ! "$@"; then
    echo "[guardrails] failed: $label" >&2
    return 1
  fi
  echo "[guardrails] passed: $label"
}

run_stage "preset runtime mode validation" ./scripts/validate_compose_runtime_mode.sh
run_stage "default runtime budget regression validation" ./scripts/validate_compose_runtime_budget.sh

echo "[guardrails] all runtime guardrails passed"
