"""Pydantic schemas for HRSimulation — aligned with PRD spec."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ATSCheck(BaseModel):
    """ATS system check results."""
    keyword_match_rate: float = 0.0
    format_compliance: bool = True
    readability_score: int = 0
    issues: list[str] = Field(default_factory=list)


class ScreeningResult(BaseModel):
    """HR screening simulation results."""
    pass_probability: int = 0
    pass_reasons: list[str] = Field(default_factory=list)
    fail_reasons: list[str] = Field(default_factory=list)


class HRFeedback(BaseModel):
    """A piece of HR feedback."""
    category: str = ""
    feedback: str = ""
    priority: str = "中"


class HRResponse(BaseModel):
    """Full HR simulation response."""
    id: str = ""
    user_id: str = ""
    job_id: str = ""
    ats_check: ATSCheck | None = None
    screening_result: ScreeningResult | None = None
    hr_feedback: list[HRFeedback] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
