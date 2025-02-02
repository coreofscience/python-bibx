from bibx.article import Article
from bibx.collection import Collection

articles = [
    Article(
        label="doi:1",
        ids={"doi:1"},
        authors=["A"],
        year=2010,
        title="Aa",
        journal="Aaa",
        volume="1",
        page="10",
        doi="1",
        times_cited=0,
        references=[],
        keywords=[],
        sources=set(),
        extra={},
    ),
    Article(
        label="doi:12",
        ids={"doi:12"},
        authors=["B"],
        year=2000,
        title="Bb",
        journal="Abb",
        volume="2",
        page="11",
        doi="12",
        times_cited=2,
        references=[],
        keywords=[],
        sources=set(),
        extra={},
    ),
    Article(
        label="doi:13",
        ids={"doi:13"},
        authors=["C"],
        year=2021,
        title="Cc",
        journal="Acc",
        volume="3",
        page="12",
        doi="13",
        times_cited=12,
        references=[],
        keywords=[],
        sources=set(),
        extra={},
    ),
    Article(
        label="doi:14",
        ids={"doi:14"},
        authors=["D"],
        year=2022,
        title="Dd",
        journal="Add",
        volume="4",
        page="13",
        doi="14",
        times_cited=2,
        references=[],
        keywords=[],
        sources=set(),
        extra={},
    ),
    Article(
        label="doi:15",
        ids={"doi:15"},
        authors=["E"],
        year=2005,
        title="Ee",
        journal="Aee",
        volume="5",
        page="14",
        doi="15",
        times_cited=0,
        references=[],
        keywords=[],
        sources=set(),
        extra={},
    ),
    Article(
        label="doi:16",
        ids={"doi:16"},
        authors=["F"],
        year=2005,
        title="Ff",
        journal="Aff",
        volume="6",
        page="15",
        doi="16",
        times_cited=None,
        references=[],
        keywords=[],
        sources=set(),
        extra={},
    ),
    Article(
        label="doi:17",
        ids={"doi:17"},
        authors=["J"],
        year=2010,
        title="Jj",
        journal="Ajj",
        volume="7",
        page="16",
        doi="17",
        times_cited=1,
        references=[],
        keywords=[],
        sources=set(),
        extra={},
    ),
    Article(
        label="doi:18",
        ids={"doi:18"},
        authors=["H"],
        year=2000,
        title="Hh",
        journal="Ahh",
        volume="8",
        page="17",
        doi="18",
        times_cited=20,
        references=[],
        keywords=[],
        sources=set(),
        extra={},
    ),
    Article(
        label="doi:19",
        ids={"doi:19"},
        authors=["I"],
        year=2021,
        title="Ii",
        journal="Aii",
        volume="9",
        page="18",
        doi="19",
        references=[],
        keywords=[],
        sources=set(),
        extra={},
    ),
    Article(
        label="doi:19",
        ids={"doi:19"},
        authors=["I"],
        year=None,
        title="Ii",
        journal="Aii",
        volume="9",
        page="18",
        doi="19",
        references=[],
        keywords=[],
        sources=set(),
        extra={},
    ),
    Article(
        label="doi:19",
        ids={"doi:19"},
        authors=["I"],
        title="Ii",
        journal="Aii",
        volume="9",
        page="18",
        doi="19",
        references=[],
        keywords=[],
        sources=set(),
        extra={},
    ),
]


def test_published_by_year() -> None:
    """Test that we can get the number of articles published by year."""
    collection = Collection(articles=articles)

    res = collection.published_by_year()
    assert res.get(2000) == 2  # noqa: PLR2004
    assert res.get(2001) == 0
    assert res.get(2002) == 0
    assert res.get(2005) == 2  # noqa: PLR2004
    assert res.get(2010) == 2  # noqa: PLR2004
    assert res.get(2021) == 2  # noqa: PLR2004
    assert res.get(2022) == 1
    assert res.get(2023) == 0


def test_cited_by_year() -> None:
    """Test that we can get the number of citations by year."""
    collection = Collection(articles=articles)

    res = collection.cited_by_year()
    assert res.get(2000) == 22  # noqa: PLR2004
    assert res.get(2001) == 0
    assert res.get(2002) == 0
    assert res.get(2005) == 0
    assert res.get(2010) == 1
    assert res.get(2021) == 12  # noqa: PLR2004
    assert res.get(2022) == 2  # noqa: PLR2004
    assert res.get(2023) == 0
