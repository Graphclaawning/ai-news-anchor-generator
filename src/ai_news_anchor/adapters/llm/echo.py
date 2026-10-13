"""Deterministic LLM adapter. Used in tests and offline demos.

Echoes the rundown back with a fixed anchor framing so the rest of the
pipeline can be exercised without a network call or a GPU.
"""

from __future__ import annotations


class EchoAdapter:
    """A no-op LLM. Returns a stub script derived from the prompt."""

    async def complete(self, *, system: str, user: str, max_tokens: int) -> str:
        headlines = [
            line.split("</article>")[0]
            for line in user.splitlines()
            if line.startswith("<article>")
        ][:6]
        body = "\n\n".join(f"Coming up: {h}." for h in headlines)
        return f"Good evening. Here is your personalized rundown.\n\n{body}\n\nThat's the news."