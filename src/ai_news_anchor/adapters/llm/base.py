"""LLM adapter protocol. Anything that can complete a prompt fits."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LlmAdapter(Protocol):
    """Minimal text-completion contract used by the script writer."""

    async def complete(self, *, system: str, user: str, max_tokens: int) -> str:
        """Return a completion. Must raise LlmError on transport failure."""
        ...


class LlmError(RuntimeError):
    """Raised when the underlying completion backend fails."""