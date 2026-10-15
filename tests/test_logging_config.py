import logging
from pathlib import Path

from importer.logging_config import configure_logging


def test_messages_are_written_to_the_log_file(tmp_path: Path) -> None:
    log_file = tmp_path / "logs" / "importer.log"

    configure_logging(log_file)
    logging.getLogger("importer.test").info("row accepted line=2 user_id=1")

    content = log_file.read_text(encoding="utf-8")
    assert "level=INFO logger=importer.test row accepted line=2 user_id=1" in content


def test_configuring_twice_does_not_duplicate_messages(tmp_path: Path) -> None:
    log_file = tmp_path / "importer.log"

    configure_logging(log_file)
    configure_logging(log_file)
    logging.getLogger("importer").warning("only once")

    assert log_file.read_text(encoding="utf-8").count("only once") == 1


def test_other_libraries_are_not_logged(tmp_path: Path) -> None:
    log_file = tmp_path / "importer.log"

    configure_logging(log_file)
    logging.getLogger("some_library").warning("not ours")

    assert "not ours" not in log_file.read_text(encoding="utf-8")
