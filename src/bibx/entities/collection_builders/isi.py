from typing import Collection, TextIO

from bibx.entities.collection_builders.base import CollectionBuilder


class IsiCollectionBuilder(CollectionBuilder):
    def __init__(self, isi_file: TextIO):
        self._file = isi_file

    def build(self) -> Collection:
        return Collection([])
