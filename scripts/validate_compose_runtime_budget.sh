#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required" >&2
  exit 1
fi

rendered="$(docker compose config)"

check_service_budget() {
  local service="$1"
  local expected_cpus="$2"
  local expected_mem="$3"
  local block actual_cpus actual_mem

  block=$(printf "%s\n" "$rendered" | awk -v svc="$service" '
    $0 ~ "^  "svc":" { in_block=1; next }
    in_block && $0 ~ "^  [a-zA-Z0-9_-]+:" { exit }
    in_block { print }
  ')

  if [ -z "$block" ]; then
    echo "Missing service block for $service" >&2
    return 1
  fi

  actual_cpus=$(printf "%s\n" "$block" | awk '/^[[:space:]]+cpus:/{print $2; exit}')
  actual_mem=$(printf "%s\n" "$block" | awk '/^[[:space:]]+mem_limit:/{print $2; exit}' | tr -d '"')

  if [ "$actual_cpus" != "$expected_cpus" ] || [ "$actual_mem" != "$expected_mem" ]; then
    echo "Default runtime budget mismatch for $service" >&2
    echo "expected cpus=$expected_cpus mem_limit=$expected_mem" >&2
    echo "actual   cpus=$actual_cpus mem_limit=$actual_mem" >&2
    return 1
  fi
}

check_service_budget pipeline 1 1610612736
check_service_budget api 1 1073741824
check_service_budget web 1 1073741824

echo "Default compose runtime budgets match expected baseline values"
