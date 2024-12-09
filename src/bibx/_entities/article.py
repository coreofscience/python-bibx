from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Article:
    authors: list[str] = field(default_factory=list)
    year: Optional[int] = None
    title: Optional[str] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    page: Optional[str] = None
    doi: Optional[str] = None
    _label: Optional[str] = None
    times_cited: Optional[int] = None
    references: list["Article"] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    sources: set[str] = field(default_factory=set)
    extra: Mapping = field(default_factory=dict)

    @property
    def key(self):
        if self.authors:
            author = self.authors[0].split(" ")[0].replace(",", "")
        else:
            author = "anonymous"
        year = self.year
        return f"{author}{year}".lower()

    @property
    def label(self):
        if self._label is not None:
            return self._label
        pieces = {
            "AU": self.authors[0].replace(",", "") if self.authors else "anonymous",
            "PY": str(self.year) if self.year else None,
            "J9": str(self.journal) if self.journal else None,
            "VL": f"V{self.volume}" if self.volume else None,
            "BP": f"P{self.page}" if self.page else None,
            "DI": f"DOI {self.doi}" if self.doi else None,
        }
        return ", ".join(value for value in pieces.values() if value)
