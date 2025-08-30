from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import TypeVar

T = TypeVar("T")


def _keep(a: T, b: T) -> T:
    return a if a is not None else b


def _keep_longest(a: str, b: str) -> str:
    return a if len(a) > len(b) else b


@dataclass
class Article:
    """A scientific article."""

    label: str
    ids: set[str]
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    title: str | None = None
    journal: str | None = None
    volume: str | None = None
    issue: str | None = None
    page: str | None = None
    doi: str | None = None
    _permalink: str | None = None
    times_cited: int | None = None
    references: list["Article"] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    sources: set[str] = field(default_factory=set)
    extra: Mapping = field(default_factory=dict)

    def merge(self, other: "Article") -> "Article":
        """Merge two articles into a new one."""
        return Article(
            label=_keep_longest(self.label, other.label),
            ids=self.ids.union(other.ids),
            authors=self.authors if self.authors else other.authors,
            year=_keep(self.year, other.year),
            title=_keep(self.title, other.title),
            journal=_keep(self.journal, other.journal),
            volume=_keep(self.volume, other.volume),
            issue=_keep(self.issue, other.issue),
            page=_keep(self.page, other.page),
            doi=_keep(self.doi, other.doi),
            _permalink=_keep(self._permalink, other._permalink),
            times_cited=_keep(self.times_cited, other.times_cited),
            references=self.references or other.references,
            keywords=self.keywords or other.keywords,
            sources=self.sources.union(other.sources),
            extra={**self.extra, **other.extra},
        )

    @property
    def key(self) -> str:
        """Return the first ID of the article."""
        return next(iter(sorted(self.ids)))

    @property
    def simple_label(self) -> str | None:
        """Return a simple label for the article."""
        pieces = {
            "AU": self.authors[0].replace(",", "") if self.authors else None,
            "PY": str(self.year) if self.year else None,
            "J9": str(self.journal) if self.journal else None,
            "VL": f"V{self.volume}" if self.volume else None,
            "BP": f"P{self.page}" if self.page else None,
            "DI": f"DOI {self.doi}" if self.doi else None,
        }
        if not any(pieces.values()):
            return None
        return ", ".join(value for value in pieces.values() if value)

    @property
    def permalink(self) -> str | None:
        """Return the permalink of the article."""
        if self._permalink is not None:
            return self._permalink
        if self.doi is not None:
            return f"https://doi.org/{self.doi}"
        return None

    @property
    def simple_id(self) -> str | None:
        """Return a simple ID for the article."""
        if not self.authors or self.year is None:
            return None
        author = self.authors[0].split(" ")[0].replace(",", "")
        return f"{author}{self.year}".lower()

    def __repr__(self) -> str:
        """Return a string representation of the article."""
        return f"Article(ids={self.ids!r}, authors={self.authors!r})"

    def add_simple_id(self) -> "Article":
        """Add a simple ID to the article."""
        if self.simple_id is None:
            return self
        self.ids.add(f"simple:{self.simple_id}")
        return self

    def set_simple_label(self) -> "Article":
        """Set the simple label as the label of the article."""
        if self.simple_label is None:
            return self
        self.label = self.simple_label
        return self

    def info(
        self,
    ) -> dict[str, str | int | list[str] | None]:
        """Return a dictionary with the information of the article."""
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
