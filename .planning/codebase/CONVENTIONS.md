# Coding Conventions

**Analysis Date:** 2026-02-07

## Naming Patterns

**Files:**
- Python modules use `snake_case.py` (`analysis/data/preprocessing.py`, `api/services/data_loader.py`).
- Test files use `test_*.py` under `tests/`.
- React components use `PascalCase.tsx` (`web/src/components/ChartCard.tsx`).
- Next.js route files use `page.tsx`, `layout.tsx`, `loading.tsx` under lowercase route directories.

**Functions:**
- Python functions use `snake_case` (`load_crime_data`, `extract_temporal_features`).
- Frontend hooks/functions use `camelCase` (`useAnnualTrends`, `onSubmit`, `adminFetcher`).
- CLI command handlers map to Typer command functions in each domain module.

**Variables:**
- Python variables use `snake_case`.
- Constants use `UPPER_SNAKE_CASE` (`PHILLY_LON_MIN`, `_RATE_LIMIT_MAX`).
- TypeScript variables use `camelCase`; component props interfaces/types use `PascalCase`.

**Types:**
- Python: Pydantic models and config classes use `PascalCase` (`GlobalConfig`, `QuestionSubmission`).
- TypeScript: interfaces/types use `PascalCase` (`TrendRow`, `ForecastResponse`).

## Code Style

**Formatting:**
- Python formatting enforced by Black with `line-length = 100` (`pyproject.toml`).
- TypeScript/TSX formatting follows Next.js/ESLint defaults; explicit Prettier config is not detected.
- Python code is heavily documented with module and function docstrings.

**Linting:**
- Python linting via Ruff (`pyproject.toml`) with isort-like import ordering and selected rule families.
- Static typing via mypy with strict flags and targeted overrides (`pyproject.toml`).
- Frontend linting via Next.js ESLint config (`web/eslint.config.mjs`).

## Import Organization

**Order:**
1. Standard library imports.
2. Third-party package imports.
3. Local application imports (`analysis.*`, `api.*`, relative modules).

**Grouping:**
- Python modules generally use grouped imports with blank lines between categories.
- TypeScript modules tend to import framework/libs first, then project aliases.

**Path Aliases:**
- Frontend alias `@/*` maps to `web/src/*` (`web/tsconfig.json`).
- Python uses package imports rooted at `analysis` and `api`.

## Error Handling

**Patterns:**
- Python utilities raise explicit exceptions for invalid input and missing files (`ValueError`, `FileNotFoundError`, `ImportError`).
- API routes raise `HTTPException` for client-visible errors and rely on global exception handlers for consistent JSON payloads (`api/main.py`).
- Optional dependency paths often degrade gracefully with `try/except ImportError` in analysis commands.

**Error Types:**
- Input/schema boundary uses Pydantic and FastAPI validation.
- Runtime data checks are typically explicit precondition checks (`if column not in df.columns: raise ValueError(...)`).
- API response errors are normalized to `{"error": ..., "message": ...}` format.

## Logging

**Framework:**
- API uses Python `logging` with request middleware timing and request IDs (`api/main.py`).
- CLI command output uses Rich console messaging/progress bars instead of logger abstraction.

**Patterns:**
- API logs request metadata (`method`, `path`, `status`, `elapsed_ms`).
- Exceptions are logged with `logger.exception` in top-level API middleware/handlers.
- Analysis modules emphasize human-readable console output and generated summary files.

## Comments

**When to Comment:**
- Module-level docstrings explain purpose and usage for most Python modules.
- Inline comments usually explain boundary conditions, optional dependency handling, or algorithm steps.
- Comments generally focus on operational intent (for example, sample mode behavior, coordinate bounds).

**JSDoc/TSDoc:**
- Python docstrings are prevalent and detailed.
- TypeScript component files generally rely on types and readable naming rather than heavy docblocks.

**TODO Comments:**
- TODO markers are present and reference migration cleanup (`analysis/utils/__init__.py`, `analysis/__init__.py`).

## Function Design

**Size:**
- CLI command handlers are often long and orchestrate full workflows within single functions (`analysis/cli/*.py`).
- Utility functions in `analysis/data/` and `analysis/utils/` are more focused and reusable.

**Parameters:**
- Typer command parameters are typed and user-facing.
- Internal helpers favor explicit parameters with sensible defaults.

**Return Values:**
- Data transforms return new DataFrames rather than mutating caller state in-place where practical.
- API handlers return plain dict/list payloads compatible with FastAPI serialization.

## Module Design

**Exports:**
- Python packages frequently declare `__all__` for explicit exports (`analysis/data/preprocessing.py`, `analysis/cli/__init__.py`).
- Frontend uses named exports for reusable components/hooks and default exports for route pages.

**Barrel Files:**
- Python package `__init__.py` files act as light aggregation layers.
- Frontend does not rely on centralized barrel files; imports are mostly direct by path.

---

*Convention analysis: 2026-02-07*
*Update when patterns change*
