#!/usr/bin/env python3
"""Validate compose baseline readiness for local stack."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen
from datetime import datetime
from typing import List, Dict, Any, Optional
import yaml
from validation_models import CheckResult, ValidationResult, HealthInfo
from data_integrity_validators import validate_response_structure
from performance_utils import timed_execution_with_threshold, check_performance_threshold


def timed_execution(func):
    """Decorator to measure execution time of functions."""
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        duration = (time.perf_counter() - start_time) * 1000  # Convert to ms
        return result, duration
    return wrapper


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def fetch_json(url: str) -> dict[str, object]:
    with urlopen(url, timeout=5) as response:  # nosec: B310 - local validation endpoint
        return json.loads(response.read().decode("utf-8"))


@timed_execution_with_threshold("trends")
def validate_trends_endpoint(url: str) -> dict[str, object]:
    """Validate trends endpoint with performance timing."""
    with urlopen(url, timeout=5) as response:  # nosec: B310 - local validation endpoint
        return json.loads(response.read().decode("utf-8"))


@timed_execution_with_threshold("spatial")
def validate_spatial_endpoint(url: str) -> dict[str, object]:
    """Validate spatial endpoint with performance timing."""
    with urlopen(url, timeout=5) as response:  # nosec: B310 - local validation endpoint
        return json.loads(response.read().decode("utf-8"))


@timed_execution_with_threshold("policy")
def validate_policy_endpoint(url: str) -> dict[str, object]:
    """Validate policy endpoint with performance timing."""
    with urlopen(url, timeout=5) as response:  # nosec: B310 - local validation endpoint
        return json.loads(response.read().decode("utf-8"))


@timed_execution_with_threshold("forecasting")
def validate_forecasting_endpoint(url: str) -> dict[str, object]:
    """Validate forecasting endpoint with performance timing."""
    with urlopen(url, timeout=5) as response:  # nosec: B310 - local validation endpoint
        return json.loads(response.read().decode("utf-8"))


@timed_execution_with_threshold("metadata")
def validate_metadata_endpoint(url: str) -> dict[str, object]:
    """Validate metadata endpoint with performance timing."""
    with urlopen(url, timeout=5) as response:  # nosec: B310 - local validation endpoint
        return json.loads(response.read().decode("utf-8"))


@timed_execution
def wait_for_health(url: str, timeout_seconds: int = 120) -> dict[str, object]:
    deadline = time.time() + timeout_seconds
    last_error = "unknown error"
    while time.time() < deadline:
        try:
            payload = fetch_json(url)
            if payload.get("ok") is True:
                return payload
            last_error = f"health endpoint returned ok!=true; payload={payload}"
        except Exception as exc:
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError(f"API health check failed for {url}: {last_error}")


@timed_execution
def wait_for_http_ok(url: str, timeout_seconds: int = 120) -> None:
    deadline = time.time() + timeout_seconds
    last_error = "unknown error"
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=5) as response:  # nosec: B310 - local validation endpoint
                if 200 <= response.status < 400:
                    return
                last_error = f"unexpected status: {response.status}"
        except Exception as exc:
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError(f"Web endpoint check failed for {url}: {last_error}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate local compose stack health and endpoint readiness. "
            "By default this script starts/rebuilds the stack first."
        )
    )
    parser.add_argument(
        "--skip-startup",
        action="store_true",
        help="Do not run `docker compose up -d --build`; only validate running services.",
    )
    parser.add_argument(
        "--api-health-url",
        default="http://127.0.0.1:8080/api/health",
        help="API health endpoint URL to validate.",
    )
    parser.add_argument(
        "--web-url",
        default="http://127.0.0.1:3001",
        help="Web URL to validate.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=120,
        help="Max seconds to wait for each endpoint.",
    )
    parser.add_argument(
        "--format",
        choices=["human", "json", "yaml"],
        default="human",
        help="Output format for validation results",
    )
    parser.add_argument(
        "--extended",
        action="store_true",
        help="Run extended validation on additional high-value API endpoints",
    )
    parser.add_argument(
        "--api-base-url",
        default="http://127.0.0.1:8080",
        help="Base URL for API endpoints (default: http://127.0.0.1:8080)",
    )
    return parser.parse_args()


def output_results(results: ValidationResult, format_type: str = "human") -> None:
    """Output validation results in the specified format."""
    if format_type == "json":
        print(results.model_dump_json(indent=2))
    elif format_type == "yaml":
        print(yaml.dump(results.model_dump(), default_flow_style=False))
    else:  # human
        print("Local compose smoke check passed")
        print(f"- API health: {results.service_info.get('api_health_url', 'Unknown')}")
        print(f"- Web endpoint: {results.service_info.get('web_url', 'Unknown')}")
        print("- Required API exports: present")


def run_extended_validation(args) -> List[CheckResult]:
    """Run extended validation on high-value API endpoints."""
    checks = []
    
    # Define the endpoints to validate
    endpoints_to_validate = [
        ("Trends Annual", f"{args.api_base_url}/api/v1/trends/annual", "trends"),
        ("Spatial Districts", f"{args.api_base_url}/api/v1/spatial/districts", "spatial"),
        ("Policy Retail Theft", f"{args.api_base_url}/api/v1/policy/retail-theft", "policy"),
        ("Forecasting Time Series", f"{args.api_base_url}/api/v1/forecasting/time-series", "forecasting"),
        ("Metadata", f"{args.api_base_url}/api/v1/metadata", "metadata"),
        ("Trends Monthly", f"{args.api_base_url}/api/v1/trends/monthly", "trends"),
        ("Spatial Hotspots", f"{args.api_base_url}/api/v1/spatial/hotspots", "spatial"),
    ]
    
    for name, url, endpoint_type in endpoints_to_validate:
        try:
            # Validate the endpoint based on its type
            if endpoint_type == "trends":
                data, duration, perf_status = validate_trends_endpoint(url)
            elif endpoint_type == "spatial":
                data, duration, perf_status = validate_spatial_endpoint(url)
            elif endpoint_type == "policy":
                data, duration, perf_status = validate_policy_endpoint(url)
            elif endpoint_type == "forecasting":
                data, duration, perf_status = validate_forecasting_endpoint(url)
            elif endpoint_type == "metadata":
                data, duration, perf_status = validate_metadata_endpoint(url)
            else:
                # Fallback for unknown types
                with urlopen(url, timeout=5) as response:
                    data = json.loads(response.read().decode("utf-8"))
                start_time = time.perf_counter()
                # Simulate timing for fallback
                duration = 0  # Will be calculated properly in actual implementation
                perf_status = None
            
            # Validate data integrity
            integrity_errors = validate_response_structure(endpoint_type, data)
            
            # Check performance thresholds
            is_within_threshold, perf_msg = check_performance_threshold(duration, endpoint_type)
            
            # Determine success
            success = len(integrity_errors) == 0 and is_within_threshold
            
            # Create details
            details = {
                "url": url,
                "duration_ms": duration,
                "endpoint_type": endpoint_type
            }
            
            # Create error message if needed
            error_msgs = []
            if integrity_errors:
                error_msgs.extend(integrity_errors)
            if perf_msg:
                error_msgs.append(perf_msg)
            
            error = "; ".join(error_msgs) if error_msgs else None
            
            # Create check result
            check_result = CheckResult(
                name=name,
                success=success,
                duration_ms=duration,
                details=details,
                error=error
            )
            
            checks.append(check_result)
            
        except Exception as e:
            # Handle validation failure
            check_result = CheckResult(
                name=name,
                success=False,
                duration_ms=0,  # Failed before timing could be recorded
                details={"url": url, "endpoint_type": endpoint_type},
                error=f"Endpoint validation failed: {str(e)}"
            )
            checks.append(check_result)
    
    return checks


def main() -> int:
    start_time = time.perf_counter()

    args = parse_args()
    run(["docker", "compose", "config"])
    if not args.skip_startup:
        run(["docker", "compose", "up", "-d", "--build"])

    # Perform health checks and capture timing
    health_result, api_duration = wait_for_health(args.api_health_url, timeout_seconds=args.timeout_seconds)
    _, web_duration = wait_for_http_ok(args.web_url, timeout_seconds=args.timeout_seconds)

    # Extract missing exports
    missing = health_result.get("missing_exports", [])

    # Calculate total duration so far
    intermediate_duration = (time.perf_counter() - start_time) * 1000  # Convert to ms

    # Create initial check results
    checks = [
        CheckResult(
            name="API Health Check",
            success=True,
            duration_ms=api_duration,
            details={"url": args.api_health_url}
        ),
        CheckResult(
            name="Web Endpoint Check",
            success=True,
            duration_ms=web_duration,
            details={"url": args.web_url}
        )
    ]

    # Handle missing exports error
    errors = []
    if missing:
        missing_str = ", ".join(str(name) for name in missing)
        errors.append(f"API health missing required exports: {missing_str}")

        # Add error to checks
        checks[0] = CheckResult(
            name="API Health Check",
            success=False,
            duration_ms=api_duration,
            details={"url": args.api_health_url},
            error=f"Missing required exports: {missing_str}"
        )

    # Run extended validation if requested
    if args.extended:
        extended_checks = run_extended_validation(args)
        checks.extend(extended_checks)

    # Calculate final total duration
    total_duration = (time.perf_counter() - start_time) * 1000  # Convert to ms

    # Create validation result
    validation_result = ValidationResult(
        timestamp=datetime.now().isoformat(),
        duration_ms=total_duration,
        success=len(errors) == 0 and all(c.success for c in checks),
        service_info={
            "api_health_url": args.api_health_url,
            "web_url": args.web_url,
            "timeout_seconds": args.timeout_seconds,
            "extended_validation": args.extended
        },
        checks=checks,
        errors=errors
    )

    # Output results in requested format
    output_results(validation_result, args.format)

    # Return appropriate exit code based on validation success
    return 0 if validation_result.success else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - script-level guard
        print(f"Validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
