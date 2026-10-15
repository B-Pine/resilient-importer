from pathlib import Path

import pytest

from importer.utils.files import atomic_write


def test_writes_content_to_target(tmp_path: Path) -> None:
    target = tmp_path / "out.txt"

    with atomic_write(target) as file:
        file.write("hello")

    assert target.read_text(encoding="utf-8") == "hello"


def test_replaces_existing_content(tmp_path: Path) -> None:
    target = tmp_path / "out.txt"
    target.write_text("old", encoding="utf-8")

    with atomic_write(target) as file:
        file.write("new")

    assert target.read_text(encoding="utf-8") == "new"


def test_leaves_no_temporary_file_after_success(tmp_path: Path) -> None:
    target = tmp_path / "out.txt"

    with atomic_write(target) as file:
        file.write("hello")

    assert list(tmp_path.iterdir()) == [target]


def test_error_inside_block_keeps_old_content(tmp_path: Path) -> None:
    target = tmp_path / "out.txt"
    target.write_text("old", encoding="utf-8")

    with pytest.raises(RuntimeError):
        with atomic_write(target) as file:
            file.write("half-written")
            raise RuntimeError("crash while writing")

    assert target.read_text(encoding="utf-8") == "old"
    assert list(tmp_path.iterdir()) == [target]


def test_error_before_first_write_creates_nothing(tmp_path: Path) -> None:
    target = tmp_path / "out.txt"

    with pytest.raises(RuntimeError):
        with atomic_write(target):
            raise RuntimeError("crash")

    assert list(tmp_path.iterdir()) == []
