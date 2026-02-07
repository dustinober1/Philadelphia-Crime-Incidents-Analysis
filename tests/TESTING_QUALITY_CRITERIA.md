# Testing Quality Criteria

**Purpose:** Ensure tests validate behavior, not just execute code.

## Core Principles

### 1. Behavior-Focused Testing

Tests should validate WHAT the code does, not HOW it does it.

**Good (behavior-focused):**
```python
def test_filter_by_district_returns_only_matching_rows(sample_crime_df):
    result = filter_by_district(sample_crime_df, district=5)
    assert result["dc_dist"].eq(5).all(), "All returned rows should be from district 5"
    assert len(result) <= len(sample_crime_df), "Result should not exceed input size"
```

**Bad (implementation-focused):**
```python
def test_filter_by_district_uses_dataframe_masking(sample_crime_df):
    # Tests implementation detail (masking) not behavior
    result = filter_by_district(sample_crime_df, district=5)
    assert hasattr(result, "loc"), "Result should be a DataFrame"
```

### 2. Meaningful Assertions Required

Every test must have at least one meaningful assertion.

**Good:**
```python
def test_date_column_conversion(sample_crime_df):
    result = convert_to_datetime(sample_crime_df, "dispatch_date")
    assert pd.api.types.is_datetime64_any_dtype(result["dispatch_date"])
    assert result["dispatch_date"].notna().sum() == len(sample_crime_df)
```

**Bad (no assertion):**
```python
def test_date_column_conversion(sample_crime_df):
    result = convert_to_datetime(sample_crime_df, "dispatch_date")
    # Just calls the function, no validation!
```

**Bad (trivial assertion):**
```python
def test_date_column_conversion(sample_crime_df):
    result = convert_to_datetime(sample_crime_df, "dispatch_date")
    assert result is not None  # Always passes, meaningless
    assert True  # Worse: no connection to actual code
```

### 3. Test Both Success and Failure Paths

Functions should be tested for both expected behavior and error cases.

```python
def test_filter_by_invalid_district_raises_error(sample_crime_df):
    with pytest.raises(ValueError, match="District must be 1-23"):
        filter_by_district(sample_crime_df, district=99)
```

### 4. Use Specific, Descriptive Assertions

Prefer specific assertions over generic ones.

**Good:**
```python
assert len(result) == 100, f"Expected 100 rows, got {len(result)}"
assert "ucr_general" in result.columns, "UCR code column missing from result"
```

**Avoid:**
```python
assert result  # Vague: what about result is being tested?
assert len(result) > 0  # Weak: doesn't verify actual expected value
```

### 5. Test Edge Cases and Boundary Conditions

Include tests for empty inputs, single values, and boundary values.

```python
def test_filter_empty_dataframe():
    empty_df = pd.DataFrame({"dc_dist": []})
    result = filter_by_district(empty_df, district=5)
    assert len(result) == 0, "Filtering empty DataFrame should return empty result"

def test_filter_single_row():
    single_row = pd.DataFrame({"dc_dist": [5]})
    result = filter_by_district(single_row, district=5)
    assert len(result) == 1, "Single matching row should be returned"
```

## Assertion Smells to Avoid

| Smell | Why It's Bad | Fix |
|-------|--------------|-----|
| No assertions | Test doesn't validate anything | Add assertions checking expected behavior |
| `assert True` or `assert False` | Never fails or always fails | Remove or make meaningful |
| `assert variable` (just existence) | Too weak, doesn't check value | Check specific value or property |
| Only calls function | Coverage gaming, no validation | Assert on return value |
| Testing implementation | Breaks on refactoring | Test behavior instead |
| Hardcoded expected values without rationale | Brittle, unclear | Explain why in assertion message |

## Test Quality Checklist

Before committing a test, verify:
- [ ] At least one meaningful assertion
- [ ] Assertion checks expected behavior (not just execution)
- [ ] Test has descriptive name (test_what_happens_when_input)
- [ ] Edge cases are covered (empty, None, boundaries)
- [ ] Error paths are tested (if applicable)
- [ ] Assertion messages explain failures (use `assert condition, "message"`)

## Fixing Common Issues

### Issue: "I just want to verify it doesn't crash"

**Fix:** Test the actual output, not just absence of crash.

```python
# Before:
def test_something():
    risky_function()  # Hope it doesn't crash

# After:
def test_something_returns_expected():
    result = risky_function()
    assert result is not None
    assert isinstance(result, ExpectedType)
```

### Issue: "The function is too complex to test thoroughly"

**Fix:** Simplify function or break into smaller, testable parts.

- Complex functions are a code smell, consider refactoring
- If truly complex, focus on input/output contract

### Issue: "Testing internal state is hard"

**Fix:** Test public behavior, not private state.

- Tests should go through public APIs
- If you need to test internals, the API might be wrong

## Coverage Gaming Examples

These achieve 100% coverage but provide ZERO value:

```python
# DON'T DO THIS - Coverage Gaming
def test_function_executes():
    my_function(param1, param2)  # Coverage: 100%, Value: 0%
    # No assertions!

# DO THIS - Real Testing
def test_function_returns_expected():
    result = my_function(param1, param2)
    assert result["expected_key"] == expected_value
    assert result["status"] == "success"
```

**Remember:** Coverage measures EXECUTION, not CORRECTNESS.
