"""Pydantic schemas for JobPost."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class QualityDetails(BaseModel):
    """Quality score breakdown."""
    completeness: float = 0
    salary_transparency: float = 0
    professionalism: float = 0


class JDExtractedData(BaseModel):
    """Structured data extracted from a JD by LLM."""
    company_name: str | None = None
    position_title: str | None = None
    responsibilities: list[str] = Field(default_factory=list)
    hard_requirements: list[str] = Field(default_factory=list)
    soft_requirements: list[str] = Field(default_factory=list)
    salary_min: int | None = None
    salary_max: int | None = None
    city: str | None = None
    industry: str | None = None
    keywords: list[str] = Field(default_factory=list)
    quality_score: float = 0
    quality_details: QualityDetails = Field(default_factory=QualityDetails)
    risk_tags: list[str] = Field(default_factory=list)


class JobCreate(BaseModel):
    """Create a single job from raw JD text."""
    company_name: str | None = None
    position_title: str | None = None
    jd_raw_text: str = Field(..., min_length=10, description="Paste the full JD here")
    source_url: str | None = None


class JobBatchImport(BaseModel):
    """Batch import multiple JDs."""
    jobs: list[JobCreate] = Field(..., min_length=1)


class JobResponse(BaseModel):
    id: str
    user_id: str
    company_name: str | None = None
    position_title: str | None = None
    jd_raw_text: str | None = None
    responsibilities: list[str] | None = None
    hard_requirements: list[str] | None = None
    soft_requirements: list[str] | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    city: str | None = None
    industry: str | None = None
    keywords: list[str] | None = None
    source_url: str | None = None
    quality_score: float | None = None
    quality_details: dict[str, Any] | None = None
    risk_tags: list[str] | None = None
    is_duplicate: bool = False
    duplicate_of: str | None = None
    status: str = "待评估"
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
