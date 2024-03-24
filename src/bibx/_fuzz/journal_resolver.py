"""
A fuzzy journal resolver that uses the Levenshtein distance to resolve journal names.
"""

from pybktree import BKTree

from bibx._entities.data_sets.journal_data_set import JournalDataSet
from bibx._entities.journal import Journal
from bibx._fuzz.distance import distance
from bibx._fuzz.utils import normalize
from bibx._utils.singleton_meta import SingletonMeta


class JournalResolver(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.journal_data_set = JournalDataSet()
        self._bk_tree: BKTree | None = None

    @property
    def bk_tree(self) -> BKTree:
        if self._bk_tree is None:
            self._bk_tree = BKTree(distance_func=distance)
            for word in self.journal_data_set.titles_and_abbreviations:
                self._bk_tree.add(word)
        return self._bk_tree

    def resolve(self, journal: str) -> Journal | None:
        _journal = normalize(journal)
        if _journal == "":
            return None
        if _journal in self.journal_data_set.titles_and_abbreviations:
            return self.journal_data_set.organized_journals[_journal]
        names = [
            name for distance, name in self.bk_tree.find(_journal, 1) if distance == 0
        ]
        if not names:
            return None
        name = max(names, key=len)
        return self.journal_data_set.organized_journals[name]
