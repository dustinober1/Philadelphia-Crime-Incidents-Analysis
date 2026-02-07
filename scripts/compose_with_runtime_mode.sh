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
  ./scripts/compose_with_runtime_mode.sh [--mode MODE] <compose-args...>

Modes:
  default           Use baseline compose behavior (default)
  low-power         Overlay .env.runtime.low-power
  high-performance  Overlay .env.runtime.high-performance

Examples:
  ./scripts/compose_with_runtime_mode.sh up -d --build
  ./scripts/compose_with_runtime_mode.sh --mode low-power up -d --build
  ./scripts/compose_with_runtime_mode.sh --mode high-performance config
USAGE
}

mode="default"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      shift
      [[ $# -gt 0 ]] || { echo "missing value for --mode" >&2; usage; exit 1; }
      mode="$1"
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

[[ $# -gt 0 ]] || { echo "missing docker compose args" >&2; usage; exit 1; }

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
