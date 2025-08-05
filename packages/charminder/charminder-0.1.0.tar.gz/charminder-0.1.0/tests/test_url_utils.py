"""Tests for charminder.url_utils module."""

from pathlib import Path

import pytest
import responses

from charminder.url_utils import convert_github_url, get_file_from_url, is_url


class TestConvertGithubUrl:
    """Test GitHub URL conversion functionality."""

    def test_github_blob_url_conversion(self):
        """Test conversion of GitHub blob URL to raw URL."""
        blob_url = "https://github.com/user/repo/blob/main/path/to/file.txt"
        expected_raw_url = (
            "https://raw.githubusercontent.com/user/repo/main/path/to/file.txt"
        )

        result = convert_github_url(blob_url)
        assert result == expected_raw_url

    def test_github_blob_url_with_subdirectories(self):
        """Test conversion with nested directory structure."""
        blob_url = (
            "https://github.com/user/repo/blob/feature-branch/deep/nested/path/file.py"
        )
        expected_raw_url = "https://raw.githubusercontent.com/user/repo/feature-branch/deep/nested/path/file.py"

        result = convert_github_url(blob_url)
        assert result == expected_raw_url

    def test_non_github_url_passthrough(self):
        """Test that non-GitHub URLs are returned unchanged."""
        original_url = "https://example.com/file.txt"
        result = convert_github_url(original_url)
        assert result == original_url

    def test_github_non_blob_url_passthrough(self):
        """Test that GitHub URLs that aren't blob URLs are unchanged."""
        original_url = "https://github.com/user/repo/releases/download/v1.0/file.txt"
        result = convert_github_url(original_url)
        assert result == original_url

    def test_invalid_github_blob_url(self):
        """Test handling of malformed GitHub blob URLs."""
        invalid_url = "https://github.com/user/blob/file.txt"  # Missing repo
        result = convert_github_url(invalid_url)
        assert result == invalid_url


class TestIsUrl:
    """Test URL detection functionality."""

    def test_valid_http_url(self):
        """Test detection of valid HTTP URLs."""
        assert is_url("http://example.com") is True
        assert is_url("http://example.com/path/to/file.txt") is True

    def test_valid_https_url(self):
        """Test detection of valid HTTPS URLs."""
        assert is_url("https://example.com") is True
        assert is_url("https://github.com/user/repo/blob/main/file.txt") is True

    def test_valid_ftp_url(self):
        """Test detection of valid FTP URLs."""
        assert is_url("ftp://ftp.example.com/file.txt") is True

    def test_invalid_url_schemes(self):
        """Test rejection of invalid URL schemes."""
        assert is_url("file:///path/to/file.txt") is False
        assert is_url("mailto:user@example.com") is False

    def test_local_file_paths(self):
        """Test that local file paths are not detected as URLs."""
        assert is_url("/path/to/file.txt") is False
        assert is_url("C:\\path\\to\\file.txt") is False
        assert is_url("./relative/path.txt") is False
        assert is_url("file.txt") is False

    def test_empty_string(self):
        """Test handling of empty string."""
        assert is_url("") is False


class TestGetFileFromUrl:
    """Test file download functionality."""

    @responses.activate
    def test_successful_download(self):
        """Test successful file download."""
        url = "https://example.com/test.txt"
        content = b"Test file content"

        responses.add(responses.GET, url, body=content, status=200)

        result_path = get_file_from_url(url)

        assert isinstance(result_path, Path)
        assert result_path.exists()
        assert result_path.read_bytes() == content

        # Clean up
        result_path.unlink()

    @responses.activate
    def test_download_with_github_conversion(self):
        """Test download with GitHub blob URL conversion."""
        blob_url = "https://github.com/user/repo/blob/main/file.txt"
        expected_raw_url = "https://raw.githubusercontent.com/user/repo/main/file.txt"
        content = b"GitHub file content"

        responses.add(responses.GET, expected_raw_url, body=content, status=200)

        result_path = get_file_from_url(blob_url)

        assert result_path.read_bytes() == content

        # Clean up
        result_path.unlink()

    @responses.activate
    def test_download_failure(self):
        """Test handling of download failure."""
        url = "https://example.com/nonexistent.txt"

        responses.add(responses.GET, url, status=404)

        with pytest.raises(ValueError, match="Failed to download file"):
            get_file_from_url(url)

    @responses.activate
    def test_network_error(self):
        """Test handling of network errors."""
        url = "https://example.com/test.txt"

        responses.add(responses.GET, url, body=Exception("Network error"))

        with pytest.raises(ValueError, match="Failed to download file"):
            get_file_from_url(url)
