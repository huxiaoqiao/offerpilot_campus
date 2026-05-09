"""Application configuration loaded from .env and environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- LLM Provider 1: OpenAI Compatible ---
    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # --- LLM Provider 2: Aliyun DashScope ---
    aliyun_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    aliyun_api_key: str = ""
    aliyun_model: str = "qwen-plus"

    # --- LLM Provider 3: Ollama Local ---
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "qwen2.5:7b"

    # --- LLM Provider Priority ---
    llm_provider_priority: str = "openai_compatible,aliyun,ollama"

    # --- App ---
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    database_url: str = "sqlite+aiosqlite:///./data/offerpilot.db"

    # --- Derived helpers ---

    @property
    def provider_priority_list(self) -> list[str]:
        """Return the provider priority as a list of strings."""
        return [p.strip() for p in self.llm_provider_priority.split(",") if p.strip()]

    def get_llm_config(self, provider: str) -> dict:
        """Return connection params for a given provider name."""
        configs = {
            "openai_compatible": {
                "base_url": self.openai_base_url,
                "api_key": self.openai_api_key,
                "model": self.openai_model,
            },
            "aliyun": {
                "base_url": self.aliyun_base_url,
                "api_key": self.aliyun_api_key,
                "model": self.aliyun_model,
            },
            "ollama": {
                "base_url": self.ollama_base_url,
                "api_key": "ollama",
                "model": self.ollama_model,
            },
        }
        return configs.get(provider, {})


settings = Settings()
