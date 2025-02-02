from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Optional, TypeVar, Union

T = TypeVar("T")


def _keep(a: T, b: T) -> T:
    return a if a is not None else b


@dataclass
class Article:
    ids: set[str]
    authors: list[str] = field(default_factory=list)
    year: Optional[int] = None
    title: Optional[str] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    page: Optional[str] = None
    doi: Optional[str] = None
    _label: Optional[str] = None
    _permalink: Optional[str] = None
    times_cited: Optional[int] = None
    references: list["Article"] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    sources: set[str] = field(default_factory=set)
    extra: Mapping = field(default_factory=dict)

    def merge(self, other: "Article") -> "Article":
        """Merge two articles into a new one."""
        return Article(
            ids=self.ids.union(other.ids),
            authors=self.authors if self.authors else other.authors,
            year=_keep(self.year, other.year),
            title=_keep(self.title, other.title),
            journal=_keep(self.journal, other.journal),
            volume=_keep(self.volume, other.volume),
            issue=_keep(self.issue, other.issue),
            page=_keep(self.page, other.page),
            doi=_keep(self.doi, other.doi),
            _label=_keep(self._label, other._label),
            _permalink=_keep(self._permalink, other._permalink),
            times_cited=_keep(self.times_cited, other.times_cited),
            references=self.references or other.references,
            keywords=self.keywords or other.keywords,
            sources=self.sources.union(other.sources),
            extra={**self.extra, **other.extra},
        )

    @property
    def key(self) -> str:
        return next(iter(sorted(self.ids)))

    @property
    def label(self) -> str:
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

    @property
    def permalink(self) -> Optional[str]:
        if self._permalink is not None:
            return self._permalink
        if self.doi is not None:
            return f"https://doi.org/{self.doi}"
        return None

    @property
    def simple_id(self) -> Optional[str]:
        if self.authors and self.year is not None:
            author = self.authors[0].split(" ")[0].replace(",", "")
            return f"{author}{self.year}".lower()
        return None

    def __repr__(self) -> str:
        return f"Article(ids={self.ids!r}, authors={self.authors!r})"

    def add_simple_id(self) -> None:
        if self.simple_id is None:
            return
        self.ids.add(f"simple:{self.simple_id}")

    def info(
        self,
    ) -> dict[str, Union[str, int, list[str], None]]:
        return {
            "permalink": self.permalink,
            "label": self.label,
            "authors": self.authors,
            "year": self.year,
            "title": self.title,
            "journal": self.journal,
            "volume": self.volume,
            "issue": self.issue,
            "page": self.page,
            "doi": self.doi,
            "times_cited": self.times_cited,
            "keywords": self.keywords,
            "sources": list(self.sources),
        }
