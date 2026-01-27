# Agentic Coding Guide: Crime Incidents Philadelphia

This document outlines the development standards, commands, and practices for agents (AI and human) working on the Crime Incidents Philadelphia project.

## 1. Environment & Build

The project is a Python-based data analysis application using helper scripts.

### 1.1. Setup
- **Python Version**: Python 3.8+ recommended.
- **Dependencies**: Managed via `requirements.txt`.
  ```bash
  pip install -r requirements.txt
  ```
- **Virtual Environment**: Always run within a virtual environment (e.g., `venv`, `conda`).

### 1.2. Build & Execution
- **No compilation step**: Python is interpreted.
- **Running Scripts**: Execute scripts directly from the root or via module notation if applicable.
  ```bash
  # Example: Run the scraper
  python scripts/helper/scrape.py
  
  # Example: Run the parquet converter
  python scripts/helper/csv_to_parquet.py
  ```
### 1.3. Linting & Formatting
*Note: strict configuration files (e.g., .flake8, pyproject.toml) are currently absent. Follow these defaults:*

- **Linter**: Use `flake8` or `ruff` if available.
  ```bash
  # Check all files
  ruff check .
  # or
  flake8 .
  ```
- **Formatter**: `black` or `ruff format` is recommended for consistency.
  ```bash
  ruff format .
  ```

### 1.4. Testing
*Currently, no dedicated test suite exists. Future tests should use `pytest`.*

- **Run All Tests**:
  ```bash
  pytest
  ```
- **Run a Single Test File**:
  ```bash
  pytest tests/test_module.py
  ```
- **Run a Single Test Function**:
  ```bash
  pytest tests/test_module.py::test_function_name
  ```

## 2. Code Style & Conventions

Adhere to the existing style observed in `scripts/helper/`.

### 2.1. Python Conventions
- **Indentation**: 4 spaces. No tabs.
- **Line Length**: Target 88-100 characters (standard Python practice).
- **Strings**: Double quotes `"` preferred over single quotes `'` for string literals, unless nesting quotes.

### 2.2. Naming
- **Variables & Functions**: `snake_case` (e.g., `download_month`, `file_path`).
- **Classes**: `PascalCase` (e.g., `CrimeAnalyzer`).
- **Constants**: `UPPER_CASE` (e.g., `BASE_URL`, `OUTPUT_DIR`).
- **File Names**: `snake_case` (e.g., `csv_to_parquet.py`).

### 2.3. Imports
Group imports in the following order, separated by a blank line:
1.  **Standard Library**: `import os`, `import time`, `import sys`, `from pathlib import Path`
2.  **Third-Party**: `import pandas as pd`, `import requests`
3.  **Local Application**: (e.g., `from src import utils`)

*Example:*
```python
import os
import time
from pathlib import Path

import pandas as pd
import requests

from src.utils import formatting
```

### 2.4. File System & Paths
- **Path Handling**: Prefer `pathlib.Path` over `os.path` for path manipulation in new code.
- **Relative Paths**: Avoid hardcoded absolute paths. Use paths relative to the script location or project root.
  ```python
  # Preferred
  from pathlib import Path
  BASE_DIR = Path(__file__).parent.parent
  DATA_DIR = BASE_DIR / "data"
  ```

### 2.5. Error Handling
- Use specific `try...except` blocks where failure is anticipated (e.g., network requests, file I/O).
- Log or print meaningful error messages.
- Clean up resources (though context managers `with open(...)` are preferred).

*Example from `scrape.py`:*
```python
try:
    response = requests.get(url, timeout=120)
    response.raise_for_status()
except Exception as e:
    print(f"Failed: {e}")
    # Handle retry or exit
```

### 2.6. Documentation
- **Docstrings**: Include docstrings for all modules, classes, and complex functions.
- **Format**: Google or NumPy style docstrings are acceptable.
- **Comments**: Comment complex logic. "Why" is more important than "What".

### 2.7. Data Handling (Pandas)
- **Type Optimization**: optimize data types to save memory (e.g., `category` for low-cardinality strings, `int8/16` for small integers).
- **Chunking**: Process large datasets in chunks to avoid OOM errors.
- **Parquet**: Prefer Parquet over CSV for intermediate storage of large datasets.

## 3. Project Structure (Inferred)

```
.
├── config.ini          # Configuration
├── data/               # Data storage (ignored in git mostly)
│   ├── raw/            # Original downloads
│   └── processed/      # Cleaned/Parquet files
├── scripts/            # Executable scripts
│   └── helper/         # ETL/Maintenance scripts
├── src/                # Reusable library code
│   └── utils/          # Utility functions
├── requirements.txt    # Dependencies
└── README.md           # Documentation
```

## 4. Cursor/Copilot Rules

*No specific `.cursorrules` or `.github/copilot-instructions.md` found. Fallback to general Python best practices.*

- **Context Awareness**: When editing, read the whole file or relevant class first.
- **Minimal Changes**: Only modify what is requested.
- **Safety**: Do not commit secrets/API keys. Verify `requests` calls have timeouts.
