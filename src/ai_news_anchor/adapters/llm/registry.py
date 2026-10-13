"""Resolve the configured LLM backend to a concrete adapter."""

from __future__ import annotations

from ai_news_anchor.adapters.llm.base import LlmAdapter
from ai_news_anchor.config.settings import LlmSettings


def build_llm_adapter(settings: LlmSettings) -> LlmAdapter:
    """Return the adapter named by settings.backend.

    Backends are imported lazily so the base install stays dependency-light.
    """
    backend = settings.backend
    if backend == "openai":
        from ai_news_anchor.adapters.llm.openai_adapter import OpenAiAdapter

        return OpenAiAdapter(model=settings.model, api_key_env=settings.api_key_env)
    if backend == "local":
        from ai_news_anchor.adapters.llm.local_llama import LocalLlamaAdapter

        return LocalLlamaAdapter(model_path=settings.model)
    if backend == "echo":
        from ai_news_anchor.adapters.llm.echo import EchoAdapter

        return EchoAdapter()
    raise ValueError(f"unknown llm backend: {backend!r}")