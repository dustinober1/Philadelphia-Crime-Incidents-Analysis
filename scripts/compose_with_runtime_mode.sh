#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required" >&2
  exit 1
fi

usage() {
  cat <<USAGE
Usage:
  ./scripts/compose_with_runtime_mode.sh [--mode MODE] [--recommend] <compose-args...>
  ./scripts/compose_with_runtime_mode.sh --recommend

Modes:
  default           Use baseline compose behavior (default)
  low-power         Overlay .env.runtime.low-power
  high-performance  Overlay .env.runtime.high-performance
  auto              Detect host resources and choose a preset automatically

Examples:
  ./scripts/compose_with_runtime_mode.sh up -d --build
  ./scripts/compose_with_runtime_mode.sh --mode low-power up -d --build
  ./scripts/compose_with_runtime_mode.sh --mode auto up -d --build
  ./scripts/compose_with_runtime_mode.sh --recommend
  ./scripts/compose_with_runtime_mode.sh --mode high-performance config
USAGE
}

mode="default"
recommend_only=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      shift
      [[ $# -gt 0 ]] || { echo "missing value for --mode" >&2; usage; exit 1; }
      mode="$1"
      shift
      ;;
    --recommend)
      recommend_only=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      break
      ;;
  esac
done

if [[ "$mode" == "auto" || "$recommend_only" == "true" ]]; then
  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required for auto resource detection mode" >&2
    exit 1
  fi

  if ! recommendation_env="$(python3 scripts/preset_calculator.py --format env)"; then
    echo "failed to calculate smart preset recommendation" >&2
    exit 1
  fi

  eval "$recommendation_env"

  if [[ "$recommend_only" == "true" ]]; then
    cat <<EOF
Platform: ${DETECTION_PLATFORM}
CPU cores: ${DETECTION_CPU_CORES}
Total RAM (GB): ${DETECTION_TOTAL_MEM_GB}
Available RAM (GB): ${DETECTION_AVAILABLE_MEM_GB}
Recommended mode: ${RECOMMENDED_MODE}
Reason: ${RECOMMENDATION_REASON}
EOF
    exit 0
  fi

  mode="${RECOMMENDED_MODE}"
  echo "[runtime-mode] auto-selected mode: ${mode} (${RECOMMENDATION_REASON})" >&2
fi

if [[ "$recommend_only" != "true" ]]; then
  [[ $# -gt 0 ]] || { echo "missing docker compose args" >&2; usage; exit 1; }
fi

preset_file=""
case "$mode" in
  default)
    ;;
  low-power)
    preset_file=".env.runtime.low-power"
    ;;
  high-performance)
    preset_file=".env.runtime.high-performance"
    ;;
  auto)
    echo "internal error: auto mode should resolve to an explicit preset" >&2
    exit 1
    ;;
  *)
    echo "invalid mode: $mode" >&2
    usage
    exit 1
    ;;
esac

args=()
if [[ -f .env ]]; then
  args+=(--env-file .env)
fi
if [[ -n "$preset_file" ]]; then
  [[ -f "$preset_file" ]] || { echo "missing preset file: $preset_file" >&2; exit 1; }
  args+=(--env-file "$preset_file")
fi

if [[ ${#args[@]} -gt 0 ]]; then
  exec docker compose "${args[@]}" "$@"
fi

exec docker compose "$@"
