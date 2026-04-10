from __future__ import annotations

import json as json_module
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

    files = client.list_files_in_dir(directory) if directory else client.list_files_in_vault()

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


@cli.command("search")
@click.argument("query")
@click.option("--context-length", "-c", default=100, help="Context around matches (default: 100)")
@click.pass_context
def search(ctx: click.Context, query: str, context_length: int) -> None:
    """Simple text search across the vault."""
    client = get_obsidian_client()
    results = client.search(query, context_length)

    if ctx.obj["json"]:
        output.print_json(results)
    else:
        output.format_search_results(results)


@cli.command("search-complex")
@click.argument("query", required=False)
@click.option("--file", "query_file", type=click.Path(exists=True), help="Read query from file")
@click.pass_context
def search_complex(ctx: click.Context, query: str | None, query_file: str | None) -> None:
    """Advanced search using JsonLogic query."""
    if query_file:
        with open(query_file) as f:
            query_obj = json_module.load(f)
    elif query:
        query_obj = json_module.loads(query)
    else:
        raise click.ClickException("Provide query as argument or via --file")

    client = get_obsidian_client()
    results = client.search_json(query_obj)

    if ctx.obj["json"]:
        output.print_json(results)
    else:
        output.print_lines(results if isinstance(results, list) else [str(results)])


def read_content(content: str | None, file: str | None) -> str:
    """Read content from argument, file, or stdin."""
    if file:
        with open(file) as f:
            return f.read()
    if content == "-":
        return sys.stdin.read()
    if content:
        return content
    raise click.ClickException("Content required (argument, --file, or - for stdin)")


@cli.command("put")
@click.argument("filepath")
@click.argument("content", required=False)
@click.option(
    "--file",
    "content_file",
    type=click.Path(exists=True),
    help="Read content from file",
)
@click.pass_context
def put_content(ctx: click.Context, filepath: str, content: str | None, content_file: str | None) -> None:
    """Create or overwrite a file."""
    text = read_content(content, content_file)
    client = get_obsidian_client()
    client.put_content(filepath, text)

    if ctx.obj["json"]:
        output.print_json({"status": "success", "filepath": filepath})
    else:
        output.print_success(f"Created/updated {filepath}")


@cli.command("append")
@click.argument("filepath")
@click.argument("content", required=False)
@click.option(
    "--file",
    "content_file",
    type=click.Path(exists=True),
    help="Read content from file",
)
@click.pass_context
def append_content(ctx: click.Context, filepath: str, content: str | None, content_file: str | None) -> None:
    """Append content to a file (creates if doesn't exist)."""
    text = read_content(content, content_file)
    client = get_obsidian_client()
    client.append_content(filepath, text)

    if ctx.obj["json"]:
        output.print_json({"status": "success", "filepath": filepath})
    else:
        output.print_success(f"Appended to {filepath}")


@cli.command("patch")
@click.argument("filepath")
@click.option(
    "--operation",
    "-o",
    type=click.Choice(["append", "prepend", "replace"]),
    required=True,
    help="Operation to perform",
)
@click.option(
    "--target-type",
    "-t",
    type=click.Choice(["heading", "block", "frontmatter"]),
    required=True,
    help="Type of target",
)
@click.option("--target", "-T", required=True, help="Target identifier")
@click.option("--content", "-c", help="Content to insert")
@click.option(
    "--file",
    "content_file",
    type=click.Path(exists=True),
    help="Read content from file",
)
@click.pass_context
def patch_content(
    ctx: click.Context,
    filepath: str,
    operation: str,
    target_type: str,
    target: str,
    content: str | None,
    content_file: str | None,
) -> None:
    """Insert content relative to a heading, block reference, or frontmatter field."""
    text = read_content(content, content_file)
    client = get_obsidian_client()
    client.patch_content(filepath, operation, target_type, target, text)

    if ctx.obj["json"]:
        output.print_json({"status": "success", "filepath": filepath})
    else:
        output.print_success(f"Patched {filepath}")
