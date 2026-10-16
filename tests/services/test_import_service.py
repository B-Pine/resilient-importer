import logging
from pathlib import Path
from unittest.mock import MagicMock, call

import pytest
from pytest_mock import MockerFixture

from importer.exceptions import DuplicateUserError, MissingFileError, StorageError
from importer.models import RawRow, SkippedRow, User
from importer.parsers.csv_parser import CsvParser
from importer.repositories.user_repository import UserRepository
from importer.services.import_service import ImportService

CSV_PATH = Path("users.csv")

ALICE_ROW = RawRow(line_number=2, values=["1", "Alice", "alice@example.com"])
JEAN_ROW = RawRow(line_number=3, values=["2", "Jean", "jean@example.com"])
NO_NAME_ROW = RawRow(line_number=4, values=["3", "", "nameless@example.com"])

ALICE = User(user_id="1", name="Alice", email="alice@example.com")
JEAN = User(user_id="2", name="Jean", email="jean@example.com")


@pytest.fixture
def parser(mocker: MockerFixture) -> MagicMock:
    mock: MagicMock = mocker.create_autospec(CsvParser, instance=True)
    return mock


@pytest.fixture
def repository(mocker: MockerFixture) -> MagicMock:
    mock: MagicMock = mocker.create_autospec(UserRepository, instance=True)
    return mock


@pytest.fixture
def service(parser: MagicMock, repository: MagicMock) -> ImportService:
    return ImportService(parser=parser, repository=repository)


# Testing happy path


def test_valid_rows_are_added_and_saved_once(
    service: ImportService, parser: MagicMock, repository: MagicMock
) -> None:
    parser.parse.return_value = [ALICE_ROW, JEAN_ROW]

    report = service.import_file(CSV_PATH)

    assert report.imported == 2
    assert report.skipped == ()
    assert repository.add.call_args_list == [call(ALICE), call(JEAN)]
    repository.save.assert_called_once()


def test_parser_receives_the_given_path(
    service: ImportService, parser: MagicMock
) -> None:
    parser.parse.return_value = []

    service.import_file(CSV_PATH)

    parser.parse.assert_called_once_with(CSV_PATH)


# Test Skipped rows


def test_invalid_row_is_skipped_and_the_rest_imported(
    service: ImportService, parser: MagicMock, repository: MagicMock
) -> None:
    parser.parse.return_value = [ALICE_ROW, NO_NAME_ROW, JEAN_ROW]

    report = service.import_file(CSV_PATH)

    assert report.imported == 2
    assert report.skipped == (SkippedRow(line_number=4, reason="name is empty"),)
    assert repository.add.call_args_list == [call(ALICE), call(JEAN)]


def test_duplicate_is_skipped_with_its_line_number(
    service: ImportService, parser: MagicMock, repository: MagicMock
) -> None:
    parser.parse.return_value = [ALICE_ROW, JEAN_ROW]
    repository.add.side_effect = [None, DuplicateUserError("2")]

    report = service.import_file(CSV_PATH)

    assert report.imported == 1
    assert report.skipped == (
        SkippedRow(line_number=3, reason="User with id '2' already exists"),
    )


def test_skipped_row_is_logged_as_warning(
    service: ImportService, parser: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    parser.parse.return_value = [NO_NAME_ROW]

    with caplog.at_level(logging.WARNING):
        service.import_file(CSV_PATH)

    assert "row skipped line=4 reason=name is empty" in caplog.text


def test_nothing_is_saved_when_no_row_is_valid(
    service: ImportService, parser: MagicMock, repository: MagicMock
) -> None:
    parser.parse.return_value = [NO_NAME_ROW]

    report = service.import_file(CSV_PATH)

    assert report.imported == 0
    repository.save.assert_not_called()


# Test Fatal errors


def test_parser_error_stops_import_before_storage(
    service: ImportService, parser: MagicMock, repository: MagicMock
) -> None:
    parser.parse.side_effect = MissingFileError("File not found: users.csv")

    with pytest.raises(MissingFileError):
        service.import_file(CSV_PATH)

    repository.add.assert_not_called()
    repository.save.assert_not_called()


def test_save_error_is_raised_instead_of_returning_a_report(
    service: ImportService, parser: MagicMock, repository: MagicMock
) -> None:
    parser.parse.return_value = [ALICE_ROW]
    repository.save.side_effect = StorageError("Could not write users.json")

    with pytest.raises(StorageError):
        service.import_file(CSV_PATH)
