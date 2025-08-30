import logging
from collections import Counter
from enum import Enum
from urllib.parse import urlparse

from bibx.clients.openalex import OpenAlexClient, Work
from bibx.models.article import Article
from bibx.models.collection import Collection

from .base import Source

logger = logging.getLogger(__name__)

_COMMON_REFERENCES = 400
_MOST_REFERENCES = 2000


class EnrichReferences(Enum):
    """How to handle references when building an openalex collection."""

    BASIC = "basic"
    COMMON = "common"
    MOST = "most"
    FULL = "full"


class OpenAlexSource(Source):
    """Builder for collections of articles from the OpenAlex API."""

    def __init__(
        self,
        query: str,
        limit: int = 600,
        enrich: EnrichReferences = EnrichReferences.BASIC,
        client: OpenAlexClient | None = None,
    ) -> None:
        self.query = query
        self.limit = limit
        self.enrich = enrich
        self.client = client or OpenAlexClient()

    def build(self) -> Collection:
        """Build a collection of articles from the OpenAlex API."""
        logger.info("building collection for query %s", self.query)
        works = self.client.list_recent_articles(self.query, self.limit)
        cache = {work.id: work for work in works}
        references: list[str] = []
        missing = set()
        for work in works:
            references.extend(work.referenced_works)
        if self.enrich in (EnrichReferences.COMMON, EnrichReferences.MOST):
            counter = Counter(references)
            count = (
                _MOST_REFERENCES
                if self.enrich == EnrichReferences.MOST
                else _COMMON_REFERENCES
            )
            most_common = {key for key, _ in counter.most_common(count)}
            missing = most_common - set(cache.keys())
        if self.enrich == EnrichReferences.FULL:
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
        journal = None
        if work.primary_location and work.primary_location.source:
            journal = work.primary_location.source.display_name
        permalink = None
        if work.primary_location and work.primary_location.landing_page_url:
            permalink = work.primary_location.landing_page_url
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
            journal=journal,
            volume=work.biblio.volume,
            issue=work.biblio.issue,
            page=work.biblio.first_page,
            doi=cls._extract_doi(work.doi) if work.doi else None,
            _permalink=permalink,
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
