from typing import Protocol

from bibx.collection import Collection


class CollectionBuilder(Protocol):
    """Protocol for classes that build collections of articles."""

    def build(self) -> Collection:
        """Build a collection of articles."""
        ...
