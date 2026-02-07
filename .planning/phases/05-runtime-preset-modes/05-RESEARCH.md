# Phase 05 Research: Runtime Preset Modes

## Objective
Research implementation approaches for adding low-power and high-performance runtime modes while keeping default compose startup unchanged.

## Current Baseline (Observed)
- `docker-compose.yml` already enforces resource limits via env-substitution defaults:
  - `pipeline`: `${PIPELINE_CPU_LIMIT:-1.00}`, `${PIPELINE_MEM_LIMIT:-1536m}`
  - `api`: `${API_CPU_LIMIT:-1.00}`, `${API_MEM_LIMIT:-1024m}`
  - `web`: `${WEB_CPU_LIMIT:-1.00}`, `${WEB_MEM_LIMIT:-1024m}`
- `.env.example` defines these same baseline values.
- Existing validation scripts assert presence of limits and profile behavior (`refresh`), but no mode-specific rendering checks exist.

## Design Constraints from Requirements
- PRESET-01/02 require documented commands that render reduced/increased limits for pipeline/api/web.
- PRESET-03 requires baseline command (`docker compose up -d --build`) and behavior remain unchanged.
- Scope is local-hosting only; avoid cloud/runtime orchestration complexity.

## Recommended Implementation Direction
1. Preserve baseline by leaving `docker-compose.yml` defaults and `.env.example` baseline values unchanged.
2. Add explicit preset env files as overlays (e.g., `.env.runtime.low-power`, `.env.runtime.high-performance`) containing only runtime-budget variables.
3. Add a helper wrapper script for mode selection that:
   - defaults to baseline when mode is unspecified,
   - applies preset env files only when explicitly requested,
   - supports both `config` rendering and `up` startup flows.
4. Add mode-specific validator script and Phase 5 integration tests asserting exact rendered limits for all three services and default-regression safety.
5. Update README/runbook with concise mode-selection guidance and copy-paste commands.

## Tradeoffs
- Env-file overlay + helper script is low-risk and transparent; no compose profile overloading is needed.
- Explicit mode validator avoids brittle doc-only enforcement and gives clear regression boundaries.
- Additional tests increase maintenance slightly but directly protect PRESET-01/02/03.

## Risks and Mitigations
- Risk: mode script accidentally changes default command semantics.
  - Mitigation: preserve direct baseline command in docs and test default render separately.
- Risk: env precedence confusion between `.env`, shell vars, and `--env-file`.
  - Mitigation: define precedence in docs and enforce deterministic helper behavior.
- Risk: drift between docs and script commands.
  - Mitigation: add integration assertions for documented preset command strings.

## Planning Guidance
- Sequence work as: contract/tooling first, docs second, regression checks third.
- Keep changes local-first and backward-compatible with existing compose workflows.
