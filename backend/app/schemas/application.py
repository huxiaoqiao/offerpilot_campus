"""Pydantic schemas for Application — aligned with frontend types."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class TimelineEntry(BaseModel):
    time: str = ""
    action: str = ""
    detail: str = ""


class ApplicationCreate(BaseModel):
    job_id: str
    job_title: str = ""
    company_name: str = ""
    status: str = "待评估"
    match_score: float | None = None
    resume_version_id: str | None = None
    next_action: str | None = None
    next_action_deadline: str | None = None
    notes: str | None = None
    tags: list[str] | None = None


class ApplicationUpdate(BaseModel):
    status: str | None = None
    match_score: float | None = None
    resume_version_id: str | None = None
    next_action: str | None = None
    next_action_deadline: str | None = None
    notes: str | None = None
    tags: list[str] | None = None
    timeline: list[TimelineEntry] | None = None


class ApplicationResponse(BaseModel):
    id: str
    user_id: str = ""
    job_id: str = ""
    job_title: str = ""
    company_name: str = ""
    status: str = "待评估"
    match_score: float | None = None
    resume_version_id: str | None = None
    next_action: str | None = None
    next_action_deadline: datetime | str | None = None
    notes: str | None = None
    tags: list[str] | None = Field(default_factory=list)
    timeline: list[dict[str, Any]] | None = Field(default_factory=list)
    created_at: datetime | str | None = None
    updated_at: datetime | str | None = None

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}


class BoardStats(BaseModel):
    total: int = 0
    by_status: dict[str, int] = Field(default_factory=dict)
    avg_match_score: float = 0
    offer_rate: float = 0
    interview_rate: float = 0
    top_dimension_scores: dict[str, float] = Field(default_factory=dict)
