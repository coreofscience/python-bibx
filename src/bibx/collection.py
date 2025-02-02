import datetime
import logging
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from functools import reduce

import networkx as nx

from .article import Article

logger = logging.getLogger(__name__)


@dataclass
class Collection:
    """A collection of scientific articles."""

    articles: list[Article]

    def merge(self, other: "Collection") -> "Collection":
        """Create a new collection merging the articles by key.

        :param other: collection to merge to.
        :return: a new collection object.
        """
        all_articles = self.articles + other.articles
        return Collection(self.deduplicate_articles(all_articles))

    @staticmethod
    def _all_articles(articles: list[Article]) -> Iterable[Article]:
        seen = set()
        for article in articles:
            if id(article) in seen:
                continue
            yield article
            seen.add(id(article))
            for reference in article.references:
                if id(reference) in seen:
                    continue
                yield reference
                seen.add(id(reference))

    @classmethod
    def _uniqe_articles_by_id(cls, articles: list[Article]) -> dict[str, Article]:
        graph = nx.Graph()
        id_to_article: defaultdict[str, list[Article]] = defaultdict(list)
        for article in cls._all_articles(articles):
            first, *rest = article.ids
            # Add a loop edge so that the unique articles are included
            graph.add_edge(first, first)
            id_to_article[first].append(article)
            for id_ in rest:
                graph.add_edge(first, id_)
                id_to_article[id_].append(article)
        components = list(nx.connected_components(graph))
        biggest = max(components, key=len)
        smallest = min(components, key=len)
        logger.info(
            "Found %d components, biggest has %d articles, smallest has %d",
            len(components),
            len(biggest),
            len(smallest),
        )

        article_by_id: dict[str, Article] = {}
        for ids in components:
            visited = set()
            articles = []
            for id_ in ids:
                for article in id_to_article[id_]:
                    if id(article) in visited:
                        continue
                    articles.append(article)
                    visited.add(id(article))
            merged = reduce(Article.merge, articles)
            article_by_id.update({id_: merged for id_ in ids})

        return article_by_id

    @classmethod
    def deduplicate_articles(
        cls,
        articles: list[Article],
    ) -> list[Article]:
        """Deduplicate a list of articles."""
        article_by_id = cls._uniqe_articles_by_id(articles)

        unique_articles: list[Article] = []
        seen = set()
        for article in articles:
            if not article.ids:
                continue
            id_ = next(iter(article.ids))
            unique = article_by_id[id_]
            if id(unique) in seen:
                continue
            unique_articles.append(unique)
            seen.add(id(unique))

        for article in unique_articles:
            new_references = []
            for ref in article.references:
                if not ref.ids:
                    continue
                id_ = next(iter(ref.ids))
                new_references.append(article_by_id.get(id_, ref))
            article.references = new_references

        return unique_articles

    @property
    def citation_pairs(self) -> Iterable[tuple[Article, Article]]:
        """Return a generator with all citation pairs."""
        for article in self.articles:
            if not article.references:
                continue
            for reference in article.references:
                yield article, reference

    @property
    def _first_year(self) -> int:
        """Returns the year of the first article in the collection.

        :return: an integer.
        """
        return min(
            [article.year for article in self.articles if article.year is not None]
        )

    def published_by_year(self) -> dict[int, int]:
        """Retrn a dictionary with the publication count by year.

        Returns a dictionary where the key is the year of publication and the
        value is the number of articles published that year. The dictionary
        starts from the oldest article to the current year consecutively. If a
        year has no publications the value will be zero.

        :return: a dictionary with the number of articles published each year.
        """
        current_year = datetime.datetime.now(datetime.timezone.utc).year
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

    def cited_by_year(self) -> dict[int, int]:
        """Return a dictionary with the citation count by year.

        Returns a dictionary where the key is the year of publication and the
        value is the number of citations in that year. The dictionary starts
        from the oldest article to the current year consecutively. If a year has
        no citations the value will be zero.

        :return: a dictionary with the number of citations each year.
        """
        current_year = datetime.datetime.now(datetime.timezone.utc).year
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
