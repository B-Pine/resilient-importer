from collections.abc import Callable
from pathlib import Path

import pytest

from importer.exceptions import FileFormatError, MissingFileError
from importer.models import RawRow
from importer.parsers import CsvParser

HEADER = "user_id,name,email\n"


@pytest.fixture
def parser() -> CsvParser:
    return CsvParser()


# Happy path testing


def test_parses_rows_with_line_numbers(
    parser: CsvParser, write_csv: Callable[[str], Path]
) -> None:
    path = write_csv(HEADER + "1,Alice,alice@example.com\n2,Jean,jean@example.com\n")

    rows = parser.parse(path)

    assert rows == [
        RawRow(line_number=2, values=["1", "Alice", "alice@example.com"]),
        RawRow(line_number=3, values=["2", "Jean", "jean@example.com"]),
    ]


def test_header_only_file_returns_no_rows(
    parser: CsvParser, write_csv: Callable[[str], Path]
) -> None:
    assert parser.parse(write_csv(HEADER)) == []


def test_skips_blank_lines_but_keeps_real_line_numbers(
    parser: CsvParser, write_csv: Callable[[str], Path]
) -> None:
    path = write_csv(HEADER + "\n1,Alice,alice@example.com\n")

    rows = parser.parse(path)

    assert rows == [RawRow(line_number=3, values=["1", "Alice", "alice@example.com"])]


def test_accepts_header_with_surrounding_spaces(
    parser: CsvParser, write_csv: Callable[[str], Path]
) -> None:
    path = write_csv(" user_id , name , email \n1,Alice,alice@example.com\n")

    assert len(parser.parse(path)) == 1


def test_keeps_comma_inside_quoted_value(
    parser: CsvParser, write_csv: Callable[[str], Path]
) -> None:
    path = write_csv(HEADER + '1,"Doe, Jane",jane@example.com\n')

    assert parser.parse(path)[0].values == ["1", "Doe, Jane", "jane@example.com"]


def test_returns_malformed_rows_unchanged_for_the_validator(
    parser: CsvParser, write_csv: Callable[[str], Path]
) -> None:
    path = write_csv(HEADER + "1,Alice\n")

    assert parser.parse(path) == [RawRow(line_number=2, values=["1", "Alice"])]


# Test for the failures


def test_missing_file_raises_missing_file_error(
    parser: CsvParser, tmp_path: Path
) -> None:
    with pytest.raises(MissingFileError):
        parser.parse(tmp_path / "does_not_exist.csv")


def test_empty_file_raises_file_format_error(
    parser: CsvParser, write_csv: Callable[[str], Path]
) -> None:
    with pytest.raises(FileFormatError, match="empty"):
        parser.parse(write_csv(""))


@pytest.mark.parametrize(
    "header",
    [
        "user_id,name\n",  # missing a column
        "user_id,email,name\n",  # wrong order
        "user_id,name,email,age\n",  # extra column
        "id,name,email\n",  # misspelled column
    ],
)
def test_wrong_header_raises_file_format_error(
    parser: CsvParser, write_csv: Callable[[str], Path], header: str
) -> None:
    with pytest.raises(FileFormatError, match="Expected header"):
        parser.parse(write_csv(header))


def test_non_utf8_file_raises_file_format_error(
    parser: CsvParser, tmp_path: Path
) -> None:
    path = tmp_path / "users.csv"
    path.write_bytes(b"user_id,name,email\n1,Ren\xe9,rene@example.com\n")

    with pytest.raises(FileFormatError, match="UTF-8"):
        parser.parse(path)
