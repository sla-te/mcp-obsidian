# MCP Obsidian

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.1.0+-green.svg)](https://github.com/modelcontextprotocol/mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

MCP server and CLI to interact with Obsidian via the Local REST API community plugin.

<a href="https://glama.ai/mcp/servers/3wko1bhuek"><img width="380" height="200" src="https://glama.ai/mcp/servers/3wko1bhuek/badge" alt="server for Obsidian MCP server" /></a>

## Features

- **MCP Server**: Full Model Context Protocol integration for AI assistants
- **CLI Tool**: Direct terminal access to your Obsidian vault via `obs` command
- **HTTP/2 Support**: Fast, efficient connections using httpx
- **13 MCP Tools**: Comprehensive vault operations
- **11 CLI Commands**: All MCP functionality available from the terminal

## Quick Start

### Prerequisites

- Python 3.11+
- [Obsidian](https://obsidian.md/) with [Local REST API plugin](https://github.com/coddingtonbear/obsidian-local-rest-api) installed
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Installation

```bash
# Install from PyPI
uvx mcp-obsidian

# Or install for CLI usage
uv tool install mcp-obsidian
```

### Configuration

Set your Obsidian REST API key:

```bash
export OBSIDIAN_API_KEY="your_api_key_here"
export OBSIDIAN_HOST="127.0.0.1"  # optional, default
export OBSIDIAN_PORT="27124"       # optional, default
```

Or create a `.env` file in your working directory.

## MCP Server

### MCP Tools

The server provides 13 tools for AI assistants:

| Tool | Description |
|------|-------------|
| `obsidian_list_files_in_vault` | List all files in vault root |
| `obsidian_list_files_in_dir` | List files in a specific directory |
| `obsidian_get_file_contents` | Get single file content |
| `obsidian_batch_get_file_contents` | Get multiple files at once |
| `obsidian_simple_search` | Text search across vault |
| `obsidian_complex_search` | JsonLogic-based advanced search |
| `obsidian_append_content` | Append to file (creates if needed) |
| `obsidian_put_content` | Create or overwrite file |
| `obsidian_patch_content` | Insert relative to heading/block |
| `obsidian_delete_file` | Delete file or directory |
| `obsidian_get_periodic_note` | Get current daily/weekly/monthly note |
| `obsidian_get_recent_periodic_notes` | Get recent periodic notes |
| `obsidian_get_recent_changes` | Get recently modified files |

### Claude Desktop Configuration

On MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "uvx",
      "args": ["mcp-obsidian"],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key>",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27124"
      }
    }
  }
}
```

<details>
<summary>Development Configuration</summary>

```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-obsidian", "run", "mcp-obsidian"],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key>"
      }
    }
  }
}
```
</details>

### Example Prompts

- "Get the contents of the last architecture call note and summarize them"
- "Search for all files where Azure CosmosDb is mentioned"
- "Summarize the last meeting notes and put them into a new note 'summary.md'"

## CLI Tool

The `obs` command provides terminal access to all Obsidian operations.

### CLI Commands

```bash
# List files
obs list-files                    # List vault root
obs list-files "Projects/"        # List specific directory

# Read files
obs get "notes/meeting.md"        # Get single file
obs get file1.md file2.md         # Get multiple files

# Search
obs search "kubernetes"           # Simple text search
obs search-complex '{"glob": ["*.md", {"var": "path"}]}'

# Write content
obs put "new-note.md" "# Title"   # Create/overwrite file
obs append "log.md" "New entry"   # Append to file
obs patch "note.md" -o append -t heading -T "## Section" -c "Content"

# Delete (requires confirmation)
obs delete "old-note.md" --confirm

# Periodic notes
obs periodic daily                # Get today's daily note
obs periodic-recent weekly -l 5   # Get last 5 weekly notes

# Recent changes
obs recent-changes -l 20 -d 30    # Last 20 files modified in 30 days
```

### CLI Options

```bash
obs --json <command>    # Output as JSON
obs --help              # Show help
```

### Piping Content

```bash
# Read from file
obs put "note.md" --file input.txt

# Read from stdin
echo "Content" | obs append "note.md" -
cat document.md | obs put "copy.md" -
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interfaces                         │
├──────────────────────────┬──────────────────────────────────┤
│      MCP Server          │           CLI (obs)              │
│   (mcp_obsidian)         │        (cli_obsidian)            │
├──────────────────────────┴──────────────────────────────────┤
│                    Obsidian API Client                       │
│                  (mcp_obsidian.obsidian)                     │
│                     HTTP/2 via httpx                         │
├─────────────────────────────────────────────────────────────┤
│              Obsidian Local REST API Plugin                  │
│                    (port 27124)                              │
└─────────────────────────────────────────────────────────────┘
```

## API Reference

### Obsidian Client

```python
from mcp_obsidian.obsidian import Obsidian

# Initialize client
client = Obsidian(api_key="your_key")

# List files
files = client.list_files_in_vault()
files = client.list_files_in_dir("Projects/")

# Read content
content = client.get_file_contents("note.md")
batch = client.get_batch_file_contents(["a.md", "b.md"])

# Search
results = client.search("query", context_length=100)
results = client.search_json({"glob": ["*.md", {"var": "path"}]})

# Write content
client.put_content("path.md", "content")
client.append_content("path.md", "more content")
client.patch_content("path.md", "append", "heading", "## Section", "content")

# Delete
client.delete_file("path.md")

# Periodic notes
note = client.get_periodic_note("daily")
recent = client.get_recent_periodic_notes("weekly", limit=5)
changes = client.get_recent_changes(limit=10, days=90)

# Cleanup
client.close()
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OBSIDIAN_API_KEY` | REST API key from plugin settings | Required |
| `OBSIDIAN_HOST` | Obsidian host address | `127.0.0.1` |
| `OBSIDIAN_PORT` | REST API port | `27124` |
| `OBSIDIAN_PROTOCOL` | Protocol (http/https) | `https` |

## Development

### Setup

```bash
git clone https://github.com/your-org/mcp-obsidian.git
cd mcp-obsidian
uv sync
```

### Testing

```bash
uv run pytest tests/ -v
```

### Code Quality

```bash
ruff check .                    # Linting
ruff format .                   # Formatting
uv run python -m pyright .      # Type checking
bandit -r src/                  # Security scan
```

### Debugging MCP Server

Use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector):

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/mcp-obsidian run mcp-obsidian
```

Server logs (macOS):
```bash
tail -f ~/Library/Logs/Claude/mcp-server-mcp-obsidian.log
```

## Project Structure

```
mcp-obsidian/
├── src/
│   ├── mcp_obsidian/          # MCP server package
│   │   ├── __init__.py        # Entry point
│   │   ├── server.py          # MCP server setup
│   │   ├── tools.py           # Tool handlers
│   │   └── obsidian.py        # HTTP client
│   └── cli_obsidian/          # CLI package
│       ├── __init__.py        # Entry point
│       ├── cli.py             # Click commands
│       └── output.py          # Output formatting
├── tests/
│   └── cli_obsidian/          # CLI tests
├── pyproject.toml             # Project config
└── README.md
```

## License

MIT License - see [LICENSE](LICENSE) for details
