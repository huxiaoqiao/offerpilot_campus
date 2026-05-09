"""Common Pydantic response wrappers."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API envelope for every response."""
    code: int = Field(default=0, description="0 = success, non-zero = error")
    message: str = "ok"
    data: T | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list wrapper."""
    code: int = 0
    message: str = "ok"
    data: list[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20


class ErrorResponse(BaseModel):
    """Error-only response."""
    code: int
    message: str
    detail: Any | None = None
