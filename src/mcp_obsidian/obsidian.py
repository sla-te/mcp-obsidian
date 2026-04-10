import os
import urllib.parse
from typing import Any

import httpx


class Obsidian:
    def __init__(
        self,
        api_key: str,
        protocol: str = os.getenv("OBSIDIAN_PROTOCOL", "https").lower(),
        host: str = str(os.getenv("OBSIDIAN_HOST", "127.0.0.1")),
        port: int = int(os.getenv("OBSIDIAN_PORT", "27124")),
        verify_ssl: bool = False,
    ):
        self.api_key = api_key

        if protocol == "http":
            self.protocol = "http"
        else:
            self.protocol = "https"  # Default to https for any other value, including 'https'

        self.host = host
        self.port = port
        self.verify_ssl = verify_ssl
        self.timeout = httpx.Timeout(6.0, connect=3.0)
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Lazy-initialize HTTP/2-enabled client."""
        if self._client is None:
            self._client = httpx.Client(
                http2=True,
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def get_base_url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}"

    def _get_headers(self) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        return headers

    def _safe_call(self, f) -> Any:
        try:
            return f()
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
            except Exception:
                error_data = {}
            code = error_data.get("errorCode", -1)
            message = error_data.get("message", "<unknown>")
            raise Exception(f"Error {code}: {message}") from e
        except httpx.RequestError as e:
            raise Exception(f"Request failed: {e!s}") from e

    def list_files_in_vault(self) -> Any:
        url = f"{self.get_base_url()}/vault/"

        def call_fn():
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()["files"]

        return self._safe_call(call_fn)

    def list_files_in_dir(self, dirpath: str) -> Any:
        url = f"{self.get_base_url()}/vault/{dirpath}/"

        def call_fn():
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()["files"]

        return self._safe_call(call_fn)

    def get_file_contents(self, filepath: str) -> Any:
        url = f"{self.get_base_url()}/vault/{filepath}"

        def call_fn():
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.text

        return self._safe_call(call_fn)

    def get_batch_file_contents(self, filepaths: list[str]) -> str:
        """Get contents of multiple files and concatenate them with headers.

        Args:
            filepaths: List of file paths to read

        Returns:
            String containing all file contents with headers
        """
        result = []

        for filepath in filepaths:
            try:
                content = self.get_file_contents(filepath)
                result.append(f"# {filepath}\n\n{content}\n\n---\n\n")
            except Exception as e:
                # Add error message but continue processing other files
                result.append(f"# {filepath}\n\nError reading file: {str(e)}\n\n---\n\n")

        return "".join(result)

    def search(self, query: str, context_length: int = 100) -> Any:
        url = f"{self.get_base_url()}/search/simple/"
        params = {"query": query, "contextLength": context_length}

        def call_fn():
            response = self.client.post(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)

    def append_content(self, filepath: str, content: str) -> Any:
        url = f"{self.get_base_url()}/vault/{filepath}"

        def call_fn():
            response = self.client.post(
                url,
                headers=self._get_headers() | {"Content-Type": "text/markdown"},
                content=content,
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def patch_content(self, filepath: str, operation: str, target_type: str, target: str, content: str) -> Any:
        url = f"{self.get_base_url()}/vault/{filepath}"

        headers = self._get_headers() | {
            "Content-Type": "text/markdown",
            "Operation": operation,
            "Target-Type": target_type,
            "Target": urllib.parse.quote(target),
        }

        def call_fn():
            response = self.client.patch(url, headers=headers, content=content)
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def put_content(self, filepath: str, content: str) -> Any:
        url = f"{self.get_base_url()}/vault/{filepath}"

        def call_fn():
            response = self.client.put(
                url,
                headers=self._get_headers() | {"Content-Type": "text/markdown"},
                content=content,
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def delete_file(self, filepath: str) -> Any:
        """Delete a file or directory from the vault.

        Args:
            filepath: Path to the file to delete (relative to vault root)

        Returns:
            None on success
        """
        url = f"{self.get_base_url()}/vault/{filepath}"

        def call_fn():
            response = self.client.delete(url, headers=self._get_headers())
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def search_json(self, query: dict) -> Any:
        url = f"{self.get_base_url()}/search/"

        headers = self._get_headers() | {"Content-Type": "application/vnd.olrapi.jsonlogic+json"}

        def call_fn():
            response = self.client.post(url, headers=headers, json=query)
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)

    def get_periodic_note(self, period: str, type: str = "content") -> Any:
        """Get current periodic note for the specified period.

        Args:
            period: The period type (daily, weekly, monthly, quarterly, yearly)
            type: Type of the data to get ('content' or 'metadata').
                'content' returns just the content in Markdown format.
                'metadata' includes note metadata (including paths, tags, etc.) and the content..

        Returns:
            Content of the periodic note
        """
        url = f"{self.get_base_url()}/periodic/{period}/"

        def call_fn():
            headers = self._get_headers()
            if type == "metadata":
                headers["Accept"] = "application/vnd.olrapi.note+json"
            response = self.client.get(url, headers=headers)
            response.raise_for_status()
            return response.text

        return self._safe_call(call_fn)

    def get_recent_periodic_notes(self, period: str, limit: int = 5, include_content: bool = False) -> Any:
        """Get most recent periodic notes for the specified period type.

        Args:
            period: The period type (daily, weekly, monthly, quarterly, yearly)
            limit: Maximum number of notes to return (default: 5)
            include_content: Whether to include note content (default: False)

        Returns:
            List of recent periodic notes
        """
        url = f"{self.get_base_url()}/periodic/{period}/recent"
        params = {"limit": limit, "includeContent": include_content}

        def call_fn():
            response = self.client.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)

    def get_server_info(self) -> Any:
        """Get basic server information."""
        url = f"{self.get_base_url()}/"

        def call_fn():
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)

    def get_active_file(self, type: str = "content") -> Any:
        """Get the currently active file in Obsidian.

        Args:
            type: Type of data ('content' or 'metadata')

        Returns:
            Content or metadata of the active file
        """
        url = f"{self.get_base_url()}/active/"

        def call_fn():
            headers = self._get_headers()
            if type == "metadata":
                headers["Accept"] = "application/vnd.olrapi.note+json"
            response = self.client.get(url, headers=headers)
            response.raise_for_status()
            return response.text if type == "content" else response.json()

        return self._safe_call(call_fn)

    def append_active(self, content: str) -> Any:
        """Append content to the active file."""
        url = f"{self.get_base_url()}/active/"

        def call_fn():
            response = self.client.post(
                url,
                headers=self._get_headers() | {"Content-Type": "text/markdown"},
                content=content,
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def put_active(self, content: str) -> Any:
        """Replace content of the active file."""
        url = f"{self.get_base_url()}/active/"

        def call_fn():
            response = self.client.put(
                url,
                headers=self._get_headers() | {"Content-Type": "text/markdown"},
                content=content,
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def patch_active(self, operation: str, target_type: str, target: str, content: str) -> Any:
        """Patch content in the active file relative to a target."""
        url = f"{self.get_base_url()}/active/"

        headers = self._get_headers() | {
            "Content-Type": "text/markdown",
            "Operation": operation,
            "Target-Type": target_type,
            "Target": urllib.parse.quote(target),
        }

        def call_fn():
            response = self.client.patch(url, headers=headers, content=content)
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def delete_active(self) -> Any:
        """Delete the active file."""
        url = f"{self.get_base_url()}/active/"

        def call_fn():
            response = self.client.delete(url, headers=self._get_headers())
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def list_commands(self) -> Any:
        """Get list of available Obsidian commands."""
        url = f"{self.get_base_url()}/commands/"

        def call_fn():
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)

    def execute_command(self, command_id: str) -> Any:
        """Execute an Obsidian command by ID."""
        url = f"{self.get_base_url()}/commands/{command_id}/"

        def call_fn():
            response = self.client.post(url, headers=self._get_headers())
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def open_file(self, filename: str, new_leaf: bool = False) -> Any:
        """Open a file in Obsidian.

        Args:
            filename: Path to the file to open
            new_leaf: Whether to open in a new pane
        """
        url = f"{self.get_base_url()}/open/{filename}"
        params = {"newLeaf": str(new_leaf).lower()}

        def call_fn():
            response = self.client.post(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def append_periodic(self, period: str, content: str) -> Any:
        """Append content to a periodic note (creates if doesn't exist).

        Args:
            period: The period type (daily, weekly, monthly, quarterly, yearly)
            content: Content to append
        """
        url = f"{self.get_base_url()}/periodic/{period}/"

        def call_fn():
            response = self.client.post(
                url,
                headers=self._get_headers() | {"Content-Type": "text/markdown"},
                content=content,
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def put_periodic(self, period: str, content: str) -> Any:
        """Replace content of a periodic note.

        Args:
            period: The period type (daily, weekly, monthly, quarterly, yearly)
            content: New content
        """
        url = f"{self.get_base_url()}/periodic/{period}/"

        def call_fn():
            response = self.client.put(
                url,
                headers=self._get_headers() | {"Content-Type": "text/markdown"},
                content=content,
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def patch_periodic(self, period: str, operation: str, target_type: str, target: str, content: str) -> Any:
        """Patch content in a periodic note relative to a target."""
        url = f"{self.get_base_url()}/periodic/{period}/"

        headers = self._get_headers() | {
            "Content-Type": "text/markdown",
            "Operation": operation,
            "Target-Type": target_type,
            "Target": urllib.parse.quote(target),
        }

        def call_fn():
            response = self.client.patch(url, headers=headers, content=content)
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def delete_periodic(self, period: str) -> Any:
        """Delete a periodic note."""
        url = f"{self.get_base_url()}/periodic/{period}/"

        def call_fn():
            response = self.client.delete(url, headers=self._get_headers())
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def get_recent_changes(self, limit: int = 10, days: int = 90) -> Any:
        """Get recently modified files in the vault.

        Args:
            limit: Maximum number of files to return (default: 10)
            days: Only include files modified within this many days (default: 90)

        Returns:
            List of recently modified files with metadata
        """
        # Build the DQL query
        query_lines = [
            "TABLE file.mtime",
            f"WHERE file.mtime >= date(today) - dur({days} days)",
            "SORT file.mtime DESC",
            f"LIMIT {limit}",
        ]

        # Join with proper DQL line breaks
        dql_query = "\n".join(query_lines)

        # Make the request to search endpoint
        url = f"{self.get_base_url()}/search/"
        headers = self._get_headers() | {"Content-Type": "application/vnd.olrapi.dataview.dql+txt"}

        def call_fn():
            response = self.client.post(url, headers=headers, content=dql_query.encode("utf-8"))
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)
