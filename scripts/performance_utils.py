"""Performance timing and threshold checking utilities."""

import time
from typing import Any, Callable, Tuple, Optional
from performance_thresholds import PERFORMANCE_THRESHOLDS


def timed_execution_with_threshold(endpoint_type: str = "default"):
    """
    Decorator to measure execution time and check against performance thresholds.
    
    Args:
        endpoint_type: Type of endpoint being tested (determines threshold values)
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Tuple[Any, float, Optional[str]]:
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start_time) * 1000  # Convert to ms
            
            # Get thresholds for this endpoint type
            thresholds = PERFORMANCE_THRESHOLDS.get(endpoint_type, PERFORMANCE_THRESHOLDS["default"])
            warning_threshold = thresholds["warning_threshold_ms"]
            error_threshold = thresholds["error_threshold_ms"]
            
            # Determine performance status
            performance_status = None
            if duration_ms > error_threshold:
                performance_status = f"PERFORMANCE_ERROR: Response took {duration_ms:.2f}ms, exceeds threshold of {error_threshold}ms"
            elif duration_ms > warning_threshold:
                performance_status = f"PERFORMANCE_WARNING: Response took {duration_ms:.2f}ms, exceeds threshold of {warning_threshold}ms"
            
            return result, duration_ms, performance_status
        return wrapper
    return decorator


def check_performance_threshold(duration_ms: float, endpoint_type: str = "default") -> Tuple[bool, Optional[str]]:
    """
    Check if a duration exceeds performance thresholds.
    
    Args:
        duration_ms: Duration in milliseconds
        endpoint_type: Type of endpoint being tested
    
    Returns:
        Tuple of (is_within_threshold, status_message)
    """
    thresholds = PERFORMANCE_THRESHOLDS.get(endpoint_type, PERFORMANCE_THRESHOLDS["default"])
    warning_threshold = thresholds["warning_threshold_ms"]
    error_threshold = thresholds["error_threshold_ms"]
    
    if duration_ms > error_threshold:
        return False, f"PERFORMANCE_ERROR: Response took {duration_ms:.2f}ms, exceeds threshold of {error_threshold}ms"
    elif duration_ms > warning_threshold:
        return True, f"PERFORMANCE_WARNING: Response took {duration_ms:.2f}ms, exceeds threshold of {warning_threshold}ms"
    else:
        return True, None