"""Pydantic schemas for MatchResult — aligned with PRD output spec."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DimensionScoreDetail(BaseModel):
    """Per-dimension score with explanation."""
    score: float = 0.0
    detail: str = ""


class MatchedEvidence(BaseModel):
    """Evidence that the resume matches a JD requirement."""
    jd_requirement: str = ""
    resume_evidence: str = ""
    evidence_source: str = ""
    strength: str = "中"  # 强|中|弱


class Gap(BaseModel):
    """Gap between JD requirement and resume."""
    jd_requirement: str = ""
    severity: str = "中"  # 高|中|低
    suggestion: str = ""


class Risk(BaseModel):
    """Risk of being filtered out by HR/ATS."""
    risk: str = ""
    level: str = "中"  # 高|中|低
    mitigation: str = ""


class MatchResponse(BaseModel):
    """Full match scoring response."""
    id: str = ""
    user_id: str = ""
    job_id: str = ""
    total_score: float | None = None
    opportunity_level: str | None = None  # 强力推荐|值得尝试|需要提升|暂不建议
    dimension_scores: dict[str, DimensionScoreDetail] | None = None
    matched_evidence: list[MatchedEvidence] | None = None
    gaps: list[Gap] | None = None
    risks: list[Risk] | None = None
    improvement_actions: list[str] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
