"""BibX is a library to work with bibliographic data."""

import logging
from typing import TextIO

from bibx.algorithms.sap import Sap
from bibx.article import Article
from bibx.builders.openalex import HandleReferences, OpenAlexCollectionBuilder
from bibx.builders.scopus_bib import ScopusBibCollectionBuilder
from bibx.builders.scopus_ris import ScopusRisCollectionBuilder
from bibx.builders.wos import WosCollectionBuilder
from bibx.collection import Collection
from bibx.exceptions import BibXError

logger = logging.getLogger(__name__)

__all__ = [
    "Article",
    "Collection",
    "HandleReferences",
    "Sap",
    "query_openalex",
    "read_any",
    "read_scopus_bib",
    "read_scopus_ris",
    "read_wos",
]

__version__ = "0.4.1"


def query_openalex(
    query: str,
    limit: int = 600,
    references: HandleReferences = HandleReferences.BASIC,
) -> Collection:
    """Query OpenAlex and return a collection."""
    return OpenAlexCollectionBuilder(query, limit, references=references).build()


def read_scopus_bib(*files: TextIO) -> Collection:
    """Take any number of bibtex files from scopus and generates a collection.

    :param files: Scopus bib files open.
    :return: the collection
    """
    return ScopusBibCollectionBuilder(*files).build()


def read_scopus_ris(*files: TextIO) -> Collection:
    """Take any number of ris files from scopus and generates a collection.

    :param files: Scopus bib files open.
    :return: the collection
    """
    return ScopusRisCollectionBuilder(*files).build()


def read_wos(*files: TextIO) -> Collection:
    """Take any number of wos text files and returns a collection.

    :param files: WoS files open.
    :return: the collection
    """
    return WosCollectionBuilder(*files).build()


def read_any(file: TextIO) -> Collection:
    """Try to read a file with the supported formats."""
    for handler in (read_wos, read_scopus_ris, read_scopus_bib):
        try:
            return handler(file)
        except BibXError as e:
            logger.debug("Error: %s", e)
        except ValueError:
            logger.debug(
                "Error: the %s function does not support this file", handler.__name__
            )
    message = "Unsupported file type"
    raise ValueError(message)
