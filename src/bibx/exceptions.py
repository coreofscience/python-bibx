class BibXError(Exception):
    """Any exception known by wostools."""


class InvalidIsiLineError(BibXError, ValueError):
    """Raised when we encounter an invalid line when processing an ISI file."""

    def __init__(self, line: str) -> None:
        super().__init__(f"'{line}' is not a valid ISI file line")


class InvalidIsiReferenceError(BibXError, ValueError):
    """Raised when we try to create an article out of an invalid ISI reference."""

    def __init__(self, reference: str) -> None:
        super().__init__(f"{reference} does not look like an ISI citation")


class MissingCriticalInformationError(BibXError, ValueError):
    """Raised when we don't have the publication year of an article."""

    def __init__(self) -> None:
        super().__init__("Article is missing some critical information")


class InvalidScopusFileError(BibXError, ValueError):
    """Raised when we find an invalid line on an scopus RIS file."""

    def __init__(self) -> None:
        super().__init__("The file contains an invalid RIS line")


class OpenAlexError(BibXError):
    """Raised when we encounter an error with the OpenAlex API."""
