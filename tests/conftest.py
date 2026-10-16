from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from importer.logging_config import reset_logging


@pytest.fixture
def write_csv(tmp_path: Path) -> Callable[[str], Path]:
    def _write(content: str) -> Path:
        path = tmp_path / "users.csv"
        path.write_text(content, encoding="utf-8")
        return path

    return _write


@pytest.fixture(autouse=True)
def clean_logging() -> Iterator[None]:
    yield
    reset_logging()
