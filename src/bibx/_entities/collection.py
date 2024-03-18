import datetime
import logging
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from bibx._entities.article import Article

logger = logging.getLogger(__name__)


@dataclass
class Collection:
    articles: List[Article]

    def merge(self, other: "Collection") -> "Collection":
        """
        Creates a new collection merging the articles by key.

        :param other: collection to merge to.
        :return: a new collection object.
        """
        keys = {a.key for a in self.articles}
        merged = self.articles[:]
        merged.extend(a for a in other.articles if a.key not in keys)
        return Collection(merged)

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

    @property
    def _first_year(self) -> int:
        """
        Returns the year of the first article in the collection.

        :return: an integer.
        """
        return min(
            [article.year for article in self.articles if article.year is not None]
        )

    def published_by_year(self) -> Dict[int, int]:
        """
        Returns a dictionary where the key is the year of publication and the value is the number of articles
        published that year. The dictionary starts from the oldest article to the current year consecutively.
        If a year has no publications the value will be zero.

        :return: a dictionary with the number of articles published each year.
        """
        current_year = datetime.date.today().year
        years = {}
        for year in range(self._first_year, current_year + 1):
            years[year] = 0

        for article in self.articles:
            if article.year is None:
                continue
            if article.year in years:
                years[article.year] += 1
            else:
                years[article.year] = 1
        return years

    def cited_by_year(self) -> Dict[int, int]:
        """
        Returns a dictionary where the key is the year of publication and the value is the number of
        citations in that year. The dictionary starts from the oldest article to the current year consecutively.
        If a year has no citations the value will be zero.

        :return: a dictionary with the number of citations each year.
        """
        current_year = datetime.date.today().year
        cited_items_per_year = {}
        for year in range(self._first_year, current_year + 1):
            cited_items_per_year[year] = 0

        for article in self.articles:
            if article.times_cited is None or article.year is None:
                continue
            if article.year in cited_items_per_year:
                cited_items_per_year[article.year] += article.times_cited
            else:
                cited_items_per_year[article.year] = article.times_cited

        return cited_items_per_year
