"""
Algorithms for preprocessing the data.
"""

from typing import Optional

from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet

from bibx import Collection


class Preprocess:
    def __init__(self, wos: Collection, scopus: Collection) -> None:
        self.wos = wos
        self.scopus = scopus
        self._merged: Optional[Collection] = None

    @property
    def merged(self):
        if self._merged is None:
            self._merged = self.wos.merge(self.scopus)
        return self._merged

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(wos={self.wos}, scopus={self.scopus})"

    def _write_collection_to_workseet(
        self,
        collection: Collection,
        workseet: Worksheet,
    ) -> None:
        for i, title in enumerate(
            [
                "Authors",
                "Year",
                "Title",
                "Journal",
                "Volume",
                "Issue",
                "Page",
                "DOI",
                "Times Cited",
                "Label",
            ]
        ):
            workseet.write(0, i, title)

        for i, row in enumerate(collection.articles, start=1):
            workseet.write(i, 0, "; ".join(row.authors))
            workseet.write(i, 1, row.year)
            workseet.write(i, 2, row.title)
            workseet.write(i, 3, row.journal)
            workseet.write(i, 4, row.volume)
            workseet.write(i, 5, row.issue)
            workseet.write(i, 6, row.page)
            workseet.write(i, 7, row.doi)
            workseet.write(i, 8, row.times_cited)
            workseet.write(i, 9, row.label)

    def write_merged_information(self, workseet: Worksheet) -> None:
        self._write_collection_to_workseet(self.merged, workseet)

    def write_wos_information(self, workseet: Worksheet) -> None:
        self._write_collection_to_workseet(self.wos, workseet)

    def write_scopus_information(self, workseet: Worksheet) -> None:
        self._write_collection_to_workseet(self.scopus, workseet)

    def write_reference_information(self, workseet: Worksheet) -> None:
        for i, title in enumerate(
            [
                "SR",
                "SR_ref",
                "Title",
                "Authors",
                "Journal",
                "Year",
                "Label",
            ]
        ):
            workseet.write(0, i, title)
        row = 1
        for article in self.merged.articles:
            for ref in article.references:
                workseet.write(row, 0, article.label)
                workseet.write(row, 1, ref.label)
                workseet.write(row, 2, ref.title)
                workseet.write(row, 3, "; ".join(ref.authors))
                workseet.write(row, 4, ref.journal)
                workseet.write(row, 5, ref.year)
                workseet.write(row, 6, ref.label)
                row += 1

    def write_journal_information(self, workseet: Worksheet) -> None:
        for i, title in enumerate(
            [
                "Label",
                "Journal",
                "Year",
                "Cited Journal",
                "Cited Year",
            ]
        ):
            workseet.write(0, i, title)
        row = 1
        for article in self.merged.articles:
            for ref in article.references:
                workseet.write(row, 0, article.label)
                workseet.write(row, 1, article.journal)
                workseet.write(row, 2, article.year)
                workseet.write(row, 3, ref.journal)
                workseet.write(row, 4, ref.year)
                row += 1

    def write_author_information(self, workseet: Worksheet) -> None:
        for i, title in enumerate(
            [
                "Author",
                "Year",
                "Cited Author",
                "Cited Year",
            ]
        ):
            workseet.write(0, i, title)
        row = 1
        for article in self.merged.articles:
            for ref in article.references:
                for author in article.authors:
                    for cited_author in ref.authors:
                        workseet.write(row, 0, author)
                        workseet.write(row, 1, article.year)
                        workseet.write(row, 2, cited_author)
                        workseet.write(row, 3, ref.year)
                        row += 1

    def write_times_cited_information(self, workseet: Worksheet) -> None:
        for i, title in enumerate(
            [
                "Year",
                "Times Cited Sum",
                "Times Cited Percentage",
            ]
        ):
            workseet.write(0, i, title)
        years = self.merged.cited_by_year()
        total = sum(years.values())
        for i, (year, times_cited) in enumerate(years.items(), start=1):
            workseet.write(i, 0, year)
            workseet.write(i, 1, times_cited)
            workseet.write(i, 2, times_cited / total)

    def create_workbook(self, filename: str) -> None:
        workbook = Workbook(filename)
        self.write_merged_information(workbook.add_worksheet("Merged"))
        self.write_wos_information(workbook.add_worksheet("WOS"))
        self.write_scopus_information(workbook.add_worksheet("Scopus"))
        self.write_reference_information(workbook.add_worksheet("References"))
        self.write_journal_information(workbook.add_worksheet("Journals"))
        self.write_author_information(workbook.add_worksheet("Authors"))
        self.write_times_cited_information(workbook.add_worksheet("Times Cited"))
        workbook.close()
