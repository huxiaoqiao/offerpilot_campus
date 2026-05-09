"""ID generation utilities."""

from __future__ import annotations

import uuid


def gen_id() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())
