"""JD parser - converts raw JD text into structured job data."""

from __future__ import annotations

import logging

from app.llm.client import llm_client
from app.prompts.jd_extract import build_jd_extract_messages
from app.schemas.job import JDExtractedData
from app.utils.text_utils import clean_text, truncate_text

logger = logging.getLogger(__name__)


class JDParser:
    """Parse job descriptions into JDExtractedData objects."""

    async def parse_jd(self, jd_text: str) -> JDExtractedData:
        """Parse a single JD text into structured data via LLM."""
        cleaned = truncate_text(clean_text(jd_text), max_len=12000)
        if not cleaned:
            return JDExtractedData()

        messages = build_jd_extract_messages(cleaned)
        try:
            result = await llm_client.chat_structured(messages, JDExtractedData)
            return result
        except Exception as e:
            logger.error("LLM JD extraction failed: %s", e)
            return JDExtractedData()

    async def parse_jd_batch(self, jd_texts: list[str]) -> list[JDExtractedData]:
        """Parse multiple JDs sequentially."""
        results = []
        for text in jd_texts:
            result = await self.parse_jd(text)
            results.append(result)
        return results


# Module-level singleton
jd_parser = JDParser()
