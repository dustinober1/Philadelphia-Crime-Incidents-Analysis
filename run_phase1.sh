#!/bin/bash
# run_phase1.sh - Quick-start script for Phase 1: High-Level Trends & Seasonality
set -e

show_help() {
    echo "Usage: ./run_phase1.sh [VERSION] [OPTIONS]"
    echo ""
    echo "Run Phase 1 notebooks (Annual Trends, Seasonality, COVID Analysis)"
    echo ""
    echo "Arguments:"
    echo "  VERSION      Artifact version label (default: v1.0)"
    echo ""
    echo "Options:"
    echo "  --fast       Run with 10% sample for quick testing (~30s)"
    echo "  --notebook   Run single notebook: annual_trend, seasonality, covid"
    echo "  --validate   Run artifact validation after execution"
    echo "  --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_phase1.sh                    # Full run with v1.0"
    echo "  ./run_phase1.sh v2.0               # Full run with custom version"
    echo "  ./run_phase1.sh v1.0 --fast        # Quick test run"
    echo "  ./run_phase1.sh --notebook covid   # Run only COVID notebook"
    echo "  ./run_phase1.sh --validate         # Run and validate artifacts"
}

# Parse arguments
VERSION="v1.0"
FAST_FLAG=""
NOTEBOOK_FLAG=""
VALIDATE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        --fast)
            FAST_FLAG="--fast"
            shift
            ;;
        --notebook)
            NOTEBOOK_FLAG="--notebook $2"
            shift 2
            ;;
        --validate)
            VALIDATE=true
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
        *)
            VERSION="$1"
            shift
            ;;
    esac
done

echo "============================================"
echo "  Phase 1: High-Level Trends & Seasonality"
echo "============================================"
echo ""

# Check prerequisites
if [ ! -f "data/crime_incidents_combined.parquet" ]; then
    echo "ERROR: Crime data not found at data/crime_incidents_combined.parquet"
    echo "Please download and prepare the data first."
    exit 1
fi

if [ ! -f "config/phase1_config.yaml" ]; then
    echo "ERROR: Configuration not found at config/phase1_config.yaml"
    echo "Please run infrastructure setup first."
    exit 1
fi

echo "Configuration:"
echo "  Version: $VERSION"
if [ -n "$FAST_FLAG" ]; then
    echo "  Mode: FAST (10% sample)"
else
    echo "  Mode: Full dataset"
fi
if [ -n "$NOTEBOOK_FLAG" ]; then
    echo "  Notebook: $(echo $NOTEBOOK_FLAG | cut -d' ' -f2)"
else
    echo "  Notebooks: annual_trend, seasonality, covid"
fi
echo ""

# Run orchestrator
echo "Starting Phase 1 execution..."
start_time=$(date +%s)

python analysis/orchestrate_phase1.py --version "$VERSION" $FAST_FLAG $NOTEBOOK_FLAG

end_time=$(date +%s)
runtime=$((end_time - start_time))

# Summary
echo ""
echo "============================================"
echo "  Phase 1 Complete!"
echo "============================================"
echo "Runtime: ${runtime} seconds"
echo "Artifacts:"
echo "  PNGs: $(ls reports/*_v*.png 2>/dev/null | wc -l | tr -d ' ')"
echo "  Reports: $(ls reports/*_report_*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "  Manifests: $(ls reports/*_manifest_*.json 2>/dev/null | wc -l | tr -d ' ')"
echo ""
echo "Output directory: reports/"

# Run validation if requested
if [ "$VALIDATE" = true ]; then
    echo ""
    echo "Running artifact validation..."
    python analysis/validate_artifacts.py
fi
