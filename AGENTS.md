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

## AI Agent Guidance (for Copilot / automated agents)
- Purpose: help agents be productive and safe—run setup, follow local style, run tests and open focused PRs.

- Setup & environment (run before making changes):
  - `conda env create -f environment.yml && conda activate crime`
  - `pip install -r requirements-dev.txt`
  - For frontend checks: `cd web && npm install` (if touching `web/`)

- Commands agents SHOULD run automatically when proposing changes:
  - `pytest tests/ --maxfail=1 -q` (prefer `--fast` when available for quicker iteration)
  - `black analysis tests && ruff check analysis tests && mypy .`
  - `make dev-api` to sanity-check API changes locally

- Code style & patterns to follow:
  - Python: 4-space indentation, Black/Ruff line length `100`, add type annotations for new/edited code.
  - Naming: `snake_case` for functions/modules, `PascalCase` for classes, tests named `test_*.py`.
  - Frontend: `PascalCase` component files, `camelCase` hooks and utilities (see `web/src/` for examples).

- Project-specific conventions & examples:
  - CLI code: follow Typer patterns in `analysis/cli/` for argument parsing.
  - Config: prefer `config/*.yaml` with loaders in `analysis/config_loader.py` and `phase*_config_loader.py`.
  - Data flow: pipeline jobs in `pipeline/` populate `api/data/`—avoid changes that break that contract without CI/test coverage.

- Integration & security notes:
  - Never commit secrets or credentials. If a change requires secrets or external access, open an issue and request human approval.
  - Changes affecting `firebase.json`, `firestore.rules`, CI, or deployment should include explicit risk notes in PR description.

- When to ask a human reviewer:
  - Schema changes, forecasts/data-contract changes, deployment or infra changes, or anything that touches external systems or secrets.

- Helpful references:
  - Core areas: `analysis/`, `api/`, `pipeline/`, `web/`, `tests/`, `config/`, `README.md`, `AGENTS.md`

If any of these points are unclear or you'd like different defaults (for example, different lint rules or test flags), tell me what to change and I'll update this section.  
