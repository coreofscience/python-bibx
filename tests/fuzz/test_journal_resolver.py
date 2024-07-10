import pytest
from bibx._fuzz.journal_resolver import JournalResolver


@pytest.fixture(scope="module")
def journal_resolver():
    return JournalResolver()


def test_journal_resolver_is_singleton():
    assert JournalResolver() is JournalResolver()


def test_journal_resolver_resolves_journal(journal_resolver: JournalResolver):
    journal = journal_resolver.resolve("Nature")
    assert journal is not None


def test_journal_resolver_with_empty_string(journal_resolver: JournalResolver):
    journal = journal_resolver.resolve("")
    assert journal is None


def test_journal_resolver_with_unknown_journal(journal_resolver: JournalResolver):
    journal = journal_resolver.resolve("Unknown Journal")
    assert journal is None


def test_journal_resolver_resolves_abbreviated_journal(
    journal_resolver: JournalResolver,
):
    journal = journal_resolver.resolve("BRIT. J. OCCUP. THER.")
    assert journal is not None


@pytest.mark.skip("The distance function doesn't work well references.")
def test_journal_resolver_resolves_journal_from_reference(
    journal_resolver: JournalResolver,
):
    journal = journal_resolver.resolve(
        "Bosworth JK, 2010, BRIT J OCCUP THER, V23, P145, DOI 10.2494/photopolymer.23.145"
    )
    assert journal is not None
