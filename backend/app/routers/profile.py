"""User profile router - CRUD operations for user profiles."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from app.schemas.common import ApiResponse
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate, StructuredResume
from app.services.profile_service import profile_service
from app.utils.file_utils import save_upload

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.post("", response_model=ApiResponse[ProfileResponse])
async def create_profile(
    body: ProfileCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new user profile."""
    profile = await profile_service.create_profile(db, body)
    return ApiResponse(data=ProfileResponse.model_validate(profile))


@router.get("/{profile_id}", response_model=ApiResponse[ProfileResponse])
async def get_profile(
    profile_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get a user profile by ID."""
    profile = await profile_service.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")
    return ApiResponse(data=ProfileResponse.model_validate(profile))


@router.put("/{profile_id}", response_model=ApiResponse[ProfileResponse])
async def update_profile(
    profile_id: str,
    body: ProfileUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Update an existing user profile."""
    try:
        profile = await profile_service.update_profile(db, profile_id, body)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ApiResponse(data=ProfileResponse.model_validate(profile))


@router.post("/{profile_id}/resume/upload", response_model=ApiResponse[ProfileResponse])
async def upload_resume(
    profile_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
):
    """Upload a resume file (PDF/DOCX/TXT/MD) and parse it."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    content = await file.read()
    file_path = await save_upload(content, file.filename)

    try:
        raw_text, structured = await profile_service.upload_resume(db, profile_id, file_path)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    profile = await profile_service.get_profile(db, profile_id)
    return ApiResponse(data=ProfileResponse.model_validate(profile))


@router.put("/{profile_id}/resume/structured", response_model=ApiResponse[ProfileResponse])
async def update_structured_resume(
    profile_id: str,
    body: StructuredResume,
    db: AsyncSession = Depends(get_db_session),
):
    """Manually update the structured resume data."""
    try:
        profile = await profile_service.update_structured_resume(db, profile_id, body)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ApiResponse(data=ProfileResponse.model_validate(profile))


@router.put("/{profile_id}/skill-ratings", response_model=ApiResponse[ProfileResponse])
async def update_skill_ratings(
    profile_id: str,
    ratings: dict[str, float],
    db: AsyncSession = Depends(get_db_session),
):
    """Update skill self-assessment ratings."""
    try:
        profile = await profile_service.update_skill_ratings(db, profile_id, ratings)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ApiResponse(data=ProfileResponse.model_validate(profile))


@router.post("/{profile_id}/resume/reparse", response_model=ApiResponse[ProfileResponse])
async def reparse_resume(
    profile_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Re-parse the existing raw resume text using LLM."""
    try:
        structured = await profile_service.reparse_resume(db, profile_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    profile = await profile_service.get_profile(db, profile_id)
    return ApiResponse(data=ProfileResponse.model_validate(profile))
