"""Raw CSV row model."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RawRow:
    """A single unvalidated row read from the CSV file.

    Attributes:
        line_number: Line in the CSV file where the row ends.
        values: The row's values as plain strings, exactly as read.
    """

    line_number: int
    values: list[str]
