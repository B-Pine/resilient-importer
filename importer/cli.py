"""Command-line interface for the importer."""

import argparse
import logging
import sys
from pathlib import Path

from importer.exceptions import ImporterError
from importer.logging_config import configure_logging
from importer.parsers.csv_parser import CsvParser
from importer.repositories.json_user_repository import JsonUserRepository
from importer.services.import_service import ImportService
from importer.utils.formatters import format_report

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Define the command-line arguments.

    Returns:
        A parser for the importer's command-line arguments.
    """
    parser = argparse.ArgumentParser(
        prog="importer",
        description="Import users from a CSV file into a JSON database.",
    )
    parser.add_argument("csv_file", type=Path, help="CSV file to import")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("data/users.json"),
        help="JSON database file (default: data/users.json)",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path("logs/importer.log"),
        help="file for the audit log (default: logs/importer.log)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the importer from the command line.

    Rows that are skipped still count as a successful run, because the
    import itself completed. Only errors that stop the import, such as a
    missing CSV file or a database that cannot be saved, count as failure.

    Args:
        argv: Command-line arguments without the program name. When None,
            the arguments given to the program are used.

    Returns:
        The exit code: 0 if the import completed, 1 if it failed.
    """
    args = build_parser().parse_args(argv)
    configure_logging(args.log_file)

    try:
        service = ImportService(
            parser=CsvParser(), repository=JsonUserRepository(args.db)
        )
        report = service.import_file(args.csv_file)
    except ImporterError as exc:
        logger.error("import failed reason=%s", exc)
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_FAILURE
    else:
        print(format_report(report))
        return EXIT_SUCCESS
