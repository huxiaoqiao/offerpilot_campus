"""UserProfile model - stores user personal and career information."""

from __future__ import annotations

from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class UserProfile(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "user_profiles"

    # Basic info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    school: Mapped[str | None] = mapped_column(String(200), nullable=True)
    major: Mapped[str | None] = mapped_column(String(200), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(50), nullable=True)
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Career targets (stored as JSON arrays/objects)
    target_positions: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    target_cities: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_industries: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    avoid_items: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)

    # Resume
    resume_raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_structured: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Skills
    skill_ratings: Mapped[dict | None] = mapped_column(JSON, nullable=True)
