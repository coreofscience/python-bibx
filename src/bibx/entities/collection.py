import logging
from dataclasses import dataclass
from typing import Iterable, List, Tuple

from bibx.entities.article import Article

logger = logging.getLogger(__name__)


@dataclass
class Collection:
    articles: List[Article]

    @property
    def all_articles(self) -> Iterable[Article]:
        """
        Yields all articles and references

        :return: an iterable over `Article`.
        """
        cache = {article.key: article for article in self.articles}
        for article in self.articles:
            for reference in article.references:
                cache.setdefault(reference.key, reference)
        yield from cache.values()

    @property
    def citation_pairs(self) -> Iterable[Tuple[Article, Article]]:
        cache = {article.key: article for article in self.articles}
        for article in self.articles:
            if not article.references:
                continue
            for reference in article.references:
                # Yield a full article if we have the metadata for a citation
                if article.key != reference.key and reference.key in cache:
                    logger.debug("Found a cache hit for key %s", reference.key)
                    yield article, cache[reference.key]
                else:
                    yield article, reference
