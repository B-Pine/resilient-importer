"""Abstract interface for user storage."""

from abc import ABC, abstractmethod

from importer.models import User


class UserRepository(ABC):
    """Stores users and keeps user IDs unique.

    Changes made with ``add`` are kept in memory until ``save`` is
    called, so a whole import can be written in one step.
    """

    @abstractmethod
    def add(self, user: User) -> None:
        """Add a user to the repository.

        Args:
            user: The validated user to add.

        Raises:
            DuplicateUserError: If a user with the same ID already exists.
        """

    @abstractmethod
    def list_all(self) -> list[User]:
        """Return every user currently in the repository.

        Returns:
            The users, in the order they were added.
        """

    @abstractmethod
    def save(self) -> None:
        """Persist all users.

        Raises:
            StorageError: If the users cannot be written.
        """
