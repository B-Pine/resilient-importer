"""Validation of raw CSV rows into User records."""

import re

from importer.exceptions import ValidationError
from importer.models import USER_FIELDS, RawRow, User
from importer.utils.formatters import normalize_email, normalize_whitespace

EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def is_valid_email(email: str) -> bool:
    """Check that an email address has a basic valid shape.

    The check is deliberately simple: one "@", no spaces, and a dot in
    the domain part. It catches typos, not every invalid address.

    Args:
        email: The email address to check.

    Returns:
        True if the address has a valid shape, otherwise False.
    """
    return EMAIL_PATTERN.fullmatch(email) is not None


def validate_row(row: RawRow) -> User:
    """Convert a raw CSV row into a validated User.

    Values are cleaned before they are checked, so a name with extra
    spaces or an email in capitals is accepted and stored in a
    consistent form.

    Args:
        row: The unvalidated row read from the CSV file.

    Returns:
        A User built from the cleaned values.

    Raises:
        ValidationError: If the row has the wrong number of values, a
            value is empty, or the email address is invalid.
    """
    if len(row.values) != len(USER_FIELDS):
        raise ValidationError(
            row.line_number,
            f"expected {len(USER_FIELDS)} values, got {len(row.values)}",
        )

    raw_id, raw_name, raw_email = row.values
    user_id = raw_id.strip()
    name = normalize_whitespace(raw_name)
    email = normalize_email(raw_email)

    for field_name, value in zip(USER_FIELDS, (user_id, name, email), strict=True):
        if not value:
            raise ValidationError(row.line_number, f"{field_name} is empty")

    if not is_valid_email(email):
        raise ValidationError(row.line_number, f"invalid email '{email}'")

    return User(user_id=user_id, name=name, email=email)
