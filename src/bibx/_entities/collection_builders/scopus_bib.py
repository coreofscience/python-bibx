import json
import re
from contextlib import suppress
from typing import Iterable, Optional, TextIO

import bibtexparser

from bibx._entities.article import Article
from bibx._entities.collection import Collection
from bibx._entities.collection_builders.base import CollectionBuilder
from bibx.exceptions import MissingCriticalInformation


class ScopusBibCollectionBuilder(CollectionBuilder):
    def __init__(self, *scopus_files: TextIO):
        self._files = scopus_files
        for file in self._files:
            file.seek(0)

    def build(self) -> Collection:
        articles = self._get_articles_from_files()
        return Collection(list(articles))

    def _get_articles_from_files(self) -> Iterable[Article]:
        for file in self._files:
            db = bibtexparser.load(file)
            for entry in db.entries:
                with suppress(MissingCriticalInformation):
                    yield self._article_from_entry(entry)

    def _article_from_entry(self, entry: dict) -> Article:
        if "author" not in entry or "year" not in entry:
            raise MissingCriticalInformation()
        return Article(
            authors=entry["author"].split(" and "),
            year=int(entry["year"]),
            title=entry.get("title"),
            journal=entry.get("journal"),
            volume=entry.get("volume"),
            issue=entry.get("issue"),
            page=entry.get("art_number"),
            doi=entry.get("doi"),
            references=list(self._articles_from_references(entry.get("references"))),
            keywords=entry.get("keywords", "").split("; "),
            extra=entry,
            sources={json.dumps(entry)},
        )

    def _articles_from_references(self, references: Optional[str]) -> Iterable[Article]:
        if references is None:
            references = ""
        for reference in references.split("; "):
            with suppress(MissingCriticalInformation):
                yield self._article_from_reference(reference)

    @staticmethod
    def _article_from_reference(reference: str) -> Article:
        match = re.search(r"\((\d{4})\)", reference)
        if not match:
            raise MissingCriticalInformation()
        year = int(match.groups()[0])
        author = reference.split(",", maxsplit=2)[0].strip()
        doi = re.search(r"(10.\d{4,9}/[-._;()/:A-Z0-9]+)", reference)
        return Article(
            authors=[author],
            year=year,
            _label=reference,
            doi=doi.groups()[0] if doi else None,
            sources={reference},
        )
