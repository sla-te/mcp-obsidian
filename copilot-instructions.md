# MCP Obsidian

MCP server and CLI for Obsidian vault operations via Local REST API plugin.

## Commands

```bash
uv sync                              # Install dependencies
uv run mcp-obsidian                  # Run MCP server
uv run obs --help                    # Run CLI

# Testing
uv run python -m pytest tests/ -v    # Run all tests
uv run python -m pytest tests/cli_obsidian/ -q  # CLI tests only

# Code quality
ruff check .                         # Lint
ruff format .                        # Format
uv run python -m pyright .           # Type check
bandit -r src/                       # Security scan
```

## Architecture

```
src/
├── mcp_obsidian/          # MCP Server package
│   ├── __init__.py        # Entry point (main)
│   ├── server.py          # MCP server setup
│   ├── tools.py           # 13 ToolHandler classes
│   └── obsidian.py        # HTTP/2 client (httpx)
└── cli_obsidian/          # CLI package
    ├── __init__.py        # Entry point (main)
    ├── cli.py             # 11 Click commands
    └── output.py          # Output formatting
```

## Key Files

- `src/mcp_obsidian/obsidian.py` - Core API client, reused by both MCP and CLI
- `src/mcp_obsidian/tools.py` - MCP tool handlers (13 tools)
- `src/cli_obsidian/cli.py` - CLI commands (11 commands)
- `pyproject.toml` - Project config, ruff/pyright settings

## Code Style

- Line length: 100 (ruff)
- Ruff rules: E, F, I, W
- Type checking: basedpyright standard mode
- Python: 3.11+

## Testing

Tests use mocking to avoid real Obsidian API calls:

```python
@patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"})
@patch("mcp_obsidian.obsidian.Obsidian")
def test_example(mock_client):
    mock_client.return_value.method.return_value = "result"
```

## Environment

Required: `OBSIDIAN_API_KEY` - Get from Obsidian Local REST API plugin settings

Optional:
- `OBSIDIAN_HOST` (default: 127.0.0.1)
- `OBSIDIAN_PORT` (default: 27124)
- `OBSIDIAN_PROTOCOL` (default: https)

## Gotchas

- **E402 ignored**: `load_dotenv()` must run before imports that use env vars
- **Lazy imports in CLI**: `cli_obsidian/cli.py` uses lazy import for `Obsidian` class to avoid triggering `mcp_obsidian.__init__` side effects
- **tools.py E501 ignored**: MCP tool descriptions are intentionally long strings
- **httpx not requests**: Project uses httpx with HTTP/2 enabled, not requests
