"""Pydantic schemas for ResumeVersion — aligned with PRD spec."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SkillChange(BaseModel):
    """A change made to the skills section."""
    skill: str = ""
    action: str = ""  # 置顶|新增|移除|重排序
    reason: str = ""


class ExperienceRewrite(BaseModel):
    """A rewritten experience entry."""
    original: str = ""
    rewritten: str = ""
    changes: list[str] = Field(default_factory=list)


class ResumeSections(BaseModel):
    """All sections of a customized resume."""
    summary: dict[str, str] = Field(default_factory=lambda: {"content": "", "source": ""})
    skills: dict[str, Any] = Field(default_factory=lambda: {"content": [], "changes": []})
    experiences: list[ExperienceRewrite] = Field(default_factory=list)
    job_intention: dict[str, str] = Field(default_factory=lambda: {"content": "", "source": ""})


class ResumeRewriteResponse(BaseModel):
    """Full resume rewrite response."""
    id: str
    user_id: str
    job_id: str
    version: int = 1
    sections: ResumeSections | None = None
    html_preview: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
