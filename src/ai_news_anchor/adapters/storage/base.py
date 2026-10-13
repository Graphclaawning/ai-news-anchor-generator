"""Storage adapter protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class StorageAdapter(Protocol):
    """Write run artifacts to somewhere. Returns the path written to."""

    async def write_text(self, relative_path: str, content: str) -> str: ...

    async def write_bytes(self, relative_path: str, content: bytes) -> str: ...