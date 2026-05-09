"""HRSimulation model - stores ATS and HR screening simulation results."""

from __future__ import annotations

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class HRSimulation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "hr_simulations"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id"), nullable=False, index=True)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_posts.id"), nullable=False, index=True)

    ats_check: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    screening_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    hr_feedback: Mapped[dict | None] = mapped_column(JSON, nullable=True)
