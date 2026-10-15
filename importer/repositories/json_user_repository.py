"""User repository backed by a JSON file."""

import json
from dataclasses import asdict
from pathlib import Path

from importer.exceptions import DuplicateUserError, StorageError
from importer.models import User
from importer.repositories.user_repository import UserRepository
from importer.utils.files import atomic_write


class JsonUserRepository(UserRepository):
    """Stores users in a JSON file that acts as a simple database.

    Existing users are loaded once, when the repository is created. New
    users are held in memory until ``save`` writes them all at once.
    """

    def __init__(self, path: Path) -> None:
        """Open the repository and load any users already stored.

        A missing file is treated as an empty database, so the first
        import creates it.

        Args:
            path: Location of the JSON database file.

        Raises:
            StorageError: If the file exists but cannot be read or does
                not contain a valid list of users.
        """
        self._path = path
        self._users = self._load()

    def add(self, user: User) -> None:
        """Add a user, keeping user IDs unique.

        Args:
            user: The validated user to add.

        Raises:
            DuplicateUserError: If a user with the same ID is already
                stored or was added earlier in this session.
        """
        if user.user_id in self._users:
            raise DuplicateUserError(user.user_id)
        self._users[user.user_id] = user

    def list_all(self) -> list[User]:
        """Return every user, both previously stored and newly added.

        Returns:
            A new list of users, so callers cannot change the
            repository's contents by modifying it.
        """
        return list(self._users.values())

    def save(self) -> None:
        """Write all users to the JSON file in a single atomic step.

        Raises:
            StorageError: If the file cannot be written. The previous
                file content is left unchanged.
        """
        data = [asdict(user) for user in self._users.values()]
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with atomic_write(self._path) as file:
                json.dump(data, file, indent=2)
        except OSError as exc:
            raise StorageError(f"Could not write {self._path}: {exc}") from exc

    def _load(self) -> dict[str, User]:
        """Read the users stored in the JSON file.

        Returns:
            The stored users keyed by user ID, or an empty dict if the
            file does not exist yet.

        Raises:
            StorageError: If the file cannot be read or is not a valid
                list of users.
        """
        try:
            text = self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return {}
        except OSError as exc:
            raise StorageError(f"Could not read {self._path}: {exc}") from exc

        try:
            users = [User(**item) for item in json.loads(text)]
        except (json.JSONDecodeError, TypeError) as exc:
            raise StorageError(f"Database file is corrupted: {self._path}") from exc
        return {user.user_id: user for user in users}
