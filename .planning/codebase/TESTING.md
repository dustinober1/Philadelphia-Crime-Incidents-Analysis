# Testing Patterns

**Analysis Date:** 2026-01-27

## Test Framework

**Runner:**
- pytest [Standard Python testing framework]
- Config: Not detected (would typically be pytest.ini, pyproject.toml, or setup.cfg)

**Assertion Library:**
- Built-in pytest assertions
- Possibly pytest-check for data comparisons

**Run Commands:**
```bash
pytest                           # Run all tests
pytest -v                        # Verbose output
pytest --cov                     # With coverage report
pytest tests/                    # Run tests in specific directory
pytest tests/test_analysis.py    # Run specific test file
```

## Test File Organization

**Location:**
- Pattern: Separate test directory (`tests/`) or co-located with source

**Naming:**
- `test_*.py` or `*_test.py` pattern
- Mirror source file naming conventions

**Structure:**
```
tests/
├── conftest.py                  # Test configuration/fixtures
├── test_data_processing.py      # Data processing tests
├── test_visualization.py        # Visualization tests
├── test_models.py               # Model/testing related tests
└── resources/                   # Test data/resources
```

## Test Structure

**Suite Organization:**
```python
import pytest
import pandas as pd
from src.analysis_module import process_crime_data

def test_process_crime_data_basic():
    """Test basic crime data processing functionality."""
    sample_data = pd.DataFrame({
        'incident_id': [1, 2, 3],
        'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'location': ['A', 'B', 'C']
    })
    
    result = process_crime_data(sample_data)
    
    assert len(result) == 3
    assert 'processed_column' in result.columns
```

**Patterns:**
- Setup fixtures in conftest.py for common test data
- Parametrized tests for multiple scenarios
- Clear arrange-act-assert structure

## Mocking

**Framework:** pytest-mock (likely)

**Patterns:**
```python
def test_file_loading_with_mock(mocker):
    mock_read_parquet = mocker.patch('pandas.read_parquet')
    mock_read_parquet.return_value = pd.DataFrame({'col': [1, 2, 3]})
    
    result = load_crime_data('dummy_path')
    
    assert len(result) == 3
    mock_read_parquet.assert_called_once()
```

**What to Mock:**
- File I/O operations (reading/writing data files)
- Network requests (API calls, geocoding services)
- External dependencies (database connections)

**What NOT to Mock:**
- Core business logic functions
- Pure data transformations
- Mathematical calculations

## Fixtures and Factories

**Test Data:**
```python
@pytest.fixture
def sample_crime_data():
    return pd.DataFrame({
        'incident_id': [1, 2, 3],
        'date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']),
        'latitude': [39.9526, 39.9547, 39.9551],
        'longitude': [-75.1652, -75.1729, -75.1800],
        'category': ['theft', 'assault', 'vandalism']
    })

@pytest.fixture
def sample_geo_dataframe():
    gdf = gpd.GeoDataFrame(
        {
            'incident_type': ['theft', 'assault'],
            'geometry': [Point(-75.1652, 39.9526), Point(-75.1729, 39.9547)]
        },
        crs='EPSG:4326'
    )
    return gdf
```

**Location:**
- tests/conftest.py for shared fixtures
- Individual test files for specific fixtures

## Coverage

**Requirements:** Not specified (typically 80%+ for data science projects)

**View Coverage:**
```bash
pytest --cov=src --cov-report=html --cov-report=term
```

## Test Types

**Unit Tests:**
- Individual function testing (data cleaning, transformation, calculation functions)
- Test pure functions with known inputs and outputs
- Fast execution, high coverage

**Integration Tests:**
- Multiple component interactions (data pipeline validation)
- End-to-end workflow testing
- Database or file system integration verification

**Data Quality Tests:**
- Schema validation
- Data type consistency
- Range/value boundary checks
- Missing value handling verification

## Common Patterns

**Data Frame Testing:**
```python
def test_dataframe_shape(dataframe):
    assert dataframe.shape[0] > 0  # Non-empty
    assert dataframe.shape[1] == expected_columns  # Correct width

def test_required_columns_present(dataframe):
    required_cols = ['incident_id', 'date', 'location']
    assert all(col in dataframe.columns for col in required_cols)
```

**Async Testing:**
- Not typically applicable for data science projects

**Error Testing:**
```python
def test_invalid_input_handling():
    with pytest.raises(ValueError):
        process_invalid_data(invalid_input)
```

## Data Science Specific Testing

**Model Validation:**
- Test prediction consistency
- Validate model performance metrics
- Check for data leakage prevention

**Visualization Testing:**
- Verify plot generation without errors
- Test plot properties (axis labels, titles)
- Compare generated plots to baselines (optional)

**Geospatial Testing:**
- Coordinate system validation
- Distance calculation accuracy
- Spatial join correctness

---

*Testing analysis: 2026-01-27*