from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

import click
from dotenv import load_dotenv

from . import output

if TYPE_CHECKING:
    from mcp_obsidian.obsidian import Obsidian

load_dotenv()


def get_obsidian_client() -> Obsidian:
    """Create Obsidian client from environment variables."""
    # Lazy import to avoid triggering mcp_obsidian.__init__ which has side effects
    from mcp_obsidian.obsidian import Obsidian

    api_key = os.getenv("OBSIDIAN_API_KEY")
    if not api_key:
        raise click.ClickException("OBSIDIAN_API_KEY environment variable not set")
    return Obsidian(api_key=api_key)


@click.group()
@click.option("--json", "-j", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx: click.Context, output_json: bool) -> None:
    """Obsidian vault CLI - interact with your vault from the terminal."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = output_json


@cli.command("list-files")
@click.argument("directory", required=False)
@click.pass_context
def list_files(ctx: click.Context, directory: str | None) -> None:
    """List files in the vault root or a specific directory."""
    client = get_obsidian_client()

    if directory:
        files = client.list_files_in_dir(directory)
    else:
        files = client.list_files_in_vault()

    if ctx.obj["json"]:
        output.print_json(files)
    else:
        output.print_lines(files)


@cli.command("get")
@click.argument("filepaths", nargs=-1, required=True)
@click.pass_context
def get_files(ctx: click.Context, filepaths: tuple[str, ...]) -> None:
    """Get contents of one or more files."""
    client = get_obsidian_client()

    if len(filepaths) == 1:
        content = client.get_file_contents(filepaths[0])
    else:
        content = client.get_batch_file_contents(list(filepaths))

    if ctx.obj["json"]:
        output.print_json(content)
    else:
        print(content)


VALID_PERIODS = ["daily", "weekly", "monthly", "quarterly", "yearly"]


@cli.command("periodic")
@click.argument("period", type=click.Choice(VALID_PERIODS))
@click.option("--metadata", "-m", is_flag=True, help="Include metadata instead of just content")
@click.pass_context
def periodic_note(ctx: click.Context, period: str, metadata: bool) -> None:
    """Get the current periodic note."""
    client = get_obsidian_client()
    note_type = "metadata" if metadata else "content"
    content = client.get_periodic_note(period, note_type)

    if ctx.obj["json"]:
        output.print_json(content)
    else:
        print(content)


@cli.command("periodic-recent")
@click.argument("period", type=click.Choice(VALID_PERIODS))
@click.option("--limit", "-l", default=5, help="Max notes to return (default: 5)")
@click.option("--include-content", is_flag=True, help="Include note content")
@click.pass_context
def periodic_recent(ctx: click.Context, period: str, limit: int, include_content: bool) -> None:
    """Get recent periodic notes."""
    client = get_obsidian_client()
    results = client.get_recent_periodic_notes(period, limit, include_content)

    if ctx.obj["json"]:
        output.print_json(results)
    else:
        for note in results:
            path = note.get("path", note.get("filename", str(note)))
            print(path)


@cli.command("recent-changes")
@click.option("--limit", "-l", default=10, help="Max files to return (default: 10)")
@click.option("--days", "-d", default=90, help="Files modified within N days (default: 90)")
@click.pass_context
def recent_changes(ctx: click.Context, limit: int, days: int) -> None:
    """Get recently modified files in the vault."""
    client = get_obsidian_client()
    results = client.get_recent_changes(limit, days)

    if ctx.obj["json"]:
        output.print_json(results)
    else:
        for item in results:
            filename = item.get("filename", str(item))
            print(filename)


@cli.command("delete")
@click.argument("filepath")
@click.option("--confirm", "-y", is_flag=True, help="Confirm deletion (required)")
@click.pass_context
def delete_file(ctx: click.Context, filepath: str, confirm: bool) -> None:
    """Delete a file or directory from the vault."""
    if not confirm:
        raise click.ClickException("Deletion requires --confirm or -y flag to prevent accidents")

    client = get_obsidian_client()
    client.delete_file(filepath)

    if ctx.obj["json"]:
        output.print_json({"status": "success", "deleted": filepath})
    else:
        output.print_success(f"Deleted {filepath}")
