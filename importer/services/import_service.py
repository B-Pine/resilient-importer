"""Coordination of a complete CSV import."""

import logging
from pathlib import Path

from importer.exceptions import DuplicateUserError, ValidationError
from importer.models import ImportReport, SkippedRow
from importer.parsers import CsvParser
from importer.repositories.user_repository import UserRepository
from importer.utils.validators import validate_row

logger = logging.getLogger(__name__)


class ImportService:
    """Imports users from a CSV file into a repository.

    The service connects the other components: the parser reads rows,
    the validator turns them into users, and the repository stores
    them. It holds no import logic of its own beyond deciding what to
    do with each row.
    """

    def __init__(self, parser: CsvParser, repository: UserRepository) -> None:
        """Create the service with the components it coordinates.

        Args:
            parser: Reads raw rows from the CSV file.
            repository: Stores the imported users.
        """
        self._parser = parser
        self._repository = repository

    def import_file(self, path: Path) -> ImportReport:
        """Import every valid, non-duplicate user from a CSV file.

        Invalid and duplicate rows are skipped and listed in the report.
        Valid users are saved together in one step at the end.

        Args:
            path: Location of the CSV file to import.

        Returns:
            A report of how many users were imported and which rows
            were skipped.

        Raises:
            MissingFileError: If the CSV file does not exist.
            FileFormatError: If the CSV file cannot be parsed.
            StorageError: If the repository cannot save the users. In
                that case nothing is stored.
        """
        logger.info("import started file=%s", path)
        rows = self._parser.parse(path)

        imported = 0
        skipped: list[SkippedRow] = []
        for row in rows:
            try:
                user = validate_row(row)
                self._repository.add(user)
            except (ValidationError, DuplicateUserError) as exc:
                skipped.append(SkippedRow(line_number=row.line_number, reason=str(exc)))
                logger.warning("row skipped line=%d reason=%s", row.line_number, exc)
            else:
                imported += 1
                logger.info(
                    "row accepted line=%d user_id=%s", row.line_number, user.user_id
                )

        if imported:
            self._repository.save()

        logger.info("import finished imported=%d skipped=%d", imported, len(skipped))
        return ImportReport(imported=imported, skipped=tuple(skipped))
