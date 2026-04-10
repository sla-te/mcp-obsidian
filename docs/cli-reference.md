# CLI Reference

Complete reference for the `obs` command-line tool.

## Global Options

```bash
obs [OPTIONS] COMMAND [ARGS]...
```

| Option | Description |
|--------|-------------|
| `--json`, `-j` | Output as JSON |
| `--help` | Show help message |

## Commands

### list-files

List files in the vault root or a specific directory.

```bash
obs list-files [DIRECTORY]
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `DIRECTORY` | No | Directory path (default: vault root) |

**Examples:**

```bash
# List vault root
obs list-files

# List specific directory
obs list-files "Projects/"
obs list-files "Daily Notes/2024"

# Output as JSON
obs --json list-files
```

---

### get

Get contents of one or more files.

```bash
obs get FILEPATHS...
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `FILEPATHS` | Yes | One or more file paths |

**Examples:**

```bash
# Single file
obs get "notes/meeting.md"

# Multiple files (concatenated with headers)
obs get "file1.md" "file2.md" "file3.md"

# Output as JSON
obs --json get "notes/meeting.md"
```

---

### search

Simple text search across the vault.

```bash
obs search [OPTIONS] QUERY
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `QUERY` | Yes | Search text |

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--context-length`, `-c` | `100` | Characters of context around matches |

**Examples:**

```bash
# Basic search
obs search "kubernetes"

# With more context
obs search -c 200 "deployment strategy"

# JSON output
obs --json search "meeting notes"
```

---

### search-complex

Advanced search using JsonLogic query.

```bash
obs search-complex [OPTIONS] [QUERY]
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `QUERY` | No* | JsonLogic query as JSON string |

**Options:**

| Option | Description |
|--------|-------------|
| `--file` | Read query from file |

*Either `QUERY` or `--file` is required.

**Examples:**

```bash
# All markdown files
obs search-complex '{"glob": ["*.md", {"var": "path"}]}'

# Files containing specific text
obs search-complex '{"regexp": ["deadline", {"var": "content"}]}'

# Combined conditions
obs search-complex '{
  "and": [
    {"glob": ["Projects/*.md", {"var": "path"}]},
    {"regexp": ["#urgent", {"var": "content"}]}
  ]
}'

# Read query from file
obs search-complex --file query.json
```

**Query Syntax:**

```json
// Match by path pattern
{"glob": ["*.md", {"var": "path"}]}

// Match by content
{"regexp": ["search-term", {"var": "content"}]}

// Combine conditions
{"and": [condition1, condition2]}
{"or": [condition1, condition2]}
```

---

### put

Create or overwrite a file.

```bash
obs put [OPTIONS] FILEPATH [CONTENT]
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `FILEPATH` | Yes | Target file path |
| `CONTENT` | No* | File content (use `-` for stdin) |

**Options:**

| Option | Description |
|--------|-------------|
| `--file` | Read content from file |

*Either `CONTENT` or `--file` is required, or use `-` for stdin.

**Examples:**

```bash
# Inline content
obs put "notes/new.md" "# New Note"

# From file
obs put "notes/copy.md" --file original.md

# From stdin
echo "# Title" | obs put "notes/new.md" -
cat document.md | obs put "notes/imported.md" -

# Create with multiline content
obs put "notes/template.md" "# Template

## Section 1

## Section 2"
```

---

### append

Append content to a file (creates if doesn't exist).

```bash
obs append [OPTIONS] FILEPATH [CONTENT]
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `FILEPATH` | Yes | Target file path |
| `CONTENT` | No* | Content to append (use `-` for stdin) |

**Options:**

| Option | Description |
|--------|-------------|
| `--file` | Read content from file |

**Examples:**

```bash
# Append text
obs append "log.md" "- New entry"

# Append from file
obs append "notes.md" --file additions.md

# Append from stdin
date | obs append "log.md" -
```

---

### patch

Insert content relative to a heading, block reference, or frontmatter field.

```bash
obs patch [OPTIONS] FILEPATH
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `FILEPATH` | Yes | Target file path |

**Options:**

| Option | Required | Values | Description |
|--------|----------|--------|-------------|
| `--operation`, `-o` | Yes | `append`, `prepend`, `replace` | Operation to perform |
| `--target-type`, `-t` | Yes | `heading`, `block`, `frontmatter` | Type of target |
| `--target`, `-T` | Yes | String | Target identifier |
| `--content`, `-c` | No* | String | Content to insert |
| `--file` | No* | Path | Read content from file |

**Examples:**

```bash
# Append under a heading
obs patch "project.md" -o append -t heading -T "## Tasks" -c "- New task"

# Prepend to a section
obs patch "notes.md" -o prepend -t heading -T "## Summary" -c "Updated: today\n"

# Replace a block
obs patch "note.md" -o replace -t block -T "^abc123" -c "New content"

# Update frontmatter
obs patch "note.md" -o replace -t frontmatter -T "status" -c "completed"

# Content from file
obs patch "note.md" -o append -t heading -T "## Notes" --file additions.md
```

---

### delete

Delete a file or directory from the vault.

```bash
obs delete [OPTIONS] FILEPATH
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `FILEPATH` | Yes | Path to delete |

**Options:**

| Option | Required | Description |
|--------|----------|-------------|
| `--confirm`, `-y` | Yes | Confirm deletion (safety flag) |

**Examples:**

```bash
# Delete file
obs delete "archive/old-note.md" --confirm

# Short form
obs delete "temp.md" -y
```

> ⚠️ **Warning:** Deletion is permanent. The `--confirm` flag is required to prevent accidental deletions.

---

### periodic

Get the current periodic note.

```bash
obs periodic [OPTIONS] PERIOD
```

**Arguments:**

| Argument | Required | Values |
|----------|----------|--------|
| `PERIOD` | Yes | `daily`, `weekly`, `monthly`, `quarterly`, `yearly` |

**Options:**

| Option | Description |
|--------|-------------|
| `--metadata`, `-m` | Include metadata instead of just content |

**Examples:**

```bash
# Today's daily note
obs periodic daily

# This week's note
obs periodic weekly

# With metadata (path, tags, etc.)
obs periodic daily --metadata

# JSON output
obs --json periodic daily
```

---

### periodic-recent

Get recent periodic notes.

```bash
obs periodic-recent [OPTIONS] PERIOD
```

**Arguments:**

| Argument | Required | Values |
|----------|----------|--------|
| `PERIOD` | Yes | `daily`, `weekly`, `monthly`, `quarterly`, `yearly` |

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--limit`, `-l` | `5` | Maximum notes to return |
| `--include-content` | `false` | Include note content |

**Examples:**

```bash
# Last 5 daily notes
obs periodic-recent daily

# Last 10 weekly notes
obs periodic-recent weekly -l 10

# With content
obs periodic-recent daily --include-content

# JSON output
obs --json periodic-recent monthly -l 3
```

---

### recent-changes

Get recently modified files in the vault.

```bash
obs recent-changes [OPTIONS]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--limit`, `-l` | `10` | Maximum files to return |
| `--days`, `-d` | `90` | Only files modified within N days |

**Examples:**

```bash
# Last 10 changed files (default)
obs recent-changes

# Last 20 files from past 30 days
obs recent-changes -l 20 -d 30

# JSON output
obs --json recent-changes
```

---

## Environment Variables

The CLI reads these environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OBSIDIAN_API_KEY` | Yes | - | REST API key |
| `OBSIDIAN_HOST` | No | `127.0.0.1` | Obsidian host |
| `OBSIDIAN_PORT` | No | `27124` | REST API port |
| `OBSIDIAN_PROTOCOL` | No | `https` | Protocol |

You can also use a `.env` file in the current directory.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error (missing argument, API error, etc.) |

---

## Tips

### Combining with Shell Tools

```bash
# Search and open in editor
obs search "TODO" | head -20

# Backup recent files
obs --json recent-changes | jq -r '.[].filename' | xargs -I{} cp {} backup/

# Count files per directory
obs list-files | cut -d/ -f1 | sort | uniq -c

# Find large notes
obs --json list-files | jq -r '.[]' | while read f; do
  echo "$(obs get "$f" | wc -c) $f"
done | sort -rn | head -10
```

### Scripting

```bash
#!/bin/bash
# daily-backup.sh

DATE=$(date +%Y-%m-%d)
obs --json list-files | jq -r '.[]' | while read file; do
    content=$(obs get "$file")
    mkdir -p "backup/$DATE/$(dirname "$file")"
    echo "$content" > "backup/$DATE/$file"
done
```

### Creating Templates

```bash
# Create meeting note template
obs put "templates/meeting.md" "# Meeting: {{title}}

**Date:** {{date}}
**Attendees:**

## Agenda

## Notes

## Action Items

- [ ] "
```
