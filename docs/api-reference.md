# API Reference

Complete reference for the `mcp_obsidian.obsidian.Obsidian` client class.

## Obsidian Client

### Constructor

```python
Obsidian(
    api_key: str,
    protocol: str = "https",
    host: str = "127.0.0.1",
    port: int = 27124,
    verify_ssl: bool = False
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | str | Required | API key from Obsidian REST API plugin |
| `protocol` | str | `"https"` | HTTP protocol (`http` or `https`) |
| `host` | str | `"127.0.0.1"` | Obsidian host address |
| `port` | int | `27124` | REST API port |
| `verify_ssl` | bool | `False` | Verify SSL certificates |

**Environment Variables:**

The constructor reads defaults from environment variables:

- `OBSIDIAN_PROTOCOL` - Protocol (default: `https`)
- `OBSIDIAN_HOST` - Host (default: `127.0.0.1`)
- `OBSIDIAN_PORT` - Port (default: `27124`)

**Example:**

```python
from mcp_obsidian.obsidian import Obsidian

# Using environment variables
client = Obsidian(api_key="your-api-key")

# Explicit configuration
client = Obsidian(
    api_key="your-api-key",
    protocol="https",
    host="192.168.1.100",
    port=27124,
    verify_ssl=True
)
```

---

## File Operations

### list_files_in_vault

List all files and directories in the vault root.

```python
list_files_in_vault() -> list[str]
```

**Returns:** List of file and directory paths

**Example:**

```python
files = client.list_files_in_vault()
# ["Projects/", "Daily Notes/", "README.md", "inbox.md"]
```

---

### list_files_in_dir

List files in a specific directory.

```python
list_files_in_dir(dirpath: str) -> list[str]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dirpath` | str | Directory path relative to vault root |

**Returns:** List of file and directory paths

**Example:**

```python
files = client.list_files_in_dir("Projects/")
# ["Projects/project-a.md", "Projects/project-b.md"]
```

---

### get_file_contents

Get the content of a single file.

```python
get_file_contents(filepath: str) -> str
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `filepath` | str | File path relative to vault root |

**Returns:** File content as string

**Example:**

```python
content = client.get_file_contents("notes/meeting.md")
print(content)
# "# Meeting Notes\n\n- Item 1\n- Item 2"
```

---

### get_batch_file_contents

Get contents of multiple files concatenated with headers.

```python
get_batch_file_contents(filepaths: list[str]) -> str
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `filepaths` | list[str] | List of file paths |

**Returns:** Concatenated content with `# filepath` headers

**Example:**

```python
content = client.get_batch_file_contents(["a.md", "b.md"])
# "# a.md\n\nContent A\n\n---\n\n# b.md\n\nContent B\n\n---\n\n"
```

---

### put_content

Create or overwrite a file.

```python
put_content(filepath: str, content: str) -> None
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `filepath` | str | Target file path |
| `content` | str | File content |

**Example:**

```python
client.put_content("notes/new-note.md", "# New Note\n\nContent here")
```

---

### append_content

Append content to a file (creates file if it doesn't exist).

```python
append_content(filepath: str, content: str) -> None
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `filepath` | str | Target file path |
| `content` | str | Content to append |

**Example:**

```python
client.append_content("log.md", "\n- New log entry")
```

---

### patch_content

Insert content relative to a heading, block reference, or frontmatter field.

```python
patch_content(
    filepath: str,
    operation: str,
    target_type: str,
    target: str,
    content: str
) -> None
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `filepath` | str | Target file path |
| `operation` | str | `append`, `prepend`, or `replace` |
| `target_type` | str | `heading`, `block`, or `frontmatter` |
| `target` | str | Target identifier |
| `content` | str | Content to insert |

**Example:**

```python
# Append under a heading
client.patch_content(
    "notes/project.md",
    operation="append",
    target_type="heading",
    target="## Tasks",
    content="\n- [ ] New task"
)

# Replace frontmatter field
client.patch_content(
    "notes/note.md",
    operation="replace",
    target_type="frontmatter",
    target="status",
    content="completed"
)
```

---

### delete_file

Delete a file or directory.

```python
delete_file(filepath: str) -> None
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `filepath` | str | Path to delete |

**Example:**

```python
client.delete_file("archive/old-note.md")
```

---

## Search Operations

### search

Simple text search across the vault.

```python
search(query: str, context_length: int = 100) -> list[dict]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | str | Required | Search text |
| `context_length` | int | `100` | Characters of context around matches |

**Returns:** List of search results

**Example:**

```python
results = client.search("kubernetes", context_length=50)
# [
#     {
#         "filename": "devops/k8s.md",
#         "score": 0.95,
#         "matches": [{"context": "...deploy to kubernetes cluster...", "match": {...}}]
#     }
# ]
```

---

### search_json

Advanced search using JsonLogic queries.

```python
search_json(query: dict) -> list[dict]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | dict | JsonLogic query object |

**Returns:** List of matching files

**JsonLogic Operators:**

- `glob` - Glob pattern matching
- `regexp` - Regular expression matching
- `and`, `or`, `not` - Logical operators
- `var` - Variable access (`path`, `content`)

**Examples:**

```python
# All markdown files
results = client.search_json({
    "glob": ["*.md", {"var": "path"}]
})

# Files in Projects/ containing "deadline"
results = client.search_json({
    "and": [
        {"glob": ["Projects/*.md", {"var": "path"}]},
        {"regexp": ["deadline", {"var": "content"}]}
    ]
})

# Files with specific tag
results = client.search_json({
    "regexp": ["#important", {"var": "content"}]
})
```

---

## Periodic Notes

### get_periodic_note

Get the current periodic note for a period type.

```python
get_periodic_note(period: str, type: str = "content") -> str
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | str | Required | `daily`, `weekly`, `monthly`, `quarterly`, `yearly` |
| `type` | str | `"content"` | `content` or `metadata` |

**Returns:** Note content or metadata JSON

**Example:**

```python
# Get today's daily note
daily = client.get_periodic_note("daily")

# Get with metadata (path, tags, etc.)
daily_meta = client.get_periodic_note("daily", type="metadata")
```

---

### get_recent_periodic_notes

Get recent periodic notes for a period type.

```python
get_recent_periodic_notes(
    period: str,
    limit: int = 5,
    include_content: bool = False
) -> list[dict]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | str | Required | `daily`, `weekly`, `monthly`, `quarterly`, `yearly` |
| `limit` | int | `5` | Maximum notes to return |
| `include_content` | bool | `False` | Include note content |

**Returns:** List of periodic notes

**Example:**

```python
# Last 7 daily notes (metadata only)
notes = client.get_recent_periodic_notes("daily", limit=7)

# Last 3 weekly notes with content
notes = client.get_recent_periodic_notes("weekly", limit=3, include_content=True)
```

---

### get_recent_changes

Get recently modified files using Dataview query.

```python
get_recent_changes(limit: int = 10, days: int = 90) -> list[dict]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | `10` | Maximum files to return |
| `days` | int | `90` | Only files modified within N days |

**Returns:** List of recently modified files with metadata

**Example:**

```python
# Last 20 files modified in past 30 days
changes = client.get_recent_changes(limit=20, days=30)
# [{"filename": "notes/recent.md", "file.mtime": "2024-01-15T10:30:00"}]
```

---

## Client Management

### close

Close the HTTP client connection.

```python
close() -> None
```

**Example:**

```python
client = Obsidian(api_key="key")
try:
    # ... use client
finally:
    client.close()
```

---

## Error Handling

All methods raise `Exception` with descriptive messages on failure:

```python
try:
    content = client.get_file_contents("nonexistent.md")
except Exception as e:
    print(f"Error: {e}")
    # "Error 404: File not found"
```

**Error Format:**

- HTTP errors: `"Error {code}: {message}"`
- Connection errors: `"Request failed: {details}"`
