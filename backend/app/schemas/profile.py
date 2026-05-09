"""Pydantic schemas for UserProfile."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ---------- sub-models ----------

class Education(BaseModel):
    school: str = ""
    major: str = ""
    degree: str = ""
    start_date: str = ""
    end_date: str = ""
    gpa: str | None = None
    description: str | None = None


class Experience(BaseModel):
    company: str = ""
    title: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""
    achievements: list[str] = Field(default_factory=list)


class StructuredResume(BaseModel):
    name: str = ""
    phone: str = ""
    email: str = ""
    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certificates: list[str] = Field(default_factory=list)
    self_evaluation: str = ""


# ---------- request / response ----------

class ProfileCreate(BaseModel):
    name: str = Field(..., max_length=100)
    school: str | None = None
    major: str | None = None
    grade: str | None = None
    graduation_year: int | None = None
    target_positions: list[str] | None = None
    target_cities: list[str] | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    target_industries: list[str] | None = None
    avoid_items: list[str] | None = None
    resume_raw_text: str | None = None
    resume_structured: StructuredResume | None = None
    skill_ratings: dict[str, float] | None = None


class ProfileUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    school: str | None = None
    major: str | None = None
    grade: str | None = None
    graduation_year: int | None = None
    target_positions: list[str] | None = None
    target_cities: list[str] | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    target_industries: list[str] | None = None
    avoid_items: list[str] | None = None
    resume_raw_text: str | None = None
    resume_structured: StructuredResume | None = None
    skill_ratings: dict[str, float] | None = None


class ProfileResponse(BaseModel):
    id: str
    name: str
    school: str | None = None
    major: str | None = None
    grade: str | None = None
    graduation_year: int | None = None
    target_positions: list[str] | None = None
    target_cities: list[str] | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    target_industries: list[str] | None = None
    avoid_items: list[str] | None = None
    resume_raw_text: str | None = None
    resume_structured: dict[str, Any] | None = None
    skill_ratings: dict[str, float] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
