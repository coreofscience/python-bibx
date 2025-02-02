import collections
import functools
import logging
import re
from collections.abc import Iterable, Mapping
from contextlib import suppress
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Optional, TextIO, Union

from bibx.article import Article
from bibx.collection import Collection
from bibx.exceptions import (
    InvalidIsiLineError,
    InvalidIsiReferenceError,
    MissingCriticalInformationError,
)

from .base import CollectionBuilder

logger = logging.getLogger(__name__)


def _joined(values: list[str], separator: str = " ") -> str:
    return separator.join(value.strip() for value in values)


def _ident(values: list[str]) -> list[str]:
    return [value.strip() for value in values]


def _delimited(values: list[str], delimiter: str = "; ") -> list[str]:
    return [
        word.replace(delimiter.strip(), "")
        for words in values
        for word in words.split(delimiter)
        if word
    ]


def _integer(values: list[str]) -> int:
    if len(values) > 1:
        message = f"Expected no more than one item and got {len(values)}"
        raise ValueError(message)

    first, *_ = values
    return int(first.strip())


@dataclass(frozen=True)
class _IsiField:
    key: str
    description: str
    parser: Callable
    aliases: list[str]

    def parse(self, value: list[str]) -> Union[str, int, list[str]]:
        return self.parser(value)


class WosCollectionBuilder(CollectionBuilder):
    """Builder for collections of articles from Web of Science (WoS) ISI files."""

    ISI_LINE_PATTERN = re.compile(
        r"^(null|.)?((?P<field>[A-Z0-9]{2})|  )( (?P<value>.*))?$"
    )
    ISI_CITATION_PATTERN = re.compile(
        r"""^(?P<AU>[^,]+),[ ]          # First author
            (?P<PY>\d{4}),[ ]           # Publication year
            (?P<J9>[^,]+)               # Journal
            (,[ ]V(?P<VL>[\w\d-]+))?    # Volume
            (,[ ][Pp](?P<BP>\w+))?      # Start page
            (,[ ]DOI[ ](?P<DI>.+))?     # The all important DOI
            """,
        re.X,
    )

    FIELDS: ClassVar = {
        "AB": _IsiField("AB", "Abstract", _joined, ["abstract"]),
        "AF": _IsiField("AF", "Author Full Names", _ident, ["author_full_names"]),
        "AR": _IsiField("AR", "Article Number", _joined, ["article_number"]),
        "AU": _IsiField("AU", "Authors", _ident, ["authors"]),
        "BA": _IsiField("BA", "Book Authors", _ident, ["book_authors"]),
        "BE": _IsiField("BE", "Editors", _ident, ["editors"]),
        "BF": _IsiField(
            "BF", "Book Authors Full Name", _ident, ["book_authors_full_name"]
        ),
        "BN": _IsiField(
            "BN",
            "International Standard Book Number (ISBN)",
            _joined,
            ["international_standard_book_number"],
        ),
        "BP": _IsiField("BP", "Beginning Page", _joined, ["beginning_page"]),
        "BS": _IsiField(
            "BS", "Book Series Subtitle", _joined, ["book_series_subtitle"]
        ),
        "C1": _IsiField("C1", "Author Address", _ident, ["author_address"]),
        "CA": _IsiField("CA", "Group Authors", _ident, ["group_authors"]),
        "CL": _IsiField("CL", "Conference Location", _joined, ["conference_location"]),
        "CR": _IsiField(
            "CR",
            "Cited References",
            _ident,
            ["cited_references", "references", "citations"],
        ),
        "CT": _IsiField(
            "CT",
            "Conference Title",
            functools.partial(_joined, separator="\n"),
            ["conference_title"],
        ),
        "CY": _IsiField("CY", "Conference Date", _joined, ["conference_date"]),
        "DE": _IsiField("DE", "Author Keywords", _delimited, ["author_keywords"]),
        "DI": _IsiField(
            "DI",
            "Digital Object Identifier (DOI)",
            _joined,
            ["digital_object_identifier", "DOI"],
        ),
        "DT": _IsiField("DT", "Document Type", _joined, ["document_type"]),
        "D2": _IsiField(
            "D2",
            "Book Digital Object Identifier (DOI)",
            _joined,
            ["book_digital_object_identifier"],
        ),
        "ED": _IsiField("ED", "Editors", _ident, ["editors"]),
        "EM": _IsiField("EM", "E-mail Address", _ident, ["email_address"]),
        "EI": _IsiField(
            "EI",
            "Electronic International Standard Serial Number (eISSN)",
            _joined,
            ["eissn"],
        ),
        "EP": _IsiField("EP", "Ending Page", _joined, ["ending_page"]),
        "FU": _IsiField(
            "FU",
            "Funding Agency and Grant Number",
            _delimited,
            ["funding_agency_and_grant_number"],
        ),
        "FX": _IsiField("FX", "Funding Text", _joined, ["funding_text"]),
        "GA": _IsiField(
            "GA",
            "Document Delivery Number",
            _joined,
            ["document_delivery_number"],
        ),
        "GP": _IsiField("GP", "Book Group Authors", _ident, ["book_group_authors"]),
        "HO": _IsiField("HO", "Conference Host", _joined, ["conference_host"]),
        "ID": _IsiField(
            "ID", "Keywords Plus", _delimited, ["keywords_plus", "keywords"]
        ),
        "IS": _IsiField("IS", "Issue", _joined, ["issue"]),
        "J9": _IsiField(
            "J9",
            "29-Character Source Abbreviation",
            _joined,
            ["source_abbreviation"],
        ),
        "JI": _IsiField(
            "JI", "ISO Source Abbreviation", _joined, ["iso_source_abbreviation"]
        ),
        "LA": _IsiField("LA", "Language", _joined, ["language"]),
        "MA": _IsiField("MA", "Meeting Abstract", _joined, ["meeting_abstract"]),
        "NR": _IsiField(
            "NR", "Cited Reference Count", _integer, ["cited_reference_count"]
        ),
        "OI": _IsiField(
            "OI",
            "ORCID Identifier (Open Researcher and Contributor ID)",
            _delimited,
            ["orcid_identifier"],
        ),
        "P2": _IsiField(
            "P2",
            "Chapter count (Book Citation Index)",
            _integer,
            ["chapter_count"],
        ),
        "PA": _IsiField(
            "PA",
            "Publisher Address",
            functools.partial(_joined, separator="\n"),
            ["publisher_address"],
        ),
        "PD": _IsiField("PD", "Publication Date", _joined, ["publication_date"]),
        "PG": _IsiField("PG", "Page Count", _integer, ["page_count"]),
        "PI": _IsiField("PI", "Publisher City", _joined, ["publisher_city"]),
        "PM": _IsiField("PM", "PubMed ID", _joined, ["pubmed_id"]),
        "PN": _IsiField("PN", "Part Number", _joined, ["part_number"]),
        "PT": _IsiField(
            "PT",
            "Publication Type (J=Journal; B=Book; S=Series; P=Patent)",
            _joined,
            ["publication_type"],
        ),
        "PU": _IsiField("PU", "Publisher", _joined, ["publisher"]),
        "PY": _IsiField(
            "PY",
            "Year Published",
            _integer,
            ["year_published", "year", "publication_year"],
        ),
        "RI": _IsiField(
            "RI", "ResearcherID Number", _delimited, ["researcherid_number"]
        ),
        "RP": _IsiField("RP", "Reprint Address", _joined, ["reprint_address"]),
        "SC": _IsiField("SC", "Research Areas", _delimited, ["research_areas"]),
        "SE": _IsiField("SE", "Book Series Title", _joined, ["book_series_title"]),
        "SI": _IsiField("SI", "Special Issue", _joined, ["special_issue"]),
        "SN": _IsiField(
            "SN",
            "International Standard Serial Number (ISSN)",
            _joined,
            ["issn"],
        ),
        "SO": _IsiField("SO", "Publication Name", _joined, ["publication_name"]),
        "SP": _IsiField(
            "SP",
            "Conference Sponsors",
            functools.partial(_delimited, delimiter=", "),
            ["conference_sponsors"],
        ),
        "SU": _IsiField("SU", "Supplement", _joined, ["supplement"]),
        "TC": _IsiField(
            "TC",
            "Web of Science Core Collection Times Cited Count",
            _integer,
            ["wos_times_cited_count", "wos_times_cited"],
        ),
        "TI": _IsiField("TI", "Document Title", _joined, ["title"]),
        "U1": _IsiField("U1", "Usage Count (Last 180 Days)", _integer, ["usage_count"]),
        "U2": _IsiField("U2", "Usage Count (Since 2013)", _integer, ["usage_count"]),
        "UT": _IsiField(
            "UT",
            "Unique Article Identifier",
            _joined,
            ["unique_article_identifier"],
        ),
        "VL": _IsiField("VL", "Volume", _joined, ["volume"]),
        "WC": _IsiField(
            "WC",
            "Web of Science Categories",
            _delimited,
            ["web_of_science_categories"],
        ),
        "Z9": _IsiField(
            "Z9",
            "Total Times Cited Count (WoS Core, BCI, and CSCD)",
            _integer,
            ["total_times_cited_count", "times_cited"],
        ),
    }

    def __init__(self, *isi_files: TextIO) -> None:
        self._files = isi_files
        for file in self._files:
            file.seek(0)

    def build(self) -> Collection:
        """Build a collection of articles from Web of Science (WoS) ISI files."""
        articles = self._get_articles_from_files()
        return Collection(list(articles))

    def _get_articles_as_str_from_files(self) -> Iterable[str]:
        for file in self._files:
            articles_as_str = file.read().split("\n\n")
            for article_as_str in articles_as_str:
                if article_as_str.strip() not in ("ER", "EF") and article_as_str:
                    # Strip `\n` at the end of the article so we don't trip
                    yield article_as_str.strip()

    def _get_articles_from_files(self) -> Iterable[Article]:
        for article_as_str in self._get_articles_as_str_from_files():
            with suppress(MissingCriticalInformationError):
                article = self._parse_article_from_str(article_as_str)
                yield article

    @classmethod
    def _get_articles_from_references(
        cls, references: Optional[list[str]]
    ) -> Iterable[Article]:
        if not references:
            return
        for ref_str in references:
            with suppress(InvalidIsiReferenceError):
                yield cls._parse_reference_from_str(ref_str)

    @classmethod
    def _parse_article_from_str(cls, article_as_str: str) -> Article:
        article_data: dict[str, list[str]] = collections.defaultdict(list)
        article_data.setdefault("CR", [])
        field = None
        for line in article_as_str.split("\n"):
            match = cls.ISI_LINE_PATTERN.match(line)
            if not match:
                raise InvalidIsiLineError(line)
            parsed = match.groupdict()
            field = parsed.get("field") or field
            if not field or "value" not in parsed or parsed["value"] is None:
                continue
            article_data[field].append(parsed["value"])
        processed = cls._parse_all(dict(article_data))
        doi = processed.get("DOI")
        return (
            Article(
                label=doi or "replaceme",
                ids=set() if doi is None else {f"doi:{doi}"},
                authors=processed.get("authors", []),
                year=processed.get("year"),
                title=processed.get("title"),
                journal=processed.get("source_abbreviation"),
                volume=processed.get("volume"),
                issue=processed.get("issue"),
                page=processed.get("beginning_page"),
                doi=doi,
                times_cited=processed.get("times_cited"),
                references=list(
                    cls._get_articles_from_references(processed.get("references"))
                ),
                keywords=processed.get("keywords", []),
                extra=processed,
                sources={article_as_str},
            )
            .add_simple_id()
            .set_simple_label()
        )

    @classmethod
    def _parse_reference_from_str(cls, reference: str) -> Article:
        match = cls.ISI_CITATION_PATTERN.match(reference)
        if not match:
            raise InvalidIsiReferenceError(reference)
        data = {key: [value] for key, value in match.groupdict().items() if value}
        processed = cls._parse_all(data)
        doi = processed.get("DOI")
        article = Article(
            label=reference,
            ids=set() if doi is None else {f"doi:{doi}"},
            title=processed.get("title"),
            authors=processed.get("authors", []),
            # FIXME: Year is required here
            year=processed.get("year", 1999),
            journal=processed.get("source_abbreviation"),
            volume=processed.get("volume"),
            page=processed.get("beginning_page"),
            doi=processed.get("DOI"),
            extra=processed,
            sources={reference},
            times_cited=processed.get("times_cited"),
        )
        article.add_simple_id()
        return article

    @classmethod
    def _parse_all(cls, article_data: dict[str, list[str]]) -> Mapping[str, Any]:
        processed_data = {}
        for key, values in article_data.items():
            parsed_values_dict = cls._parse(key, values)
            processed_data.update(parsed_values_dict)
        return processed_data

    @classmethod
    def _parse(cls, key: str, value: list[str]) -> dict:
        if key in {"FN", "VR", "ER"}:
            return {}

        if key in cls.FIELDS:
            field = cls.FIELDS[key]
            parsed_value = field.parse(value)
            return {new_key: parsed_value for new_key in [field.key, *field.aliases]}

        logger.debug("Found an unknown field with key %s and value %s", key, value)
        return {key: _ident(value)}
