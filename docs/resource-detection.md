# Host Resource Detection and Smart Presets

Phase 9 adds resource-aware startup helpers for local Docker Compose workflows.

## What it does

- Detects host CPU core count and memory (total + available) before startup
- Supports Linux, macOS, and Windows WSL detection paths
- Recommends one of three runtime modes based on detected resources:
  - `low-power`
  - `default`
  - `high-performance`

## Detection commands

Inspect detected host resources:

```bash
python3 scripts/resource_detector.py
```

Get a recommended runtime mode:

```bash
python3 scripts/preset_calculator.py
```

Get machine-friendly recommendation output:

```bash
python3 scripts/preset_calculator.py --format json
```

## Smart compose startup

Use auto mode to apply the recommended preset before invoking `docker compose`:

```bash
./scripts/compose_with_runtime_mode.sh --mode auto up -d --build
```

To see recommendation details without starting containers:

```bash
./scripts/compose_with_runtime_mode.sh --recommend
```

## Recommendation thresholds

- `high-performance`: CPU cores >= 8 and total RAM >= 16 GB and available RAM >= 8 GB
- `low-power`: CPU cores < 4 or total RAM < 8 GB or available RAM < 4 GB
- `default`: all other hosts

If resource detection is incomplete, the system falls back to `default` mode.
