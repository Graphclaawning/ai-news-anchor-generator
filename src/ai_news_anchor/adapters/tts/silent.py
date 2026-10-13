"""Silent TTS adapter. Emits a valid, empty 16 kHz mono WAV.

Used in CI and for dry runs where you want the pipeline to complete without
pulling a voice model.
"""

from __future__ import annotations

import io
import struct
import wave

_SAMPLE_RATE = 16_000
_WORDS_PER_MINUTE = 155


class SilentAdapter:
    """Renders nothing but a valid WAV container."""

    async def synthesize(self, text: str, *, voice: str) -> bytes:
        duration = self.estimate_duration_s(text)
        frames = int(_SAMPLE_RATE * duration)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(_SAMPLE_RATE)
            wav.writeframes(struct.pack("<h", 0) * frames)
        return buf.getvalue()

    def estimate_duration_s(self, text: str) -> float:
        words = len(text.split())
        return max(1.0, words / _WORDS_PER_MINUTE * 60.0)