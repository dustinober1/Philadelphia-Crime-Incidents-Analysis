# Repository Guidelines

## Project Structure & Module Organization
- `analysis/`: core Python analytics package (CLI commands, data loading/validation, models, visualization, config schemas).
- `api/`: FastAPI service exposing exported analysis artifacts in `api/data/`.
- `pipeline/`: data export/refresh jobs that populate API-ready JSON/GeoJSON files.
- `web/`: Next.js frontend (`src/app`, `src/components`, `src/lib`).
- `tests/`: unit, CLI, and integration tests (`tests/integration/`).
- `config/`, `data/`, `reports/`, `docs/`: runtime config, local datasets, generated outputs, and documentation.

## Build, Test, and Development Commands
- `conda env create -f environment.yml && conda activate crime`: create Python environment.
- `pip install -r requirements-dev.txt`: install test/lint/type tooling.
- `pytest tests/`: run full Python test suite.
- `pytest tests/ --cov=analysis --cov-report=term-missing`: run coverage for analysis package.
- `black analysis tests && ruff check analysis tests && mypy .`: format, lint, and type-check Python code.
- `make dev-api` / `make dev-web`: run API (`uvicorn`) or frontend (`next dev`).
- `docker compose up -d --build`: run pipeline + API + web stack locally.
- `cd web && npm run lint && npm run typecheck`: frontend linting and TypeScript checks.

## Coding Style & Naming Conventions
- Python: 4-space indentation, Black/Ruff line length `100`, strict typing for new/edited code.
- Python naming: `snake_case` for functions/modules, `PascalCase` for classes, tests named `test_*.py`.
- TypeScript/React: prefer `PascalCase` component files (example: `StatCard.tsx`), hooks/util APIs in `camelCase`.
- Keep CLI commands and options aligned with existing Typer patterns in `analysis/cli/`.

## Testing Guidelines
- Framework: `pytest` with markers `integration` and `slow`.
- Fast iteration: use CLI `--fast` flag in tests and local validation when possible.
- Add/update tests with each behavior change, especially CLI output artifacts under `reports/test/...`.

## Commit & Pull Request Guidelines
- Follow Conventional Commit style used in history: `feat(scope): ...`, `test(scope): ...`, `docs(scope): ...`.
- Keep commits focused and atomic; include scope tags when useful (example: `feat(02-01): ...`).
- PRs should include: summary, affected paths, test evidence (commands run), and screenshots for `web/` UI changes.
- Link related issue/task and call out config or environment changes (`.env`, compose budgets, data contracts).
