"""Local filesystem storage adapter.

Paths are joined under a fixed root and rejected if they escape it. This is
the only module that should ever call `Path.open` for run artifacts.
"""

from __future__ import annotations

import asyncio
from pathlib import Path


class LocalStorageAdapter:
    """Writes run artifacts under a root directory."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    async def write_text(self, relative_path: str, content: str) -> str:
        target = self._resolve(relative_path)
        await asyncio.to_thread(target.write_text, content, encoding="utf-8")
        return str(target)

    async def write_bytes(self, relative_path: str, content: bytes) -> str:
        target = self._resolve(relative_path)
        await asyncio.to_thread(target.write_bytes, content)
        return str(target)

    def _resolve(self, relative_path: str) -> Path:
        candidate = (self._root / relative_path).resolve()
        if self._root not in candidate.parents:
            raise ValueError(f"path escapes storage root: {relative_path!r}")
        candidate.parent.mkdir(parent