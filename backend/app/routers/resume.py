"""Resume router - AI-powered resume tailoring."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from app.schemas.resume import ResumeRewriteResponse
from app.services.resume_service import resume_service

router = APIRouter(prefix="/api/resume", tags=["Resume"])

DEFAULT_USER_ID = "default"


@router.post("/{job_id}", response_model=ResumeRewriteResponse)
async def rewrite_resume(
    job_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Generate a tailored resume for a specific job."""
    return await resume_service.rewrite_resume(db, user_id, job_id)


@router.get("/{job_id}/versions", response_model=list[ResumeRewriteResponse])
async def get_resume_versions(
    job_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Get all resume versions for a job."""
    return await resume_service.get_resume_versions(db, user_id, job_id)


@router.get("/{job_id}/html", response_class=HTMLResponse)
async def get_resume_html(
    job_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Get HTML preview of the latest resume."""
    html = await resume_service.get_resume_html(db, user_id, job_id)
    return HTMLResponse(content=html)


@router.get("/{job_id}", response_model=ResumeRewriteResponse)
async def get_latest_resume(
    job_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Get the latest resume version for a job."""
    return await resume_service.get_resume(db, user_id, job_id)


@router.delete("/{job_id}")
async def delete_resume(
    job_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete all resume versions for a job."""
    await resume_service.delete_resume(db, user_id, job_id)
    return {"detail": "Resume versions deleted"}
