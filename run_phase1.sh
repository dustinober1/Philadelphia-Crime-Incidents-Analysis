#!/bin/bash
# run_phase1.sh - Quick-start script for Phase 1: High-Level Trends & Seasonality
set -e

show_help() {
    echo "Usage: ./run_phase1.sh [OPTIONS]"
    echo ""
    echo "Run Phase 1 analyses via CLI (Annual Trends, Seasonality, COVID)"
    echo ""
    echo "Options:"
    echo "  --fast       Run with 10% sample for quick testing (~30s)"
    echo "  --single     Run single command: trends, seasonality, covid"
    echo "  --validate   Run artifact validation after execution"
    echo "  --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_phase1.sh                # Full run with --fast flag"
    echo "  ./run_phase1.sh --fast         # Explicit fast mode"
    echo "  ./run_phase1.sh --single covid # Run only COVID analysis"
    echo "  ./run_phase1.sh --validate     # Run and validate artifacts"
}

# Parse arguments
FAST_FLAG=""
SINGLE_FLAG=""
SINGLE_COMMAND=""
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
        --single)
            SINGLE_COMMAND="$2"
            SINGLE_FLAG="--single"
            shift 2
            ;;
        --validate)
            VALIDATE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
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
    exit 1
fi

if ! python -c "import analysis.cli" 2>/dev/null; then
    echo "ERROR: CLI module not found. Please run: pip install -r requirements-dev.txt"
    exit 1
fi

echo "Configuration:"
if [ -n "$FAST_FLAG" ]; then
    echo "  Mode: FAST (10% sample)"
else
    echo "  Mode: Full dataset"
fi
if [ -n "$SINGLE_COMMAND" ]; then
    echo "  Command: chief $SINGLE_COMMAND"
else
    echo "  Commands: chief trends, chief seasonality, chief covid"
fi
echo ""

# Run CLI commands
echo "Starting Phase 1 execution..."
start_time=$(date +%s)

if [ -n "$SINGLE_COMMAND" ]; then
    python -m analysis.cli chief $SINGLE_COMMAND $FAST_FLAG
else
    echo "Running chief trends..."
    python -m analysis.cli chief trends $FAST_FLAG
    echo "Running chief seasonality..."
    python -m analysis.cli chief seasonality $FAST_FLAG
    echo "Running chief covid..."
    python -m analysis.cli chief covid $FAST_FLAG
fi

end_time=$(date +%s)
runtime=$((end_time - start_time))

# Summary
echo ""
echo "============================================"
echo "  Phase 1 Complete!"
echo "============================================"
echo "Runtime: ${runtime} seconds"
echo ""
echo "Output directory: reports/v1.0/chief/"
echo "Artifacts:"
if [ -d "reports/v1.0/chief" ]; then
    echo "  Files: $(ls reports/v1.0/chief/* 2>/dev/null | wc -l | tr -d ' ')"
fi

# Run validation if requested
if [ "$VALIDATE" = true ]; then
    echo ""
    echo "Running artifact validation..."
    python analysis/validate_artifacts.py
fi
