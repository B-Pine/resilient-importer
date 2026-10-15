"""Text formatting helpers shared across the importer."""


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
