import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
from enum import Enum
from typing import Optional, Union

import requests
from pydantic import BaseModel, ValidationError

from bibx.exceptions import OpenAlexError
from bibx.utils import chunks

logger = logging.getLogger(__name__)

MAX_WORKS_PER_PAGE = 200
MAX_IDS_PER_REQUEST = 80


class AuthorPosition(Enum):
    """Position of an author in a work."""

    FIRST = "first"
    MIDDLE = "middle"
    LAST = "last"


class Author(BaseModel):
    """An author from the openalex API."""

    id: str
    display_name: str
    orcid: Optional[str] = None


class WorkAuthorship(BaseModel):
    """An authorship from the openalex API."""

    author_position: AuthorPosition
    author: Author
    is_corresponding: bool


class WorkKeyword(BaseModel):
    """A keyword from the openalex API."""

    id: str
    display_name: str
    score: float


class WorkBiblio(BaseModel):
    """Work bibliographic information from the openalex API."""

    volume: Optional[str] = None
    issue: Optional[str] = None
    first_page: Optional[str] = None
    last_page: Optional[str] = None


class WorkLocationSource(BaseModel):
    """Source of the work location from the openalex API."""

    id: str
    display_name: str
    type: str


class WorkLoacation(BaseModel):
    """Location of the work from the openalex API."""

    is_oa: bool
    landing_page_url: Optional[str] = None
    pdf_url: Optional[str] = None
    source: Optional[WorkLocationSource]


class Work(BaseModel):
    """A work from the openalex API."""

    id: str
    ids: dict[str, str]
    doi: Optional[str] = None
    title: Optional[str] = None
    publication_year: int
    authorships: list[WorkAuthorship]
    cited_by_count: int
    keywords: list[WorkKeyword]
    referenced_works: list[str]
    biblio: WorkBiblio
    primary_location: Optional[WorkLoacation] = None


class ResponseMeta(BaseModel):
    """Metadata from the openalex API response."""

    count: int
    page: int
    per_page: int


class WorkResponse(BaseModel):
    """Response from the openalex API."""

    results: list[Work]
    meta: ResponseMeta


class OpenAlexClient:
    """Client for the openalex API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        self.base_url = base_url or "https://api.openalex.org"
        self.session = requests.Session()
        self.email = email or "technology@coreofscience.org"
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": f"Python/requests/bibx mailto:{email}",
            }
        )

    def _fetch_works(self, params: dict[str, Union[str, int]]) -> WorkResponse:
        response = self.session.get(
            f"{self.base_url}/works",
            params=params,
        )
        try:
            response.raise_for_status()
            data = response.json()
            return WorkResponse.model_validate(data)
        except (requests.RequestException, ValidationError) as error:
            raise OpenAlexError(str(error)) from error

    def list_recent_articles(self, query: str, limit: int = 600) -> list[Work]:
        """List recent articles from the openalex API."""
        select = ",".join(Work.model_fields.keys())
        filter_ = ",".join(
            [
                f"title_and_abstract.search:{query.replace(' ', '+')}",
                "type:types/article",
                "cited_by_count:>1",
            ]
        )
        pages = (limit // MAX_WORKS_PER_PAGE) + 1
        results: list[Work] = []
        with ThreadPoolExecutor(max_workers=min(pages, 25)) as executor:
            futures = [
                executor.submit(
                    self._fetch_works,
                    {
                        "select": select,
                        "filter": filter_,
                        "sort": "publication_year:desc",
                        "per_page": MAX_WORKS_PER_PAGE,
                        "page": page,
                    },
                )
                for page in range(1, pages + 1)
            ]
            wait(futures)
            for future in futures:
                work_response = future.result()
                results.extend(work_response.results)
                if len(results) >= limit:
                    break
        return results[:limit]

    def list_articles_by_openalex_id(self, ids: list[str]) -> list[Work]:
        """List articles by openalex id."""
        select = ",".join(Work.model_fields.keys())
        results: list[Work] = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(
                    self._fetch_works,
                    {
                        "select": select,
                        "filter": f"ids.openalex:{'|'.join(ids)},type:types/article",
                        "per_page": MAX_IDS_PER_REQUEST,
                    },
                )
                for ids in chunks(ids, MAX_IDS_PER_REQUEST)
            ]
            for future in as_completed(futures):
                work_response = future.result()
                logger.info(
                    "got %s works from the openalex api", len(work_response.results)
                )
                results.extend(work_response.results)
        return results
