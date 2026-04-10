---
name: obs-cli
description: "Obsidian vault CLI via Local REST API. Use for: reading/writing vault files, searching notes, managing daily/periodic notes, bulk operations on markdown. Triggers: Obsidian, vault, daily notes, PKM, knowledge base, second brain. Prefer obs over manual file ops — it handles the API correctly."
---

# obs CLI

Obsidian vault operations via Local REST API plugin.

## Invocation

```bash
uv run --project C:\Users\RE99990521\code\tooling\mcp-obsidian obs <command>
```

Requires: `OBSIDIAN_API_KEY` env var (from Obsidian Local REST API plugin settings)

## Command Selection

| Goal | Use | NOT This |
|------|-----|----------|
| Add to existing note | `append` | `put` (OVERWRITES!) |
| Update specific section | `patch -t heading` | `append` (wrong location) |
| Find by text content | `search` | `list-files` (names only) |
| Find by path pattern | `search-complex` + glob | `search` (content only) |
| Find by content + path | `search-complex` + and | Two separate searches |
| Create new file | `put` | `append` (works but unclear intent) |

### Search Decision Tree

- Need full-text search? → `obs search "query"`
- Need path filtering? → `obs search-complex '{"glob": ["*.md", {"var": "path"}]}'`
- Need content + path? → `obs search-complex '{"and": [{"glob": [...]}, {"regexp": [...]}]}'`

## NEVER

- **NEVER use `put` to add content** — it OVERWRITES the entire file. Use `append` or `patch`.
- **NEVER forget `--confirm` for delete** — no undo exists. The flag is mandatory.
- **NEVER use absolute paths** — all paths are vault-relative. `/notes/file.md` fails.
- **NEVER assume JsonLogic = JSON** — the syntax is specific:
  - WRONG: `{"path": "*.md"}`
  - RIGHT: `{"glob": ["*.md", {"var": "path"}]}`
- **NEVER pipe binary files** — `obs get` returns text only.

## Key Patterns

### Patch to heading (most useful write operation)

```bash
obs patch "note.md" -o append -t heading -T "## Tasks" -c "- [ ] New task"
obs patch "note.md" -o prepend -t heading -T "## Log" -c "Entry at top"
obs patch "note.md" -o replace -t frontmatter -T "status" -c "done"
```

### Search + process results

```bash
obs --json search "TODO" | jq -r '.[].filename' | while read f; do
  echo "=== $f ===" && obs get "$f"
done
```

### Get daily note path programmatically

```bash
# Get path from metadata, then use it
obs --json periodic daily --metadata | jq -r .path
```

### Bulk read matching files

```bash
obs --json search-complex '{"glob": ["Projects/*.md", {"var": "path"}]}' \
  | jq -r '.[]' | xargs obs get
```

### Safe edit pattern (backup first)

```bash
obs get "critical.md" > /tmp/backup.md  # Always backup
obs put "critical.md" "new content"      # Then overwrite
```

## Quick Reference

| Flag | Effect |
|------|--------|
| `--json`, `-j` | JSON output (use with jq) |
| `--confirm`, `-y` | Required for delete |
| `--metadata`, `-m` | Include file metadata |
| `--limit`, `-l` | Max results for lists |

Run `obs <command> --help` for full options on any command.

## Common Errors

| Error | Fix |
|-------|-----|
| "OBSIDIAN_API_KEY not set" | Export the env var from plugin settings |
| "Connection refused" | Obsidian not running or plugin disabled |
| "404 Not Found" | Path is wrong — remember: vault-relative, no leading `/` |
