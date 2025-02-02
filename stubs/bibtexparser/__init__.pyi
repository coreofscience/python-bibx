from typing import TextIO

from _typeshed import Incomplete
from bibtexparser.bparser import BibDatabase

def load(bibtex_file: TextIO, parser: Incomplete | None = None) -> BibDatabase: ...
