"""Unified LLM client with provider priority rotation and retry logic."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any, Type, TypeVar

from pydantic import BaseModel

from app.llm.output_parser import parse_json_output, validate_schema
from app.llm.providers import get_client, get_default_model, get_provider_list

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

MAX_RETRIES_PER_PROVIDER = 3


class LLMClient:
    """Multi-provider LLM client with automatic failover.

    Tries providers in the order specified by config.LLM_PROVIDER_PRIORITY.
    Each provider is attempted up to MAX_RETRIES_PER_PROVIDER times before
    falling back to the next provider.
    """

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> str | AsyncGenerator[str, None]:
        """Send a chat completion request.

        When *stream* is True returns an async generator that yields text chunks.
        Otherwise returns the complete response text.
        """
        providers = get_provider_list()
        if not providers:
            raise RuntimeError("No LLM providers configured. Check your .env file.")

        last_error: Exception | None = None
        for provider_cfg in providers:
            client = get_client(provider_cfg.name)
            use_model = model or provider_cfg.model
            for attempt in range(1, MAX_RETRIES_PER_PROVIDER + 1):
                try:
                    logger.info(
                        "LLM chat: provider=%s model=%s attempt=%d stream=%s",
                        provider_cfg.name, use_model, attempt, stream,
                    )
                    if stream:
                        return self._stream_response(client, messages, use_model, **kwargs)
                    response = await client.chat.completions.create(
                        model=use_model,
                        messages=messages,
                        **kwargs,
                    )
                    return response.choices[0].message.content or ""
                except Exception as exc:
                    last_error = exc
                    logger.warning(
                        "LLM chat failed (provider=%s attempt=%d): %s",
                        provider_cfg.name, attempt, exc,
                    )

        raise RuntimeError(
            f"All LLM providers exhausted. Last error: {last_error}"
        )

    async def chat_structured(
        self,
        messages: list[dict[str, str]],
        schema_class: Type[T],
        model: str | None = None,
        **kwargs: Any,
    ) -> T:
        """Send a chat request and parse the response into a Pydantic model.

        Strategy:
        1. Try json_schema response_format.
        2. On failure, fall back to plain text + function calling style prompt.
        """
        providers = get_provider_list()
        if not providers:
            raise RuntimeError("No LLM providers configured. Check your .env file.")

        last_error: Exception | None = None
        for provider_cfg in providers:
            client = get_client(provider_cfg.name)
            use_model = model or provider_cfg.model
            for attempt in range(1, MAX_RETRIES_PER_PROVIDER + 1):
                # --- Attempt 1: json_schema mode ---
                try:
                    logger.info(
                        "LLM structured (json_schema): provider=%s model=%s attempt=%d",
                        provider_cfg.name, use_model, attempt,
                    )
                    schema_dict = schema_class.model_json_schema()
                    response = await client.chat.completions.create(
                        model=use_model,
                        messages=messages,
                        response_format={
                            "type": "json_schema",
                            "json_schema": {
                                "name": schema_class.__name__,
                                "schema": schema_dict,
                            },
                        },
                        **kwargs,
                    )
                    raw = response.choices[0].message.content or "{}"
                    data = parse_json_output(raw)
                    return validate_schema(data, schema_class)
                except Exception as exc:
                    logger.debug(
                        "json_schema mode failed (provider=%s attempt=%d): %s",
                        provider_cfg.name, attempt, exc,
                    )
                    last_error = exc

                # --- Attempt 2: function calling fallback ---
                try:
                    logger.info(
                        "LLM structured (function_call): provider=%s model=%s attempt=%d",
                        provider_cfg.name, use_model, attempt,
                    )
                    schema_dict = schema_class.model_json_schema()
                    tool_messages = list(messages) + [{
                        "role": "system",
                        "content": (
                            "You MUST respond with a single valid JSON object that "
                            f"matches this schema:\n{json.dumps(schema_dict, ensure_ascii=False)}\n"
                            "Return ONLY the JSON, no extra text."
                        ),
                    }]
                    response = await client.chat.completions.create(
                        model=use_model,
                        messages=tool_messages,
                        tools=[{
                            "type": "function",
                            "function": {
                                "name": f"output_{schema_class.__name__}",
                                "description": f"Return structured {schema_class.__name__} data",
                                "parameters": schema_dict,
                            },
                        }],
                        tool_choice={"type": "function", "function": {"name": f"output_{schema_class.__name__}"}},
                        **kwargs,
                    )
                    choice = response.choices[0]
                    # Extract from tool_calls
                    if choice.message.tool_calls:
                        args_str = choice.message.tool_calls[0].function.arguments
                        data = json.loads(args_str)
                    else:
                        raw = choice.message.content or "{}"
                        data = parse_json_output(raw)
                    return validate_schema(data, schema_class)
                except Exception as exc:
                    last_error = exc
                    logger.warning(
                        "function_call fallback failed (provider=%s attempt=%d): %s",
                        provider_cfg.name, attempt, exc,
                    )

        raise RuntimeError(
            f"All LLM providers exhausted for structured output. Last error: {last_error}"
        )

    @staticmethod
    async def _stream_response(
        client: Any,
        messages: list[dict[str, str]],
        model: str,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Yield streamed text chunks from the LLM."""
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            **kwargs,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content


# Module-level singleton
llm_client = LLMClient()
