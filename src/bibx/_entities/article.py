from dataclasses import dataclass, field
from typing import List, Mapping, Optional, Set


@dataclass
class Article:
    authors: List[str]
    year: int
    title: Optional[str] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    page: Optional[str] = None
    doi: Optional[str] = None
    _label: Optional[str] = None
    references: List["Article"] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    sources: Set[str] = field(default_factory=set)
    extra: Mapping = field(default_factory=dict)

    @property
    def key(self):
        author = self.authors[0].split(" ")[0].replace(",", "")
        year = self.year
        return f"{author}{year}".lower()

    @property
    def label(self):
        if self._label is not None:
            return self._label
        pieces = {
            "AU": self.authors[0].replace(",", ""),
            "PY": str(self.year),
            "J9": str(self.journal),
            "VL": f"V{self.volume}" if self.volume else None,
            "BP": f"P{self.page}" if self.page else None,
            "DI": f"DOI {self.doi}" if self.doi else None,
        }
        return ", ".join(value for value in pieces.values() if value)
