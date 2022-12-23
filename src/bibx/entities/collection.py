from dataclasses import dataclass
from typing import List

from bibx.entities.article import Article


@dataclass
class Collection:
    articles: List[Article]

    @property
    def citation_pairs(self):
        raise NotImplementedError("We need implement this.")
