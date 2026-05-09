"""JobPost model - stores parsed job description data."""

from __future__ import annotations

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class JobPost(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "job_posts"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id"), nullable=False, index=True)
    company_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    position_title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    jd_raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Structured JD fields (JSON)
    responsibilities: Mapped[list | None] = mapped_column(JSON, nullable=True)
    hard_requirements: Mapped[list | None] = mapped_column(JSON, nullable=True)
    soft_requirements: Mapped[list | None] = mapped_column(JSON, nullable=True)

    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(200), nullable=True)

    keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    risk_tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    duplicate_of: Mapped[str | None] = mapped_column(String(36), nullable=True)

    status: Mapped[str] = mapped_column(String(50), default="待评估", nullable=False)
