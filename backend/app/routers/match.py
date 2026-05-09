"""Match router - job-candidate matching analysis."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from app.schemas.match import MatchResponse
from app.services.match_service import match_service

router = APIRouter(prefix="/api/match", tags=["Match"])

DEFAULT_USER_ID = "default"


@router.post("/{job_id}", response_model=MatchResponse)
async def run_match(
    job_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Run LLM-powered match scoring for a job."""
    return await match_service.calculate_match(db, user_id, job_id)


@router.get("/compare", response_model=list[MatchResponse])
async def compare_matches(
    job_ids: str = Query(..., description="Comma-separated job IDs"),
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Compare match results across multiple jobs."""
    ids = [jid.strip() for jid in job_ids.split(",") if jid.strip()]
    return await match_service.compare_matches(db, user_id, ids)


@router.get("/{job_id}", response_model=MatchResponse)
async def get_match_result(
    job_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Get an existing match result."""
    return await match_service.get_match(db, user_id, job_id)


@router.delete("/{job_id}")
async def delete_match(
    job_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a match result."""
    await match_service.delete_match(db, user_id, job_id)
    return {"detail": "Match result deleted"}
