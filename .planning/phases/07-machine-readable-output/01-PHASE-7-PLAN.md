# Phase 7: Machine-Readable Output for Automation - Plan

## Objective

Implement machine-readable output for automation tools by enhancing the existing validation scripts to provide JSON/YAML formatted output, proper exit codes, and timing information for CI/CD integration.

## Execution Context

@~/.qwen/get-shit-done/references/plan-format.md
@~/.qwen/get-shit-done/references/scope-estimation.md
@~/.qwen/get-shit-done/references/tdd.md

## Context

### Phase Description
Phase 7: Machine-Readable Output for Automation (LWF-03)
Goal: Enable seamless integration with CI/CD systems and automation tools.

### Requirements Mapped
- LWF-03-1: Developer can run smoke-check validation with JSON-formatted output for CI parsing
- LWF-03-2: System outputs structured status reports in JSON/YAML format
- LWF-03-3: Validation script provides exit codes that reflect validation outcomes
- LWF-03-4: Machine-readable output includes timing information for performance monitoring

### Success Criteria
- Developer can run smoke-check validation with JSON-formatted output for CI parsing
- System outputs structured status reports in JSON/YAML format
- Validation script provides exit codes that reflect validation outcomes
- Machine-readable output includes timing information for performance monitoring

### Prior Decisions & State
From STATE.md: v1.0 established services containerized with appropriate boundaries, Docker Compose orchestration, resource limits, image size optimization. v1.1 established automated post-start smoke checks, runtime presets, preserved default docker compose up behavior, runtime guardrails.

Currently, the system has validation scripts in the `/scripts` directory, including `validate_local_stack.py` which performs health checks on the API and web services.

### Research Insights
From RESEARCH.md:
- Use Python's built-in `json` module for JSON formatting
- Leverage `PyYAML` library for YAML output
- Implement timing measurements with `time.time()` or `time.perf_counter()`
- Utilize `python-json-logger` for structured logging
- Employ `argparse` for CLI argument parsing with format options
- Use `pydantic` models for data validation

## Truths (Must-Haves)

- [ ] Validation scripts output structured data in JSON format when requested
- [ ] Validation scripts output structured data in YAML format when requested
- [ ] Validation scripts return appropriate exit codes (0 for success, non-zero for failure)
- [ ] Validation output includes timing information for performance monitoring
- [ ] Human-readable output remains the default to preserve backward compatibility
- [ ] Existing functionality continues to work without changes for current users

## Artifacts

- [ ] Updated validation script with machine-readable output options
- [ ] Pydantic models for validation results structure
- [ ] Documentation for new CLI options
- [ ] Updated README with examples of machine-readable usage

## Key Links

- [.planning/ROADMAP.md](.planning/ROADMAP.md) - Phase definition and requirements
- [.planning/RESEARCH.md](.planning/phases/07-machine-readable-output/RESEARCH.md) - Implementation research
- [.planning/CONTEXT.md](.planning/phases/07-machine-readable-output/CONTEXT.md) - Phase context

## Tasks

### Task 1: Create Pydantic Models for Validation Results
Create structured data models for validation results that include all required fields for machine-readable output.

**Actions:**
1. Create a `ValidationResult` Pydantic model with fields for timestamp, duration, success status, service info, checks, errors, and metadata
2. Create supporting models for individual check results and error information
3. Ensure the model supports both success and failure scenarios

### Task 2: Enhance Validation Script with Format Options
Modify the existing validation script to accept format options and output structured data accordingly.

**Actions:**
1. Add `--format` argument to validation script with choices: "human", "json", "yaml"
2. Implement logic to output results in the requested format using the Pydantic models
3. Ensure human-readable output remains the default to maintain backward compatibility
4. Add error handling for format conversion failures

### Task 3: Implement Timing Measurement
Add timing measurement functionality to capture performance data for the validation process.

**Actions:**
1. Implement a timing decorator or context manager to measure validation execution time
2. Add timing information to the validation result model
3. Ensure timing is captured for the entire validation process and potentially for individual checks

### Task 4: Implement Proper Exit Codes
Update the validation script to return appropriate exit codes based on validation outcomes.

**Actions:**
1. Modify the script to return exit code 0 when validation succeeds
2. Return exit code 1 when validation fails
3. Consider additional specific exit codes for different failure types if needed
4. Ensure exit codes are returned consistently regardless of output format

### Task 5: Test Machine-Readable Output
Test the new functionality to ensure it works as expected.

**Actions:**
1. Run validation with JSON format and verify structured output
2. Run validation with YAML format and verify structured output
3. Verify exit codes are correct for both success and failure scenarios
4. Verify timing information is included in output
5. Confirm human-readable output still works as before

### Task 6: Update Documentation
Document the new functionality for users.

**Actions:**
1. Update README with examples of using the new format options
2. Document the structure of the machine-readable output
3. Explain the meaning of exit codes
4. Provide examples for CI/CD integration

## Verification

### Verification Steps
1. Execute validation script with `--format json` and verify JSON output structure
2. Execute validation script with `--format yaml` and verify YAML output structure
3. Execute validation script with successful validation and verify exit code 0
4. Execute validation script with simulated failure and verify non-zero exit code
5. Verify timing information is present in machine-readable output
6. Verify human-readable output remains unchanged when no format specified
7. Confirm existing functionality continues to work without changes

### Acceptance Criteria
- [ ] JSON output follows consistent structure suitable for CI parsing
- [ ] YAML output follows consistent structure suitable for CI parsing
- [ ] Exit codes accurately reflect validation outcomes
- [ ] Timing information is included in machine-readable output
- [ ] Backward compatibility is maintained for human-readable output
- [ ] Documentation is updated with usage examples

## Success Criteria

Phase 7 will be complete when:
1. All validation scripts support JSON-formatted output for CI parsing (LWF-03-1)
2. System outputs structured status reports in JSON/YAML format (LWF-03-2)
3. Validation script provides exit codes that reflect validation outcomes (LWF-03-3)
4. Machine-readable output includes timing information for performance monitoring (LWF-03-4)
5. All verification steps pass successfully
6. Documentation is updated to reflect new functionality

## Output

- Enhanced validation script with machine-readable output capabilities
- Structured data models for validation results
- Updated documentation with usage examples
- Verified functionality that meets all LWF-03 requirements

---
*Plan created: February 7, 2026*
*Phase: 7 - Machine-Readable Output for Automation*