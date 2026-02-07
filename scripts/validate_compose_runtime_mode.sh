#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required" >&2
  exit 1
fi

SERVICES=(pipeline api web)

expected_for() {
  local mode="$1"
  local service="$2"
  case "$mode:$service" in
    default:pipeline) echo "1 1610612736" ;;
    default:api) echo "1 1073741824" ;;
    default:web) echo "1 1073741824" ;;
    low-power:pipeline) echo "0.5 805306368" ;;
    low-power:api) echo "0.5 536870912" ;;
    low-power:web) echo "0.5 536870912" ;;
    high-performance:pipeline) echo "2 3221225472" ;;
    high-performance:api) echo "2 2147483648" ;;
    high-performance:web) echo "2 2147483648" ;;
    *)
      echo "unsupported mode/service: $mode $service" >&2
      return 1
      ;;
  esac
}

extract_value() {
  local config="$1"
  local service="$2"
  local key="$3"

  awk -v svc="$service" -v target="$key" '
    $0 ~ "^  "svc":" { in_block=1; next }
    in_block && $0 ~ "^  [A-Za-z0-9_-]+:" { in_block=0 }
    in_block {
      line=$0
      sub(/^[[:space:]]+/, "", line)
      if (index(line, target":") == 1) {
        sub(target": *", "", line)
        gsub(/\"/, "", line)
        print line
        exit
      }
    }
  ' <<<"$config"
}

check_mode() {
  local mode="$1"
  local rendered

  rendered="$(./scripts/compose_with_runtime_mode.sh --mode "$mode" config)"

  for service in "${SERVICES[@]}"; do
    local expected_cpus expected_mem actual_cpus actual_mem
    read -r expected_cpus expected_mem <<<"$(expected_for "$mode" "$service")"
    actual_cpus="$(extract_value "$rendered" "$service" "cpus")"
    actual_mem="$(extract_value "$rendered" "$service" "mem_limit")"

    if [[ -z "$actual_cpus" || -z "$actual_mem" ]]; then
      echo "missing runtime limits for mode=$mode service=$service" >&2
      return 1
    fi

    if [[ "$actual_cpus" != "$expected_cpus" || "$actual_mem" != "$expected_mem" ]]; then
      echo "runtime mismatch for mode=$mode service=$service" >&2
      echo "expected cpus=$expected_cpus mem_limit=$expected_mem" >&2
      echo "actual   cpus=$actual_cpus mem_limit=$actual_mem" >&2
      return 1
    fi
  done
}

check_mode default
check_mode low-power
check_mode high-performance

echo "compose runtime mode validation passed"
