"""FastAPI dependency-injection helpers."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session and close it when done."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
