"""URL handling and remote file operations."""

from __future__ import annotations

import tempfile
from pathlib import Path
from urllib.parse import urlparse

import requests


def convert_github_url(url: str) -> str:
    """Convert a GitHub blob URL to a raw URL."""
    parsed_url = urlparse(url)
    if parsed_url.netloc == "github.com":
        parts = parsed_url.path.strip("/").split("/")
        if len(parts) >= 4 and parts[2] == "blob":  # noqa: PLR2004
            user, repo, _, branch = parts[:4]
            file_path = "/".join(parts[4:])
            return (
                f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path}"
            )
    return url


def get_file_from_url(url: str) -> Path:
    """Download file from URL to a temporary file and return Path."""
    actual_url = convert_github_url(url)

    try:
        response = requests.get(actual_url, timeout=30)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(
            mode="wb",
            delete=False,
            suffix=".tmp",
        ) as temp_file:
            temp_file.write(response.content)
            return Path(temp_file.name)

    except Exception as e:
        msg = f"Failed to download file from {actual_url}: {e}"
        raise ValueError(msg) from e


def is_url(path: str) -> bool:
    """Check if the given string is a URL."""
    parsed = urlparse(path)
    return parsed.scheme in ("http", "https", "ftp")
