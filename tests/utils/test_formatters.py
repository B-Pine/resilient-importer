import pytest

from importer.utils.formatters import normalize_email, normalize_whitespace


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
