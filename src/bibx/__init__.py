from io import StringIO

from src.bibx.entities.collection import Collection
from src.bibx.entities.collection_builders.isi import IsiCollectionBuilder
from src.bibx.entities.collection_builders.scopus import ScopusCollectionBuilder


def read_scopus(*files: StringIO) -> Collection:
    """
    Takes any number of bibtex files from scopus and generates a collection.

    :param files: Scopus bib files open.
    :return: the collection
    """
    return ScopusCollectionBuilder(*files).build()


def read_wos(*files: StringIO) -> Collection:
    """
    Takes any number of wos text files and returns a collection.

    :param files: WoS files open.
    :return: the collection
    """
    return IsiCollectionBuilder(*files).build()
