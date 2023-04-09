from bibx._entities.collection import Collection
from bibx._entities.collection_builders.base import CollectionBuilder


class CrossRefCollectionBuilder(CollectionBuilder):
    def __init__(self, query: str, count: int = 100):
        self._query = query
        self._count = count

    def with_count(self, count: int):
        self._count = count
        return self

    def build(self) -> Collection:
        return Collection([])
