# CLI Obsidian Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a `cli_obsidian` package that exposes all Obsidian vault operations via a Click-based CLI tool named `obs`.

**Architecture:** New `cli_obsidian/` package imports `Obsidian` class from `mcp_obsidian.obsidian` for API calls. Click handles argument parsing and command structure. Output formatter handles human-readable vs JSON output.

**Tech Stack:** Python 3.11+, Click 8.x, existing `mcp_obsidian.obsidian` API client

---

## File Structure

```
src/
├── mcp_obsidian/           # Existing (unchanged)
│   ├── __init__.py
│   ├── obsidian.py         # API client (reused)
│   ├── tools.py
│   └── server.py
└── cli_obsidian/           # New package
    ├── __init__.py         # Exports main(), cli_main()
    ├── cli.py              # Click commands and groups
    └── output.py           # Output formatting helpers
tests/
└── cli_obsidian/
    ├── __init__.py
    ├── test_cli.py         # CLI command tests
    └── test_output.py      # Output formatter tests
```

**Responsibilities:**
- `cli.py`: Click command definitions, argument parsing, calls to Obsidian API
- `output.py`: Format results as human-readable or JSON, print to stdout/stderr
- `__init__.py`: Package entry point exposing `main()`

---

## Task 1: Add Click dependency and create package skeleton

**Files:**
- Modify: `pyproject.toml:7-12` (dependencies)
- Modify: `pyproject.toml:27` (scripts)
- Create: `src/cli_obsidian/__init__.py`
- Create: `src/cli_obsidian/cli.py`
- Create: `src/cli_obsidian/output.py`
- Create: `tests/cli_obsidian/__init__.py`

- [ ] **Step 1: Add click dependency to pyproject.toml**

Edit `pyproject.toml` dependencies section:

```toml
dependencies = [
 "mcp>=1.1.0",
 "pip_system_certs",
 "python-dotenv>=1.0.1",
 "requests>=2.32.3",
 "click>=8.0.0",
]
```

- [ ] **Step 2: Add obs entry point to pyproject.toml**

Edit `pyproject.toml` scripts section:

```toml
[project.scripts]
mcp-obsidian = "mcp_obsidian:main"
obs = "cli_obsidian:main"
```

- [ ] **Step 3: Create cli_obsidian package __init__.py**

Create `src/cli_obsidian/__init__.py`:

```python
from .cli import cli


def main() -> None:
    """CLI entry point."""
    cli()


__all__ = ["main", "cli"]
```

- [ ] **Step 4: Create output.py with formatting helpers**

Create `src/cli_obsidian/output.py`:

```python
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
```

- [ ] **Step 5: Create minimal cli.py with Click group**

Create `src/cli_obsidian/cli.py`:

```python
import click


@click.group()
@click.option("--json", "-j", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx: click.Context, output_json: bool) -> None:
    """Obsidian vault CLI - interact with your vault from the terminal."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = output_json
```

- [ ] **Step 6: Create test package __init__.py**

Create `tests/cli_obsidian/__init__.py`:

```python
"""Tests for cli_obsidian package."""
```

- [ ] **Step 7: Sync dependencies**

Run: `uv sync`
Expected: Dependencies installed, lockfile updated

- [ ] **Step 8: Verify obs command exists**

Run: `uv run obs --help`
Expected: Shows help with "Obsidian vault CLI" description

- [ ] **Step 9: Commit**

```bash
git add pyproject.toml uv.lock src/cli_obsidian/ tests/cli_obsidian/
git commit -m "feat(cli): add cli_obsidian package skeleton with Click"
```

---

## Task 2: Implement list-files command

**Files:**
- Modify: `src/cli_obsidian/cli.py`
- Create: `tests/cli_obsidian/test_cli.py`

- [ ] **Step 1: Write the failing test for list-files**

Create `tests/cli_obsidian/test_cli.py`:

```python
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from cli_obsidian.cli import cli


class TestListFiles:
    def test_list_files_vault_root(self) -> None:
        """Test listing files in vault root."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.list_files_in_vault.return_value = [
            "notes/todo.md",
            "notes/ideas.md",
            "attachments/",
        ]

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["list-files"])

        assert result.exit_code == 0
        assert "notes/todo.md" in result.output
        assert "notes/ideas.md" in result.output
        assert "attachments/" in result.output

    def test_list_files_directory(self) -> None:
        """Test listing files in a specific directory."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.list_files_in_dir.return_value = [
            "todo.md",
            "ideas.md",
        ]

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["list-files", "notes"])

        assert result.exit_code == 0
        mock_obsidian.list_files_in_dir.assert_called_once_with("notes")

    def test_list_files_json_output(self) -> None:
        """Test listing files with JSON output."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.list_files_in_vault.return_value = ["file1.md", "file2.md"]

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["--json", "list-files"])

        assert result.exit_code == 0
        assert '"file1.md"' in result.output
        assert '"file2.md"' in result.output
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/cli_obsidian/test_cli.py::TestListFiles -v`
Expected: FAIL with "No such command 'list-files'"

- [ ] **Step 3: Implement list-files command**

Edit `src/cli_obsidian/cli.py`:

```python
import os
import click
from dotenv import load_dotenv
from mcp_obsidian.obsidian import Obsidian
from . import output

load_dotenv()


def get_obsidian_client() -> Obsidian:
    """Create Obsidian client from environment variables."""
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/cli_obsidian/test_cli.py::TestListFiles -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add src/cli_obsidian/cli.py tests/cli_obsidian/test_cli.py
git commit -m "feat(cli): add list-files command"
```

---

## Task 3: Implement get command (single and batch)

**Files:**
- Modify: `src/cli_obsidian/cli.py`
- Modify: `tests/cli_obsidian/test_cli.py`

- [ ] **Step 1: Write the failing tests for get command**

Append to `tests/cli_obsidian/test_cli.py`:

```python
class TestGetFiles:
    def test_get_single_file(self) -> None:
        """Test getting a single file's contents."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.get_file_contents.return_value = "# My Note\n\nContent here."

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["get", "notes/todo.md"])

        assert result.exit_code == 0
        assert "# My Note" in result.output
        mock_obsidian.get_file_contents.assert_called_once_with("notes/todo.md")

    def test_get_multiple_files(self) -> None:
        """Test getting multiple files' contents."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.get_batch_file_contents.return_value = (
            "# notes/a.md\n\nContent A\n\n---\n\n"
            "# notes/b.md\n\nContent B\n\n---\n\n"
        )

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["get", "notes/a.md", "notes/b.md"])

        assert result.exit_code == 0
        assert "Content A" in result.output
        assert "Content B" in result.output
        mock_obsidian.get_batch_file_contents.assert_called_once_with(
            ["notes/a.md", "notes/b.md"]
        )

    def test_get_file_json_output(self) -> None:
        """Test getting file with JSON output."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.get_file_contents.return_value = "# Note"

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["--json", "get", "note.md"])

        assert result.exit_code == 0
        assert '"# Note"' in result.output
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/cli_obsidian/test_cli.py::TestGetFiles -v`
Expected: FAIL with "No such command 'get'"

- [ ] **Step 3: Implement get command**

Add to `src/cli_obsidian/cli.py` after the list-files command:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/cli_obsidian/test_cli.py::TestGetFiles -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add src/cli_obsidian/cli.py tests/cli_obsidian/test_cli.py
git commit -m "feat(cli): add get command for single and batch file retrieval"
```

---

## Task 4: Implement search and search-complex commands

**Files:**
- Modify: `src/cli_obsidian/cli.py`
- Modify: `src/cli_obsidian/output.py`
- Modify: `tests/cli_obsidian/test_cli.py`

- [ ] **Step 1: Add search result formatter to output.py**

Add to `src/cli_obsidian/output.py`:

```python
def format_search_results(results: list[dict[str, Any]]) -> None:
    """Print search results in human-readable format."""
    for result in results:
        filename = result.get("filename", "")
        for match in result.get("matches", []):
            context = match.get("context", "").strip()
            print(f"{filename}: {context}")
```

- [ ] **Step 2: Write the failing tests for search commands**

Append to `tests/cli_obsidian/test_cli.py`:

```python
class TestSearch:
    def test_simple_search(self) -> None:
        """Test simple text search."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.search.return_value = [
            {
                "filename": "notes/todo.md",
                "score": 10,
                "matches": [{"context": "...found the query here..."}],
            }
        ]

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["search", "query"])

        assert result.exit_code == 0
        assert "notes/todo.md" in result.output
        mock_obsidian.search.assert_called_once_with("query", 100)

    def test_simple_search_with_context(self) -> None:
        """Test simple search with custom context length."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.search.return_value = []

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(
                    cli, ["search", "query", "--context-length", "200"]
                )

        assert result.exit_code == 0
        mock_obsidian.search.assert_called_once_with("query", 200)

    def test_complex_search(self) -> None:
        """Test JsonLogic search."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.search_json.return_value = ["file1.md", "file2.md"]

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(
                    cli,
                    ["search-complex", '{"glob": ["*.md", {"var": "path"}]}'],
                )

        assert result.exit_code == 0
        mock_obsidian.search_json.assert_called_once()
```

- [ ] **Step 3: Run test to verify it fails**

Run: `uv run pytest tests/cli_obsidian/test_cli.py::TestSearch -v`
Expected: FAIL with "No such command 'search'"

- [ ] **Step 4: Implement search commands**

Add to `src/cli_obsidian/cli.py`:

```python
import json as json_module


@cli.command("search")
@click.argument("query")
@click.option(
    "--context-length", "-c", default=100, help="Context around matches (default: 100)"
)
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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run pytest tests/cli_obsidian/test_cli.py::TestSearch -v`
Expected: PASS (3 tests)

- [ ] **Step 6: Commit**

```bash
git add src/cli_obsidian/cli.py src/cli_obsidian/output.py tests/cli_obsidian/test_cli.py
git commit -m "feat(cli): add search and search-complex commands"
```

---

## Task 5: Implement put, append, and patch commands (content writing)

**Files:**
- Modify: `src/cli_obsidian/cli.py`
- Modify: `tests/cli_obsidian/test_cli.py`

- [ ] **Step 1: Write the failing tests for content commands**

Append to `tests/cli_obsidian/test_cli.py`:

```python
class TestContentCommands:
    def test_put_content(self) -> None:
        """Test creating/overwriting a file."""
        runner = CliRunner()
        mock_obsidian = MagicMock()

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["put", "notes/new.md", "# New Note"])

        assert result.exit_code == 0
        assert "notes/new.md" in result.output
        mock_obsidian.put_content.assert_called_once_with("notes/new.md", "# New Note")

    def test_put_from_stdin(self) -> None:
        """Test put with stdin input."""
        runner = CliRunner()
        mock_obsidian = MagicMock()

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(
                    cli, ["put", "notes/new.md", "-"], input="# From stdin"
                )

        assert result.exit_code == 0
        mock_obsidian.put_content.assert_called_once_with("notes/new.md", "# From stdin")

    def test_append_content(self) -> None:
        """Test appending to a file."""
        runner = CliRunner()
        mock_obsidian = MagicMock()

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["append", "notes/log.md", "- New entry"])

        assert result.exit_code == 0
        mock_obsidian.append_content.assert_called_once_with(
            "notes/log.md", "- New entry"
        )

    def test_patch_content(self) -> None:
        """Test patching content at a target."""
        runner = CliRunner()
        mock_obsidian = MagicMock()

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(
                    cli,
                    [
                        "patch",
                        "notes/todo.md",
                        "-o", "append",
                        "-t", "heading",
                        "-T", "## Tasks",
                        "-c", "- New task",
                    ],
                )

        assert result.exit_code == 0
        mock_obsidian.patch_content.assert_called_once_with(
            "notes/todo.md", "append", "heading", "## Tasks", "- New task"
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/cli_obsidian/test_cli.py::TestContentCommands -v`
Expected: FAIL with "No such command 'put'"

- [ ] **Step 3: Add helper function for reading content**

Add to `src/cli_obsidian/cli.py` after imports:

```python
import sys


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
```

- [ ] **Step 4: Implement put, append, and patch commands**

Add to `src/cli_obsidian/cli.py`:

```python
@cli.command("put")
@click.argument("filepath")
@click.argument("content", required=False)
@click.option("--file", "content_file", type=click.Path(exists=True), help="Read content from file")
@click.pass_context
def put_content(
    ctx: click.Context, filepath: str, content: str | None, content_file: str | None
) -> None:
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
@click.option("--file", "content_file", type=click.Path(exists=True), help="Read content from file")
@click.pass_context
def append_content(
    ctx: click.Context, filepath: str, content: str | None, content_file: str | None
) -> None:
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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run pytest tests/cli_obsidian/test_cli.py::TestContentCommands -v`
Expected: PASS (4 tests)

- [ ] **Step 6: Commit**

```bash
git add src/cli_obsidian/cli.py tests/cli_obsidian/test_cli.py
git commit -m "feat(cli): add put, append, and patch commands"
```

---

## Task 6: Implement delete command with confirmation

**Files:**
- Modify: `src/cli_obsidian/cli.py`
- Modify: `tests/cli_obsidian/test_cli.py`

- [ ] **Step 1: Write the failing tests for delete command**

Append to `tests/cli_obsidian/test_cli.py`:

```python
class TestDeleteCommand:
    def test_delete_requires_confirm(self) -> None:
        """Test that delete requires --confirm flag."""
        runner = CliRunner()
        mock_obsidian = MagicMock()

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["delete", "notes/old.md"])

        assert result.exit_code != 0
        assert "confirm" in result.output.lower() or "confirm" in str(result.exception).lower()
        mock_obsidian.delete_file.assert_not_called()

    def test_delete_with_confirm(self) -> None:
        """Test delete with --confirm flag."""
        runner = CliRunner()
        mock_obsidian = MagicMock()

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["delete", "notes/old.md", "--confirm"])

        assert result.exit_code == 0
        mock_obsidian.delete_file.assert_called_once_with("notes/old.md")

    def test_delete_with_short_flag(self) -> None:
        """Test delete with -y flag."""
        runner = CliRunner()
        mock_obsidian = MagicMock()

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["delete", "notes/old.md", "-y"])

        assert result.exit_code == 0
        mock_obsidian.delete_file.assert_called_once_with("notes/old.md")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/cli_obsidian/test_cli.py::TestDeleteCommand -v`
Expected: FAIL with "No such command 'delete'"

- [ ] **Step 3: Implement delete command**

Add to `src/cli_obsidian/cli.py`:

```python
@cli.command("delete")
@click.argument("filepath")
@click.option("--confirm", "-y", is_flag=True, help="Confirm deletion (required)")
@click.pass_context
def delete_file(ctx: click.Context, filepath: str, confirm: bool) -> None:
    """Delete a file or directory from the vault."""
    if not confirm:
        raise click.ClickException(
            "Deletion requires --confirm or -y flag to prevent accidents"
        )

    client = get_obsidian_client()
    client.delete_file(filepath)

    if ctx.obj["json"]:
        output.print_json({"status": "success", "deleted": filepath})
    else:
        output.print_success(f"Deleted {filepath}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/cli_obsidian/test_cli.py::TestDeleteCommand -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add src/cli_obsidian/cli.py tests/cli_obsidian/test_cli.py
git commit -m "feat(cli): add delete command with confirmation requirement"
```

---

## Task 7: Implement periodic note commands

**Files:**
- Modify: `src/cli_obsidian/cli.py`
- Modify: `tests/cli_obsidian/test_cli.py`

- [ ] **Step 1: Write the failing tests for periodic commands**

Append to `tests/cli_obsidian/test_cli.py`:

```python
class TestPeriodicCommands:
    def test_periodic_note(self) -> None:
        """Test getting current periodic note."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.get_periodic_note.return_value = "# Daily Note\n\nContent"

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["periodic", "daily"])

        assert result.exit_code == 0
        assert "Daily Note" in result.output
        mock_obsidian.get_periodic_note.assert_called_once_with("daily", "content")

    def test_periodic_note_with_metadata(self) -> None:
        """Test getting periodic note with metadata."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.get_periodic_note.return_value = '{"path": "daily/2026-04-10.md"}'

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["periodic", "daily", "--metadata"])

        assert result.exit_code == 0
        mock_obsidian.get_periodic_note.assert_called_once_with("daily", "metadata")

    def test_periodic_recent(self) -> None:
        """Test getting recent periodic notes."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.get_recent_periodic_notes.return_value = [
            {"path": "daily/2026-04-10.md"},
            {"path": "daily/2026-04-09.md"},
        ]

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["periodic-recent", "daily", "--limit", "2"])

        assert result.exit_code == 0
        mock_obsidian.get_recent_periodic_notes.assert_called_once_with("daily", 2, False)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/cli_obsidian/test_cli.py::TestPeriodicCommands -v`
Expected: FAIL with "No such command 'periodic'"

- [ ] **Step 3: Implement periodic commands**

Add to `src/cli_obsidian/cli.py`:

```python
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
def periodic_recent(
    ctx: click.Context, period: str, limit: int, include_content: bool
) -> None:
    """Get recent periodic notes."""
    client = get_obsidian_client()
    results = client.get_recent_periodic_notes(period, limit, include_content)

    if ctx.obj["json"]:
        output.print_json(results)
    else:
        for note in results:
            path = note.get("path", note.get("filename", str(note)))
            print(path)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/cli_obsidian/test_cli.py::TestPeriodicCommands -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add src/cli_obsidian/cli.py tests/cli_obsidian/test_cli.py
git commit -m "feat(cli): add periodic and periodic-recent commands"
```

---

## Task 8: Implement recent-changes command

**Files:**
- Modify: `src/cli_obsidian/cli.py`
- Modify: `tests/cli_obsidian/test_cli.py`

- [ ] **Step 1: Write the failing test for recent-changes**

Append to `tests/cli_obsidian/test_cli.py`:

```python
class TestRecentChanges:
    def test_recent_changes(self) -> None:
        """Test getting recently modified files."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.get_recent_changes.return_value = [
            {"filename": "notes/todo.md", "mtime": "2026-04-10T10:00:00"},
            {"filename": "notes/ideas.md", "mtime": "2026-04-09T15:30:00"},
        ]

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["recent-changes"])

        assert result.exit_code == 0
        mock_obsidian.get_recent_changes.assert_called_once_with(10, 90)

    def test_recent_changes_with_options(self) -> None:
        """Test recent-changes with custom options."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.get_recent_changes.return_value = []

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(
                    cli, ["recent-changes", "--limit", "20", "--days", "7"]
                )

        assert result.exit_code == 0
        mock_obsidian.get_recent_changes.assert_called_once_with(20, 7)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/cli_obsidian/test_cli.py::TestRecentChanges -v`
Expected: FAIL with "No such command 'recent-changes'"

- [ ] **Step 3: Implement recent-changes command**

Add to `src/cli_obsidian/cli.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/cli_obsidian/test_cli.py::TestRecentChanges -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add src/cli_obsidian/cli.py tests/cli_obsidian/test_cli.py
git commit -m "feat(cli): add recent-changes command"
```

---

## Task 9: Add error handling tests and polish

**Files:**
- Modify: `tests/cli_obsidian/test_cli.py`

- [ ] **Step 1: Write error handling tests**

Append to `tests/cli_obsidian/test_cli.py`:

```python
class TestErrorHandling:
    def test_missing_api_key(self) -> None:
        """Test error when API key is missing."""
        runner = CliRunner()

        with patch.dict("os.environ", {}, clear=True):
            # Remove OBSIDIAN_API_KEY if present
            import os
            os.environ.pop("OBSIDIAN_API_KEY", None)
            result = runner.invoke(cli, ["list-files"])

        assert result.exit_code != 0
        assert "OBSIDIAN_API_KEY" in result.output

    def test_connection_error(self) -> None:
        """Test error when Obsidian is not reachable."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.list_files_in_vault.side_effect = Exception(
            "Request failed: Connection refused"
        )

        with patch("cli_obsidian.cli.Obsidian", return_value=mock_obsidian):
            with patch.dict("os.environ", {"OBSIDIAN_API_KEY": "test-key"}):
                result = runner.invoke(cli, ["list-files"])

        assert result.exit_code != 0
        assert "Connection" in result.output or "Error" in result.output
```

- [ ] **Step 2: Run all tests**

Run: `uv run pytest tests/cli_obsidian/ -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/cli_obsidian/test_cli.py
git commit -m "test(cli): add error handling tests"
```

---

## Task 10: Run full test suite and final verification

**Files:**
- None (verification only)

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 2: Run type checker**

Run: `uv run pyright src/cli_obsidian/`
Expected: No errors (or only acceptable library-rooted warnings)

- [ ] **Step 3: Verify CLI help**

Run: `uv run obs --help`
Expected: Shows all commands with descriptions

Run: `uv run obs list-files --help`
Expected: Shows list-files options

- [ ] **Step 4: Final commit with all changes**

```bash
git add -A
git status
# If anything uncommitted:
git commit -m "chore(cli): final cleanup"
```

- [ ] **Step 5: Summary commit**

```bash
git log --oneline -10
```
Expected: Shows all cli_obsidian commits in sequence
