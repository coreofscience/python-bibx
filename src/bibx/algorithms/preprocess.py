"""Algorithms for preprocessing the data."""

from typing import Optional

from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet

from bibx.collection import Collection

from .sap import BRANCH, LEAF, ROOT, TRUNK, Sap


class Preprocess:
    """Preprocess the data."""

    def __init__(self, wos: Collection, scopus: Collection) -> None:
        self.wos = wos
        self.scopus = scopus
        self._merged: Optional[Collection] = None

    @property
    def merged(self) -> Collection:
        """Merge the collections."""
        if self._merged is None:
            self._merged = self.wos.merge(self.scopus)
        return self._merged

    def __repr__(self) -> str:
        """Return the representation of the object."""
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
        """Write the merged information to a worksheet."""
        self._write_collection_to_workseet(self.merged, workseet)

    def write_wos_information(self, workseet: Worksheet) -> None:
        """Write the WOS information to a worksheet."""
        self._write_collection_to_workseet(self.wos, workseet)

    def write_scopus_information(self, workseet: Worksheet) -> None:
        """Write the Scopus information to a worksheet."""
        self._write_collection_to_workseet(self.scopus, workseet)

    def write_reference_information(self, workseet: Worksheet) -> None:
        """Write the reference information to a worksheet."""
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
        """Write the journal information to the worksheet."""
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
        """Write the author information to the worksheet."""
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
        """Write the times cited information to the worksheet."""
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

    @staticmethod
    def _get_tos(data: dict) -> str:
        if data[ROOT] > 0:
            return "Root"
        if data[TRUNK] > 0:
            return "Trunk"
        if data[LEAF] > 0:
            return "Leaf"
        if data[BRANCH] > 0:
            return f"Branch {data[BRANCH]}"
        return "_"

    def write_tree_of_science_information(self, workseet: Worksheet) -> None:
        """Write the tree of science information to the worksheet."""
        s = Sap()
        g = s.create_graph(self.merged)
        g = s.clean_graph(g)
        g = s.tree(g)

        for i, title in enumerate(
            [
                "TOS",
                "Label",
                "Authors",
                "Year",
                "Title",
                "Journal",
                "Volume",
                "Issue",
                "Page",
                "DOI",
                "Times Cited",
            ]
        ):
            workseet.write(0, i, title)

        i = 1
        for label, data in sorted(
            g.nodes(data=True), key=lambda x: self._get_tos(x[1])
        ):
            tos = self._get_tos(data)
            if tos == "_":
                continue
            workseet.write(i, 0, tos)
            workseet.write(i, 1, label)
            workseet.write(i, 2, "; ".join(data["authors"]))
            workseet.write(i, 3, data["year"])
            workseet.write(i, 4, data["title"])
            workseet.write(i, 5, data["journal"])
            workseet.write(i, 6, data["volume"])
            workseet.write(i, 7, data["issue"])
            workseet.write(i, 8, data["page"])
            workseet.write(i, 9, data["doi"])
            workseet.write(i, 10, data["times_cited"])
            i += 1

    def create_workbook(self, filename: str) -> None:
        """Create a workbook with the information."""
        workbook = Workbook(filename)
        self.write_merged_information(workbook.add_worksheet("Merged"))
        self.write_wos_information(workbook.add_worksheet("WOS"))
        self.write_scopus_information(workbook.add_worksheet("Scopus"))
        self.write_reference_information(workbook.add_worksheet("References"))
        self.write_journal_information(workbook.add_worksheet("Journals"))
        self.write_author_information(workbook.add_worksheet("Authors"))
        self.write_times_cited_information(workbook.add_worksheet("Times Cited"))
        self.write_tree_of_science_information(
            workbook.add_worksheet("Tree of Science")
        )
        workbook.close()
