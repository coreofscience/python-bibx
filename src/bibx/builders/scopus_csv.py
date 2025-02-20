"""CSV based builder for Scopus data."""

import csv
import logging
from collections.abc import Generator
from typing import Annotated, Optional, TextIO

from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator

from bibx.article import Article
from bibx.collection import Collection

from .base import CollectionBuilder

logger = logging.getLogger(__name__)


def _str_or_none(value: Optional[str]) -> Optional[str]:
    return value if value else None


def _split_str(value: Optional[str]) -> list[str]:
    return value.strip().split("; ") if value else []


class Row(BaseModel):
    """Row model for Scopus CSV data."""

    authors: Annotated[
        list[str],
        Field(validation_alias='﻿"Authors"'),
        BeforeValidator(_split_str),
    ]
    year: Annotated[int, Field(validation_alias="Year")]
    title: Annotated[str, Field(validation_alias="Title")]
    journal: Annotated[str, Field(validation_alias="Abbreviated Source Title")]
    volume: Annotated[
        Optional[str],
        Field(validation_alias="Volume"),
        BeforeValidator(_str_or_none),
    ]
    issue: Annotated[
        Optional[str],
        Field(validation_alias="Issue"),
        BeforeValidator(_str_or_none),
    ]
    page: Annotated[
        Optional[str],
        Field(validation_alias="Page start"),
        BeforeValidator(_str_or_none),
    ]
    doi: Annotated[
        Optional[str],
        Field(validation_alias="DOI"),
        BeforeValidator(_str_or_none),
    ]
    cited_by: Annotated[
        Optional[int],
        Field(validation_alias="Cited by"),
        BeforeValidator(_str_or_none),
    ]
    references: Annotated[
        list[str],
        Field(validation_alias="References"),
        BeforeValidator(_split_str),
    ]
    author_keywords: Annotated[
        list[str],
        Field(validation_alias="Author Keywords"),
        BeforeValidator(_split_str),
    ]
    index_keywords: Annotated[
        list[str],
        Field(validation_alias="Index Keywords"),
        BeforeValidator(_split_str),
    ]
    source: Annotated[str, Field(validation_alias="Source")]


class ScopusCsvCollectionBuilder(CollectionBuilder):
    """Builder for Scopus data from CSV files."""

    def __init__(self, *files: TextIO) -> None:
        self._files = files
        for file in self._files:
            file.seek(0)

    def build(self) -> Collection:
        """Build the collection."""
        articles = self._articles_from_files()
        return Collection(articles=Collection.deduplicate_articles(list(articles)))

    def _articles_from_files(self) -> Generator[Article]:
        for file in self._files:
            yield from self._parse_file(file)

    def _parse_file(self, file: TextIO) -> Generator[Article]:
        reader = csv.DictReader(file)
        for row in reader:
            datum = Row.model_validate(row)
            if not datum.authors or not datum.year:
                logger.info(
                    "skipping row with missing authors or year: %s",
                    datum.model_dump_json(indent=2),
                )
                continue
            yield (
                Article(
                    label="",
                    ids=set(),
                    title=datum.title,
                    authors=datum.authors,
                    year=datum.year,
                    journal=datum.journal,
                    volume=datum.volume,
                    issue=datum.issue,
                    page=datum.page,
                    doi=datum.doi,
                    times_cited=datum.cited_by,
                    references=list(
                        filter(
                            None,
                            [
                                self._article_from_reference(ref)
                                for ref in datum.references
                            ],
                        )
                    ),
                    keywords=list(set(datum.author_keywords + datum.index_keywords)),
                    sources={datum.source},
                )
                .add_simple_id()
                .set_simple_label()
            )

    def _article_from_reference(self, reference: str) -> Optional[Article]:
        try:
            *authors, journal, issue, year = reference.split(", ")
            if not authors:
                message = "a minimum of one author is required"
                raise ValueError(message)
            _year = int(year.lstrip("(").rstrip(")"))
            return Article(
                label=reference,
                ids={reference},
                authors=authors,
                year=_year,
                journal=journal,
                issue=issue,
            ).add_simple_id()
        except ValueError:
            logger.debug("error parsing reference: %s", reference)
            return None
