"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

COLORS = {
    "Violent": "#E63946",
    "Property": "#457B9D",
    "Other": "#A8DADC",
}


class TrendDataPoint(BaseModel):
    year: int | None = None
    month: str | None = None
    crime_category: str | None = None
    count: int


class CovidComparison(BaseModel):
    period: str
    start: str
    end: str
    count: int


class SeasonalityData(BaseModel):
    by_month: list[dict[str, Any]]
    by_day_of_week: list[dict[str, Any]]
    by_hour: list[dict[str, Any]]


class ForecastPayload(BaseModel):
    model: str
    historical: list[dict[str, Any]]
    forecast: list[dict[str, Any]]


class QuestionSubmission(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr | None = None
    question_text: str = Field(min_length=1, max_length=1000)
    honeypot: str = Field(default="", max_length=0)


class QuestionUpdate(BaseModel):
    answer_text: str = Field(min_length=1, max_length=2000)
    status: str = Field(default="answered")


class QuestionResponse(BaseModel):
    id: str
    name: str
    email: str | None = None
    question_text: str
    answer_text: str | None = None
    status: str
    created_at: datetime
    answered_at: datetime | None = None


class AdminLoginRequest(BaseModel):
    password: str = Field(min_length=1, max_length=256)


class AdminSessionResponse(BaseModel):
    token: str
    expires_at: str


class MetadataResponse(BaseModel):
    total_incidents: int
    date_start: str
    date_end: str
    last_updated: str
    source: str
    colors: dict[str, str] = COLORS
