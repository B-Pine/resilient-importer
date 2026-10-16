"""Skipped row model."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SkippedRow:
    """A CSV row that was not imported, and why.

    Attributes:
        line_number: Line in the CSV file where the row ends.
        reason: Why the row was skipped.
    """

    line_number: int
    reason: str
