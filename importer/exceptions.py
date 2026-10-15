"""Custom exceptions raised by the importer."""


class ImporterError(Exception):
    """Base class for all importer errors.

    Catching this single class lets the CLI handle every importer
    failure in one place.
    """


class MissingFileError(ImporterError):
    """Raised when the source CSV file does not exist."""


class FileFormatError(ImporterError):
    """Raised when the CSV structure is invalid, such as missing headers."""


class ValidationError(ImporterError):
    """Raised when a single row contains invalid data.

    Attributes:
        row_number: Line number of the offending row in the CSV file.
    """

    def __init__(self, row_number: int, message: str) -> None:
        """Initialize the error with its row number and a description.

        Args:
            row_number: Line number of the offending row in the CSV file.
            message: Explanation of what is wrong with the row.
        """
        super().__init__(f"Row {row_number}: {message}")
        self.row_number = row_number


class DuplicateUserError(ImporterError):
    """Raised when a user with the same ID already exists.

    Attributes:
        user_id: The ID that was found more than once.
    """

    def __init__(self, user_id: str) -> None:
        """Initialize the error with the duplicated user ID.

        Args:
            user_id: The ID that was found more than once.
        """
        super().__init__(f"User with id '{user_id}' already exists")
        self.user_id = user_id


class StorageError(ImporterError):
    """Raised when the JSON database cannot be read or written."""
