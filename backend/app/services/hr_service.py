"""HRService - ATS and HR screening simulation with LLM."""

from __future__ import annotations

import json
import logging

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.client import llm_client
from app.models.hr import HRSimulation
from app.models.job import JobPost
from app.models.profile import UserProfile
from app.prompts.hr_simulate import build_hr_messages
from app.schemas.hr import HRResponse
from app.utils.id_utils import gen_id

logger = logging.getLogger(__name__)


class HRService:
    """Async service for HR/ATS simulation."""

    async def simulate_hr(
        self, db: AsyncSession, user_id: str, job_id: str
    ) -> HRResponse:
        """Run HR simulation and persist the result."""
        profile = await self._get_profile(db, user_id)
        job = await self._get_job(db, job_id)

        resume_text = profile.resume_raw_text or ""
        jd_text = job.jd_raw_text or ""

        if not resume_text:
            raise HTTPException(status_code=400, detail="User has no resume text")
        if not jd_text:
            raise HTTPException(status_code=400, detail="Job has no JD text")

        messages = build_hr_messages(resume_text, jd_text)
        result = await llm_client.chat_structured(messages, HRResponse)

        record = HRSimulation(
            id=gen_id(),
            user_id=user_id,
            job_id=job_id,
            ats_check=result.ats_check.model_dump() if result.ats_check else None,
            screening_result=result.screening_result.model_dump() if result.screening_result else None,
            hr_feedback=result.hr_feedback.model_dump() if result.hr_feedback else None,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)

        return HRResponse(
            id=record.id,
            user_id=record.user_id,
            job_id=record.job_id,
            ats_check=result.ats_check,
            screening_result=result.screening_result,
            hr_feedback=result.hr_feedback,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    async def get_simulation(
        self, db: AsyncSession, user_id: str, job_id: str
    ) -> HRResponse:
        """Retrieve an existing HR simulation result."""
        result = await db.execute(
            select(HRSimulation).where(
                HRSimulation.user_id == user_id,
                HRSimulation.job_id == job_id,
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="HR simulation not found")
        return self._to_response(record)

    async def delete_simulation(
        self, db: AsyncSession, user_id: str, job_id: str
    ) -> None:
        """Delete an HR simulation result."""
        result = await db.execute(
            select(HRSimulation).where(
                HRSimulation.user_id == user_id,
                HRSimulation.job_id == job_id,
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="HR simulation not found")
        await db.delete(record)
        await db.commit()

    @staticmethod
    def _to_response(record: HRSimulation) -> HRResponse:
        from app.schemas.hr import ATSCheck, HRFeedback, ScreeningResult
        return HRResponse(
            id=record.id,
            user_id=record.user_id,
            job_id=record.job_id,
            ats_check=ATSCheck.model_validate(record.ats_check) if record.ats_check else None,
            screening_result=ScreeningResult.model_validate(record.screening_result) if record.screening_result else None,
            hr_feedback=HRFeedback.model_validate(record.hr_feedback) if record.hr_feedback else None,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    @staticmethod
    async def _get_profile(db: AsyncSession, user_id: str) -> UserProfile:
        result = await db.execute(select(UserProfile).where(UserProfile.id == user_id))
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        return profile

    @staticmethod
    async def _get_job(db: AsyncSession, job_id: str) -> JobPost:
        result = await db.execute(select(JobPost).where(JobPost.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=404, detail="Job post not found")
        return job


hr_service = HRService()
