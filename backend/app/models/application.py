"""Application model - tracks the full application lifecycle per job."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Application(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "applications"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id"), nullable=False, index=True)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_posts.id"), nullable=False, index=True)

    job_title: Mapped[str] = mapped_column(String(300), default="", nullable=False)
    company_name: Mapped[str] = mapped_column(String(300), default="", nullable=False)

    status: Mapped[str] = mapped_column(String(50), default="待评估", nullable=False)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    resume_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    next_action: Mapped[str | None] = mapped_column(String(300), nullable=True)
    next_action_deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    timeline: Mapped[list | None] = mapped_column(JSON, nullable=True)
