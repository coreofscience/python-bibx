import json
import re
from collections.abc import Iterable
from contextlib import suppress
from typing import Optional, TextIO

import bibtexparser

from bibx.article import Article
from bibx.collection import Collection
from bibx.exceptions import MissingCriticalInformationError

from .base import CollectionBuilder


class ScopusBibCollectionBuilder(CollectionBuilder):
    """Builder for collections of articles from Scopus BibTeX files."""

    def __init__(self, *scopus_files: TextIO) -> None:
        self._files = scopus_files
        for file in self._files:
            file.seek(0)

    def build(self) -> Collection:
        """Build a collection of articles from Scopus BibTeX files."""
        articles = self._get_articles_from_files()
        return Collection(Collection.deduplicate_articles(list(articles)))

    def _get_articles_from_files(self) -> Iterable[Article]:
        for file in self._files:
            db = bibtexparser.load(file)
            for entry in db.entries:
                with suppress(MissingCriticalInformationError):
                    yield self._article_from_entry(entry)

    def _article_from_entry(self, entry: dict) -> Article:
        if "author" not in entry or "year" not in entry:
            raise MissingCriticalInformationError()
        if "note" in entry:
            match = re.search(r"cited By (\d+)", entry["note"], re.IGNORECASE)
            times_cited = int(match.groups()[0]) if match else None
        else:
            times_cited = None
        ids = set()
        doi = entry.get("doi")
        if doi is not None:
            ids.add(f"doi:{doi}")
        return (
            Article(
                label=doi or entry.get("title", "replaceme"),
                ids=ids,
                authors=entry["author"].split(" and "),
                year=int(entry["year"]),
                title=entry.get("title"),
                journal=entry.get("journal"),
                volume=entry.get("volume"),
                issue=entry.get("issue"),
                page=entry.get("art_number"),
                doi=entry.get("doi"),
                references=list(
                    self._articles_from_references(entry.get("references"))
                ),
                keywords=entry.get("keywords", "").split("; "),
                extra=entry,
                sources={json.dumps(entry)},
                times_cited=times_cited,
            )
            .add_simple_id()
            .set_simple_label()
        )

    def _articles_from_references(self, references: Optional[str]) -> Iterable[Article]:
        if references is None:
            references = ""
        for reference in references.split("; "):
            with suppress(MissingCriticalInformationError):
                yield self._article_from_reference(reference)

    @staticmethod
    def _article_from_reference(reference: str) -> Article:
        match = re.search(r"\((\d{4})\)", reference)
        if not match:
            raise MissingCriticalInformationError()
        year = int(match.groups()[0])
        author = reference.split(",", maxsplit=2)[0].strip()
        match = re.search(r"(10.\d{4,9}/[-._;()/:A-Z0-9]+)", reference)
        doi = match.groups()[0] if match else None
        return Article(
            label=reference,
            ids=set() if doi is None else {f"doi:{doi}"},
            authors=[author],
            year=year,
            doi=doi,
            sources={reference},
        ).add_simple_id()
