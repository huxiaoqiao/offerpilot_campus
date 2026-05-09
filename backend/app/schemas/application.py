"""Pydantic schemas for Application."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TimelineEntry(BaseModel):
    date: str = ""
    action: str = ""
    detail: str = ""


class ApplicationCreate(BaseModel):
    job_id: str
    status: str = "待评估"
    match_score: float | None = None
    resume_version_id: str | None = None
    next_action: str | None = None
    next_action_deadline: datetime | None = None
    notes: str | None = None
    tags: list[str] | None = None
    timeline: list[TimelineEntry] | None = None


class ApplicationUpdate(BaseModel):
    status: str | None = None
    match_score: float | None = None
    resume_version_id: str | None = None
    next_action: str | None = None
    next_action_deadline: datetime | None = None
    notes: str | None = None
    tags: list[str] | None = None
    timeline: list[TimelineEntry] | None = None


class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    job_id: str
    status: str = "待评估"
    match_score: float | None = None
    resume_version_id: str | None = None
    next_action: str | None = None
    next_action_deadline: datetime | None = None
    notes: str | None = None
    tags: list[str] | None = None
    timeline: list[dict[str, Any]] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class BoardStats(BaseModel):
    total: int = 0
    by_status: dict[str, int] = Field(default_factory=dict)
    upcoming_deadlines: list[ApplicationResponse] = Field(default_factory=list)
