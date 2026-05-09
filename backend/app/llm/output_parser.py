"""Output parsing and validation helpers for LLM responses."""

from __future__ import annotations

import json
import re
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def parse_json_output(text: str) -> dict:
    """Extract a JSON object from LLM output text.

    Handles:
    - Raw JSON strings
    - Markdown code blocks (```json ... ```)
    - Text with embedded JSON objects
    """
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    code_block_match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if code_block_match:
        inner = code_block_match.group(1).strip()
        try:
            return json.loads(inner)
        except json.JSONDecodeError:
            pass

    # Try finding the first { ... } block
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract valid JSON from LLM output: {text[:200]}...")


def validate_schema(data: dict, schema_class: Type[T]) -> T:
    """Validate parsed JSON data against a Pydantic schema.

    Returns the validated model instance, or raises ValueError with details
    suitable for retry prompt adjustment.
    """
    try:
        return schema_class.model_validate(data)
    except ValidationError as e:
        errors = e.errors()
        error_summary = "; ".join(
            f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
            for err in errors
        )
        raise ValueError(
            f"Schema validation failed for {schema_class.__name__}: {error_summary}"
        ) from e
