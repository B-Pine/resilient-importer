import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

from importer.cli import EXIT_FAILURE, EXIT_SUCCESS, main

VALID_CSV = "user_id,name,email\n1,Alice,alice@example.com\n"


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "users.json"


@pytest.fixture
def log_file(tmp_path: Path) -> Path:
    return tmp_path / "importer.log"


def run(csv_path: Path, db_path: Path, log_file: Path) -> int:
    return main([str(csv_path), "--db", str(db_path), "--log-file", str(log_file)])


# Test Success


def test_successful_import_prints_report_and_exits_zero(
    write_csv: Callable[[str], Path],
    db_path: Path,
    log_file: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run(write_csv(VALID_CSV), db_path, log_file)

    assert exit_code == EXIT_SUCCESS
    assert capsys.readouterr().out == "Imported 1 user(s).\n"
    assert db_path.exists()


def test_skipped_rows_still_exit_zero(
    write_csv: Callable[[str], Path],
    db_path: Path,
    log_file: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    csv_path = write_csv(VALID_CSV + "2,,nameless@example.com\n")

    exit_code = run(csv_path, db_path, log_file)

    assert exit_code == EXIT_SUCCESS
    assert "line 3: name is empty" in capsys.readouterr().out


def test_import_is_recorded_in_the_log_file(
    write_csv: Callable[[str], Path], db_path: Path, log_file: Path
) -> None:
    run(write_csv(VALID_CSV), db_path, log_file)

    content = log_file.read_text(encoding="utf-8")
    assert "import started" in content
    assert "row accepted line=2 user_id=1" in content
    assert "import finished imported=1 skipped=0" in content


# Test Failures


def test_missing_csv_prints_error_and_exits_one(
    tmp_path: Path, db_path: Path, log_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = run(tmp_path / "nope.csv", db_path, log_file)

    captured = capsys.readouterr()
    assert exit_code == EXIT_FAILURE
    assert captured.err.startswith("Error: File not found")
    assert captured.out == ""
    assert not db_path.exists()


def test_bad_header_exits_one(
    write_csv: Callable[[str], Path], db_path: Path, log_file: Path
) -> None:
    assert run(write_csv("id,name\n"), db_path, log_file) == EXIT_FAILURE


def test_corrupted_database_exits_one_and_is_left_untouched(
    write_csv: Callable[[str], Path], db_path: Path, log_file: Path
) -> None:
    db_path.write_text("not json", encoding="utf-8")

    exit_code = run(write_csv(VALID_CSV), db_path, log_file)

    assert exit_code == EXIT_FAILURE
    assert db_path.read_text(encoding="utf-8") == "not json"


def test_failure_is_recorded_in_the_log_file(
    tmp_path: Path, db_path: Path, log_file: Path
) -> None:
    run(tmp_path / "nope.csv", db_path, log_file)

    assert "level=ERROR" in log_file.read_text(encoding="utf-8")


def test_missing_argument_exits_with_usage_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main([])

    assert exc_info.value.code == 2
    assert "usage:" in capsys.readouterr().err


# Test Running as a program


def test_can_run_as_python_module() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "importer", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Import users from a CSV file" in result.stdout
