from dataclasses import dataclass
from typing import Iterable, List, Tuple

from bibx.entities.article import Article


@dataclass
class Collection:
    articles: List[Article]

    @property
    def citation_pairs(self) -> Iterable[Tuple[Article, Article]]:
        for article in self.articles:
            if not article.references:
                continue
            for reference in article.references:
                yield (article, reference)
