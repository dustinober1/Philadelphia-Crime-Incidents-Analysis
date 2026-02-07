#!/usr/bin/env sh
set -eu

OUTPUT_DIR="${PIPELINE_OUTPUT_DIR:-/shared/api-data}"
INTERVAL_SECONDS="${PIPELINE_REFRESH_INTERVAL_SECONDS:-900}"
HEALTH_FILE="${PIPELINE_HEALTH_FILE:-/tmp/pipeline-refresh.ok}"

mkdir -p "${OUTPUT_DIR}"

if [ -d "/app/api/data" ] && [ -z "$(ls -A "${OUTPUT_DIR}" 2>/dev/null)" ]; then
  echo "Seeding ${OUTPUT_DIR} from repository api/data snapshot"
  cp -R /app/api/data/. "${OUTPUT_DIR}/"
fi

if [ -f "${OUTPUT_DIR}/metadata.json" ]; then
  touch "${HEALTH_FILE}"
fi

echo "Pipeline compose entrypoint started"
echo "Output directory: ${OUTPUT_DIR}"
echo "Refresh interval: ${INTERVAL_SECONDS}s"

while true; do
  echo "Refreshing exports at $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  if python -m pipeline.refresh_data --output-dir "${OUTPUT_DIR}"; then
    touch "${HEALTH_FILE}"
    echo "Refresh completed; sleeping ${INTERVAL_SECONDS}s"
  else
    rm -f "${HEALTH_FILE}"
    echo "Refresh failed; retaining previous artifacts and retrying in ${INTERVAL_SECONDS}s"
  fi
  sleep "${INTERVAL_SECONDS}"
done
