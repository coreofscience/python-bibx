from bibx._entities.collection import Collection
from bibx._entities.collection_builders.base import CollectionBuilder


class GenericCollectionBuilder(CollectionBuilder):
    def __init__(self, *collections: Collection):
        self._collections = collections

    def build(self) -> Collection:
        return Collection([])
