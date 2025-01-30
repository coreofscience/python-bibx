from typing import Optional

import requests


class OpenAlexClient:
    """Client for the openalex API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        self.base_url = base_url or "https://openalex.org/api/v1"
        self.session = requests.Session()
        self.email = email or "technology@coreofscience.org"
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": f"Python/requests/bibx mailto:{email}",
            }
        )
