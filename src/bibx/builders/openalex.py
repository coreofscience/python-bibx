import logging
from collections import Counter
from enum import Enum
from typing import Optional
from urllib.parse import urlparse

from bibx.article import Article
from bibx.clients.openalex import OpenAlexClient, Work
from bibx.collection import Collection

from .base import CollectionBuilder

logger = logging.getLogger(__name__)

MAX_REFERENCES = 400


class HandleReferences(Enum):
    """How to handle references when building an openalex collection."""

    BASIC = "basic"
    COMMON = "common"
    FULL = "full"


class OpenAlexCollectionBuilder(CollectionBuilder):
    """Builder for collections of articles from the OpenAlex API."""

    def __init__(
        self,
        query: str,
        limit: int = 600,
        references: HandleReferences = HandleReferences.BASIC,
        client: Optional[OpenAlexClient] = None,
    ) -> None:
        self.query = query
        self.limit = limit
        self.references = references
        self.client = client or OpenAlexClient()

    def build(self) -> Collection:
        """Build a collection of articles from the OpenAlex API."""
        logger.info("building collection for query %s", self.query)
        works = self.client.list_recent_articles(self.query, self.limit)
        cache = {work.id: work for work in works}
        references: list[str] = []
        for work in works:
            references.extend(work.referenced_works)
        if self.references == HandleReferences.COMMON:
            counter = Counter(references)
            most_common = {key for key, _ in counter.most_common(MAX_REFERENCES)}
            missing = most_common - set(cache.keys())
            logger.info("fetching %d missing references", len(missing))
            missing_works = self.client.list_articles_by_openalex_id(list(missing))
            cache.update({work.id: work for work in missing_works})
        if self.references == HandleReferences.FULL:
            missing = set(references) - set(cache.keys())
            logger.info("fetching %d missing references", len(missing))
            missing_works = self.client.list_articles_by_openalex_id(list(missing))
            cache.update({work.id: work for work in missing_works})

        article_cache = {
            openalexid: self._work_to_article(work)
            for openalexid, work in cache.items()
        }
        logger.info("enriching references")
        articles = []
        for work in works:
            article = article_cache[work.id]
            article.references = [
                article_cache.get(reference, self._reference_to_article(reference))
                for reference in work.referenced_works
                if reference != work.id
            ]
            articles.append(article)
        return Collection(Collection.deduplicate_articles(articles))

    @staticmethod
    def _invert_name(name: str) -> str:
        *first, last = name.split()
        return f"{last}, {' '.join(first)}"

    @staticmethod
    def _extract_doi(url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme != "https":
            # maybe it was actually a DOI
            return url
        return parsed.path.lstrip("/")

    @classmethod
    def _work_to_article(cls, work: Work) -> Article:
        article = Article(
            label=work.id,
            ids={
                f"{source}:{id_}"
                if source != "doi"
                else f"{source}:{cls._extract_doi(id_)}"
                for source, id_ in work.ids.items()
            },
            authors=[cls._invert_name(a.author.display_name) for a in work.authorships],
            year=work.publication_year,
            title=work.title,
            journal=(
                work.primary_location
                and work.primary_location.source
                and work.primary_location.source.display_name
            ),
            volume=work.biblio.volume,
            issue=work.biblio.issue,
            page=work.biblio.first_page,
            doi=cls._extract_doi(work.doi) if work.doi else None,
            _permalink=work.primary_location and work.primary_location.landing_page_url,
            times_cited=work.cited_by_count,
            references=[cls._reference_to_article(r) for r in work.referenced_works],
            keywords=[k.display_name for k in work.keywords],
            sources={"openalex"},
            extra={},
        )
        if article.simple_id:
            article.ids.add(f"simple:{article.simple_id}")
        return article

    @staticmethod
    def _reference_to_article(reference: str) -> Article:
        return Article(
            label=reference,
            ids={f"openalex:{reference}"},
            _permalink=reference,
            sources={"openalex"},
        )
