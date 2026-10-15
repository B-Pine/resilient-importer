"""File helpers shared across the importer."""

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import TextIO


@contextmanager
def atomic_write(path: Path) -> Generator[TextIO, None, None]:
    """Write a text file so it is either fully replaced or left untouched.

    Content is written to a temporary file next to the target. Only when
    the ``with`` block finishes without an error is the temporary file
    moved over the target. If anything fails, the target keeps its old
    content and the temporary file is removed.

    Args:
        path: The file to write.

    Yields:
        An open text file to write the new content into.

    Example:
        >>> with atomic_write(Path("users.json")) as file:
        ...     file.write("[]")
    """
    temp_path = path.with_name(path.name + ".tmp")
    try:
        with temp_path.open("w", encoding="utf-8") as file:
            yield file
        temp_path.replace(path)
    finally:
        temp_path.unlink(missing_ok=True)
