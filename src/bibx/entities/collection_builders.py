from typing import List, Protocol, TextIO

from bibx.entities.article import Article
from bibx.entities.collection import Collection


class CollectionBuilder(Protocol):
    def build(self) -> Collection:
        ...


class SimpleCollectionBuilder(CollectionBuilder):
    def __init__(self, articles: List[Article]):
        self.articles = articles

    def build(self) -> Collection:
        return Collection(self.articles[:])


class IsiCollectionBuilder(CollectionBuilder):
    def __init__(self, isi_file: TextIO):
        self._file = isi_file

    def build(self) -> Collection:
        return Collection([])


class ScopusCollectionBuilder(CollectionBuilder):
    def __init__(self, scopus_ris: TextIO):
        self._file = scopus_ris

    def build(self) -> Collection:
        return Collection([])


class CrossRefCollectionBuilder(CollectionBuilder):
    def __init__(self, query: str, count: int = 100):
        self._query = query
        self._count = count

    def with_count(self, count: int):
        self._count = count
        return self

    def build(self) -> Collection:
        # Rust es bello
        return Collection([])


class GenericCollectionBuilder(CollectionBuilder):
    def __init__(self, *collections: Collection):
        self._collections = collections

    def build(self) -> Collection:
        return Collection([])
