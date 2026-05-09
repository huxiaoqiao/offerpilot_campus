"""Job posts router - CRUD and batch import for JDs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.job import JobCreate, JobBatchImport, JobResponse
from app.services.job_service import job_service
from app.utils.file_utils import save_upload

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.post("", response_model=ApiResponse[JobResponse])
async def create_job(
    body: JobCreate,
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db_session),
):
    """Import a single JD and parse it."""
    job = await job_service.create_job(db, user_id, body)
    return ApiResponse(data=JobResponse.model_validate(job))


@router.post("/batch", response_model=ApiResponse[list[JobResponse]])
async def batch_import_jobs(
    body: JobBatchImport,
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db_session),
):
    """Batch import multiple JDs."""
    jobs = await job_service.create_jobs_batch(db, user_id, body.jobs)
    return ApiResponse(data=[JobResponse.model_validate(j) for j in jobs])


@router.post("/import-csv", response_model=ApiResponse[list[JobResponse]])
async def import_csv(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
):
    """Import jobs from a CSV file.

    Expected columns: company_name, position_title, jd_raw_text, source_url (optional)
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    content = await file.read()
    file_path = await save_upload(content, file.filename)

    try:
        jobs = await job_service.import_csv(db, user_id, file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV import failed: {e}")

    return ApiResponse(data=[JobResponse.model_validate(j) for j in jobs])


@router.get("", response_model=PaginatedResponse[JobResponse])
async def list_jobs(
    user_id: str = Query(..., description="User ID"),
    sort_by: str = Query("created_at", description="Sort field"),
    order: str = Query("desc", description="Sort order: asc or desc"),
    city: str | None = Query(None, description="Filter by city"),
    industry: str | None = Query(None, description="Filter by industry"),
    min_score: float | None = Query(None, description="Minimum quality score"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    """Get paginated job list with filters."""
    return await job_service.get_jobs(
        db, user_id,
        sort_by=sort_by,
        order=order,
        city=city,
        industry=industry,
        min_score=min_score,
        page=page,
        page_size=page_size,
    )


@router.get("/{job_id}", response_model=ApiResponse[JobResponse])
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get a job post by ID."""
    job = await job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return ApiResponse(data=JobResponse.model_validate(job))


@router.delete("/{job_id}", response_model=ApiResponse)
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a job post."""
    try:
        await job_service.delete_job(db, job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ApiResponse(message="deleted")


@router.post("/{job_id}/reparse", response_model=ApiResponse[JobResponse])
async def reparse_job(
    job_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Re-parse the raw JD text using LLM."""
    try:
        job = await job_service.reparse_job(db, job_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ApiResponse(data=JobResponse.model_validate(job))
