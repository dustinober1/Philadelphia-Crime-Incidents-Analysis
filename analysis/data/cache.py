"""Caching layer for data loading using joblib.Memory.

This module provides a memory-backed caching system for expensive data
loading operations. Cached data is stored in .cache/joblib/ at the
project root and persists between Python sessions.

Example:
    >>> from analysis.data.cache import clear_cache
    >>> clear_cache()  # Clear all cached data
"""

from joblib import Memory
from pathlib import Path
import shutil

# Cache location: project root/.cache/joblib
_CACHE_DIR = Path(__file__).resolve().parent.parent.parent / ".cache" / "joblib"

# Create cache directory if it doesn't exist
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Global memory instance for caching function results
memory = Memory(location=_CACHE_DIR, verbose=0)


def clear_cache() -> None:
    """Clear all cached data from the joblib cache directory.

    This function removes all cached function results from the cache
    directory. The next call to a cached function will recompute and
    cache the result.

    Example:
        >>> from analysis.data.cache import clear_cache
        >>> clear_cache()
        Cache cleared: /path/to/project/.cache/joblib
    """
    if _CACHE_DIR.exists():
        # Remove all cache contents
        for item in _CACHE_DIR.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                shutil.rmtree(item)
            elif item.is_file():
                item.unlink()
    print(f"Cache cleared: {_CACHE_DIR}")


__all__ = ["memory", "clear_cache"]
