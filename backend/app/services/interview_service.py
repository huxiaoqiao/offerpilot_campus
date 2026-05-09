"""InterviewService - interview question generation with LLM."""

from __future__ import annotations

import json
import logging

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.client import llm_client
from app.models.interview import InterviewSet
from app.models.job import JobPost
from app.models.match import MatchResult
from app.models.profile import UserProfile
from app.prompts.interview_gen import build_interview_messages
from app.schemas.interview import InterviewResponse
from app.utils.id_utils import gen_id

logger = logging.getLogger(__name__)


class InterviewService:
    """Async service for interview question generation."""

    async def generate_interview(
        self, db: AsyncSession, user_id: str, job_id: str
    ) -> InterviewResponse:
        """Generate interview preparation materials and persist them."""
        profile = await self._get_profile(db, user_id)
        job = await self._get_job(db, job_id)

        resume_text = profile.resume_raw_text or ""
        jd_text = job.jd_raw_text or ""

        if not resume_text:
            raise HTTPException(status_code=400, detail="User has no resume text")
        if not jd_text:
            raise HTTPException(status_code=400, detail="Job has no JD text")

        # Try to get existing match result as context
        match_summary = "暂无匹配分析"
        match_result = await db.execute(
            select(MatchResult).where(
                MatchResult.user_id == user_id,
                MatchResult.job_id == job_id,
            )
        )
        match_record = match_result.scalar_one_or_none()
        if match_record:
            parts = []
            if match_record.total_score is not None:
                parts.append(f"总分: {match_record.total_score}")
            if match_record.opportunity_level:
                parts.append(f"推荐等级: {match_record.opportunity_level}")
            if match_record.gaps:
                gap_items = [g.get("item", "") for g in match_record.gaps if isinstance(g, dict)]
                if gap_items:
                    parts.append(f"主要缺口: {', '.join(gap_items)}")
            if parts:
                match_summary = "; ".join(parts)

        messages = build_interview_messages(resume_text, jd_text, match_summary)
        result = await llm_client.chat_structured(messages, InterviewResponse)

        record = InterviewSet(
            id=gen_id(),
            user_id=user_id,
            job_id=job_id,
            questions=[q.model_dump() for q in (result.questions or [])],
            star_stories=[s.model_dump() for s in (result.star_stories or [])],
            risk_followups=[r.model_dump() for r in (result.risk_followups or [])],
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)

        return InterviewResponse(
            id=record.id,
            user_id=record.user_id,
            job_id=record.job_id,
            questions=result.questions,
            star_stories=result.star_stories,
            risk_followups=result.risk_followups,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    async def get_interview(
        self, db: AsyncSession, user_id: str, job_id: str
    ) -> InterviewResponse:
        """Retrieve an existing interview set."""
        result = await db.execute(
            select(InterviewSet).where(
                InterviewSet.user_id == user_id,
                InterviewSet.job_id == job_id,
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="Interview set not found")
        return self._to_response(record)

    async def delete_interview(
        self, db: AsyncSession, user_id: str, job_id: str
    ) -> None:
        """Delete an interview set."""
        result = await db.execute(
            select(InterviewSet).where(
                InterviewSet.user_id == user_id,
                InterviewSet.job_id == job_id,
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="Interview set not found")
        await db.delete(record)
        await db.commit()

    @staticmethod
    def _to_response(record: InterviewSet) -> InterviewResponse:
        from app.schemas.interview import InterviewQuestion, RiskFollowup, STARStory
        questions = [InterviewQuestion.model_validate(q) for q in (record.questions or [])]
        star_stories = [STARStory.model_validate(s) for s in (record.star_stories or [])]
        risk_followups = [RiskFollowup.model_validate(r) for r in (record.risk_followups or [])]
        return InterviewResponse(
            id=record.id,
            user_id=record.user_id,
            job_id=record.job_id,
            questions=questions,
            star_stories=star_stories,
            risk_followups=risk_followups,
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


interview_service = InterviewService()
