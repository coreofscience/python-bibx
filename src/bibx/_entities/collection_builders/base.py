from typing import Protocol

from bibx._entities.collection import Collection


class CollectionBuilder(Protocol):
    def build(self) -> Collection:
        ...
