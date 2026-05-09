"""Resume parser - converts raw files/text into structured resume data."""

from __future__ import annotations

import logging
from pathlib import Path

from app.llm.client import llm_client
from app.prompts.resume_extract import build_resume_extract_messages
from app.schemas.profile import StructuredResume
from app.utils.text_utils import clean_text, truncate_text

logger = logging.getLogger(__name__)


class ResumeParser:
    """Parse resume files and text into StructuredResume objects."""

    async def parse_file(self, file_path: str) -> str:
        """Read a resume file (PDF/DOCX/TXT/Markdown) into plain text using MarkItDown.

        Falls back to raw read if MarkItDown is unavailable or fails.
        """
        try:
            from markitdown import MarkItDown
            md = MarkItDown()
            result = md.convert(file_path)
            text = result.text_content if hasattr(result, "text_content") else str(result)
            if text and text.strip():
                return clean_text(text)
        except Exception as e:
            logger.warning("MarkItDown failed for %s: %s", file_path, e)

        # Fallback: read file as raw text
        try:
            p = Path(file_path)
            return clean_text(p.read_text(encoding="utf-8", errors="replace"))
        except Exception as e:
            logger.error("Failed to read file %s: %s", file_path, e)
            return ""

    async def parse_text(self, text: str) -> StructuredResume:
        """Parse raw resume text into a StructuredResume via LLM extraction."""
        cleaned = truncate_text(clean_text(text), max_len=12000)
        if not cleaned:
            return StructuredResume()

        messages = build_resume_extract_messages(cleaned)
        try:
            result = await llm_client.chat_structured(messages, StructuredResume)
            return result
        except Exception as e:
            logger.error("LLM resume extraction failed: %s", e)
            return StructuredResume()

    async def parse_file_to_structured(self, file_path: str) -> tuple[str, StructuredResume]:
        """Convenience: parse file -> (raw_text, structured_resume)."""
        raw_text = await self.parse_file(file_path)
        structured = await self.parse_text(raw_text) if raw_text else StructuredResume()
        return raw_text, structured


# Module-level singleton
resume_parser = ResumeParser()
