"""Text formatting helpers shared across the importer."""

from importer.models import ImportReport


def normalize_whitespace(value: str) -> str:
    """Trim a value and collapse inner whitespace to single spaces.

    Args:
        value: The text to clean, for example "  Jean   Habimana ".

    Returns:
        The cleaned text, for example "Jean Habimana".
    """
    return " ".join(value.split())


def normalize_email(value: str) -> str:
    """Trim an email address and convert it to lowercase.

    Args:
        value: The email address to clean, for example " Alice@Example.COM".

    Returns:
        The cleaned address, for example "alice@example.com".
    """
    return value.strip().lower()


def format_report(report: ImportReport) -> str:
    """Turn an import report into text for the terminal.

    Args:
        report: The report of a completed import.

    Returns:
        A summary line, followed by one line per skipped row if any rows
        were skipped.
    """
    lines = [f"Imported {report.imported} user(s)."]
    if report.skipped:
        lines.append(f"Skipped {len(report.skipped)} row(s):")
        lines.extend(
            f"  line {row.line_number}: {row.reason}" for row in report.skipped
        )
    return "\n".join(lines)
