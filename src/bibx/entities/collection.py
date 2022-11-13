from dataclasses import dataclass
from typing import List

from bibx.entities.article import Article




@dataclass
class Collection:g
    articles: List[Article]


    @classmethod
    def build(cls, context, type_):
        if type_ == 'a':
            tales_a(context)
        elif type_ == 'b':
            tales_b(context, type_)
        ...
