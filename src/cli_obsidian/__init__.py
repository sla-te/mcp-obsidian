from .cli import cli


def main() -> None:
    """CLI entry point."""
    cli()


__all__ = ["main", "cli"]
