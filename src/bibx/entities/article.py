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
    references: Optional[List["Article"]] = field(default_factory=list)
    keywords: Optional[List[str]] = field(default_factory=list)
    sources: Optional[Set[str]] = field(default_factory=set)
    extra: Optional[Mapping] = field(default_factory=dict)
