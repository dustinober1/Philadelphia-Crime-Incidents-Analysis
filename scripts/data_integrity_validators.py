"""Data integrity validation functions for API responses."""

from typing import Any, Dict, List, Optional, Callable
import json


def validate_json_structure(data: Any, expected_type: type, required_fields: Optional[List[str]] = None) -> List[str]:
    """
    Validate basic JSON structure and required fields.
    
    Args:
        data: The data to validate
        expected_type: The expected Python type (list, dict, etc.)
        required_fields: List of required field names for dict objects
    
    Returns:
        List of error messages if validation fails, empty list if valid
    """
    errors = []
    
    if not isinstance(data, expected_type):
        errors.append(f"Expected {expected_type.__name__}, got {type(data).__name__}")
        return errors
    
    if expected_type == dict and required_fields:
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
    
    return errors


def validate_trends_data(data: Any) -> List[str]:
    """Validate trends endpoint responses."""
    errors = validate_json_structure(data, list)
    if errors:
        return errors
    
    # Validate each item in the trends data
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"Trend item at index {i} is not a dictionary")
            continue
            
        # Common fields for trend data
        required_fields = ["crime_category", "date", "count"] if "crime_category" in item else ["date", "value"]
        for field in required_fields:
            if field not in item:
                errors.append(f"Trend item at index {i} missing required field: {field}")
                
        # Validate data types
        if "date" in item and not isinstance(item["date"], str):
            errors.append(f"Trend item at index {i} has non-string date field")
        if "count" in item and not isinstance(item["count"], (int, float)):
            errors.append(f"Trend item at index {i} has non-numeric count field")
        if "value" in item and not isinstance(item["value"], (int, float)):
            errors.append(f"Trend item at index {i} has non-numeric value field")
            
    return errors


def validate_spatial_data(data: Any) -> List[str]:
    """Validate spatial GeoJSON endpoint responses."""
    errors = validate_json_structure(data, dict, ["type", "features"])
    if errors:
        return errors
    
    # Validate GeoJSON structure
    geojson_type = data.get("type")
    if geojson_type != "FeatureCollection":
        errors.append(f"Expected GeoJSON FeatureCollection, got {geojson_type}")
    
    features = data.get("features", [])
    if not isinstance(features, list):
        errors.append("GeoJSON features property is not a list")
        return errors
    
    # Validate each feature
    for i, feature in enumerate(features):
        if not isinstance(feature, dict):
            errors.append(f"GeoJSON feature at index {i} is not a dictionary")
            continue
            
        required_fields = ["type", "geometry", "properties"]
        for field in required_fields:
            if field not in feature:
                errors.append(f"GeoJSON feature at index {i} missing required field: {field}")
                
        # Validate geometry structure
        geometry = feature.get("geometry", {})
        if not isinstance(geometry, dict):
            errors.append(f"GeoJSON feature at index {i} has non-dictionary geometry")
            continue
            
        geom_type = geometry.get("type")
        if geom_type not in ["Point", "Polygon", "MultiPolygon", "LineString"]:
            errors.append(f"GeoJSON feature at index {i} has unsupported geometry type: {geom_type}")
    
    return errors


def validate_policy_data(data: Any) -> List[str]:
    """Validate policy endpoint responses."""
    errors = validate_json_structure(data, list)
    if errors:
        return errors
    
    # Validate each item in the policy data
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"Policy item at index {i} is not a dictionary")
            continue
            
        # Common fields for policy data
        required_fields = ["category", "metric", "value"] if "category" in item else ["type", "value"]
        for field in required_fields:
            if field not in item:
                errors.append(f"Policy item at index {i} missing required field: {field}")
                
        # Validate data types
        if "value" in item and not isinstance(item["value"], (int, float)):
            errors.append(f"Policy item at index {i} has non-numeric value field")
        if "metric" in item and not isinstance(item["metric"], str):
            errors.append(f"Policy item at index {i} has non-string metric field")
            
    return errors


def validate_forecasting_data(data: Any) -> List[str]:
    """Validate forecasting endpoint responses."""
    errors = validate_json_structure(data, (dict, list))
    if errors:
        return errors
    
    if isinstance(data, list):
        # If it's a list, validate as a sequence of forecast points
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                errors.append(f"Forecast item at index {i} is not a dictionary")
                continue
                
            required_fields = ["date", "prediction"]
            for field in required_fields:
                if field not in item:
                    errors.append(f"Forecast item at index {i} missing required field: {field}")
                    
            # Validate data types
            if "date" in item and not isinstance(item["date"], str):
                errors.append(f"Forecast item at index {i} has non-string date field")
            if "prediction" in item and not isinstance(item["prediction"], (int, float)):
                errors.append(f"Forecast item at index {i} has non-numeric prediction field")
    else:
        # If it's a dict, validate as a single forecast object
        required_fields = ["predictions", "confidence_intervals"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Forecast object missing required field: {field}")
                
        predictions = data.get("predictions", [])
        if not isinstance(predictions, list):
            errors.append("Forecast predictions property is not a list")
    
    return errors


def validate_metadata_data(data: Any) -> List[str]:
    """Validate metadata endpoint responses."""
    errors = validate_json_structure(data, dict, ["version", "last_updated", "data_sources"])
    if errors:
        return errors
    
    # Validate specific fields
    if "version" in data and not isinstance(data["version"], str):
        errors.append("Metadata version field is not a string")
    if "last_updated" in data and not isinstance(data["last_updated"], str):
        errors.append("Metadata last_updated field is not a string")
    if "data_sources" in data and not isinstance(data["data_sources"], list):
        errors.append("Metadata data_sources field is not a list")
    
    return errors


def validate_response_structure(endpoint_type: str, data: Any) -> List[str]:
    """
    Validate response structure based on endpoint type.
    
    Args:
        endpoint_type: Type of endpoint ('trends', 'spatial', 'policy', 'forecasting', 'metadata')
        data: The response data to validate
    
    Returns:
        List of error messages if validation fails, empty list if valid
    """
    validators: Dict[str, Callable[[Any], List[str]]] = {
        'trends': validate_trends_data,
        'spatial': validate_spatial_data,
        'policy': validate_policy_data,
        'forecasting': validate_forecasting_data,
        'metadata': validate_metadata_data
    }
    
    validator = validators.get(endpoint_type)
    if not validator:
        return [f"No validator found for endpoint type: {endpoint_type}"]
    
    return validator(data)