from __future__ import annotations

import os
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
