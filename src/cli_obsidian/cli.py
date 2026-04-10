import click


@click.group()
@click.option("--json", "-j", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx: click.Context, output_json: bool) -> None:
    """Obsidian vault CLI - interact with your vault from the terminal."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = output_json
