"""Composition root. Wires adapters into services. One place, no globals."""

from __future__ import annotations

from dataclasses import dataclass

from ai_news_anchor.adapters.llm.base import LlmAdapter
from ai_news_anchor.adapters.llm.registry import build_llm_adapter
from ai_news_anchor.adapters.storage.base import StorageAdapter
from ai_news_anchor.adapters.storage.local import LocalStorageAdapter
from ai_news_anchor.adapters.tts.base import TtsAdapter
from ai_news_anchor.adapters.tts.registry import build_tts_adapter
from ai_news_anchor.config.settings import Settings
from ai_news_anchor.services.broadcast import BroadcastService
from ai_news_anchor.services.personalizer import PersonalizerService
from ai_news_anchor.services.script_writer import ScriptWriterService
from ai_news_anchor.services.segmenter import SegmenterService
from ai_news_anchor.services.source_ingest import SourceIngestService


@dataclass(slots=True)
class Container:
    """Holds fully-constructed, ready-to-use services.

    Construction order is dependency order: adapters -> leaf services ->
    orchestrating services. Nothing in here touches the network or disk
    until a service method is actually called.
    """

    settings: Settings
    storage: StorageAdapter
    llm: LlmAdapter
    tts: TtsAdapter
    ingest: SourceIngestService
    segmenter: SegmenterService
    writer: ScriptWriterService
    personalizer: PersonalizerService
    broadcast: BroadcastService


def build_container(settings: Settings | None = None) -> Container:
    """Build the service graph. Idempotent; safe to call once per process."""
    settings = settings or Settings()
    storage = LocalStorageAdapter(root=settings.output_dir)
    llm = build_llm_adapter(settings.llm)
    tts = build_tts_adapter(settings.tts)

    ingest = SourceIngestService(settings=settings)
    segmenter = SegmenterService(settings=settings)
    writer = ScriptWriterService(llm=llm, settings=settings)
    personalizer = PersonalizerService(settings=settings)
    broadcast = BroadcastService(
        ingest=ingest,
        segmenter=segmenter,
        writer=writer,
        personalizer=personalizer,
        tts=tts,
        storage=storage,
    )
    return Container(
        settings=settings,
        storage=storage,
        llm=llm,
        tts=tts,
        ingest=ingest,
        segmenter=segmenter,
        writer=writer,
        personalizer=personalizer,
        broadcast=broadcast,
    )