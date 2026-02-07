---
phase: 12-api-&-cli-testing
plan: 02
subsystem: api
tags: [fastapi, testclient, geojson, spatial, integration-tests]

# Dependency graph
requires:
  - phase: 11-core-module-testing
    provides: test infrastructure with pytest and TestClient patterns
provides:
  - Comprehensive integration tests for all 4 spatial GeoJSON endpoints
  - GeoJSON structure validation tests per RFC 7946 spec
  - Error handling tests for missing and empty GeoJSON data
affects: [12-api-&-cli-testing]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Parametrized GeoJSON structure validation with pytest.mark.parametrize
    - Coordinate bounds checking for geographic data validation
    - Monkeypatch-based error simulation for missing data scenarios

key-files:
  created: []
  modified:
    - tests/test_api_endpoints.py - Added 12 spatial endpoint tests

key-decisions:
  - "GeoJSON validation: Use actual data structure from files, not assumed schemas"
  - "District numbers: Validate positive integers, not fixed range (1-24) due to real data having values like 25, 26, 35, 39, 77"
  - "Error handling: Test actual KeyError behavior, not assumed 500 response (FastAPI TestClient propagates unhandled exceptions)"

patterns-established:
  - "Parametrized endpoint testing: Test multiple endpoints with same structure validation logic"
  - "Bounds checking: Validate geographic coordinates are within expected Philadelphia region"
  - "Error simulation: Use monkeypatch to clear cache for missing data tests"

# Metrics
duration: 6min
completed: 2026-02-07
---

# Phase 12: Spatial API Endpoints Summary

**Comprehensive integration tests for all 4 spatial GeoJSON endpoints with 100% coverage, validating RFC 7946 structure, geometry types, and error handling**

## Performance

- **Duration:** 6 minutes
- **Started:** 2026-02-07T17:19:09Z
- **Completed:** 2026-02-07T17:25:00Z
- **Tasks:** 3
- **Files modified:** 1

## Accomplishments

- All 4 spatial endpoints (districts, tracts, hotspots, corridors) have comprehensive integration tests
- GeoJSON FeatureCollection structure validated per RFC 7946 specification
- Geometry types validated (Point, Polygon, MultiPolygon, LineString, MultiLineString)
- Error handling tested for missing and empty GeoJSON data
- Achieved 100% test coverage for api/routers/spatial.py

## Task Commits

Each task was committed atomically:

1. **Task 1: Add tests for all 4 spatial GeoJSON endpoints** - `427b875` (feat)
2. **Task 2: Add spatial endpoint GeoJSON structure validation** - (included in auto-commit from linter)
3. **Task 3: Add spatial endpoint error handling tests** - `d2a66a5` (test)

**Plan metadata:** To be committed with STATE.md update

## Files Created/Modified

- `tests/test_api_endpoints.py` - Extended from 108 to 931 lines with 12 new spatial endpoint tests
  - 4 endpoint-specific tests (districts, tracts, hotspots, corridors)
  - 1 parametrized structure validation test (tests all 4 endpoints)
  - 2 property-specific tests (districts properties, hotspots centroids)
  - 2 error handling tests (missing data, empty features)

## Test Coverage

### Spatial Endpoint Coverage (100%)

- **api/routers/spatial.py:** 100% coverage (17/17 statements)
  - `test_spatial_districts` - Validates /api/v1/spatial/districts endpoint
  - `test_spatial_tracts` - Validates /api/v1/spatial/tracts endpoint
  - `test_spatial_hotspots` - Validates /api/v1/spatial/hotspots endpoint
  - `test_spatial_corridors` - Validates /api/v1/spatial/corridors endpoint

### GeoJSON Structure Validation

- **test_spatial_geojson_structure** (parametrized) - Validates all endpoints return valid FeatureCollection with:
  - `type == "FeatureCollection"`
  - `features` is a list
  - Each feature has `type == "Feature"`
  - Each feature has `geometry` with `type` and `coordinates`
  - Each feature has `properties` dict

### Property-Specific Validation

- **test_spatial_districts_properties** - Validates:
  - All features have `dist_num` property
  - District numbers are positive integers (actual data has values 1-77)
  - District numbers stored as strings in GeoJSON

- **test_spatial_hotspots_centroids** - Validates:
  - All features have Point geometry
  - Coordinates within Philadelphia bounds (-75.3 to -74.95 longitude, 39.85 to 40.15 latitude)
  - Properties include `cluster` and `incident_count`
  - `incident_count` is non-negative integer

### Error Handling

- **test_spatial_endpoint_missing_geojson** - Validates KeyError raised when GeoJSON data missing from cache
  - Simulates missing data by clearing `_DATA_CACHE`
  - Verifies KeyError is raised with appropriate message
  - Tests unhandled exception behavior (FastAPI TestClient propagates KeyError)

- **test_spatial_empty_features** - Validates empty FeatureCollection returns 200
  - Mocks empty FeatureCollection in cache
  - Verifies endpoint returns 200 with empty features list
  - Tests empty state edge case

## Decisions Made

### GeoJSON Structure Validation

- **Decision:** Validate actual GeoJSON structure from real data files, not assumed schemas
- **Rationale:** Discovered district numbers include values beyond 1-23 (actual data has 25, 26, 35, 39, 77). Tests must validate real data, not assumptions.
- **Impact:** Tests adapted to validate positive integers instead of fixed range, making them more robust to data changes.

### Error Handling Behavior

- **Decision:** Test actual KeyError behavior instead of assuming 500 HTTP response
- **Rationale:** FastAPI TestClient propagates unhandled exceptions. The spatial endpoints don't catch KeyError, so TestClient raises it rather than returning HTTP 500.
- **Impact:** Tests use `pytest.raises(KeyError)` to document current behavior. This identifies a potential improvement opportunity (adding exception handlers in spatial.py).

### Hotspot Property Names

- **Decision:** Validate `incident_count` property instead of `intensity`
- **Rationale:** Real hotspot GeoJSON uses `incident_count`, not `intensity` as assumed in plan.
- **Impact:** Tests validate correct property names, ensuring they match actual data structure.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed district number range validation**
- **Found during:** Task 2 (test_spatial_districts_properties)
- **Issue:** Plan assumed district numbers 1-23, but actual data includes 24, 25, 26, 35, 39, 77
- **Fix:** Changed validation from `assert 1 <= dist_num <= 23` to `assert dist_num > 0`
- **Files modified:** tests/test_api_endpoints.py
- **Verification:** All 21 district features pass validation
- **Committed in:** Included in Task 2 auto-commit

**2. [Rule 1 - Bug] Fixed hotspot property name**
- **Found during:** Task 2 (test_spatial_hotspots_centroids)
- **Issue:** Plan assumed `intensity` property, but actual data uses `incident_count`
- **Fix:** Updated test to validate `incident_count` and `cluster` properties
- **Files modified:** tests/test_api_endpoints.py
- **Verification:** All hotspot features have expected properties
- **Committed in:** Included in Task 2 auto-commit

**3. [Rule 1 - Bug] Fixed error handling test expectation**
- **Found during:** Task 3 (test_spatial_endpoint_missing_geojson)
- **Issue:** Plan expected 500 HTTP response, but FastAPI TestClient propagates unhandled KeyError
- **Fix:** Changed test to use `pytest.raises(KeyError)` instead of `assert response.status_code == 500`
- **Files modified:** tests/test_api_endpoints.py
- **Verification:** Test correctly catches KeyError when data missing from cache
- **Committed in:** d2a66a5

---

**Total deviations:** 3 auto-fixed (all Rule 1 - bugs)
**Impact on plan:** All auto-fixes corrected assumptions about data structure and error handling behavior. Tests now validate actual rather than assumed behavior. No scope creep.

## Issues Encountered

### File Modification Conflicts

- **Issue:** File was modified by linter/formatter between read and write operations, causing Edit tool to fail
- **Resolution:** Used sed commands for simple replacements, re-read file before edits
- **Impact:** Minor delays, no functional impact

### Git Stash Conflicts

- **Issue:** Uncommitted test changes from plan 12-01 were stashed and later applied
- **Resolution:** Changes were auto-committed, verified tests still pass
- **Impact:** No conflicts, tests continue to pass

## Verification Results

### Test Execution Summary

```bash
$ pytest tests/test_api_endpoints.py -v -k "spatial"
# 12 passed in 0.69s
```

**Tests added:** 12 new tests for spatial endpoints
- 4 endpoint-specific happy path tests
- 4 parametrized structure validation tests (one per endpoint)
- 2 property-specific validation tests
- 2 error handling tests

**Test coverage:** 100% for api/routers/spatial.py

### Coverage Report

```
Name                     Stmts   Miss Branch BrPart    Cover   Missing
----------------------------------------------------------------------
api/routers/spatial.py      17      0      0      0  100.00%
----------------------------------------------------------------------
```

All 4 spatial endpoints fully covered:
- `/api/v1/spatial/districts`
- `/api/v1/spatial/tracts`
- `/api/v1/spatial/hotspots`
- `/api/v1/spatial/corridors`

## GeoJSON Structure Validation Results

All endpoints return valid GeoJSON FeatureCollection per RFC 7946:

1. **Top-level structure:** ✅ `type: "FeatureCollection"`, `features: [...]`
2. **Feature structure:** ✅ `type: "Feature"`, `geometry: {...}`, `properties: {...}`
3. **Geometry structure:** ✅ `type: [Point|Polygon|MultiPolygon|LineString|MultiLineString]`, `coordinates: [...]`
4. **Properties validation:**
   - Districts: ✅ `dist_num` (string, positive integer value)
   - Hotspots: ✅ `cluster`, `incident_count` (non-negative int), coordinates within Philly bounds
   - Tracts: ✅ Polygon/MultiPolygon geometry
   - Corridors: ✅ LineString/MultiLineString geometry

## Next Phase Readiness

### Complete

- All spatial endpoints have comprehensive test coverage
- GeoJSON structure validation patterns established for reuse
- Error handling tests document current behavior (KeyError propagation)

### Improvement Opportunities

- Consider adding exception handlers in spatial.py to catch KeyError and return HTTP 500
- Consider adding response status endpoint tests (beyond just structure validation)
- Consider adding performance tests for large GeoJSON payloads

### Ready for Next Plan

Phase 12 Plan 03 (Policy Endpoint Tests) can proceed with:
- Established TestClient patterns
- GeoJSON validation patterns
- Error testing patterns using monkeypatch

---
*Phase: 12-api-&-cli-testing*
*Completed: 2026-02-07*
