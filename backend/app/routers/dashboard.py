"""Dashboard router - application tracking board and statistics."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from app.schemas.common import ApiResponse
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationUpdate, BoardStats
from app.services.board_service import board_service

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

DEFAULT_USER_ID = "default"


@router.post("/applications", response_model=ApiResponse)
async def create_application(
    data: ApplicationCreate,
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new application entry."""
    result = await board_service.create_application(db, user_id, data)
    return ApiResponse(data=result.model_dump())


@router.get("/applications", response_model=ApiResponse)
async def list_applications(
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """List all applications for a user."""
    results = await board_service.get_applications(db, user_id)
    return ApiResponse(data=[r.model_dump() for r in results])


@router.get("/applications/{app_id}", response_model=ApiResponse)
async def get_application(
    app_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get a single application by ID."""
    result = await board_service.get_application(db, app_id)
    return ApiResponse(data=result.model_dump())


@router.put("/applications/{app_id}", response_model=ApiResponse)
async def update_application(
    app_id: str,
    data: ApplicationUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Update an application (with status transition validation)."""
    result = await board_service.update_application(db, app_id, data)
    return ApiResponse(data=result.model_dump())


@router.delete("/applications/{app_id}")
async def delete_application(
    app_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Delete an application."""
    await board_service.delete_application(db, app_id)
    return ApiResponse(message="deleted")


@router.get("/stats", response_model=ApiResponse)
async def get_stats(
    user_id: str = Query(default=DEFAULT_USER_ID),
    db: AsyncSession = Depends(get_db_session),
):
    """Get dashboard statistics."""
    result = await board_service.get_stats(db, user_id)
    return ApiResponse(data=result.model_dump())
