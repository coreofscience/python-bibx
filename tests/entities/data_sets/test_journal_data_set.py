import pytest
from bibx._entities.data_sets.journal_data_set import JournalDataSet


@pytest.fixture(scope="module")
def journal_data_set():
    return JournalDataSet()


def test_journal_data_set_is_singleton():
    assert JournalDataSet() is JournalDataSet()


def test_journal_data_is_singleton(journal_data_set: JournalDataSet):
    assert journal_data_set.journal_data is journal_data_set.journal_data


def test_journals_are_singleton(journal_data_set: JournalDataSet):
    assert journal_data_set.journals is journal_data_set.journals


def test_journal_data_set_has_titles(journal_data_set: JournalDataSet):
    assert len(journal_data_set.titles) > 0
    assert "" not in journal_data_set.titles


def test_journal_data_has_all_titles(journal_data_set: JournalDataSet):
    assert len(journal_data_set.titles_and_abbreviations) > len(journal_data_set.titles)
    assert "" in journal_data_set.titles_and_abbreviations


def test_journal_data_has_titles_to_abbreviations(journal_data_set: JournalDataSet):
    assert len(journal_data_set.titles_to_abbreviations) > 0
    assert len(journal_data_set.titles_to_abbreviations) <= len(journal_data_set.titles)
    assert "" in journal_data_set.titles_to_abbreviations


def test_journal_data_has_organized_journals(journal_data_set: JournalDataSet):
    assert len(journal_data_set.organized_journals) > 0
    assert "" not in journal_data_set.organized_journals
    assert None not in journal_data_set.organized_journals
