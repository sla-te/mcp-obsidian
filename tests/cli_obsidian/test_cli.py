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
