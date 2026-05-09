"""ResumeVersion model - stores AI-tailored resume versions."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class ResumeVersion(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "resume_versions"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id"), nullable=False, index=True)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_posts.id"), nullable=False, index=True)

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    sections: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    html_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
