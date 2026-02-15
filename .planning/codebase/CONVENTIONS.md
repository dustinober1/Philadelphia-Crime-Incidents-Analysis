# Code Quality Conventions

## Coding Style and Formatting

The project uses **Black** for code formatting with the following configuration:
- Line length: 100 characters
- Target Python version: 3.13
- Includes: `.py` and `.pyi` files
- Excludes: build, dist, notebooks, reports, web directories

## Linting and Quality Tools

**Ruff** is used for linting with comprehensive rule selection:
- pycodestyle (E, W)
- pyflakes (F)
- isort (I)
- flake8-bugbear (B)
- flake8-comprehensions (C4)
- pyupgrade (UP)
- flake8-unused-arguments (ARG)
- flake8-simplify (SIM)

Specific ignores:
- E501: Line too long (handled by Black)
- B008: Function calls in argument defaults
- B904: Raise without from inside except
- B905: Zip without strict parameter

Per-file ignores:
- `__init__.py`: F401 (unused imports allowed)
- `tests/*`: ARG (unused arguments allowed)
- Specific files have targeted ignores for legacy code

**MyPy** for type checking:
- Strict configuration with Python 3.13
- Excludes analysis/, reports/, scripts/, web/, most tests/
- Warns on return any, unused configs
- Disallows untyped defs, any generics
- Strict equality checking

## Naming Conventions

- **Variables and functions**: snake_case
- **Classes**: PascalCase
- **Constants**: UPPER_SNAKE_CASE
- **Modules**: snake_case
- **Packages**: snake_case

## Documentation Standards

- Docstrings for all public functions, classes, and modules
- Google-style docstring format
- Type hints using `from __future__ import annotations`
- Comments for complex logic

## Code Organization

- Imports organized by standard library, third-party, local
- Relative imports within packages
- Clear separation of concerns
- Modular design with single responsibility

## Commit Message Conventions

- Conventional commits format
- Clear, descriptive messages
- Reference issue numbers when applicable

## Import Organization

- isort configuration in ruff
- known-first-party: analysis, api, pipeline
- Consistent import ordering