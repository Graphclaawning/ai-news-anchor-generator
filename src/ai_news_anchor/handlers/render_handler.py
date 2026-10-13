"""HTTP-shaped handler for a render request. No framework, just a function.

The web layer (or a Lambda, or a queue consumer) calls `handle` with a dict
and gets a dict back. Keeps the service boundary honest.
"""

from __future__ import annotations

from typing import Any

from ai_news_anchor.bootstrap.container import Container
from ai_news_anchor.models.broadcast import BroadcastRequest


async def handle(container: Container, payload: dict[str, Any]) -> dict[str, Any]:
    """Handle a render request. Raises pydantic ValidationError on bad input."""
    request = BroadcastRequest.model_validate(payload)
    result = await container.broadcast.run(request)
    return {
        "audio_path": str(result.audio_path),
        "script_path": str(result.script_path),
        "duration_s": result.duration_s,
        "segments": result.segment_count,
    }