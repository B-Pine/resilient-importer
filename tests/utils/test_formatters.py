import pytest

from importer.models import ImportReport, SkippedRow
from importer.utils.formatters import (
    format_report,
    normalize_email,
    normalize_whitespace,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Alice", "Alice"),
        ("  Alice  ", "Alice"),
        ("Jean   Habimana", "Jean Habimana"),
        ("\tJean \n Habimana ", "Jean Habimana"),
        ("   ", ""),
    ],
)
def test_normalize_whitespace(value: str, expected: str) -> None:
    assert normalize_whitespace(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("alice@example.com", "alice@example.com"),
        ("Alice@Example.COM", "alice@example.com"),
        ("  alice@example.com  ", "alice@example.com"),
        ("   ", ""),
    ],
)
def test_normalize_email(value: str, expected: str) -> None:
    assert normalize_email(value) == expected


def test_format_report_without_skipped_rows() -> None:
    report = ImportReport(imported=2, skipped=())

    assert format_report(report) == "Imported 2 user(s)."


def test_format_report_lists_each_skipped_row() -> None:
    report = ImportReport(
        imported=1,
        skipped=(
            SkippedRow(line_number=4, reason="name is empty"),
            SkippedRow(line_number=6, reason="invalid email 'x'"),
        ),
    )

    assert format_report(report) == (
        "Imported 1 user(s).\n"
        "Skipped 2 row(s):\n"
        "  line 4: name is empty\n"
        "  line 6: invalid email 'x'"
    )
