"""Text processing utilities."""

from __future__ import annotations

import re


def clean_text(text: str) -> str:
    """Remove excessive whitespace while preserving single newlines."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def truncate_text(text: str, max_len: int = 8000) -> str:
    """Truncate text to *max_len* characters, appending ellipsis if trimmed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def similarity(a: str, b: str) -> float:
    """Compute a simple bigram-based string similarity score in [0, 1].

    Used for lightweight deduplication of job titles / company names.
    """
    if not a or not b:
        return 0.0
    a_lower = a.lower().strip()
    b_lower = b.lower().strip()
    if a_lower == b_lower:
        return 1.0

    def _bigrams(s: str) -> set[str]:
        return {s[i : i + 2] for i in range(len(s) - 1)}

    a_bigrams = _bigrams(a_lower)
    b_bigrams = _bigrams(b_lower)
    if not a_bigrams or not b_bigrams:
        return 0.0
    intersection = a_bigrams & b_bigrams
    return 2.0 * len(intersection) / (len(a_bigrams) + len(b_bigrams))
