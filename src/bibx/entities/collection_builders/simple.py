from typing import List

from bibx.entities.article import Article
from bibx.entities.collection import Collection
from bibx.entities.collection_builders.base import CollectionBuilder


class SimpleCollectionBuilder(CollectionBuilder):
    def __init__(self, articles: List[Article]):
        self.articles = articles

    def build(self) -> Collection:
        return Collection(self.articles[:])
