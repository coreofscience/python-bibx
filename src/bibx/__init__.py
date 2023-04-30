from typing import TextIO

from bibx._entities.article import Article
from bibx._entities.collection import Collection
from bibx._entities.collection_builders.isi import IsiCollectionBuilder
from bibx._entities.collection_builders.scopus import ScopusCollectionBuilder
from bibx.algorithms.sap import Sap
from bibx.exceptions import BibXError

__all__ = ["Article", "Collection", "Sap", "read_scopus", "read_wos", "read_any"]

__version__ = "0.0.1a2"


def read_scopus(*files: TextIO) -> Collection:
    """
    Takes any number of bibtex files from scopus and generates a collection.

    :param files: Scopus bib files open.
    :return: the collection
    """
    return ScopusCollectionBuilder(*files).build()


def read_wos(*files: TextIO) -> Collection:
    """
    Takes any number of wos text files and returns a collection.

    :param files: WoS files open.
    :return: the collection
    """
    return IsiCollectionBuilder(*files).build()


def read_any(file: TextIO) -> Collection:
    """
    Tries to read a file with the supported formats.
    """
    try:
        return read_wos(file)
    except BibXError:
        return read_scopus(file)
