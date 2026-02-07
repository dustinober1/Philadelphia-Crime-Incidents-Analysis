#!/usr/bin/env sh
set -eu

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required" >&2
  exit 1
fi

run_build() {
  service="$1"
  dockerfile="$2"
  tag="$3"
  log_file="$4"

  start_ts=$(date +%s)
  docker build --progress=plain -f "$dockerfile" -t "$tag" . >"$log_file" 2>&1
  end_ts=$(date +%s)
  elapsed=$((end_ts - start_ts))

  context=$(grep -E "transferring context:" "$log_file" | tail -1 | sed 's/^.*transferring context: *//' | tr -d '\r' || true)
  image_bytes=$(docker image inspect "$tag" --format '{{.Size}}')

  echo "$service|$elapsed|${context:-unknown}|$image_bytes"
}

format_mb() {
  bytes="$1"
  awk "BEGIN { printf \"%.1f\", $bytes / 1024 / 1024 }"
}

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

api_cold=$(run_build "api" "api/Dockerfile" "phase2-bench-api:cold" "$tmp_dir/api-cold.log")
api_warm=$(run_build "api" "api/Dockerfile" "phase2-bench-api:warm" "$tmp_dir/api-warm.log")

pipeline_cold=$(run_build "pipeline" "pipeline/Dockerfile" "phase2-bench-pipeline:cold" "$tmp_dir/pipeline-cold.log")
pipeline_warm=$(run_build "pipeline" "pipeline/Dockerfile" "phase2-bench-pipeline:warm" "$tmp_dir/pipeline-warm.log")

web_cold=$(run_build "web" "web/Dockerfile" "phase2-bench-web:cold" "$tmp_dir/web-cold.log")
web_warm=$(run_build "web" "web/Dockerfile" "phase2-bench-web:warm" "$tmp_dir/web-warm.log")

printf "\nContainer build benchmark (cold vs warm)\n"
printf "%-10s %-7s %-12s %-18s %-10s\n" "Service" "Run" "Time(s)" "Context" "Image(MB)"

print_row() {
  row="$1"
  run_label="$2"
  service=$(echo "$row" | cut -d'|' -f1)
  seconds=$(echo "$row" | cut -d'|' -f2)
  context=$(echo "$row" | cut -d'|' -f3)
  size_bytes=$(echo "$row" | cut -d'|' -f4)
  size_mb=$(format_mb "$size_bytes")
  printf "%-10s %-7s %-12s %-18s %-10s\n" "$service" "$run_label" "$seconds" "$context" "$size_mb"
}

print_row "$api_cold" "cold"
print_row "$api_warm" "warm"
print_row "$pipeline_cold" "cold"
print_row "$pipeline_warm" "warm"
print_row "$web_cold" "cold"
print_row "$web_warm" "warm"
