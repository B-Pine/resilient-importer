"""User data model."""

from dataclasses import dataclass, fields


@dataclass(frozen=True)
class User:
    """A validated user record.

    Attributes:
        user_id: Unique identifier of the user.
        name: Full name of the user.
        email: Email address, normalized to lowercase.
    """

    user_id: str
    name: str
    email: str


# Field names in order. The CSV header must match these exactly.
USER_FIELDS: tuple[str, ...] = tuple(field.name for field in fields(User))
