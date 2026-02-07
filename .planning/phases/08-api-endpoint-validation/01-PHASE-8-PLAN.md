# Phase 8: Additional API Endpoint Validation - Plan

## Objective

Enhance validation beyond basic health checks to verify critical functionality of high-value API endpoints, including crime dataset validation, response time thresholds, and data integrity checks for recently processed datasets.

## Execution Context

@~/.qwen/get-shit-done/references/plan-format.md
@~/.qwen/get-shit-done/references/scope-estimation.md
@~/.qwen/get-shit-done/references/tdd.md

## Context

### Phase Description
Phase 8: Additional API Endpoint Validation (LWF-04)
Goal: Enhance validation beyond basic health checks to verify critical functionality.

### Requirements Mapped
- LWF-04-1: Developer can run extended smoke checks that validate specific high-value API endpoints
- LWF-04-2: System outputs structured status reports in JSON/YAML format
- LWF-04-3: API validation includes response time thresholds for performance verification
- LWF-04-4: Extended validation includes data integrity checks for recently processed datasets

### Success Criteria
- Extended smoke checks validate specific high-value API endpoints
- Crime dataset endpoints return expected data structures
- API validation includes response time thresholds for performance verification
- Extended validation includes data integrity checks for recently processed datasets

### Prior Decisions & State
From STATE.md: v1.0 established services containerized with appropriate boundaries, Docker Compose orchestration, resource limits, image size optimization. v1.1 established automated post-start smoke checks, runtime presets, preserved default docker compose up behavior, runtime guardrails. v1.2 phase 7 established machine-readable output with JSON/YAML formats, proper exit codes, and timing information.

Currently, the system has validation scripts in the `/scripts` directory, including `validate_local_stack.py` which performs health checks on the API and web services. The API has multiple endpoints across different routers (trends, spatial, policy, forecasting, questions, metadata).

### Research Insights
- High-value API endpoints include: /api/v1/trends/annual, /api/v1/spatial/districts, /api/v1/policy/retail-theft, /api/v1/forecasting/time-series
- Response time thresholds should be configurable (default 2-5 seconds depending on endpoint complexity)
- Data integrity checks should verify expected data structure and required fields
- Need to extend the existing validation script to include these additional checks
- Should leverage existing Pydantic models from phase 7

## Truths (Must-Haves)

- [ ] Extended smoke checks validate specific high-value API endpoints (LWF-04-1)
- [ ] Crime dataset endpoints return expected data structures (LWF-04-2)
- [ ] API validation includes response time thresholds for performance verification (LWF-04-3)
- [ ] Extended validation includes data integrity checks for recently processed datasets (LWF-04-4)
- [ ] New validation functionality integrates with existing validation script
- [ ] Performance thresholds are configurable and customizable
- [ ] Validation results maintain consistent structure with existing models
- [ ] Backward compatibility is preserved for existing functionality

## Artifacts

- [ ] Enhanced validation script with additional API endpoint checks
- [ ] Configuration for performance thresholds
- [ ] Data integrity validation functions
- [ ] Updated documentation for new validation features
- [ ] Test cases for new validation functionality

## Key Links

- [.planning/ROADMAP.md](.planning/ROADMAP.md) - Phase definition and requirements
- [.planning/REQUIREMENTS.md](.planning/REQUIREMENTS.md) - Detailed requirements
- [.planning/STATE.md](.planning/STATE.md) - Project state
- [scripts/validate_local_stack.py](scripts/validate_local_stack.py) - Main validation script
- [scripts/validation_models.py](scripts/validation_models.py) - Validation models from phase 7

## Tasks

### Task 1: Identify High-Value API Endpoints
Identify and document the most critical API endpoints that should be validated beyond basic health checks.

**Actions:**
1. Enumerate all available API endpoints from router files
2. Categorize endpoints by importance and usage frequency
3. Select 5-8 high-value endpoints for validation
4. Document expected response structure for each endpoint
5. Determine appropriate timeout values for each endpoint type

### Task 2: Create Data Integrity Validation Functions
Develop functions to validate the structure and content of API responses.

**Actions:**
1. Create validation functions for different data types (trends, spatial, policy, etc.)
2. Define expected data structure for each endpoint
3. Implement checks for required fields and data types
4. Create helper functions to validate JSON response structure
5. Add error reporting for data integrity failures

### Task 3: Implement Performance Threshold Checks
Add response time validation with configurable thresholds.

**Actions:**
1. Extend the timed_execution decorator to support threshold checking
2. Create configuration for performance thresholds per endpoint
3. Implement warning/error logic based on response times
4. Add performance metrics to validation results
5. Ensure timing measurements are accurate and reliable

### Task 4: Extend Validation Script with New Checks
Integrate the new validation functionality into the existing script.

**Actions:**
1. Add new command-line arguments for extended validation options
2. Create functions to validate each selected high-value endpoint
3. Integrate performance and data integrity checks
4. Update the main validation flow to include new checks
5. Ensure all new checks follow the same pattern as existing ones

### Task 5: Update Validation Models
Extend Pydantic models to accommodate new validation types.

**Actions:**
1. Add new fields to ValidationResult model for extended validation
2. Create additional CheckResult types for API-specific validations
3. Update models to include performance metrics
4. Ensure backward compatibility with existing functionality
5. Add validation for new model fields

### Task 6: Test Extended Validation Functionality
Thoroughly test the new validation features.

**Actions:**
1. Run extended validation with actual API endpoints
2. Verify that performance thresholds work correctly
3. Test data integrity checks with valid and invalid data
4. Confirm that all validation results are properly reported
5. Ensure exit codes are correct for different failure scenarios

### Task 7: Update Documentation
Document the new validation features for users.

**Actions:**
1. Update README with information about extended validation
2. Document new command-line options
3. Provide examples of extended validation usage
4. Explain performance threshold configuration
5. Describe the new validation results format

## Verification

### Verification Steps
1. Execute validation script with extended API checks and verify all endpoints are tested
2. Verify that data integrity checks properly validate response structures
3. Execute validation with performance threshold violations and verify warnings/errors
4. Confirm that new validation results are properly formatted in JSON/YAML
5. Verify that exit codes accurately reflect validation outcomes with extended checks
6. Test that backward compatibility is maintained for existing functionality
7. Confirm that timing information is accurate for all validation types

### Acceptance Criteria
- [ ] All high-value API endpoints are validated during extended checks
- [ ] Data integrity checks verify expected response structures
- [ ] Performance thresholds are enforced and reported correctly
- [ ] Data integrity checks identify malformed responses
- [ ] Extended validation results follow consistent structure
- [ ] Backward compatibility is maintained for existing functionality
- [ ] Documentation includes information about new features

## Success Criteria

Phase 8 will be complete when:
1. Extended smoke checks validate specific high-value API endpoints (LWF-04-1)
2. Crime dataset endpoints return expected data structures (LWF-04-2)
3. API validation includes response time thresholds for performance verification (LWF-04-3)
4. Extended validation includes data integrity checks for recently processed datasets (LWF-04-4)
5. All verification steps pass successfully
6. Documentation is updated to reflect new functionality

## Output

- Enhanced validation script with additional API endpoint validation
- Performance threshold validation with configurable limits
- Data integrity checks for API responses
- Updated documentation with usage examples
- Verified functionality that meets all LWF-04 requirements

---
*Plan created: February 7, 2026*
*Phase: 8 - Additional API Endpoint Validation*