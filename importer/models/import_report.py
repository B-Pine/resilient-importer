"""Import report model."""

from dataclasses import dataclass

from importer.models.skipped_row import SkippedRow


@dataclass(frozen=True)
class ImportReport:
    """The outcome of a completed import.

    A report is only created after the users have been saved, so its
    numbers always match what is stored.

    Attributes:
        imported: Number of users added and saved.
        skipped: Rows that were not imported, in file order.
    """

    imported: int
    skipped: tuple[SkippedRow, ...]
