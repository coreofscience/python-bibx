from bibx.models.article import Article
from bibx.models.collection import Collection

from .base import Source


class SimpleSource(Source):
    """Builder for collections of articles from a list of articles."""

    def __init__(self, articles: list[Article]) -> None:
        self.articles = articles

    def build(self) -> Collection:
        """Build a collection of articles from a list of articles."""
        return Collection(Collection.deduplicate_articles(self.articles))
