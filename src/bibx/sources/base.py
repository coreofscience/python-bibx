from typing import Protocol

from bibx.models.collection import Collection


class Source(Protocol):
    """Protocol for classes that build collections of articles."""

    def build(self) -> Collection:
        """Build a collection of articles."""
        ...
