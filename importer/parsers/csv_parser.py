"""CSV parsing for user import files."""

import csv
from pathlib import Path

from importer.exceptions import FileFormatError, MissingFileError
from importer.models import USER_FIELDS, RawRow


class CsvParser:
    """Reads raw rows from a user CSV file.

    The parser only checks the file as a whole: that it exists, can be
    decoded, and has the expected header. Checking individual rows is
    the validator's job.
    """

    def parse(self, path: Path) -> list[RawRow]:
        """Read every data row from the CSV file.

        Args:
            path: Location of the CSV file.

        Returns:
            The data rows in file order, without the header or blank lines.

        Raises:
            MissingFileError: If the file does not exist.
            FileFormatError: If the file is empty, is not valid UTF-8, or
                has an unexpected header.
        """
        try:
            with path.open(encoding="utf-8", newline="") as file:
                reader = csv.reader(file)  # reads line by line
                self._check_header(next(reader, None))
                rows: list[RawRow] = []
                for values in reader:
                    if not values:
                        continue
                    rows.append(RawRow(line_number=reader.line_num, values=values))
                return rows
        except FileNotFoundError as exc:
            raise MissingFileError(f"File not found: {path}") from exc
        except UnicodeDecodeError as exc:
            raise FileFormatError(f"File is not valid UTF-8: {path}") from exc

    @staticmethod
    def _check_header(header: list[str] | None) -> None:
        """Ensure the header matches the expected columns.

        Args:
            header: The first row of the file, or None if the file is empty.

        Raises:
            FileFormatError: If the file is empty or the header is wrong.
        """
        if header is None:
            raise FileFormatError("File is empty")
        columns = tuple(column.strip() for column in header)
        if columns != USER_FIELDS:
            raise FileFormatError(
                f"Expected header {', '.join(USER_FIELDS)}, got {', '.join(columns)}"
            )
