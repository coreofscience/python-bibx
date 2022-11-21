import collections
import functools
import logging
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping, TextIO

import bibx.utils.isi_field_parsers as parsers
from bibx.entities.article import Article
from bibx.entities.collection import Collection
from bibx.entities.collection_builders.base import CollectionBuilder
from bibx.exceptions import InvalidIsiLineError, InvalidIsiReference

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IsiField:
    key: str
    description: str
    parser: Callable
    aliases: List[str]

    def parse(self, value: List[str]):
        return self.parser(value)


class IsiCollectionBuilder(CollectionBuilder):
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
        "AB": IsiField("AB", "Abstract", parsers.joined, ["abstract"]),
        "AF": IsiField("AF", "Author Full Names", parsers.ident, ["author_full_names"]),
        "AR": IsiField("AR", "Article Number", parsers.joined, ["article_number"]),
        "AU": IsiField("AU", "Authors", parsers.ident, ["authors"]),
        "BA": IsiField("BA", "Book Authors", parsers.ident, ["book_authors"]),
        "BE": IsiField("BE", "Editors", parsers.ident, ["editors"]),
        "BF": IsiField(
            "BF", "Book Authors Full Name", parsers.ident, ["book_authors_full_name"]
        ),
        "BN": IsiField(
            "BN",
            "International Standard Book Number (ISBN)",
            parsers.joined,
            ["international_standard_book_number"],
        ),
        "BP": IsiField("BP", "Beginning Page", parsers.joined, ["beginning_page"]),
        "BS": IsiField(
            "BS", "Book Series Subtitle", parsers.joined, ["book_series_subtitle"]
        ),
        "C1": IsiField("C1", "Author Address", parsers.ident, ["author_address"]),
        "CA": IsiField("CA", "Group Authors", parsers.ident, ["group_authors"]),
        "CL": IsiField(
            "CL", "Conference Location", parsers.joined, ["conference_location"]
        ),
        "CR": IsiField(
            "CR",
            "Cited References",
            parsers.ident,
            ["cited_references", "references", "citations"],
        ),
        "CT": IsiField(
            "CT",
            "Conference Title",
            functools.partial(parsers.joined, separator="\n"),
            ["conference_title"],
        ),
        "CY": IsiField("CY", "Conference Date", parsers.joined, ["conference_date"]),
        "DE": IsiField("DE", "Author Keywords", parsers.delimited, ["author_keywords"]),
        "DI": IsiField(
            "DI",
            "Digital Object Identifier (DOI)",
            parsers.joined,
            ["digital_object_identifier", "DOI"],
        ),
        "DT": IsiField("DT", "Document Type", parsers.joined, ["document_type"]),
        "D2": IsiField(
            "D2",
            "Book Digital Object Identifier (DOI)",
            parsers.joined,
            ["book_digital_object_identifier"],
        ),
        "ED": IsiField("ED", "Editors", parsers.ident, ["editors"]),
        "EM": IsiField("EM", "E-mail Address", parsers.ident, ["email_address"]),
        "EI": IsiField(
            "EI",
            "Electronic International Standard Serial Number (eISSN)",
            parsers.joined,
            ["eissn"],
        ),
        "EP": IsiField("EP", "Ending Page", parsers.joined, ["ending_page"]),
        "FU": IsiField(
            "FU",
            "Funding Agency and Grant Number",
            parsers.delimited,
            ["funding_agency_and_grant_number"],
        ),
        "FX": IsiField("FX", "Funding Text", parsers.joined, ["funding_text"]),
        "GA": IsiField(
            "GA",
            "Document Delivery Number",
            parsers.joined,
            ["document_delivery_number"],
        ),
        "GP": IsiField(
            "GP", "Book Group Authors", parsers.ident, ["book_group_authors"]
        ),
        "HO": IsiField("HO", "Conference Host", parsers.joined, ["conference_host"]),
        "ID": IsiField(
            "ID", "Keywords Plus", parsers.delimited, ["keywords_plus", "keywords"]
        ),
        "IS": IsiField("IS", "Issue", parsers.joined, ["issue"]),
        "J9": IsiField(
            "J9",
            "29-Character Source Abbreviation",
            parsers.joined,
            ["source_abbreviation"],
        ),
        "JI": IsiField(
            "JI", "ISO Source Abbreviation", parsers.joined, ["iso_source_abbreviation"]
        ),
        "LA": IsiField("LA", "Language", parsers.joined, ["language"]),
        "MA": IsiField("MA", "Meeting Abstract", parsers.joined, ["meeting_abstract"]),
        "NR": IsiField(
            "NR", "Cited Reference Count", parsers.integer, ["cited_reference_count"]
        ),
        "OI": IsiField(
            "OI",
            "ORCID Identifier (Open Researcher and Contributor ID)",
            parsers.delimited,
            ["orcid_identifier"],
        ),
        "P2": IsiField(
            "P2",
            "Chapter count (Book Citation Index)",
            parsers.integer,
            ["chapter_count"],
        ),
        "PA": IsiField(
            "PA",
            "Publisher Address",
            functools.partial(parsers.joined, separator="\n"),
            ["publisher_address"],
        ),
        "PD": IsiField("PD", "Publication Date", parsers.joined, ["publication_date"]),
        "PG": IsiField("PG", "Page Count", parsers.integer, ["page_count"]),
        "PI": IsiField("PI", "Publisher City", parsers.joined, ["publisher_city"]),
        "PM": IsiField("PM", "PubMed ID", parsers.joined, ["pubmed_id"]),
        "PN": IsiField("PN", "Part Number", parsers.joined, ["part_number"]),
        "PT": IsiField(
            "PT",
            "Publication Type (J=Journal; B=Book; S=Series; P=Patent)",
            parsers.joined,
            ["publication_type"],
        ),
        "PU": IsiField("PU", "Publisher", parsers.joined, ["publisher"]),
        "PY": IsiField(
            "PY",
            "Year Published",
            parsers.integer,
            ["year_published", "year", "publication_year"],
        ),
        "RI": IsiField(
            "RI", "ResearcherID Number", parsers.delimited, ["researcherid_number"]
        ),
        "RP": IsiField("RP", "Reprint Address", parsers.joined, ["reprint_address"]),
        "SC": IsiField("SC", "Research Areas", parsers.delimited, ["research_areas"]),
        "SE": IsiField(
            "SE", "Book Series Title", parsers.joined, ["book_series_title"]
        ),
        "SI": IsiField("SI", "Special Issue", parsers.joined, ["special_issue"]),
        "SN": IsiField(
            "SN",
            "International Standard Serial Number (ISSN)",
            parsers.joined,
            ["issn"],
        ),
        "SO": IsiField("SO", "Publication Name", parsers.joined, ["publication_name"]),
        "SP": IsiField(
            "SP",
            "Conference Sponsors",
            functools.partial(parsers.delimited, delimiter=", "),
            ["conference_sponsors"],
        ),
        "SU": IsiField("SU", "Supplement", parsers.joined, ["supplement"]),
        "TC": IsiField(
            "TC",
            "Web of Science Core Collection Times Cited Count",
            parsers.integer,
            ["wos_times_cited_count", "wos_times_cited"],
        ),
        "TI": IsiField("TI", "Document Title", parsers.joined, ["title"]),
        "U1": IsiField(
            "U1", "Usage Count (Last 180 Days)", parsers.integer, ["usage_count"]
        ),
        "U2": IsiField(
            "U2", "Usage Count (Since 2013)", parsers.integer, ["usage_count"]
        ),
        "UT": IsiField(
            "UT",
            "Unique Article Identifier",
            parsers.joined,
            ["unique_article_identifier"],
        ),
        "VL": IsiField("VL", "Volume", parsers.joined, ["volume"]),
        "WC": IsiField(
            "WC",
            "Web of Science Categories",
            parsers.delimited,
            ["web_of_science_categories"],
        ),
        "Z9": IsiField(
            "Z9",
            "Total Times Cited Count (WoS Core, BCI, and CSCD)",
            parsers.integer,
            ["total_times_cited_count", "times_cited"],
        ),
    }

    def __init__(self, *isi_files: TextIO):
        self._files = isi_files
        for file in self._files:
            file.seek(0)

    def build(self) -> Collection:
        articles = self._get_articles_from_files()
        return Collection(articles)

    def _get_articles_as_str_from_files(self) -> Iterable[str]:
        for file in self._files:
            articles_as_str = file.read().split("\n\n")
            for article_as_str in articles_as_str:
                if article_as_str != "ER":
                    yield article_as_str

    def _get_articles_from_files(self) -> List[Article]:
        for article_as_str in self._get_articles_as_str_from_files():
            article = self._parse_article_as_str(article_as_str)
            yield article
            for reference in article.references:
                reference_article = self._parse_reference_as_str(reference)
                yield reference_article

    @staticmethod
    def _parse_article_as_str(article_as_str: str) -> Article:
        article_data = collections.defaultdict(list)
        article_data.setdefault("CR", [])
        field = None
        for line in article_as_str.split("\n"):
            match = IsiCollectionBuilder.ISI_LINE_PATTERN.match(line)
            if not match:
                raise InvalidIsiLineError(line)
            parsed = match.groupdict()
            field = parsed.get("field") or field
            if not field or "value" not in parsed or parsed["value"] is None:
                continue
            article_data[field].append(parsed["value"])

        processed = IsiCollectionBuilder._parse_all(dict(article_data))
        return Article(
            title=processed.get("title"),
            authors=processed.get("authors", []),
            year=processed.get("year"),
            journal=processed.get("source_abbreviation"),
            volume=processed.get("volume"),
            issue=processed.get("issue"),
            page=processed.get("beginning_page"),
            doi=processed.get("DOI"),
            references=processed.get("references"),
            keywords=processed.get("keywords"),
            extra=processed,
            sources={article_as_str},
        )

    @staticmethod
    def _parse_reference_as_str(reference: str) -> Article:
        match = IsiCollectionBuilder.ISI_CITATION_PATTERN.match(reference)
        if not match:
            raise InvalidIsiReference(reference)
        data = {key: [value] for key, value in match.groupdict().items() if value}
        processed = IsiCollectionBuilder._parse_all(data)
        return Article(
            title=processed.get("title"),
            authors=processed.get("authors", []),
            year=processed.get("year"),
            journal=processed.get("source_abbreviation"),
            volume=processed.get("volume"),
            page=processed.get("beginning_page"),
            doi=processed.get("DOI"),
            extra=processed,
            sources={reference},
        )

    @staticmethod
    def _parse_all(article_data: Dict[str, List[str]]) -> Mapping[str, Any]:
        processed_data = {}
        for key, values in article_data.items():
            parsed_values_dict = IsiCollectionBuilder._parse(key, values)
            processed_data.update(parsed_values_dict)
        return processed_data

    @staticmethod
    def _parse(key: str, value: List[str]) -> Dict:
        if key in {"FN", "VR", "ER"}:
            return {}

        if key in IsiCollectionBuilder.FIELDS:
            field = IsiCollectionBuilder.FIELDS[key]
            parsed_value = field.parse(value)
            return {new_key: parsed_value for new_key in [field.key, *field.aliases]}

        logger.info(f"Found an unknown field with key {key} and value {value}")
        return {key: parsers.ident(value)}
