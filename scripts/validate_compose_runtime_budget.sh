#!/usr/bin/env sh
set -eu

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required" >&2
  exit 1
fi

rendered=$(docker compose config)

check_service_budget() {
  service="$1"
  block=$(printf "%s\n" "$rendered" | awk -v svc="$service" '
    $0 ~ "^  "svc":" { in_block=1; next }
    in_block && $0 ~ "^  [a-zA-Z0-9_-]+:" { exit }
    in_block { print }
  ')

  if [ -z "$block" ]; then
    echo "Missing service block for $service" >&2
    return 1
  fi

  echo "$block" | grep -q "cpus:" || {
    echo "Missing cpus limit for $service" >&2
    return 1
  }

  echo "$block" | grep -q "mem_limit:" || {
    echo "Missing mem_limit for $service" >&2
    return 1
  }
}

check_service_budget pipeline
check_service_budget api
check_service_budget web

echo "Compose runtime budgets are present for pipeline, api, and web"
