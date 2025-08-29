from bibx import read_scopus_csv


def test_scopus_csv() -> None:
    """Test the ScopusCsvSource class."""
    with open("docs/examples/scopus.csv") as file:
        collection = read_scopus_csv(file)
    assert collection is not None
