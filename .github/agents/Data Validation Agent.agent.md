```chatagent
---
description: 'Runs dataset validation suites (Great Expectations and/or pandera) on processed data; used on commit and scheduled runs.'
tools:
  - great_expectations
  - pandera
  - pandas
  - pytest
  - markdown
---
This agent executes data validation suites against `data/processed` artifacts. It is intended to run in CI on each push and on a daily schedule to catch schema drift, missingness, or upstream changes early. It produces human-readable reports (HTML/Markdown) in `reports/validation/` and returns non-zero exit codes when critical expectations fail so CI can block merges.

When to use
- Run automatically on every push that touches `data/processed` or code that affects schemas.
- Run nightly as a scheduled job to detect drift.

Behavior
- Prefer Great Expectations for declarative suites and historical expectation evaluation.
- Use pandera for lightweight, code-first schema checks in CI or unit tests.
- Save GE validation results and pandera exception summaries to `reports/validation/{source}/{YYYY-MM-DD}/`.
- Exit with code 1 if any critical expectation fails; allow non-blocking warnings for non-critical checks.

Inputs
- `--source` name matching processed artifact folder (e.g., `opd_incidents`).
- `--date` optional; if omitted, validate latest processed file.

Outputs
- `reports/validation/{source}/{YYYY-MM-DD}/summary.md` — human-readable summary.
- `reports/validation/{source}/{YYYY-MM-DD}/ge_result.json` — raw GE result (if GE used).
- `reports/validation/{source}/{YYYY-MM-DD}/pandera_errors.json` — pandera error details (if used).

CI integration
- Provide a GitHub Actions workflow `.github/workflows/validation.yml` that installs dependencies and runs `python infra/validate.py --source {source}` for configured sources.

Developer notes
- Keep canonical schema definitions under `infra/validation/schemas/` (pandera) and GE expectations under `great_expectations/` when used.
- Mark expectations as `critical` vs `warning` by convention in GE or with `severity` metadata in pandera wrappers.

Example commands
```
# run validation locally for a source
python infra/validate.py --source opd_incidents --date 2026-01-31
```

End of agent spec.
```
