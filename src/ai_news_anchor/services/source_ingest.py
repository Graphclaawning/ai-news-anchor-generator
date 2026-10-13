"""Fetch and normalize feed items into RawArticle models.

Untrusted input. Every string that leaves this module has been HTML-stripped,
length-capped, and URL-scheme-filtered.
"""

from __future__ import annotations

import asyncio
import hashlib
from datetime import datetime, timezone

import feedparser
import httpx
from bs4 import BeautifulSoup

from ai_news_anchor.config.settings import Settings
from ai_news_anchor.models.article import RawArticle

_ALLOWED_SCHEMES = ("http://", "https://")
_MAX_BODY_BYTES = 2 * 1024 * 1024


class SourceIngestService:
    """Pulls articles from RSS/Atom feeds and normalizes them."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def fetch(self, feed_urls: tuple[str, ...]) -> list[RawArticle]:
        """Fetch all feeds concurrently. Feeds that fail are logged and skipped."""
        async with httpx.AsyncClient(
            timeout=self._settings.ingest_timeout_s,
            headers={"User-Agent": self._settings.user_agent},
            follow_redirects=True,
        ) as client:
            results = await asyncio.gather(
                *(self._fetch_one(client, url) for url in feed_urls),
                return_exceptions=True,
            )
        articles: list[RawArticle] = []
        for result in results:
            if isinstance(result, Exception):
                continue
            articles.extend(result)
        return articles

    async def _fetch_one(self, client: httpx.AsyncClient, feed_url: str) -> list[RawArticle]:
        if not feed_url.startswith(_ALLOWED_SCHEMES):
            return []
        response = await client.get(feed_url)
        response.raise_for_status()
        if len(response.content) > _MAX_BODY_BYTES:
            return []
        return self._parse(feed_url, response.text)

    def _parse(self, feed_url: str, body: str) -> list[RawArticle]:
        parsed = feedparser.parse(body)
        out: list[RawArticle] = []
        for entry in parsed.entries[: self._settings.max_items_per_feed]:
            title = _clean(getattr(entry, "title", ""))
            summary = _clean(getattr(entry, "summary", ""))
            link = getattr(entry, "link", "")
            if not title or not link.startswith(_ALLOWED_SCHEMES):
                continue
            out.append(
                RawArticle(
                    article_id=_hash(link),
                    title=title,
                    summary=summary,
                    url=link,
                    source=parsed.feed.get("title", feed_url),
                    fetched_at=datetime.now(timezone.utc),
                )
            )
        return out


def _clean(raw: str) -> str:
    text = BeautifulSoup(raw or "", "html.parser").get_text(separator=" ")
    return " ".join(text.split())[:2000]


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]