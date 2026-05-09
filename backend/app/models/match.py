"""MatchResult model - stores job-candidate matching analysis."""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class MatchResult(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "match_results"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id"), nullable=False, index=True)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_posts.id"), nullable=False, index=True)

    total_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    opportunity_level: Mapped[str | None] = mapped_column(String(50), nullable=True)

    dimension_scores: Mapped[list | None] = mapped_column(JSON, nullable=True)
    matched_evidence: Mapped[list | None] = mapped_column(JSON, nullable=True)
    gaps: Mapped[list | None] = mapped_column(JSON, nullable=True)
    risks: Mapped[list | None] = mapped_column(JSON, nullable=True)
    improvement_actions: Mapped[list | None] = mapped_column(JSON, nullable=True)
