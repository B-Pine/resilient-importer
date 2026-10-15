from collections.abc import Callable
from pathlib import Path

import pytest

from importer.models import SkippedRow, User
from importer.parsers.csv_parser import CsvParser
from importer.repositories.json_user_repository import JsonUserRepository
from importer.services.import_service import ImportService

SAMPLE_CSV = (
    "user_id,name,email\n"
    "1,Alice Mukamana,alice@example.com\n"
    "2,Jean Habimana,jean@example.com\n"
    "3,,missing.name@example.com\n"
    "1,Alice Duplicate,alice2@example.com\n"
    "4,Bad Email,not-an-email\n"
)


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "users.json"


def make_service(db_path: Path) -> ImportService:
    return ImportService(parser=CsvParser(), repository=JsonUserRepository(db_path))


def test_full_import_stores_valid_users_and_reports_the_rest(
    write_csv: Callable[[str], Path], db_path: Path
) -> None:
    csv_path = write_csv(SAMPLE_CSV)

    report = make_service(db_path).import_file(csv_path)

    assert report.imported == 2
    assert report.skipped == (
        SkippedRow(line_number=4, reason="name is empty"),
        SkippedRow(line_number=5, reason="User with id '1' already exists"),
        SkippedRow(line_number=6, reason="invalid email 'not-an-email'"),
    )
    assert JsonUserRepository(db_path).list_all() == [
        User(user_id="1", name="Alice Mukamana", email="alice@example.com"),
        User(user_id="2", name="Jean Habimana", email="jean@example.com"),
    ]


def test_running_the_same_import_twice_changes_nothing(
    write_csv: Callable[[str], Path], db_path: Path
) -> None:
    csv_path = write_csv(SAMPLE_CSV)
    make_service(db_path).import_file(csv_path)
    after_first_run = db_path.read_text(encoding="utf-8")

    report = make_service(db_path).import_file(csv_path)

    assert report.imported == 0
    assert len(report.skipped) == 5
    assert db_path.read_text(encoding="utf-8") == after_first_run
