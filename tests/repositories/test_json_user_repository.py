import json
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from importer.exceptions import DuplicateUserError, StorageError
from importer.models import User
from importer.repositories.json_user_repository import JsonUserRepository

ALICE = User(user_id="1", name="Alice Mukamana", email="alice@example.com")
JEAN = User(user_id="2", name="Jean Habimana", email="jean@example.com")


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "users.json"


def write_db(path: Path, users: list[User]) -> None:
    data = [{"user_id": u.user_id, "name": u.name, "email": u.email} for u in users]
    path.write_text(json.dumps(data), encoding="utf-8")


# test loading


def test_missing_file_starts_empty(db_path: Path) -> None:
    assert JsonUserRepository(db_path).list_all() == []


def test_loads_existing_users(db_path: Path) -> None:
    write_db(db_path, [ALICE, JEAN])

    assert JsonUserRepository(db_path).list_all() == [ALICE, JEAN]


@pytest.mark.parametrize(
    "content",
    [
        "not json at all",  # invalid JSON
        "",  # empty file
        "42",  # valid JSON, but not a list
        '{"user_id": "1"}',  # an object instead of a list
        '[{"user_id": "1", "name": "Alice"}]',  # missing a field
        '[{"user_id": "1", "name": "A", "email": "a@b.co", "age": 3}]',  # extra
    ],
)
def test_corrupted_file_raises_storage_error(db_path: Path, content: str) -> None:
    db_path.write_text(content, encoding="utf-8")

    with pytest.raises(StorageError, match="corrupted"):
        JsonUserRepository(db_path)


def test_unreadable_file_raises_storage_error(
    db_path: Path, mocker: MockerFixture
) -> None:
    mocker.patch.object(Path, "read_text", side_effect=PermissionError("denied"))

    with pytest.raises(StorageError, match="Could not read"):
        JsonUserRepository(db_path)


# Tests for  Adding records to JSON database


def test_add_then_list_returns_user(db_path: Path) -> None:
    repo = JsonUserRepository(db_path)

    repo.add(ALICE)

    assert repo.list_all() == [ALICE]


def test_adding_id_already_in_file_raises_duplicate(db_path: Path) -> None:
    write_db(db_path, [ALICE])
    repo = JsonUserRepository(db_path)
    same_id = User(user_id="1", name="Someone Else", email="else@example.com")

    with pytest.raises(DuplicateUserError) as exc_info:
        repo.add(same_id)

    assert exc_info.value.user_id == "1"


def test_adding_same_id_twice_in_one_session_raises_duplicate(
    db_path: Path,
) -> None:
    repo = JsonUserRepository(db_path)
    repo.add(ALICE)

    with pytest.raises(DuplicateUserError):
        repo.add(ALICE)


def test_rejected_duplicate_does_not_change_state(db_path: Path) -> None:
    repo = JsonUserRepository(db_path)
    repo.add(ALICE)
    impostor = User(user_id="1", name="Impostor", email="fake@example.com")

    with pytest.raises(DuplicateUserError):
        repo.add(impostor)

    assert repo.list_all() == [ALICE]


def test_changing_returned_list_does_not_change_repository(db_path: Path) -> None:
    repo = JsonUserRepository(db_path)
    repo.add(ALICE)

    repo.list_all().clear()

    assert repo.list_all() == [ALICE]


# Tests Saving in JSON database


def test_nothing_is_written_before_save(db_path: Path) -> None:
    repo = JsonUserRepository(db_path)

    repo.add(ALICE)

    assert not db_path.exists()


def test_saved_users_can_be_loaded_again(db_path: Path) -> None:
    repo = JsonUserRepository(db_path)
    repo.add(ALICE)
    repo.add(JEAN)

    repo.save()

    assert JsonUserRepository(db_path).list_all() == [ALICE, JEAN]


def test_save_keeps_previously_stored_users(db_path: Path) -> None:
    write_db(db_path, [ALICE])
    repo = JsonUserRepository(db_path)
    repo.add(JEAN)

    repo.save()

    assert JsonUserRepository(db_path).list_all() == [ALICE, JEAN]


def test_save_creates_missing_folder(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "users.json"
    repo = JsonUserRepository(db_path)
    repo.add(ALICE)

    repo.save()

    assert db_path.exists()


def test_failed_save_raises_and_keeps_old_file(
    db_path: Path, mocker: MockerFixture
) -> None:
    write_db(db_path, [ALICE])
    original = db_path.read_text(encoding="utf-8")
    repo = JsonUserRepository(db_path)
    repo.add(JEAN)
    mocker.patch.object(Path, "replace", side_effect=PermissionError("locked"))

    with pytest.raises(StorageError, match="Could not write"):
        repo.save()

    assert db_path.read_text(encoding="utf-8") == original
    assert list(db_path.parent.iterdir()) == [db_path]
