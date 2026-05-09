"""BoardService - application tracking kanban board with status management."""

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application
from app.models.match import MatchResult
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
    BoardStats,
    TimelineEntry,
)
from app.utils.id_utils import gen_id

logger = logging.getLogger(__name__)

VALID_STATUS_TRANSITIONS: dict[str, list[str]] = {
    "待评估": ["已评估", "放弃"],
    "已评估": ["准备中", "放弃"],
    "准备中": ["已投递", "放弃"],
    "已投递": ["面试中", "已拒绝", "放弃"],
    "面试中": ["已offer", "已拒绝", "放弃"],
}


class BoardService:
    """Async service for application lifecycle management."""

    async def create_application(
        self, db: AsyncSession, user_id: str, data: ApplicationCreate
    ) -> ApplicationResponse:
        """Create a new application entry."""
        # Try to pull match_score if available
        match_score = data.match_score
        if match_score is None:
            match_result = await db.execute(
                select(MatchResult).where(
                    MatchResult.user_id == user_id,
                    MatchResult.job_id == data.job_id,
                )
            )
            match_record = match_result.scalar_one_or_none()
            if match_record and match_record.total_score is not None:
                match_score = match_record.total_score

        now = datetime.utcnow()
        timeline_data = None
        if data.timeline:
            timeline_data = [t.model_dump() for t in data.timeline]
        else:
            timeline_data = [{"date": now.strftime("%Y-%m-%d"), "action": "创建", "detail": "新建投递记录"}]

        app_record = Application(
            id=gen_id(),
            user_id=user_id,
            job_id=data.job_id,
            status=data.status,
            match_score=match_score,
            resume_version_id=data.resume_version_id,
            next_action=data.next_action,
            next_action_deadline=data.next_action_deadline,
            notes=data.notes,
            tags=data.tags,
            timeline=timeline_data,
        )
        db.add(app_record)
        await db.commit()
        await db.refresh(app_record)
        return ApplicationResponse.model_validate(app_record)

    async def get_applications(
        self, db: AsyncSession, user_id: str
    ) -> list[ApplicationResponse]:
        """Get all applications for a user."""
        result = await db.execute(
            select(Application)
            .where(Application.user_id == user_id)
            .order_by(Application.created_at.desc())
        )
        records = result.scalars().all()
        return [ApplicationResponse.model_validate(r) for r in records]

    async def get_application(
        self, db: AsyncSession, app_id: str
    ) -> ApplicationResponse:
        """Get a single application by ID."""
        result = await db.execute(
            select(Application).where(Application.id == app_id)
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="Application not found")
        return ApplicationResponse.model_validate(record)

    async def update_application(
        self, db: AsyncSession, app_id: str, data: ApplicationUpdate
    ) -> ApplicationResponse:
        """Update an application with status transition validation."""
        result = await db.execute(
            select(Application).where(Application.id == app_id)
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="Application not found")

        # Validate status transition
        if data.status is not None and data.status != record.status:
            allowed = VALID_STATUS_TRANSITIONS.get(record.status, [])
            if data.status not in allowed:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status transition: '{record.status}' -> '{data.status}'. "
                           f"Allowed: {allowed}",
                )
            # Append to timeline
            current_timeline = record.timeline or []
            current_timeline.append({
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "action": f"状态变更: {record.status} -> {data.status}",
                "detail": f"从{record.status}变更为{data.status}",
            })
            record.timeline = current_timeline
            record.status = data.status

        update_fields = [
            "match_score", "resume_version_id", "next_action",
            "next_action_deadline", "notes", "tags",
        ]
        for field in update_fields:
            val = getattr(data, field, None)
            if val is not None:
                setattr(record, field, val)

        await db.commit()
        await db.refresh(record)
        return ApplicationResponse.model_validate(record)

    async def delete_application(self, db: AsyncSession, app_id: str) -> None:
        """Delete an application."""
        result = await db.execute(
            select(Application).where(Application.id == app_id)
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="Application not found")
        await db.delete(record)
        await db.commit()

    async def get_stats(
        self, db: AsyncSession, user_id: str
    ) -> BoardStats:
        """Get dashboard statistics for a user."""
        result = await db.execute(
            select(Application).where(Application.user_id == user_id)
        )
        records = result.scalars().all()

        total = len(records)
        by_status: dict[str, int] = {}
        upcoming: list[ApplicationResponse] = []

        now = datetime.utcnow()
        for r in records:
            by_status[r.status] = by_status.get(r.status, 0) + 1
            if r.next_action_deadline and r.next_action_deadline >= now:
                upcoming.append(ApplicationResponse.model_validate(r))

        # Sort upcoming by deadline
        upcoming.sort(key=lambda x: x.next_action_deadline or datetime.max)

        return BoardStats(
            total=total,
            by_status=by_status,
            upcoming_deadlines=upcoming,
        )


board_service = BoardService()
