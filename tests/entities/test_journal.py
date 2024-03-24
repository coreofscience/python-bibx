from bibx._entities.journal import Journal


def test_journal_classification_existing_year():
    journal = Journal("title", "abbr", "issn", {2021: "Q1"})
    assert journal.classification(2021) == "Q1"


def test_journal_classification_future_year():
    journal = Journal("title", "abbr", "issn", {2021: "Q1"})
    assert journal.classification(2022) == "Q1"


def test_journal_classification_inbetween_years():
    journal = Journal("title", "abbr", "issn", {2021: "Q1", 2023: "Q2"})
    assert journal.classification(2022) == "Q1"


def test_journal_classification_inbetween_years_complex():
    journal = Journal("title", "abbr", "issn", {2021: "Q1", 2023: "Q2", 2025: "Q3"})
    assert journal.classification(2022) == "Q1"
    assert journal.classification(2024) == "Q2"
    assert journal.classification(2023) == "Q2"


def test_journal_classification_older_year():
    journal = Journal("title", "abbr", "issn", {2021: "Q1", 2023: "Q2", 2025: "Q3"})
    assert journal.classification(2020) is None
