import csv
import io
import os
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

import zstandard

from bibx._entities.journal import Journal
from bibx._fuzz.utils import normalize
from bibx._utils.singleton_meta import SingletonMeta


class JournalDataSet(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._filename = os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            os.path.pardir,
            "_data/scimago.csv.zst",
        )
        self._journal_data: Optional[List[Dict]] = None
        self._journals: Optional[List[Journal]] = None
        self._titles: Optional[Set[str]] = None
        self._abbreviations: Optional[Set[str]] = None
        self._titles_and_abbreviations: Optional[Set[str]] = None
        self._titles_to_abbreviations: Optional[Dict[str, str]] = None
        self._organized_journals: Optional[Dict[str, Journal]] = None

    @property
    def journal_data(self) -> List[Dict]:
        if self._journal_data is None:
            with open(self._filename, "rb") as file:
                decompressor = zstandard.ZstdDecompressor()
                decompressed = io.BytesIO()
                decompressor.copy_stream(file, decompressed)
                decompressed.seek(0)
                decompressed_text = io.TextIOWrapper(decompressed, encoding="utf-8")
                reader = csv.DictReader(decompressed_text)
                self._journal_data = list(reader)
        return self._journal_data

    @property
    def journals(self) -> List[Journal]:
        if self._journals is None:
            classifications: Dict[Tuple[str, str, str], Dict[int, str]] = defaultdict(
                dict
            )
            for row in self.journal_data:
                title = normalize(row["title"])
                abbr = normalize(row["abbr"])
                issn = normalize(row["issn"])
                year = int(row["year"])
                category = row["category"]
                classifications[(title, abbr, issn)][year] = category
            self._journals = [
                Journal(title, abbr, issn, classification)
                for (title, abbr, issn), classification in classifications.items()
            ]
        return self._journals

    @property
    def titles(self) -> Set[str]:
        if self._titles is None:
            self._titles = {journal.title for journal in self.journals if journal.title}
        return self._titles

    @property
    def abbreviations(self) -> Set[str]:
        if self._abbreviations is None:
            self._abbreviations = {
                journal.abbr for journal in self.journals if journal.abbr
            }
        return self._abbreviations

    @property
    def titles_and_abbreviations(self) -> Set[str]:
        if self._titles_and_abbreviations is None:
            self._titles_and_abbreviations = self.titles.union(self.abbreviations)
        return self._titles_and_abbreviations

    @property
    def titles_to_abbreviations(self) -> Dict[str, str]:
        if self._titles_to_abbreviations is None:
            self._titles_to_abbreviations = {
                journal.title: journal.abbr for journal in self.journals if journal.abbr
            }
        return self._titles_to_abbreviations

    @property
    def organized_journals(self) -> Dict[str, Journal]:
        if self._organized_journals is None:
            self._organized_journals = {
                journal.title: journal for journal in self.journals if journal.title
            }
            self._organized_journals.update(
                {journal.abbr: journal for journal in self.journals if journal.abbr}
            )
        return self._organized_journals
