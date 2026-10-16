import pytest

from importer.exceptions import ValidationError
from importer.models import RawRow, User
from importer.utils.validators import is_valid_email, validate_row


def make_row(*values: str) -> RawRow:
    return RawRow(line_number=7, values=list(values))


# here we're testing is_valid_email function


@pytest.mark.parametrize(
    "email",
    ["alice@example.com", "jean.habimana@mail.co.rw", "a+tag@example.org"],
)
def test_accepts_valid_emails(email: str) -> None:
    assert is_valid_email(email)


@pytest.mark.parametrize(
    "email",
    [
        "not-an-email",  # no @
        "alice@example",  # no dot in domain
        "@example.com",  # nothing before @
        "alice@@example.com",  # two @
        "ali ce@example.com",  # space
        "",  # empty
    ],
)
def test_rejects_invalid_emails(email: str) -> None:
    assert not is_valid_email(email)


# testing validate_row: happy path


def test_valid_row_becomes_user() -> None:
    user = validate_row(make_row("1", "Alice Mukamana", "alice@example.com"))

    assert user == User(user_id="1", name="Alice Mukamana", email="alice@example.com")


def test_values_are_cleaned_before_storing() -> None:
    user = validate_row(make_row(" 1 ", "  Alice   Mukamana ", " Alice@Example.COM "))

    assert user == User(user_id="1", name="Alice Mukamana", email="alice@example.com")


# testing validate_row: failures


@pytest.mark.parametrize(
    "values",
    [
        ("1", "Alice"),  # too few
        ("1", "Alice", "alice@example.com", "extra"),  # too many
        (),  # nothing at all
    ],
)
def test_wrong_number_of_values_is_rejected(values: tuple[str, ...]) -> None:
    with pytest.raises(ValidationError, match="expected 3 values"):
        validate_row(make_row(*values))


@pytest.mark.parametrize(
    ("values", "empty_field"),
    [
        (("", "Alice", "alice@example.com"), "user_id"),
        (("1", "", "alice@example.com"), "name"),
        (("1", "Alice", ""), "email"),
        (("   ", "Alice", "alice@example.com"), "user_id"),  # only spaces
        (("1", "   ", "alice@example.com"), "name"),  # only spaces
    ],
)
def test_empty_value_is_rejected(values: tuple[str, ...], empty_field: str) -> None:
    with pytest.raises(ValidationError, match=f"{empty_field} is empty"):
        validate_row(make_row(*values))


def test_invalid_email_is_rejected() -> None:
    with pytest.raises(ValidationError, match="invalid email 'not-an-email'"):
        validate_row(make_row("1", "Alice", "not-an-email"))


def test_error_reports_the_row_line_number() -> None:
    with pytest.raises(ValidationError) as exc_info:
        validate_row(make_row("1", "", "alice@example.com"))

    assert exc_info.value.row_number == 7
