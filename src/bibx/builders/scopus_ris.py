import logging
import re
from collections import defaultdict
from collections.abc import Iterable
from typing import Optional, TextIO

from bibx.article import Article
from bibx.collection import Collection
from bibx.exceptions import InvalidScopusFileError, MissingCriticalInformationError

from .base import CollectionBuilder

logger = logging.getLogger(__name__)

_RIS_PATTERN = re.compile(r"^(((?P<key>[A-Z0-9]{2}))[ ]{2}-[ ]{1})?(?P<value>(.*))$")


def _size(file: TextIO) -> int:
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    return size


def _int_or_nothing(raw: Optional[list[str]]) -> Optional[int]:
    if not raw:
        return None
    try:
        return int(raw[0])
    except TypeError:
        return None


def _joined(raw: Optional[list[str]]) -> Optional[str]:
    if not raw:
        return None
    return " ".join(raw)


class ScopusRisCollectionBuilder(CollectionBuilder):
    """Builder for collections of articles from Scopus RIS files."""

    def __init__(self, *ris_files: TextIO) -> None:
        self._files = ris_files
        for file in self._files:
            file.seek(0)

    def build(self) -> Collection:
        """Build a collection of articles from Scopus RIS files."""
        articles = self._get_articles_from_files()
        return Collection(Collection.deduplicate_articles(list(articles)))

    def _get_articles_from_files(self) -> Iterable[Article]:
        for file in self._files:
            yield from self._parse_file(file)

    @staticmethod
    def _find_volume_info(ref: str) -> tuple[dict[str, str], str]:
        volume_pattern = re.compile(r"(?P<volume>\d+)( \((?P<issue>.+?)\))?")
        page_pattern = re.compile(r"(pp?\. (?P<page>\w+)(-[^,\s]+)?)")
        page = page_pattern.search(ref)
        last_index = 0
        if page:
            last_index = page.lastindex or 0
            first, *_ = ref.split(page.group())
            volume = volume_pattern.search(first)
        else:
            volume = volume_pattern.search(ref)
            if volume:
                last_index = volume.lastindex or 0

        if not page and not volume:
            return {}, ref

        data = {}
        if page:
            data.update(page.groupdict())
        if volume:
            data.update(volume.groupdict())

        if data.get("volume"):
            data["volume"] = f"V{data['volume']}"
        if data.get("page"):
            data["page"] = f"P{data['page']}"

        return data, ref[last_index:]

    @staticmethod
    def _find_doi(ref: str) -> tuple[Optional[str], str]:
        pattern = re.compile(
            r"((doi.org\/)|(aps.org\/doi\/)|(DOI:?)) ?(?P<doi>[^\s,;:]{5,})", re.I
        )
        result = re.search(pattern, ref)
        if result is None or "doi" not in result.groupdict():
            return None, ref
        doi = result.groupdict()["doi"]
        return f"DOI {doi}", ref[result.lastindex :]

    @classmethod
    def _article_form_reference(cls, scopusref: str) -> Article:
        authors, year, rest = re.split(r"(\(\d{4}\))", scopusref, maxsplit=1)
        first_name, last_name, *_ = authors.split(", ")
        year = year[1:-1]
        journal, rest = rest.split(", ", 1)
        volume_info, rest = cls._find_volume_info(rest)
        doi, _ = cls._find_doi(scopusref)
        if not authors or not year:
            raise MissingCriticalInformationError()
        return Article(
            label=scopusref,
            ids=set() if doi is None else {f"doi:{doi}"},
            authors=[f"{first_name} {last_name.replace(' ', '').replace('.', '')}"],
            year=int(year),
            journal=(
                journal.strip().replace(".", "").upper()
                if not journal.isspace()
                else None
            ),
            volume=volume_info.get("volume"),
            page=volume_info.get("page"),
            doi=doi,
        ).add_simple_id()

    @classmethod
    def _parse_references(cls, refs: list[str]) -> list[Article]:
        if not refs:
            return []
        result = []
        for ref in refs:
            try:
                result.append(cls._article_form_reference(ref))
            except (KeyError, IndexError, TypeError, ValueError):
                logging.debug("Ignoring invalid reference %s", ref)
        return result

    @staticmethod
    def _ris_to_dict(record: str) -> dict[str, list[str]]:
        parsed = defaultdict(list)
        current = None
        for line in record.split("\n"):
            match = _RIS_PATTERN.match(line)
            if not match:
                raise InvalidScopusFileError()
            data = match.groupdict()
            key = data.get("key")
            value = data.get("value")
            if "ER" in data:
                break
            if key:
                if key == "N1" and value and ":" in value:
                    label, value = value.split(":", 1)
                    value = value.strip()
                    current = f"{key}:{label.strip()}"
                else:
                    current = data["key"]
            if value and current:
                parsed[current].append(data.get("value", ""))
        return dict(parsed)

    @classmethod
    def _article_from_record(cls, record: str) -> Article:
        data = cls._ris_to_dict(record)
        year = _int_or_nothing(data.get("PY", []))
        times_cited = _int_or_nothing(data.get("TC"))
        authors = data.get("AU", [])
        if not authors or not year:
            raise MissingCriticalInformationError()
        doi_list = data.get("DO")
        doi = doi_list[0] if doi_list else None
        return (
            Article(
                label=doi or "replaceme",
                ids=set() if doi is None else {f"doi:{doi}"},
                title=_joined(data.get("TI")),
                authors=authors,
                year=year,
                journal=_joined(data.get("J2")),
                volume=_joined(data.get("VL")),
                issue=_joined(data.get("IS")),
                page=_joined(data.get("SP")),
                doi=doi,
                keywords=data.get("KW", []),
                references=cls._parse_references(data.get("N1:References", [])),
                sources={"scopus"},
                extra=data,
                times_cited=times_cited,
            )
            .add_simple_id()
            .set_simple_label()
        )

    @classmethod
    def _parse_file(cls, file: TextIO) -> Iterable[Article]:
        if not _size(file):
            return
        for item in file.read().split("\n\n"):
            if item.isspace():
                continue
            try:
                article = cls._article_from_record(item.strip())
                yield article
            except MissingCriticalInformationError:
                logger.info("Missing critical information for record %s", item)
