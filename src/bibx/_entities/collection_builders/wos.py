import collections
import functools
import logging
import re
from contextlib import suppress
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, TextIO

from bibx._entities.article import Article
from bibx._entities.collection import Collection
from bibx._entities.collection_builders.base import CollectionBuilder
from bibx.exceptions import (
    InvalidIsiLineError,
    InvalidIsiReference,
    MissingCriticalInformation,
)

logger = logging.getLogger(__name__)


def _joined(values: List[str], separator: str = " ") -> str:
    return separator.join(value.strip() for value in values)


def _ident(values: List[str]) -> List[str]:
    return [value.strip() for value in values]


def _delimited(values: List[str], delimiter: str = "; ") -> List[str]:
    return [
        word.replace(delimiter.strip(), "")
        for words in values
        for word in words.split(delimiter)
        if word
    ]


def _integer(values: List[str]) -> int:
    if len(values) > 1:
        raise ValueError(f"Expected no more than one item and got {len(values)}")

    first, *_ = values
    return int(first.strip())


@dataclass(frozen=True)
class IsiField:
    key: str
    description: str
    parser: Callable
    aliases: List[str]

    def parse(self, value: List[str]):
        return self.parser(value)


class WosCollectionBuilder(CollectionBuilder):
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

    FIELDS = {
        "AB": IsiField("AB", "Abstract", _joined, ["abstract"]),
        "AF": IsiField("AF", "Author Full Names", _ident, ["author_full_names"]),
        "AR": IsiField("AR", "Article Number", _joined, ["article_number"]),
        "AU": IsiField("AU", "Authors", _ident, ["authors"]),
        "BA": IsiField("BA", "Book Authors", _ident, ["book_authors"]),
        "BE": IsiField("BE", "Editors", _ident, ["editors"]),
        "BF": IsiField(
            "BF", "Book Authors Full Name", _ident, ["book_authors_full_name"]
        ),
        "BN": IsiField(
            "BN",
            "International Standard Book Number (ISBN)",
            _joined,
            ["international_standard_book_number"],
        ),
        "BP": IsiField("BP", "Beginning Page", _joined, ["beginning_page"]),
        "BS": IsiField("BS", "Book Series Subtitle", _joined, ["book_series_subtitle"]),
        "C1": IsiField("C1", "Author Address", _ident, ["author_address"]),
        "CA": IsiField("CA", "Group Authors", _ident, ["group_authors"]),
        "CL": IsiField("CL", "Conference Location", _joined, ["conference_location"]),
        "CR": IsiField(
            "CR",
            "Cited References",
            _ident,
            ["cited_references", "references", "citations"],
        ),
        "CT": IsiField(
            "CT",
            "Conference Title",
            functools.partial(_joined, separator="\n"),
            ["conference_title"],
        ),
        "CY": IsiField("CY", "Conference Date", _joined, ["conference_date"]),
        "DE": IsiField("DE", "Author Keywords", _delimited, ["author_keywords"]),
        "DI": IsiField(
            "DI",
            "Digital Object Identifier (DOI)",
            _joined,
            ["digital_object_identifier", "DOI"],
        ),
        "DT": IsiField("DT", "Document Type", _joined, ["document_type"]),
        "D2": IsiField(
            "D2",
            "Book Digital Object Identifier (DOI)",
            _joined,
            ["book_digital_object_identifier"],
        ),
        "ED": IsiField("ED", "Editors", _ident, ["editors"]),
        "EM": IsiField("EM", "E-mail Address", _ident, ["email_address"]),
        "EI": IsiField(
            "EI",
            "Electronic International Standard Serial Number (eISSN)",
            _joined,
            ["eissn"],
        ),
        "EP": IsiField("EP", "Ending Page", _joined, ["ending_page"]),
        "FU": IsiField(
            "FU",
            "Funding Agency and Grant Number",
            _delimited,
            ["funding_agency_and_grant_number"],
        ),
        "FX": IsiField("FX", "Funding Text", _joined, ["funding_text"]),
        "GA": IsiField(
            "GA",
            "Document Delivery Number",
            _joined,
            ["document_delivery_number"],
        ),
        "GP": IsiField("GP", "Book Group Authors", _ident, ["book_group_authors"]),
        "HO": IsiField("HO", "Conference Host", _joined, ["conference_host"]),
        "ID": IsiField(
            "ID", "Keywords Plus", _delimited, ["keywords_plus", "keywords"]
        ),
        "IS": IsiField("IS", "Issue", _joined, ["issue"]),
        "J9": IsiField(
            "J9",
            "29-Character Source Abbreviation",
            _joined,
            ["source_abbreviation"],
        ),
        "JI": IsiField(
            "JI", "ISO Source Abbreviation", _joined, ["iso_source_abbreviation"]
        ),
        "LA": IsiField("LA", "Language", _joined, ["language"]),
        "MA": IsiField("MA", "Meeting Abstract", _joined, ["meeting_abstract"]),
        "NR": IsiField(
            "NR", "Cited Reference Count", _integer, ["cited_reference_count"]
        ),
        "OI": IsiField(
            "OI",
            "ORCID Identifier (Open Researcher and Contributor ID)",
            _delimited,
            ["orcid_identifier"],
        ),
        "P2": IsiField(
            "P2",
            "Chapter count (Book Citation Index)",
            _integer,
            ["chapter_count"],
        ),
        "PA": IsiField(
            "PA",
            "Publisher Address",
            functools.partial(_joined, separator="\n"),
            ["publisher_address"],
        ),
        "PD": IsiField("PD", "Publication Date", _joined, ["publication_date"]),
        "PG": IsiField("PG", "Page Count", _integer, ["page_count"]),
        "PI": IsiField("PI", "Publisher City", _joined, ["publisher_city"]),
        "PM": IsiField("PM", "PubMed ID", _joined, ["pubmed_id"]),
        "PN": IsiField("PN", "Part Number", _joined, ["part_number"]),
        "PT": IsiField(
            "PT",
            "Publication Type (J=Journal; B=Book; S=Series; P=Patent)",
            _joined,
            ["publication_type"],
        ),
        "PU": IsiField("PU", "Publisher", _joined, ["publisher"]),
        "PY": IsiField(
            "PY",
            "Year Published",
            _integer,
            ["year_published", "year", "publication_year"],
        ),
        "RI": IsiField(
            "RI", "ResearcherID Number", _delimited, ["researcherid_number"]
        ),
        "RP": IsiField("RP", "Reprint Address", _joined, ["reprint_address"]),
        "SC": IsiField("SC", "Research Areas", _delimited, ["research_areas"]),
        "SE": IsiField("SE", "Book Series Title", _joined, ["book_series_title"]),
        "SI": IsiField("SI", "Special Issue", _joined, ["special_issue"]),
        "SN": IsiField(
            "SN",
            "International Standard Serial Number (ISSN)",
            _joined,
            ["issn"],
        ),
        "SO": IsiField("SO", "Publication Name", _joined, ["publication_name"]),
        "SP": IsiField(
            "SP",
            "Conference Sponsors",
            functools.partial(_delimited, delimiter=", "),
            ["conference_sponsors"],
        ),
        "SU": IsiField("SU", "Supplement", _joined, ["supplement"]),
        "TC": IsiField(
            "TC",
            "Web of Science Core Collection Times Cited Count",
            _integer,
            ["wos_times_cited_count", "wos_times_cited"],
        ),
        "TI": IsiField("TI", "Document Title", _joined, ["title"]),
        "U1": IsiField("U1", "Usage Count (Last 180 Days)", _integer, ["usage_count"]),
        "U2": IsiField("U2", "Usage Count (Since 2013)", _integer, ["usage_count"]),
        "UT": IsiField(
            "UT",
            "Unique Article Identifier",
            _joined,
            ["unique_article_identifier"],
        ),
        "VL": IsiField("VL", "Volume", _joined, ["volume"]),
        "WC": IsiField(
            "WC",
            "Web of Science Categories",
            _delimited,
            ["web_of_science_categories"],
        ),
        "Z9": IsiField(
            "Z9",
            "Total Times Cited Count (WoS Core, BCI, and CSCD)",
            _integer,
            ["total_times_cited_count", "times_cited"],
        ),
    }

    def __init__(self, *isi_files: TextIO):
        self._files = isi_files
        for file in self._files:
            file.seek(0)

    def build(self) -> Collection:
        articles = self._get_articles_from_files()
        return Collection(list(articles))

    def _get_articles_as_str_from_files(self) -> Iterable[str]:
        for file in self._files:
            articles_as_str = file.read().split("\n\n")
            for article_as_str in articles_as_str:
                if article_as_str != "ER" and article_as_str:
                    # Strip `\n` at the end of the article so we don't trip
                    yield article_as_str.strip()

    def _get_articles_from_files(self) -> Iterable[Article]:
        for article_as_str in self._get_articles_as_str_from_files():
            with suppress(MissingCriticalInformation):
                article = self._parse_article_from_str(article_as_str)
                yield article

    @classmethod
    def _get_articles_from_references(
        cls, references: Optional[List[str]]
    ) -> Iterable[Article]:
        if not references:
            return
        for ref_str in references:
            with suppress(InvalidIsiReference):
                yield cls._parse_reference_from_str(ref_str)

    @classmethod
    def _parse_article_from_str(cls, article_as_str: str) -> Article:
        article_data = collections.defaultdict(list)
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

        if not processed.get("year") or not processed.get("authors"):
            raise MissingCriticalInformation()

        return Article(
            authors=processed["authors"],
            year=processed["year"],
            title=processed.get("title"),
            journal=processed.get("source_abbreviation"),
            volume=processed.get("volume"),
            issue=processed.get("issue"),
            page=processed.get("beginning_page"),
            doi=processed.get("DOI"),
            references=list(
                cls._get_articles_from_references(processed.get("references"))
            ),
            keywords=processed.get("keywords", []),
            extra=processed,
            sources={article_as_str},
        )

    @classmethod
    def _parse_reference_from_str(cls, reference: str) -> Article:
        match = cls.ISI_CITATION_PATTERN.match(reference)
        if not match:
            raise InvalidIsiReference(reference)
        data = {key: [value] for key, value in match.groupdict().items() if value}
        processed = cls._parse_all(data)
        return Article(
            _label=reference,
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
        )

    @classmethod
    def _parse_all(cls, article_data: Dict[str, List[str]]) -> Mapping[str, Any]:
        processed_data = {}
        for key, values in article_data.items():
            parsed_values_dict = cls._parse(key, values)
            processed_data.update(parsed_values_dict)
        return processed_data

    @classmethod
    def _parse(cls, key: str, value: List[str]) -> Dict:
        if key in {"FN", "VR", "ER"}:
            return {}

        if key in cls.FIELDS:
            field = cls.FIELDS[key]
            parsed_value = field.parse(value)
            return {new_key: parsed_value for new_key in [field.key, *field.aliases]}

        logger.info(f"Found an unknown field with key {key} and value {value}")
        return {key: _ident(value)}
