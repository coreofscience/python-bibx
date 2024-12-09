from bibx._entities.article import Article
from bibx._entities.collection import Collection
from bibx._entities.collection_builders.base import CollectionBuilder


class SimpleCollectionBuilder(CollectionBuilder):
    def __init__(self, articles: list[Article]):
        self.articles = articles

    def build(self) -> Collection:
        return Collection(self.articles[:])
