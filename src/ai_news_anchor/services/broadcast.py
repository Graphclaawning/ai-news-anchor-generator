"""Orchestrates ingest -> segment -> personalize -> write -> synthesize.

This is the only service that talks to more than one other service. It owns
the ordering and the error policy for the full pipeline.
"""

from __future__ import annotations

import logging
from pathlib import Path

from ai_news_anchor.adapters.storage.base import StorageAdapter
from ai_news_anchor.adapters.tts.base import TtsAdapter
from ai_news_anchor.config.personas import load_persona
from ai_news_anchor.config.settings import Settings
from ai_news_anchor.models.broadcast import BroadcastRequest, BroadcastResult
from ai_news_anchor.services.personalizer import PersonalizerService
from ai_news_anchor.services.script_writer import ScriptWriterService
from ai_news_anchor.services.segmenter import SegmenterService
from ai_news_anchor.services.source_ingest import SourceIngestService

log = logging.getLogger(__name__)


class BroadcastService:
    """Runs the full pipeline for a single request."""

    def __init__(
        self,
        *,
        ingest: SourceIngestService,
        segmenter: SegmenterService,
        writer: ScriptWriterService,
        personalizer: PersonalizerService,
        tts: TtsAdapter,
        storage: StorageAdapter,
    ) -> None:
        self._ingest = ingest
        self._segmenter = segmenter
        self._writer = writer
        self._personalizer = personalizer
        self._tts = tts
        self._storage = storage

    async def run(self, request: BroadcastRequest) -> BroadcastResult:
        """Run the pipeline. Raises RuntimeError if no articles were ingested."""
        persona = load_persona(request.persona)
        articles = await self._ingest.fetch(request.feed_urls)
        if not articles:
            raise RuntimeError("no articles ingested from any feed")
        log.info("ingested %d article(s) from %d feed(s)", len(articles), len(request.feed_urls))

        rundown = self._segmenter.build_rundown(articles, request.interest_tags)
        rundown = self._personalizer.apply(rundown, request.interest_tags)
        script = await self._writer.write(rundown, persona)

        audio = await self._tts.synthesize(script, voice=persona.voice_profile)
        run_id = _run_id(request)
        script_path = await self._storage.write_text(f"{run_id}/script.txt", script)
        audio_path = await self._storage.write_bytes(f"{run_id}/anchor.wav", audio)

        return BroadcastResult(
            script_path=Path(script_path),
            audio_path=Path(audio_path),
            duration_s=self._tts.estimate_duration_s(script),
            segment_count=len(rundown),
        )


def _run_id(request: BroadcastRequest) -> str:
    seed = request.persona + "|" + "|".join(request.feed_urls)
    return f"run-{abs(hash(seed)) % 10**10:010d}"