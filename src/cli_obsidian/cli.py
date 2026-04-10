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


# =============================================================================
# Server & Status Commands
# =============================================================================


@cli.command("status")
@click.pass_context
def server_status(ctx: click.Context) -> None:
    """Get server info and connection status."""
    client = get_obsidian_client()
    info = client.get_server_info()

    if ctx.obj["json"]:
        output.print_json(info)
    else:
        print("Status: OK")
        print(f"Authenticated: {info.get('authenticated', 'unknown')}")
        if "versions" in info:
            print(f"Obsidian: {info['versions'].get('obsidian', 'unknown')}")
            print(f"API: {info['versions'].get('self', 'unknown')}")


# =============================================================================
# Active File Commands
# =============================================================================


@cli.command("active")
@click.option("--metadata", "-m", is_flag=True, help="Include metadata instead of just content")
@click.pass_context
def get_active(ctx: click.Context, metadata: bool) -> None:
    """Get the currently active file in Obsidian."""
    client = get_obsidian_client()
    note_type = "metadata" if metadata else "content"
    content = client.get_active_file(note_type)

    if ctx.obj["json"]:
        output.print_json(content)
    else:
        print(content)


@cli.command("active-append")
@click.argument("content", required=False)
@click.option("--file", "content_file", type=click.Path(exists=True), help="Read content from file")
@click.pass_context
def active_append(ctx: click.Context, content: str | None, content_file: str | None) -> None:
    """Append content to the active file."""
    text = read_content(content, content_file)
    client = get_obsidian_client()
    client.append_active(text)

    if ctx.obj["json"]:
        output.print_json({"status": "success", "action": "appended to active"})
    else:
        output.print_success("Appended to active file")


@cli.command("active-put")
@click.argument("content", required=False)
@click.option("--file", "content_file", type=click.Path(exists=True), help="Read content from file")
@click.pass_context
def active_put(ctx: click.Context, content: str | None, content_file: str | None) -> None:
    """Replace content of the active file."""
    text = read_content(content, content_file)
    client = get_obsidian_client()
    client.put_active(text)

    if ctx.obj["json"]:
        output.print_json({"status": "success", "action": "replaced active"})
    else:
        output.print_success("Replaced active file content")


@cli.command("active-patch")
@click.option(
    "--operation", "-o",
    type=click.Choice(["append", "prepend", "replace"]),
    required=True,
    help="Operation to perform",
)
@click.option(
    "--target-type", "-t",
    type=click.Choice(["heading", "block", "frontmatter"]),
    required=True,
    help="Type of target",
)
@click.option("--target", "-T", required=True, help="Target identifier")
@click.option("--content", "-c", help="Content to insert")
@click.option("--file", "content_file", type=click.Path(exists=True), help="Read content from file")
@click.pass_context
def active_patch(
    ctx: click.Context,
    operation: str,
    target_type: str,
    target: str,
    content: str | None,
    content_file: str | None,
) -> None:
    """Patch content in the active file relative to a target."""
    text = read_content(content, content_file)
    client = get_obsidian_client()
    client.patch_active(operation, target_type, target, text)

    if ctx.obj["json"]:
        output.print_json({"status": "success", "action": "patched active"})
    else:
        output.print_success("Patched active file")


@cli.command("active-delete")
@click.option("--confirm", "-y", is_flag=True, help="Confirm deletion (required)")
@click.pass_context
def active_delete(ctx: click.Context, confirm: bool) -> None:
    """Delete the currently active file."""
    if not confirm:
        raise click.ClickException("Deletion requires --confirm or -y flag to prevent accidents")

    client = get_obsidian_client()
    client.delete_active()

    if ctx.obj["json"]:
        output.print_json({"status": "success", "action": "deleted active"})
    else:
        output.print_success("Deleted active file")


# =============================================================================
# Command Execution
# =============================================================================


@cli.command("commands")
@click.pass_context
def list_commands(ctx: click.Context) -> None:
    """List available Obsidian commands."""
    client = get_obsidian_client()
    commands = client.list_commands()

    if ctx.obj["json"]:
        output.print_json(commands)
    else:
        cmd_list = commands.get("commands", commands)
        for cmd in cmd_list:
            cmd_id = cmd.get("id", str(cmd))
            cmd_name = cmd.get("name", "")
            print(f"{cmd_id}: {cmd_name}" if cmd_name else cmd_id)


@cli.command("run")
@click.argument("command_id")
@click.pass_context
def run_command(ctx: click.Context, command_id: str) -> None:
    """Execute an Obsidian command by ID."""
    client = get_obsidian_client()
    client.execute_command(command_id)

    if ctx.obj["json"]:
        output.print_json({"status": "success", "command": command_id})
    else:
        output.print_success(f"Executed command: {command_id}")


@cli.command("open")
@click.argument("filepath")
@click.option("--new-pane", "-n", is_flag=True, help="Open in a new pane")
@click.pass_context
def open_file(ctx: click.Context, filepath: str, new_pane: bool) -> None:
    """Open a file in Obsidian."""
    client = get_obsidian_client()
    client.open_file(filepath, new_leaf=new_pane)

    if ctx.obj["json"]:
        output.print_json({"status": "success", "opened": filepath})
    else:
        output.print_success(f"Opened {filepath}")


# =============================================================================
# Periodic Note Write Commands
# =============================================================================


@cli.command("periodic-append")
@click.argument("period", type=click.Choice(VALID_PERIODS))
@click.argument("content", required=False)
@click.option("--file", "content_file", type=click.Path(exists=True), help="Read content from file")
@click.pass_context
def periodic_append(ctx: click.Context, period: str, content: str | None, content_file: str | None) -> None:
    """Append to a periodic note (creates if doesn't exist)."""
    text = read_content(content, content_file)
    client = get_obsidian_client()
    client.append_periodic(period, text)

    if ctx.obj["json"]:
        output.print_json({"status": "success", "period": period, "action": "appended"})
    else:
        output.print_success(f"Appended to {period} note")


@cli.command("periodic-put")
@click.argument("period", type=click.Choice(VALID_PERIODS))
@click.argument("content", required=False)
@click.option("--file", "content_file", type=click.Path(exists=True), help="Read content from file")
@click.pass_context
def periodic_put(ctx: click.Context, period: str, content: str | None, content_file: str | None) -> None:
    """Replace content of a periodic note."""
    text = read_content(content, content_file)
    client = get_obsidian_client()
    client.put_periodic(period, text)

    if ctx.obj["json"]:
        output.print_json({"status": "success", "period": period, "action": "replaced"})
    else:
        output.print_success(f"Replaced {period} note content")


@cli.command("periodic-patch")
@click.argument("period", type=click.Choice(VALID_PERIODS))
@click.option(
    "--operation", "-o",
    type=click.Choice(["append", "prepend", "replace"]),
    required=True,
    help="Operation to perform",
)
@click.option(
    "--target-type", "-t",
    type=click.Choice(["heading", "block", "frontmatter"]),
    required=True,
    help="Type of target",
)
@click.option("--target", "-T", required=True, help="Target identifier")
@click.option("--content", "-c", help="Content to insert")
@click.option("--file", "content_file", type=click.Path(exists=True), help="Read content from file")
@click.pass_context
def periodic_patch(
    ctx: click.Context,
    period: str,
    operation: str,
    target_type: str,
    target: str,
    content: str | None,
    content_file: str | None,
) -> None:
    """Patch content in a periodic note relative to a target."""
    text = read_content(content, content_file)
    client = get_obsidian_client()
    client.patch_periodic(period, operation, target_type, target, text)

    if ctx.obj["json"]:
        output.print_json({"status": "success", "period": period, "action": "patched"})
    else:
        output.print_success(f"Patched {period} note")


@cli.command("periodic-delete")
@click.argument("period", type=click.Choice(VALID_PERIODS))
@click.option("--confirm", "-y", is_flag=True, help="Confirm deletion (required)")
@click.pass_context
def periodic_delete(ctx: click.Context, period: str, confirm: bool) -> None:
    """Delete a periodic note."""
    if not confirm:
        raise click.ClickException("Deletion requires --confirm or -y flag to prevent accidents")

    client = get_obsidian_client()
    client.delete_periodic(period)

    if ctx.obj["json"]:
        output.print_json({"status": "success", "period": period, "action": "deleted"})
    else:
        output.print_success(f"Deleted {period} note")
