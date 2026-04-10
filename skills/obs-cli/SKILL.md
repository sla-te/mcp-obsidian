---
name: obs-cli
description: "Obsidian vault operations via CLI. Use when the user wants to read, write, search, or manage files in their Obsidian vault. Triggers on: Obsidian, vault, daily notes, periodic notes, markdown notes, knowledge base, PKM, second brain. Always use this skill for Obsidian operations - the obs CLI is faster than manual file operations."
---

# Obsidian CLI (obs)

CLI tool for interacting with Obsidian vaults via the Local REST API plugin.

## Invocation

```bash
uv run --project C:\Users\RE99990521\code\tooling\mcp-obsidian obs <command> [options]
```

## Environment

Requires `OBSIDIAN_API_KEY` environment variable. Get from Obsidian Local REST API plugin settings.

Optional:
- `OBSIDIAN_HOST` (default: 127.0.0.1)
- `OBSIDIAN_PORT` (default: 27124)

## Commands

### List Files

```bash
# List vault root
obs list-files

# List directory
obs list-files "Projects/"

# JSON output
obs --json list-files
```

### Read Files

```bash
# Single file
obs get "notes/meeting.md"

# Multiple files (concatenated with headers)
obs get "file1.md" "file2.md" "file3.md"
```

### Search

```bash
# Simple text search
obs search "kubernetes"
obs search "query" --context-length 200

# Advanced JsonLogic search
obs search-complex '{"glob": ["*.md", {"var": "path"}]}'
obs search-complex '{"and": [{"glob": ["Projects/*.md", {"var": "path"}]}, {"regexp": ["urgent", {"var": "content"}]}]}'
```

### Write Content

```bash
# Create/overwrite file
obs put "notes/new.md" "# New Note"
obs put "notes/copy.md" --file original.md

# Append to file
obs append "log.md" "- New entry"

# Patch relative to heading/block
obs patch "note.md" -o append -t heading -T "## Tasks" -c "- New task"
obs patch "note.md" -o replace -t frontmatter -T "status" -c "done"
```

### Delete

```bash
# Requires --confirm flag
obs delete "old-note.md" --confirm
obs delete "archive/temp.md" -y
```

### Periodic Notes

```bash
# Current daily/weekly/monthly note
obs periodic daily
obs periodic weekly --metadata

# Recent periodic notes
obs periodic-recent daily --limit 7
obs periodic-recent weekly -l 3 --include-content
```

### Recent Changes

```bash
# Recently modified files
obs recent-changes
obs recent-changes --limit 20 --days 30
```

## Output Formats

- Default: Human-readable
- `--json` or `-j`: JSON output for parsing

## Examples

```bash
# Get today's daily note and append a task
obs periodic daily
obs patch "Daily Notes/2026-04-10.md" -o append -t heading -T "## Tasks" -c "- [ ] Review PRs"

# Search for todos and get matching files
obs search "TODO" --context-length 50

# Backup recent notes
for file in $(obs --json recent-changes | jq -r '.[].filename'); do
    obs get "$file" > "backup/$file"
done

# Create note from template
obs put "Projects/new-project.md" "# New Project

## Overview

## Tasks

## Notes
"
```

## Error Handling

- Missing API key: Set `OBSIDIAN_API_KEY` environment variable
- Connection failed: Ensure Obsidian is running with Local REST API plugin enabled
- File not found: Check file path is relative to vault root
