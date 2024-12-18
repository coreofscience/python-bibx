import logging
from typing import TextIO

from bibx._entities.article import Article
from bibx._entities.collection import Collection
from bibx._entities.collection_builders.scopus_bib import ScopusBibCollectionBuilder
from bibx._entities.collection_builders.scopus_ris import ScopusRisCollectionBuilder
from bibx._entities.collection_builders.wos import WosCollectionBuilder
from bibx.algorithms.sap import Sap
from bibx.exceptions import BibXError

logger = logging.getLogger(__name__)

__all__ = [
    "Article",
    "Collection",
    "Sap",
    "read_scopus_bib",
    "read_scopus_ris",
    "read_wos",
    "read_any",
]

__version__ = "0.2.0"


def read_scopus_bib(*files: TextIO) -> Collection:
    """
    Takes any number of bibtex files from scopus and generates a collection.

    :param files: Scopus bib files open.
    :return: the collection
    """
    return ScopusBibCollectionBuilder(*files).build()


def read_scopus_ris(*files: TextIO) -> Collection:
    """
    Takes any number of ris files from scopus and generates a collection.

    :param files: Scopus bib files open.
    :return: the collection
    """
    return ScopusRisCollectionBuilder(*files).build()


def read_wos(*files: TextIO) -> Collection:
    """
    Takes any number of wos text files and returns a collection.

    :param files: WoS files open.
    :return: the collection
    """
    return WosCollectionBuilder(*files).build()


def read_any(file: TextIO) -> Collection:
    """
    Tries to read a file with the supported formats.
    """
    for handler in (read_wos, read_scopus_ris, read_scopus_bib):
        try:
            return handler(file)
        except BibXError as e:
            logger.debug(f"Error: {e}")
        except ValueError:
            logger.debug(
                f"Error: the {handler.__name__} function does not support this file"
            )
    raise ValueError("Unsupported file type")
