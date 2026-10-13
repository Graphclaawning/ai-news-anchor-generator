"""Bias the rundown toward a viewer's stated interests.

Personalization is a re-ranking pass. It does not touch the article text —
only the order and weight of segments the writer sees.
"""

from __future__ import annotations

from ai_news_anchor.config.settings import Settings
from ai_news_anchor.models.segment import Segment
from ai_news_anchor.utils.text import tokenize


class PersonalizerService:
    """Re-ranks segments by viewer profile."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def apply(self, segments: list[Segment], interest_tags: tuple[str, ...]) -> list[Segment]:
        """Return segments re-ordered for the viewer, indices reassigned."""
        if not interest_tags:
            return segments
        tags = {t.lower() for t in interest_tags}
        ranked = sorted(segments, key=lambda s: self._affinity(s, tags), reverse=True)
        return [seg.model_copy(update={"index": i}) for i, seg in enumerate(ranked)]

    def _affinity(self, segment: Segment, tags: set[str]) -> float:
        text = " ".join(
            [segment.lead.title, segment.lead.summary]
            + [a.title for a in segment.supporting]
        ).lower()
        tokens = set(tokenize(text))
        return len(tags & tokens) / max(1, len(tags))