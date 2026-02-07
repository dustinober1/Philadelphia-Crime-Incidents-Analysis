# Phase 7: Machine-Readable Output for Automation - Research

## Standard Stack

For machine-readable output in Python applications, use the following standard libraries and approaches:

- **JSON formatting**: Built-in `json` module with `json.dumps()` for structured output
- **YAML formatting**: `PyYAML` library (already in requirements) with `yaml.dump()` for YAML output
- **Timing measurements**: `time.time()` or `time.perf_counter()` for accurate timing information
- **Structured logging**: `python-json-logger` (already in requirements) for consistent log formatting
- **CLI argument parsing**: `argparse` module with `--format` and `--output` options for specifying output format
- **Exit code handling**: Standard `sys.exit()` with appropriate return codes (0=success, non-zero=failure)

## Architecture Patterns

The established architecture pattern for this phase should follow:

- **Dual output capability**: Scripts maintain human-readable output by default while adding machine-readable output as an option
- **Validation result objects**: Create structured data classes/dictionaries that contain validation results, timing info, and metadata
- **Format-agnostic core logic**: Separate validation logic from output formatting to support multiple formats (JSON/YAML)
- **Health check integration**: Extend existing health check mechanisms to return structured data
- **Backward compatibility**: Preserve existing CLI interface while adding new flags for machine-readable output
- **Performance timing wrapper**: Implement a decorator or context manager to measure execution time of validation functions

## Don't Hand-Roll

For this phase, do NOT implement custom solutions for:

- **JSON/YAML serialization**: Use built-in `json` module and `PyYAML` library instead of creating custom serializers
- **Time measurement utilities**: Use `time.time()` or `time.perf_counter()` instead of implementing custom timing logic
- **CLI argument parsing**: Use `argparse` module instead of manual argument parsing
- **Structured data validation**: Use `pydantic` models (already in requirements) for validating output structure
- **Exit code logic**: Follow standard Unix conventions (0=success, 1=general error, specific codes for different error types)
- **Configuration parsing**: Use existing environment variable and configuration handling patterns

## Common Pitfalls

When implementing machine-readable output, avoid these common mistakes:

- **Inconsistent data structures**: Ensure JSON/YAML output has consistent field names and types across all validation scenarios
- **Missing error details**: Include sufficient error information in machine-readable output for debugging automation failures
- **Timing precision issues**: Use appropriate time measurement functions (`perf_counter` for intervals) to avoid precision loss
- **Encoding problems**: Ensure Unicode characters in error messages are properly handled in JSON output
- **Schema drift**: Maintain consistent output schema even as validation logic evolves
- **Mixed output formats**: Don't mix human-readable and machine-readable output in the same stream when producing machine-readable output
- **Incorrect exit codes**: Ensure exit codes accurately reflect validation outcomes, not just script execution success/failure
- **Performance overhead**: Minimize additional processing when generating timing information to avoid skewing measurements

## Code Examples

### Basic Structure for Validation Result Class
```python
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ValidationResult(BaseModel):
    timestamp: str
    duration_ms: float
    success: bool
    service: str
    checks: List[Dict[str, Any]]
    errors: List[str]
    metadata: Dict[str, Any] = {}
```

### Timing Decorator Example
```python
import time
from functools import wraps

def timed_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            duration = (time.perf_counter() - start_time) * 1000  # Convert to ms
            return result, duration
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            raise e
    return wrapper
```

### CLI Format Option Example
```python
parser.add_argument(
    "--format",
    choices=["human", "json", "yaml"],
    default="human",
    help="Output format for validation results"
)
```

### Machine-Readable Output Function
```python
def output_results(results: ValidationResult, format_type: str = "human"):
    if format_type == "json":
        print(results.model_dump_json(indent=2))
    elif format_type == "yaml":
        import yaml
        print(yaml.dump(results.model_dump(), default_flow_style=False))
    else:  # human
        # existing human-readable output
        print_human_readable(results)
```

### Proper Exit Code Handling
```python
def main():
    try:
        results = run_validation()
        output_format = get_output_format()
        output_results(results, output_format)
        
        # Return appropriate exit code based on validation success
        return 0 if results.success else 1
    except Exception as e:
        # Log error appropriately
        if is_machine_readable_format():
            error_result = {"error": str(e), "success": False}
            print(json.dumps(error_result))
        else:
            print(f"Validation failed: {e}")
        return 1
```