import csv
import os
from collections import defaultdict
from typing import Dict, List, Set

from bibx._entities.journal import Journal
from bibx._fuzz.utils import normalize
from bibx._utils.singleton_meta import SingletonMeta


class JournalDataSet(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._filename = os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            os.path.pardir,
            "_data/scimago.csv",
        )
        self._journal_data = None
        self._journals: List[Journal] | None = None
        self._titles: Set[str] | None = None
        self._abbreviations: Set[str] | None = None
        self._titles_and_abbreviations: Set[str] | None = None
        self._titles_to_abbreviations: Dict[str, str] | None = None
        self._organized_journals: Dict[str, Journal] | None = None

    @property
    def journal_data(self):
        if self._journal_data is None:
            with open(self._filename, "r") as file:
                reader = csv.DictReader(file)
                self._journal_data = list(reader)
        return self._journal_data

    @property
    def journals(self):
        if self._journals is None:
            classifications = defaultdict(dict)
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
    def titles(self):
        if self._titles is None:
            self._titles = {journal.title for journal in self.journals if journal.title}
        return self._titles

    @property
    def abbreviations(self):
        if self._abbreviations is None:
            self._abbreviations = {
                journal.abbr for journal in self.journals if journal.abbr
            }
        return self._abbreviations

    @property
    def titles_and_abbreviations(self):
        if self._titles_and_abbreviations is None:
            self._titles_and_abbreviations = self.titles.union(self.abbreviations)
        return self._titles_and_abbreviations

    @property
    def titles_to_abbreviations(self):
        if self._titles_to_abbreviations is None:
            self._titles_to_abbreviations = {
                journal.title: journal.abbr for journal in self.journals if journal.abbr
            }
        return self._titles_to_abbreviations

    @property
    def organized_journals(self):
        if self._organized_journals is None:
            self._organized_journals = {
                journal.title: journal for journal in self.journals if journal.title
            }
            self._organized_journals.update(
                {journal.abbr: journal for journal in self.journals if journal.abbr}
            )
        return self._organized_journals
