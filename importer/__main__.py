"""Allow the importer to be run with ``python -m importer``."""

from importer.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
