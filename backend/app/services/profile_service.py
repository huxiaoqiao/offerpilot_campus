"""ProfileService - business logic for user profile operations."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import UserProfile
from app.parser.resume_parser import resume_parser
from app.schemas.profile import ProfileCreate, ProfileUpdate, StructuredResume
from app.utils.id_utils import gen_id

logger = logging.getLogger(__name__)


class ProfileService:
    """Async service layer for user profile CRUD and resume operations."""

    async def create_profile(self, db: AsyncSession, profile_data: ProfileCreate) -> UserProfile:
        """Create a new user profile."""
        profile = UserProfile(
            id=gen_id(),
            name=profile_data.name,
            school=profile_data.school,
            major=profile_data.major,
            grade=profile_data.grade,
            graduation_year=profile_data.graduation_year,
            target_positions=profile_data.target_positions,
            target_cities=profile_data.target_cities,
            salary_min=profile_data.salary_min,
            salary_max=profile_data.salary_max,
            target_industries=profile_data.target_industries,
            avoid_items=profile_data.avoid_items,
            resume_raw_text=profile_data.resume_raw_text,
            resume_structured=profile_data.resume_structured.model_dump() if profile_data.resume_structured else None,
            skill_ratings=profile_data.skill_ratings,
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile

    async def get_profile(self, db: AsyncSession, profile_id: str) -> UserProfile | None:
        """Get a profile by ID."""
        result = await db.execute(select(UserProfile).where(UserProfile.id == profile_id))
        return result.scalar_one_or_none()

    async def update_profile(self, db: AsyncSession, profile_id: str, update_data: ProfileUpdate) -> UserProfile:
        """Update an existing profile."""
        profile = await self.get_profile(db, profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")

        update_dict = update_data.model_dump(exclude_unset=True)
        # Handle StructuredResume -> dict conversion
        if "resume_structured" in update_dict and update_dict["resume_structured"] is not None:
            sr = update_dict["resume_structured"]
            if isinstance(sr, StructuredResume):
                update_dict["resume_structured"] = sr.model_dump()

        for field, value in update_dict.items():
            setattr(profile, field, value)

        await db.commit()
        await db.refresh(profile)
        return profile

    async def upload_resume(
        self, db: AsyncSession, profile_id: str, file_path: str
    ) -> tuple[str, StructuredResume]:
        """Upload and parse a resume file, updating the profile."""
        profile = await self.get_profile(db, profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")

        raw_text, structured = await resume_parser.parse_file_to_structured(file_path)

        profile.resume_raw_text = raw_text
        profile.resume_structured = structured.model_dump()
        await db.commit()
        await db.refresh(profile)

        return raw_text, structured

    async def update_structured_resume(
        self, db: AsyncSession, profile_id: str, structured: StructuredResume
    ) -> UserProfile:
        """Manually update the structured resume data."""
        profile = await self.get_profile(db, profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")

        profile.resume_structured = structured.model_dump()
        await db.commit()
        await db.refresh(profile)
        return profile

    async def update_skill_ratings(
        self, db: AsyncSession, profile_id: str, ratings: dict[str, float]
    ) -> UserProfile:
        """Update skill self-assessment ratings."""
        profile = await self.get_profile(db, profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")

        profile.skill_ratings = ratings
        await db.commit()
        await db.refresh(profile)
        return profile

    async def reparse_resume(self, db: AsyncSession, profile_id: str) -> StructuredResume:
        """Re-parse the existing raw resume text using LLM."""
        profile = await self.get_profile(db, profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")
        if not profile.resume_raw_text:
            raise ValueError("No raw resume text to reparse")

        structured = await resume_parser.parse_text(profile.resume_raw_text)
        profile.resume_structured = structured.model_dump()
        await db.commit()
        await db.refresh(profile)
        return structured


# Module-level singleton
profile_service = ProfileService()
