"""Pydantic models for validation results structure."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class CheckResult(BaseModel):
    """Model for individual check results."""
    name: str
    success: bool
    duration_ms: float
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ValidationResult(BaseModel):
    """Model for overall validation results."""
    timestamp: str
    duration_ms: float
    success: bool
    service_info: Dict[str, Any]
    checks: List[CheckResult]
    errors: List[str]
    metadata: Dict[str, Any] = {}


class HealthInfo(BaseModel):
    """Model for health check information."""
    api_health_url: str
    web_url: str
    timeout_seconds: int
    missing_exports: List[str]