"""HR simulator router - ATS check and HR screening simulation."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from app.schemas.hr import HRResponse
from app.services.hr_service import hr_service

router = APIRouter(prefix="/api/hr", tags=["HR Simulator"])

DEFAULT_USER_ID = "default"


@router.post("/{job_id}", response_model=HRResponse)
async def run_hr_simulation(
    job_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Run HR/ATS simulation for a job."""
    return await hr_service.simulate_hr(db, user_id, job_id)


@router.get("/{job_id}", response_model=HRResponse)
async def get_hr_result(
    job_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Get an existing HR simulation result."""
    return await hr_service.get_simulation(db, user_id, job_id)


@router.delete("/{job_id}")
async def delete_hr_result(
    job_id: str,
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete an HR simulation result."""
    await hr_service.delete_simulation(db, user_id, job_id)
    return {"detail": "HR simulation deleted"}
