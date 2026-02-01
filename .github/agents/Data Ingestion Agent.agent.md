```chatagent
---
description: 'Automates fetching, normalizing, and storing raw crime incident data from external sources into the repository data folders.'
tools:
  - requests
  - s3
  - prefect
  - pandas
  - pyarrow
---
This agent performs scheduled and on-demand ingestion of external crime incident data (OpenDataPhilly, supplemental CSVs, partner APIs). It focuses on durable, auditable ingestion: fetching remote data, validating basic sanity, normalizing to the project's canonical schema, writing into `data/raw/` and producing a compact `data/processed/` artifact (Parquet), and emitting provenance metadata for downstream reproducibility.

When to use
- Schedule daily or weekly ingestion to keep `data/raw` up to date.
- Run on-demand when adding a new source, backfilling historic dates, or when upstream APIs change.

What it will NOT do
- It will not perform deep validation, exploratory cleaning, or final analytic transformations (those responsibilities belong to the Data Validation and processing steps). It will not publish dashboards.

Inputs
- Source descriptor(s): name, type (api/csv/zip), endpoint/URL, auth (token/env var), expected cadence.
- Date range or `since` parameter for incremental pulls.

Outputs
- Raw file saved to `data/raw/{source}/{YYYY-MM-DD}.csv` (or original compressed form) with checksum.
- Processed Parquet written to `data/processed/{source}/{YYYY-MM-DD}.parquet` following canonical schema.
- Provenance metadata: JSON record with `source`, `url`, `fetched_at`, `rows_raw`, `rows_processed`, `checksum`, `processor_version` saved to `data/processed/_provenance/{source}_{YYYY-MM-DD}.json`.

Core behaviors
- Idempotent: repeated runs for the same date-source should detect existing outputs and either skip or verify checksums depending on `--force`.
- Atomic writes: write to temporary files then rename to final path to avoid partial artifacts.
- Retries: exponential backoff for transient HTTP failures.
- Small-sample sanity checks: ensure required key columns exist and non-empty before marking processed output as valid.

Suggested connectors
- OpenDataPhilly REST API (Socrata). Use the Socrata endpoint with app token via env `ODP_APP_TOKEN`.
- Generic authenticated REST API (Bearer token) for partner feeds.
- Local or remote CSV/ZIP files (HTTP or S3).

Scheduling / Orchestration
- Ship as a Prefect flow or Airflow DAG. Recommended: Prefect flow with tasks: fetch -> validate_basic -> normalize -> write_raw -> write_processed -> record_provenance.

Configuration / Environment
- Environment variables for secrets: `ODP_APP_TOKEN`, `PARTNER_API_KEY`, `S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`.
- Config file: `config/ingestion.yaml` with source definitions and retention policy.

Error handling & reporting
- Emit structured logs (INFO/ERROR) and write a per-run log file to `data/processed/_logs/{source}_{YYYY-MM-DD}.log`.
- On irrecoverable errors (schema missing, required columns absent), write a failure metadata file and optionally notify (Slack/email) via a notifier task.

Testing & Validation
- Unit tests for normalization mapping and small-sample assertions.
- Integration test that runs a single small-source ingest using a canned fixture and asserts provenance metadata created.

Security considerations
- Do not commit API keys to repo. Use environment secrets in CI and Prefect deployment.
- Limit raw retention in `config/ingestion.yaml` and provide a `prune` utility to remove old raw files if desired.

Example usage (CLI)
```
# fetch yesterday's incidents (idempotent)
python infra/ingest.py --source opd_incidents --date 2026-01-31

# force re-run and overwrite outputs
python infra/ingest.py --source opd_incidents --date 2026-01-31 --force
```

Example Prefect flow (minimal)
```python
from prefect import flow, task
import pandas as pd
import requests
from pathlib import Path

@task(retries=3, retry_delay_seconds=60)
def fetch_json(url, headers=None):
	r = requests.get(url, headers=headers, timeout=30)
	r.raise_for_status()
	return r.json()

@task
def normalize_to_schema(df: pd.DataFrame) -> pd.DataFrame:
	# minimal mapping example — real mapping kept in analysis/utils.py
	mapping = {"dispatch_time": "occurred_on", "offense": "crime_type"}
	df = df.rename(columns=mapping)
	return df[["occurred_on", "crime_type", "lat", "lon"]]

@task
def write_parquet(df: pd.DataFrame, out: str):
	Path(out).parent.mkdir(parents=True, exist_ok=True)
	df.to_parquet(out, index=False)

@flow
def ingest_opd(date: str):
	url = f"https://data.phila.gov/resource/xxxx.json?$where=date%20%3D%20{date}"
	raw = fetch_json(url)
	df = pd.DataFrame(raw)
	df2 = normalize_to_schema(df)
	write_parquet(df2, f"data/processed/opd_incidents/{date}.parquet")

if __name__ == '__main__':
	ingest_opd("2026-01-31")
```

Developer notes
- Keep the canonical schema documented in `analysis/config.py` (or `analysis/utils.py`) so normalization code can import it.
- Add a lightweight CLI wrapper `infra/ingest.py` that parses args and submits Prefect flows (or runs local tasks for dev).

Next steps to implement in repo
- Add `infra/ingest.py` CLI and minimal Prefect flow.
- Add `config/ingestion.yaml` with at least one `opd_incidents` source configured.
- Add tests under `tests/test_ingest.py` to validate normalization mappings.

End of agent spec.
```