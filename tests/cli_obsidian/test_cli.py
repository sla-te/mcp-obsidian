import os
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

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
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

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, ["list-files", "notes"])

        assert result.exit_code == 0
        mock_obsidian.list_files_in_dir.assert_called_once_with("notes")

    def test_list_files_json_output(self) -> None:
        """Test listing files with JSON output."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.list_files_in_vault.return_value = ["file1.md", "file2.md"]

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, ["--json", "list-files"])

        assert result.exit_code == 0
        assert '"file1.md"' in result.output
        assert '"file2.md"' in result.output


class TestGetFiles:
    def test_get_single_file(self) -> None:
        """Test getting a single file's contents."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.get_file_contents.return_value = "# My Note\n\nContent here."

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
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

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
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

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, ["--json", "get", "note.md"])

        assert result.exit_code == 0
        assert '"# Note"' in result.output


class TestPeriodicCommands:
    def test_periodic_note(self) -> None:
        """Test getting current periodic note."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.get_periodic_note.return_value = "# Daily Note\n\nContent"

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, ["periodic", "daily"])

        assert result.exit_code == 0
        assert "Daily Note" in result.output
        mock_obsidian.get_periodic_note.assert_called_once_with("daily", "content")

    def test_periodic_note_with_metadata(self) -> None:
        """Test getting periodic note with metadata."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.get_periodic_note.return_value = '{"path": "daily/2026-04-10.md"}'

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
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

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, ["periodic-recent", "daily", "--limit", "2"])

        assert result.exit_code == 0
        mock_obsidian.get_recent_periodic_notes.assert_called_once_with("daily", 2, False)


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

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, ["search", "query"])

        assert result.exit_code == 0
        assert "notes/todo.md" in result.output
        mock_obsidian.search.assert_called_once_with("query", 100)

    def test_simple_search_with_context(self) -> None:
        """Test simple search with custom context length."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.search.return_value = []

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, ["search", "query", "--context-length", "200"])

        assert result.exit_code == 0
        mock_obsidian.search.assert_called_once_with("query", 200)

    def test_complex_search(self) -> None:
        """Test JsonLogic search."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.search_json.return_value = ["file1.md", "file2.md"]

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, ["search-complex", '{"glob": ["*.md", {"var": "path"}]}'])

        assert result.exit_code == 0
        mock_obsidian.search_json.assert_called_once()


class TestRecentChanges:
    def test_recent_changes(self) -> None:
        """Test getting recently modified files."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.get_recent_changes.return_value = [
            {"filename": "notes/todo.md", "mtime": "2026-04-10T10:00:00"},
            {"filename": "notes/ideas.md", "mtime": "2026-04-09T15:30:00"},
        ]

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, ["recent-changes"])

        assert result.exit_code == 0
        mock_obsidian.get_recent_changes.assert_called_once_with(10, 90)

    def test_recent_changes_with_options(self) -> None:
        """Test recent-changes with custom options."""
        runner = CliRunner()
        mock_obsidian = MagicMock()
        mock_obsidian.get_recent_changes.return_value = []

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, ["recent-changes", "--limit", "20", "--days", "7"])

        assert result.exit_code == 0
        mock_obsidian.get_recent_changes.assert_called_once_with(20, 7)


class TestDeleteCommand:
    def test_delete_requires_confirm(self) -> None:
        """Test that delete requires --confirm flag."""
        runner = CliRunner()
        mock_obsidian = MagicMock()

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, ["delete", "notes/old.md"])

        assert result.exit_code != 0
        assert "confirm" in result.output.lower() or "confirm" in str(result.exception).lower()
        mock_obsidian.delete_file.assert_not_called()

    def test_delete_with_confirm(self) -> None:
        """Test delete with --confirm flag."""
        runner = CliRunner()
        mock_obsidian = MagicMock()

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, ["delete", "notes/old.md", "--confirm"])

        assert result.exit_code == 0
        mock_obsidian.delete_file.assert_called_once_with("notes/old.md")

    def test_delete_with_short_flag(self) -> None:
        """Test delete with -y flag."""
        runner = CliRunner()
        mock_obsidian = MagicMock()

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, ["delete", "notes/old.md", "-y"])

        assert result.exit_code == 0
        mock_obsidian.delete_file.assert_called_once_with("notes/old.md")


class TestContentCommands:
    def test_put_content(self) -> None:
        """Test creating/overwriting a file."""
        runner = CliRunner()
        mock_obsidian = MagicMock()

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, ["put", "notes/new.md", "# New Note"])

        assert result.exit_code == 0
        assert "notes/new.md" in result.output
        mock_obsidian.put_content.assert_called_once_with("notes/new.md", "# New Note")

    def test_put_from_stdin(self) -> None:
        """Test put with stdin input."""
        runner = CliRunner()
        mock_obsidian = MagicMock()

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, ["put", "notes/new.md", "-"], input="# From stdin")

        assert result.exit_code == 0
        mock_obsidian.put_content.assert_called_once_with("notes/new.md", "# From stdin")

    def test_append_content(self) -> None:
        """Test appending to a file."""
        runner = CliRunner()
        mock_obsidian = MagicMock()

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, ["append", "notes/log.md", "--", "- New entry"])

        assert result.exit_code == 0
        mock_obsidian.append_content.assert_called_once_with("notes/log.md", "- New entry")

    def test_patch_content(self) -> None:
        """Test patching content at a target."""
        runner = CliRunner()
        mock_obsidian = MagicMock()

        with patch.dict(os.environ, {"OBSIDIAN_API_KEY": "test-key"}):
            with patch("mcp_obsidian.obsidian.Obsidian", return_value=mock_obsidian):
                result = runner.invoke(cli, [
                    "patch", "notes/todo.md",
                    "-o", "append",
                    "-t", "heading",
                    "-T", "## Tasks",
                    "-c", "- New task",
                ])

        assert result.exit_code == 0
        mock_obsidian.patch_content.assert_called_once_with(
            "notes/todo.md", "append", "heading", "## Tasks", "- New task"
        )
