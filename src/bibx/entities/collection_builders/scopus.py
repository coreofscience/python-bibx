from typing import TextIO

from bibx.entities.collection import Collection
from bibx.entities.collection_builders.base import CollectionBuilder


class ScopusCollectionBuilder(CollectionBuilder):
    def __init__(self, scopus_ris: TextIO):
        self._file = scopus_ris

    def build(self) -> Collection:
        return Collection([])
