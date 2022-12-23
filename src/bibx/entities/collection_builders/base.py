from typing import Protocol

from bibx.entities.collection import Collection


class CollectionBuilder(Protocol):
    def build(self) -> Collection:
        ...
