"""CSV based builder for Scopus data."""

import csv
from typing import Annotated, TextIO

from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator

from bibx.collection import Collection

from .base import CollectionBuilder


class Row(BaseModel):
    """Row model for Scopus CSV data."""

    authors: Annotated[
        list[str],
        Field(validation_alias='﻿"Authors"'),
        BeforeValidator(lambda x: x.strip().split("; ")),
    ]
    title: Annotated[str, Field(validation_alias="Title")]
    year: Annotated[int, Field(validation_alias="Year")]


class ScopusCsvCollectionBuilder(CollectionBuilder):
    """Builder for Scopus data from CSV files."""

    def __init__(self, *files: TextIO) -> None:
        self._files = files
        for file in self._files:
            file.seek(0)

    def build(self) -> Collection:
        """Build the collection."""
        for file in self._files:
            reader = csv.DictReader(file)
            print(reader.fieldnames)
            for row in reader:
                datum = Row.model_validate(row)
                print(datum.model_dump_json(indent=2))
        return Collection(articles=[])
