# CLI Obsidian Design Specification

A command-line interface for interacting with Obsidian vaults via the Local REST API plugin.

## Overview

**Purpose**: Provide direct terminal access to all Obsidian vault operations currently available through the MCP server, enabling quick vault operations from the command line.

**Target user**: Developers and power users who want to interact with their Obsidian vault from the terminal without going through an AI client.

**CLI name**: `obs`

## Architecture

```
src/
├── mcp_obsidian/           # Existing MCP server package (unchanged)
│   ├── __init__.py
│   ├── obsidian.py         # API client (reused by CLI)
│   ├── tools.py
│   └── server.py
└── cli_obsidian/           # New CLI package
    ├── __init__.py         # Exports main() entry point
    └── cli.py              # Click commands
```

### Key Decisions

1. **Separate package**: `cli_obsidian/` is a new package alongside `mcp_obsidian/`
2. **Reuses existing API client**: Imports `Obsidian` class from `mcp_obsidian.obsidian`
3. **Shared configuration**: Same environment variables (`OBSIDIAN_API_KEY`, `OBSIDIAN_HOST`, `OBSIDIAN_PORT`, `OBSIDIAN_PROTOCOL`)
4. **Entry point**: `obs = "cli_obsidian:main"` in `pyproject.toml`
5. **Framework**: Click library for command parsing

### Dependencies

Add to `pyproject.toml`:
```toml
dependencies = [
    # ... existing deps ...
    "click>=8.0.0",
]
```

## Commands

All commands mirror the 13 MCP tools. Commands use kebab-case naming.

### File Operations

#### `obs list-files [DIRECTORY]`
List files in the vault root or a specific directory.

| Option | Description |
|--------|-------------|
| `DIRECTORY` | Optional path to list (omit for vault root) |
| `--json` / `-j` | Output as JSON |

```bash
obs list-files
obs list-files notes/projects
obs list-files --json
```

#### `obs get FILEPATH [FILEPATH...]`
Get contents of one or more files.

| Option | Description |
|--------|-------------|
| `FILEPATH` | Path(s) to file(s) relative to vault root |
| `--json` / `-j` | Output as JSON |

```bash
obs get notes/todo.md
obs get notes/a.md notes/b.md notes/c.md
```

When multiple files are provided, outputs are concatenated with headers (matching `obsidian_batch_get_file_contents` behavior).

#### `obs put FILEPATH [CONTENT]`
Create or overwrite a file.

| Option | Description |
|--------|-------------|
| `FILEPATH` | Path to file relative to vault root |
| `CONTENT` | Content to write (or use `--file` / `-`) |
| `--file FILE` | Read content from local file |
| `--json` / `-j` | Output as JSON |

```bash
obs put notes/new.md "# New Note"
obs put notes/new.md --file ./local-content.md
echo "# New Note" | obs put notes/new.md -
```

#### `obs append FILEPATH [CONTENT]`
Append content to a file (creates if doesn't exist).

| Option | Description |
|--------|-------------|
| `FILEPATH` | Path to file relative to vault root |
| `CONTENT` | Content to append (or use `--file` / `-`) |
| `--file FILE` | Read content from local file |
| `--json` / `-j` | Output as JSON |

```bash
obs append notes/log.md "- New entry"
cat updates.md | obs append notes/changelog.md -
```

#### `obs patch FILEPATH`
Insert content relative to a heading, block reference, or frontmatter field.

| Option | Description |
|--------|-------------|
| `FILEPATH` | Path to file relative to vault root |
| `--operation` / `-o` | Operation: `append`, `prepend`, or `replace` (required) |
| `--target-type` / `-t` | Target type: `heading`, `block`, or `frontmatter` (required) |
| `--target` / `-T` | Target identifier (required) |
| `--content` / `-c` | Content to insert (or use `--file` / `-`) |
| `--file FILE` | Read content from local file |
| `--json` / `-j` | Output as JSON |

```bash
obs patch notes/todo.md -o append -t heading -T "## Tasks" -c "- New task"
```

#### `obs delete FILEPATH --confirm`
Delete a file or directory.

| Option | Description |
|--------|-------------|
| `FILEPATH` | Path to file/directory relative to vault root |
| `--confirm` / `-y` | Required confirmation flag |
| `--json` / `-j` | Output as JSON |

```bash
obs delete notes/old.md --confirm
obs delete notes/old.md -y
```

### Search Operations

#### `obs search QUERY`
Simple text search across the vault.

| Option | Description |
|--------|-------------|
| `QUERY` | Text to search for |
| `--context-length` / `-c` | Context around matches (default: 100) |
| `--json` / `-j` | Output as JSON |

```bash
obs search "project alpha"
obs search "TODO" --context-length 200
```

#### `obs search-complex QUERY`
Advanced search using JsonLogic query.

| Option | Description |
|--------|-------------|
| `QUERY` | JsonLogic query as JSON string |
| `--file FILE` | Read query from file |
| `--json` / `-j` | Output as JSON |

```bash
obs search-complex '{"glob": ["*.md", {"var": "path"}]}'
obs search-complex --file query.json
```

### Periodic Notes

#### `obs periodic PERIOD`
Get the current periodic note.

| Option | Description |
|--------|-------------|
| `PERIOD` | Period type: `daily`, `weekly`, `monthly`, `quarterly`, `yearly` |
| `--metadata` / `-m` | Include metadata (paths, tags) instead of just content |
| `--json` / `-j` | Output as JSON |

```bash
obs periodic daily
obs periodic weekly --metadata
```

#### `obs periodic-recent PERIOD`
Get recent periodic notes.

| Option | Description |
|--------|-------------|
| `PERIOD` | Period type: `daily`, `weekly`, `monthly`, `quarterly`, `yearly` |
| `--limit` / `-l` | Max notes to return (default: 5, max: 50) |
| `--include-content` | Include note content |
| `--json` / `-j` | Output as JSON |

```bash
obs periodic-recent daily --limit 7
obs periodic-recent weekly --include-content
```

### Recent Changes

#### `obs recent-changes`
Get recently modified files.

| Option | Description |
|--------|-------------|
| `--limit` / `-l` | Max files to return (default: 10, max: 100) |
| `--days` / `-d` | Only files modified within N days (default: 90) |
| `--json` / `-j` | Output as JSON |

```bash
obs recent-changes
obs recent-changes --limit 20 --days 7
```

## Global Options

Applied to all commands:

| Option | Description |
|--------|-------------|
| `--json` / `-j` | Output as JSON instead of human-readable |
| `--help` | Show help for command |

## Output Formatting

### Human-readable (default)

- **File lists**: One file per line
- **Search results**: `filename:line: match context` format
- **File contents**: Raw content without modification
- **Success messages**: Short confirmation, e.g., "Appended to notes/todo.md"

### JSON (--json flag)

Structured JSON matching the underlying API response shape. Suitable for scripting and piping to `jq`.

## Error Handling

- **Exit codes**: 0 on success, non-zero on failure
- **Error output**: Messages to stderr with clear context
- **Missing env vars**: Specific message indicating which variable is missing
- **Connection failures**: Clear message about Obsidian REST API availability

Example error messages:
```
Error: OBSIDIAN_API_KEY environment variable not set
Error: Could not connect to Obsidian REST API at https://127.0.0.1:27124
Error: File not found: notes/missing.md
```

## Configuration

Uses the same environment variables as the MCP server:

| Variable | Description | Default |
|----------|-------------|---------|
| `OBSIDIAN_API_KEY` | API key from Obsidian plugin (required) | - |
| `OBSIDIAN_HOST` | Obsidian REST API host | `127.0.0.1` |
| `OBSIDIAN_PORT` | Obsidian REST API port | `27124` |
| `OBSIDIAN_PROTOCOL` | Protocol (`http` or `https`) | `https` |

Supports `.env` file in the current working directory via `python-dotenv`.

## Implementation Notes

1. The `Obsidian` class from `mcp_obsidian.obsidian` handles all API communication
2. CLI code focuses on argument parsing, input handling, and output formatting
3. Stdin support via `-` argument reads from `sys.stdin`
4. The `--file` option reads content from a local file path
