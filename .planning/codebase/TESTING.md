# Testing Strategy and Implementation

## Test Framework

**Pytest** is the primary testing framework with the following configuration:
- Minimum version: 8.0
- Test paths: `tests/` directory
- Auto-detect CPU count for parallel execution
- Strict markers and config
- Coverage reporting for analysis, api, pipeline modules

## Test Organization

Tests are organized in the `tests/` directory with naming convention `test_*.py`:
- `test_cli_*.py`: CLI command tests
- `test_api_*.py`: API endpoint and service tests
- `test_data_*.py`: Data loading and validation tests
- `test_models_*.py`: Model tests
- `test_config_*.py`: Configuration tests
- `test_pipeline_*.py`: Pipeline tests
- `integration/`: Integration tests

## Test Types

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions (marked with `@pytest.mark.integration`)
- **CLI Tests**: Use `CliRunner` for command-line interface testing
- **API Tests**: Test FastAPI endpoints and services

## Test Coverage

- Target modules: analysis, api, pipeline
- Coverage tools: pytest-cov, diff-cover
- Reports: XML, terminal, HTML
- Branch coverage enabled
- Parallel execution support

## Test Fixtures

Shared fixtures in `conftest.py`:
- `sample_crime_df`: 100-row sample DataFrame with representative crime data
- `mock_geo_data`: Mock GeoDataFrame for spatial tests
- `clean_test_dir`: Temporary directory cleanup
- `skip_slow_tests`: Marker for slow tests

## Test Markers

- `slow`: Tests that take >5 seconds or require full datasets
- `integration`: End-to-end integration tests

## CI/CD Integration

- Tests run in CI pipeline
- Coverage reports generated
- Quality gates: linting, formatting, type checking
- Parallel test execution for faster feedback

## Test Data Management

- Sample datasets for fast testing
- Mock data for external dependencies
- Temporary directories for output testing
- Reproducible random seeds (np.random.seed(42))

## Test Quality Metrics

- 90%+ coverage target
- All tests pass
- Fast execution (<5 seconds for unit tests)
- Clear test names and documentation