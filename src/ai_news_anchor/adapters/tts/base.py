"""TTS adapter protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class TtsAdapter(Protocol):
    """Synthesize text to a WAV byte string."""

    async def synthesize(self, text: str, *, voice: str) -> bytes:
        """Return WAV bytes. Must raise TtsError on failure."""
        ...

    def estimate_duration_s(self, text: str) -> float:
        """Return an estimated duration in seconds."""
        ...


class TtsError(RuntimeError):
    """Raised when a TTS backend fails to render."""