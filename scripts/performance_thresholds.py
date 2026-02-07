# Performance Threshold Configuration
# Default timeout values in seconds for different endpoint types

PERFORMANCE_THRESHOLDS = {
    # Simple endpoints
    "metadata": {
        "warning_threshold_ms": 1000,  # 1 second
        "error_threshold_ms": 2000     # 2 seconds
    },
    
    # Medium complexity endpoints
    "trends": {
        "warning_threshold_ms": 2000,  # 2 seconds
        "error_threshold_ms": 3000     # 3 seconds
    },
    
    "policy": {
        "warning_threshold_ms": 2000,  # 2 seconds
        "error_threshold_ms": 3000     # 3 seconds
    },
    
    # Complex endpoints
    "spatial": {
        "warning_threshold_ms": 3000,  # 3 seconds
        "error_threshold_ms": 5000     # 5 seconds
    },
    
    "forecasting": {
        "warning_threshold_ms": 3000,  # 3 seconds
        "error_threshold_ms": 5000     # 5 seconds
    },
    
    # Default values if endpoint type not specified
    "default": {
        "warning_threshold_ms": 2000,  # 2 seconds
        "error_threshold_ms": 4000     # 4 seconds
    }
}