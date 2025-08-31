"""BibX is a library to work with bibliographic data."""

import logging
from typing import TextIO

from bibx.algorithms.sap import Sap
from bibx.exceptions import BibXError
from bibx.models.article import Article
from bibx.models.collection import Collection
from bibx.sources.openalex import EnrichReferences, OpenAlexSource
from bibx.sources.scopus_bib import ScopusBibSource
from bibx.sources.scopus_csv import ScopusCsvSource
from bibx.sources.scopus_ris import ScopusRisSource
from bibx.sources.wos import WosSource

logger = logging.getLogger(__name__)

__all__ = [
    "Article",
    "Collection",
    "EnrichReferences",
    "Sap",
    "query_openalex",
    "read_any",
    "read_scopus_bib",
    "read_scopus_csv",
    "read_scopus_ris",
    "read_wos",
]

__version__ = "0.9.0"


def query_openalex(
    query: str,
    limit: int = 600,
    enrich: EnrichReferences = EnrichReferences.BASIC,
) -> Collection:
    """Query OpenAlex and return a collection."""
    return OpenAlexSource(query, limit, enrich=enrich).build()


def read_scopus_bib(*files: TextIO) -> Collection:
    """Take any number of bibtex files from scopus and generates a collection.

    :param files: Scopus bib files open.
    :return: the collection
    """
    return ScopusBibSource(*files).build()


def read_scopus_ris(*files: TextIO) -> Collection:
    """Take any number of ris files from scopus and generates a collection.

    :param files: Scopus bib files open.
    :return: the collection
    """
    return ScopusRisSource(*files).build()


def read_scopus_csv(*files: TextIO) -> Collection:
    """Take any number of csv files from scopus and generates a collection.

    :param files: Scopus csv files open.
    :return: the collection
    """
    return ScopusCsvSource(*files).build()


def read_wos(*files: TextIO) -> Collection:
    """Take any number of wos text files and returns a collection.

    :param files: WoS files open.
    :return: the collection
    """
    return WosSource(*files).build()


def read_any(file: TextIO) -> Collection:
    """Try to read a file with the supported formats."""
    for handler in (read_wos, read_scopus_ris, read_scopus_csv, read_scopus_bib):
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
