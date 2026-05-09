"""Pydantic schemas for InterviewSet — aligned with PRD spec."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class InterviewQuestion(BaseModel):
    """A single interview question."""
    id: str = ""
    category: str = ""  # 自我介绍|行为面试|技术问题|情景模拟|反问环节
    question: str = ""
    reference_answer_framework: str = ""
    related_resume_item: str | None = None
    related_risk: str | None = None


class STARStory(BaseModel):
    """A STAR method story."""
    title: str = ""
    situation: str = ""
    task: str = ""
    action: str = ""
    result: str = ""
    applicable_questions: list[str] = Field(default_factory=list)


class RiskFollowup(BaseModel):
    """A risk-based follow-up question."""
    risk: str = ""
    possible_question: str = ""
    suggested_answer: str = ""


class InterviewResponse(BaseModel):
    """Full interview preparation response."""
    id: str = ""
    user_id: str = ""
    job_id: str = ""
    questions: list[InterviewQuestion] | None = None
    star_stories: list[STARStory] | None = None
    risk_followups: list[RiskFollowup] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
