from collections.abc import Callable
from pathlib import Path

import pytest


@pytest.fixture
def write_csv(tmp_path: Path) -> Callable[[str], Path]:
    def _write(content: str) -> Path:
        path = tmp_path / "users.csv"
        path.write_text(content, encoding="utf-8")
        return path

    return _write
