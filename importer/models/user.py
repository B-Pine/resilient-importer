"""User data model."""

from dataclasses import dataclass


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
