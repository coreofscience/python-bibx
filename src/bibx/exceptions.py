class BibXError(Exception):
    """
    Any exception known by wostools.
    """


class InvalidIsiLineError(BibXError, ValueError):
    """
    Raised when we encounter an invalid line when processing an ISI file.
    """

    def __init__(self, line: str):
        super().__init__(f"'{line}' is not a valid ISI file line")


class InvalidIsiReference(BibXError, ValueError):
    """
    Raised when we try to create an article out of an invalid ISI reference.
    """

    def __init__(self, reference: str):
        super().__init__(f"{reference} does not look like an ISI citation")
