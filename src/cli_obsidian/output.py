import json
import sys
from typing import Any


def print_json(data: Any) -> None:
    """Print data as formatted JSON to stdout."""
    print(json.dumps(data, indent=2))


def print_error(message: str) -> None:
    """Print error message to stderr."""
    print(f"Error: {message}", file=sys.stderr)


def print_success(message: str) -> None:
    """Print success message to stdout."""
    print(message)


def print_lines(items: list[str]) -> None:
    """Print items one per line."""
    for item in items:
        print(item)
