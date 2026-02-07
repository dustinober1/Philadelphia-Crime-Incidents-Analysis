#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: ./scripts/reset_local_stack.sh [--prune-images]

Performs a reproducible local reset:
1) docker compose down -v --remove-orphans
2) optional docker image prune -f
3) prints restart and validation commands

Options:
  --prune-images  Also prune dangling Docker images after compose shutdown
  -h, --help      Show this help text
USAGE
}

PRUNE_IMAGES=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prune-images)
      PRUNE_IMAGES=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

echo "[reset] Stopping local compose stack and removing project volumes..."
docker compose down -v --remove-orphans

if [[ "$PRUNE_IMAGES" == "true" ]]; then
  echo "[reset] Pruning dangling Docker images..."
  docker image prune -f
else
  echo "[reset] Skipping image prune (pass --prune-images to enable)."
fi

cat <<'NEXT'

[reset] Local reset complete.

Next steps:
  1) docker compose up -d --build
  2) docker compose ps
  3) python scripts/validate_local_stack.py --skip-startup

If services still fail health checks:
  - docker compose logs -f pipeline api web
NEXT
