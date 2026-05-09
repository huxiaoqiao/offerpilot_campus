"""LLM provider configuration and client factory."""

from __future__ import annotations

from dataclasses import dataclass

from openai import AsyncOpenAI

from app.config import settings


@dataclass
class ProviderConfig:
    """Connection parameters for a single LLM provider."""
    name: str
    base_url: str
    api_key: str
    model: str


def _build_provider_list() -> list[ProviderConfig]:
    """Build the full provider list from settings."""
    all_configs: dict[str, dict] = {
        "openai_compatible": settings.get_llm_config("openai_compatible"),
        "aliyun": settings.get_llm_config("aliyun"),
        "ollama": settings.get_llm_config("ollama"),
    }
    providers = []
    for name in settings.provider_priority_list:
        cfg = all_configs.get(name)
        if cfg and cfg.get("api_key"):
            providers.append(ProviderConfig(
                name=name,
                base_url=cfg["base_url"],
                api_key=cfg["api_key"],
                model=cfg["model"],
            ))
    return providers


# Module-level cache; rebuilt once at import time.
_PROVIDER_LIST: list[ProviderConfig] = _build_provider_list()
_CLIENT_CACHE: dict[str, AsyncOpenAI] = {}


def get_provider_list() -> list[ProviderConfig]:
    """Return the ordered list of configured providers."""
    return _PROVIDER_LIST


def get_client(provider_name: str) -> AsyncOpenAI:
    """Return (or create and cache) an AsyncOpenAI client for the given provider."""
    if provider_name in _CLIENT_CACHE:
        return _CLIENT_CACHE[provider_name]

    cfg = settings.get_llm_config(provider_name)
    if not cfg:
        raise ValueError(f"Unknown LLM provider: {provider_name}")

    client = AsyncOpenAI(
        base_url=cfg["base_url"],
        api_key=cfg["api_key"],
    )
    _CLIENT_CACHE[provider_name] = client
    return client


def get_default_model(provider_name: str) -> str:
    """Return the default model name for a provider."""
    cfg = settings.get_llm_config(provider_name)
    return cfg.get("model", "") if cfg else ""
