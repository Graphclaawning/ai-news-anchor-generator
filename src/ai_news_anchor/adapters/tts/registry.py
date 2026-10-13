"""Resolve the configured TTS backend to a concrete adapter."""

from __future__ import annotations

from ai_news_anchor.adapters.tts.base import TtsAdapter
from ai_news_anchor.config.settings import TtsSettings


def build_tts_adapter(settings: TtsSettings) -> TtsAdapter:
    """Return the adapter named by settings.backend."""
    backend = settings.backend
    if backend == "piper":
        from ai_news_anchor.adapters.tts.piper_adapter import PiperAdapter

        return PiperAdapter(voices_dir=settings.voices_dir)
    if backend == "azure":
        from ai_news_anchor.adapters.tts.azure_adapter import AzureTtsAdapter

        return AzureTtsAdapter(region=settings.region, api_key_env=settings.api_key_env)
    if backend == "silent":
        from ai_news_anchor.adapters.tts.silent import SilentAdapter

        return SilentAdapter()
    raise ValueError(f"unknown tts backend: {backend!r}")