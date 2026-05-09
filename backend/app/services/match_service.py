"""MatchService - job-candidate matching analysis with LLM."""

from __future__ import annotations

import json
import logging

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.client import llm_client
from app.models.job import JobPost
from app.models.match import MatchResult
from app.models.profile import UserProfile
from app.prompts.match_score import build_match_messages
from app.schemas.match import MatchResponse
from app.utils.id_utils import gen_id

logger = logging.getLogger(__name__)


class MatchService:
    """Async service for job-candidate match scoring."""

    async def calculate_match(
        self, db: AsyncSession, user_id: str, job_id: str
    ) -> MatchResponse:
        """Run LLM match scoring and persist the result."""
        profile = await self._get_profile(db, user_id)
        job = await self._get_job(db, job_id)

        resume_text = profile.resume_raw_text or ""
        jd_text = job.jd_raw_text or ""

        if not resume_text:
            raise HTTPException(status_code=400, detail="User has no resume text")
        if not jd_text:
            raise HTTPException(status_code=400, detail="Job has no JD text")

        messages = build_match_messages(resume_text, jd_text)
        raw_text = await llm_client.chat(messages, max_tokens=4000)
        from app.llm.output_parser import parse_json_output, validate_schema
        data = parse_json_output(raw_text)
        result = validate_schema(data, MatchResponse)
        
        # Persist to DB - convert dimension_scores Pydantic objects to dicts
        dim_scores_dict = None
        if result.dimension_scores:
            dim_scores_dict = {k: v.model_dump() for k, v in result.dimension_scores.items()}
        
        match_record = MatchResult(
            id=gen_id(),
            user_id=user_id,
            job_id=job_id,
            total_score=result.total_score,
            opportunity_level=result.opportunity_level,
            dimension_scores=dim_scores_dict,
            matched_evidence=[e.model_dump() for e in (result.matched_evidence or [])],
            gaps=[g.model_dump() for g in (result.gaps or [])],
            risks=[r.model_dump() for r in (result.risks or [])],
            improvement_actions=result.improvement_actions,
        )
        db.add(match_record)
        await db.commit()
        await db.refresh(match_record)

        return MatchResponse.model_validate(match_record)

    async def get_match(
        self, db: AsyncSession, user_id: str, job_id: str
    ) -> MatchResponse:
        """Retrieve an existing match result."""
        result = await db.execute(
            select(MatchResult).where(
                MatchResult.user_id == user_id,
                MatchResult.job_id == job_id,
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="Match result not found")
        return MatchResponse.model_validate(record)

    async def compare_matches(
        self, db: AsyncSession, user_id: str, job_ids: list[str]
    ) -> list[MatchResponse]:
        """Compare match results across multiple jobs."""
        results = []
        for job_id in job_ids:
            try:
                match = await self.get_match(db, user_id, job_id)
                results.append(match)
            except HTTPException:
                continue
        return results

    async def delete_match(
        self, db: AsyncSession, user_id: str, job_id: str
    ) -> None:
        """Delete a match result."""
        result = await db.execute(
            select(MatchResult).where(
                MatchResult.user_id == user_id,
                MatchResult.job_id == job_id,
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="Match result not found")
        await db.delete(record)
        await db.commit()

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


match_service = MatchService()
