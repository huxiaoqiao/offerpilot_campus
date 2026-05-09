"""Interview router - mock interview questions and STAR stories."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from app.schemas.interview import InterviewResponse
from app.services.interview_service import interview_service

router = APIRouter(prefix="/api/interview", tags=["Interview"])

DEFAULT_USER_ID = "default"


@router.post("/{job_id}", response_model=InterviewResponse)
async def generate_interview_set(
    job_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Generate interview preparation materials for a job."""
    return await interview_service.generate_interview(db, user_id, job_id)


@router.get("/{job_id}", response_model=InterviewResponse)
async def get_interview_set(
    job_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Get an existing interview set."""
    return await interview_service.get_interview(db, user_id, job_id)


@router.delete("/{job_id}")
async def delete_interview_set(
    job_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete an interview set."""
    await interview_service.delete_interview(db, user_id, job_id)
    return {"detail": "Interview set deleted"}
