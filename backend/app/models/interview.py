"""InterviewSet model - stores generated interview questions and stories."""

from __future__ import annotations

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class InterviewSet(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "interview_sets"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id"), nullable=False, index=True)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_posts.id"), nullable=False, index=True)

    questions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    star_stories: Mapped[list | None] = mapped_column(JSON, nullable=True)
    risk_followups: Mapped[list | None] = mapped_column(JSON, nullable=True)
