"""File handling utilities."""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path

import aiofiles

UPLOAD_DIR = Path("data/uploads")


def detect_mime(file_path: str) -> str:
    """Detect MIME type of a file by extension."""
    mime, _ = mimetypes.guess_type(file_path)
    return mime or "application/octet-stream"


async def read_file(file_path: str) -> str:
    """Read a text file asynchronously and return its content."""
    async with aiofiles.open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return await f.read()


async def save_upload(file_content: bytes, filename: str) -> str:
    """Save uploaded file content to the uploads directory and return the path."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    # Avoid collisions by prefixing with a short hash
    import uuid
    safe_name = f"{uuid.uuid4().hex[:8]}_{filename}"
    dest = UPLOAD_DIR / safe_name
    async with aiofiles.open(dest, "wb") as f:
        await f.write(file_content)
    return str(dest)
