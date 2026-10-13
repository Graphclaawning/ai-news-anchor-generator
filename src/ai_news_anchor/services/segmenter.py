"""Cluster and rank articles into a broadcast rundown.

Input: raw articles. Output: ordered segments, each with a lead article and
supporting context, ready for the script writer.
"""

from __future__ import annotations

from collections import defaultdict

from ai_news_anchor.config.settings import Settings
from ai_news_anchor.models.article import RawArticle
from ai_news_anchor.models.segment import Segment
from ai_news_anchor.utils.text import jaccard, tokenize


class SegmenterService:
    """Groups articles into topical segments and ranks them."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def build_rundown(
        self, articles: list[RawArticle], interest_tags: tuple[str, ...]
    ) -> list[Segment]:
        """Return segments ordered by relevance to interest_tags."""
        clusters = self._cluster(articles)
        scored = [
            (self._score(cluster, interest_tags), cluster) for cluster in clusters.values()
        ]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            Segment(
                index=i,
                lead=cluster[0],
                supporting=tuple(cluster[1:3]),
                relevance=score,
            )
            for i, (score, cluster) in enumerate(scored[: self._settings.max_segments])
        ]

    def _cluster(self, articles: list[RawArticle]) -> dict[str, list[RawArticle]]:
        clusters: dict[str, list[RawArticle]] = defaultdict(list)
        for article in articles:
            key = self._nearest_cluster(article, clusters)
            clusters[key].append(article)
        for cluster in clusters.values():
            cluster.sort(key=lambda a: a.fetched_at, reverse=True)
        return dict(clusters)

    def _nearest_cluster(
        self, article: RawArticle, clusters: dict[str, list[RawArticle]]
    ) -> str:
        best_key, best_sim = article.article_id, 0.0
        art_tokens = set(tokenize(article.title + " " + article.summary))
        for key, cluster in clusters.items():
            sim = jaccard(art_tokens, set(tokenize(cluster[0].title + " " + cluster[0].summary)))
            if sim > best_sim and sim >= self._settings.cluster_threshold:
                best_key, best_sim = key, sim
        return best_key

    def _score(self, cluster: list[RawArticle], interest_tags: tuple[str, ...]) -> float:
        if not interest_tags:
            return 1.0 / (1.0 + len(cluster))
        text = " ".join(a.title + " " + a.summary for a in cluster).lower()
        hits = sum(1 for tag in interest_tags if tag.lower() in text)
        return hits / len(interest_tags) + 1.0 / (1.0 + len(cluster))