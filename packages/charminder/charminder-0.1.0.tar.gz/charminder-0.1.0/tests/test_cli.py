"""Tests for charminder.cli module."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import responses
from click.testing import CliRunner

from charminder.cli import main
from charminder.models import Encoding


class TestCliMain:
    """Test the CLI main function."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_help_command(self):
        """Test the help command."""
        result = self.runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Run the check_encoding script" in result.output
        assert "--mdf-files" in result.output
        assert "--encoding" in result.output

    def test_valid_local_file(self, sample_utf8_file):
        """Test processing a valid local file."""
        result = self.runner.invoke(main, ["-f", str(sample_utf8_file), "-e", "UTF8"])

        assert result.exit_code == 0
        assert "✓" in result.output
        assert str(sample_utf8_file) in result.output
        assert "Valid utf-8 encoding" in result.output

    def test_invalid_local_file_encoding(self, sample_mixed_encoding_file):
        """Test processing a file with encoding issues."""
        result = self.runner.invoke(
            main,
            ["-f", str(sample_mixed_encoding_file), "-e", "ASCII"],
        )

        assert result.exit_code == 1
        assert "✗" in result.output
        assert "Invalid ascii encoding" in result.output

    def test_nonexistent_file(self, temp_dir):
        """Test handling of nonexistent file."""
        nonexistent = temp_dir / "does_not_exist.txt"
        result = self.runner.invoke(main, ["-f", str(nonexistent)])

        assert result.exit_code == 1
        assert "File not found" in result.output

    def test_multiple_files(self, sample_utf8_file, sample_ascii_file):
        """Test processing multiple files."""
        result = self.runner.invoke(
            main,
            [
                "-f",
                str(sample_utf8_file),
                "-f",
                str(sample_ascii_file),
                "-e",
                "UTF8",
            ],
        )

        assert result.exit_code == 0
        assert str(sample_utf8_file) in result.output
        assert str(sample_ascii_file) in result.output

    def test_mixed_results_multiple_files(
        self,
        sample_utf8_file,
        sample_mixed_encoding_file,
    ):
        """Test processing multiple files with mixed results."""
        result = self.runner.invoke(
            main,
            [
                "-f",
                str(sample_utf8_file),
                "-f",
                str(sample_mixed_encoding_file),
                "-e",
                "ASCII",
            ],
        )

        # Should exit with error code because one file has issues
        assert result.exit_code == 1
        # Both files should fail ASCII check since they contain UTF-8 content
        assert "✗" in result.output

    @responses.activate
    def test_url_download_success(self):
        """Test successful URL download and processing."""
        url = "https://example.com/test.txt"
        content = "Hello world!\nThis is a test file."

        responses.add(responses.GET, url, body=content, status=200)

        result = self.runner.invoke(main, ["-f", url, "-e", "UTF8"])

        assert result.exit_code == 0
        assert "Downloading" in result.output
        assert url in result.output
        # Should be valid (may have warnings)
        assert "✓" in result.output or "⚠" in result.output

    @responses.activate
    def test_url_download_failure(self):
        """Test handling of URL download failure."""
        url = "https://example.com/nonexistent.txt"

        responses.add(responses.GET, url, status=404)

        result = self.runner.invoke(main, ["-f", url])

        assert result.exit_code == 1
        assert "Error processing file" in result.output

    @responses.activate
    def test_github_url_conversion(self):
        """Test GitHub blob URL conversion and download."""
        blob_url = "https://github.com/user/repo/blob/main/test.txt"
        raw_url = "https://raw.githubusercontent.com/user/repo/main/test.txt"
        content = "GitHub file content"

        # Only mock the raw URL, not the blob URL
        responses.add(responses.GET, raw_url, body=content, status=200)

        result = self.runner.invoke(main, ["-f", blob_url, "-e", "UTF8"])

        assert result.exit_code == 0
        assert "Downloading" in result.output
        # Should be valid (may have warnings)
        assert "✓" in result.output or "⚠" in result.output

    def test_encoding_parameter_choices(self):
        """Test that encoding parameter accepts valid choices."""
        # Test with each valid encoding
        for encoding in Encoding:
            result = self.runner.invoke(main, ["-f", "/dev/null", "-e", encoding.name])
            # Should not fail due to invalid encoding choice
            # (might fail for other reasons)
            assert "Invalid value" not in result.output

    def test_invalid_encoding_parameter(self):
        """Test that invalid encoding parameter is rejected."""
        result = self.runner.invoke(main, ["-f", "/dev/null", "-e", "invalid"])

        assert result.exit_code != 0
        assert "Invalid value" in result.output

    def test_default_encoding(self, sample_utf8_file):
        """Test that default encoding is UTF-8."""
        result = self.runner.invoke(main, ["-f", str(sample_utf8_file)])

        # Should use UTF-8 by default
        assert "utf-8 encoding" in result.output

    def test_file_processing_exception_handling(self, temp_dir):
        """Test handling of unexpected exceptions during file processing."""
        # Create a file and then make it inaccessible
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        # Mock an exception in the encoding checker
        with patch(
            "charminder.cli.check_encoding_issues",
            side_effect=OSError("Unexpected error"),
        ):
            result = self.runner.invoke(main, ["-f", str(test_file)])

            assert result.exit_code == 1
            assert "Error processing file" in result.output
            assert "Unexpected error" in result.output

    def test_url_and_file_mixed(self, sample_utf8_file):
        """Test processing a mix of URLs and local files."""
        url = "https://example.com/test.txt"

        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, url, body="URL content", status=200)

            result = self.runner.invoke(
                main,
                [
                    "-f",
                    str(sample_utf8_file),
                    "-f",
                    url,
                    "-e",
                    "UTF8",
                ],
            )

            assert result.exit_code == 0
            assert str(sample_utf8_file) in result.output
            assert url in result.output
            assert "Downloading" in result.output

    def test_temporary_file_cleanup(self):
        """Test that temporary files are cleaned up after processing."""
        url = "https://example.com/test.txt"

        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, url, body="URL content", status=200)

            # Track if any temp files exist before and after
            temp_dir = Path(tempfile.gettempdir())
            temp_files_before = list(temp_dir.glob("*.tmp"))

            self.runner.invoke(main, ["-f", url, "-e", "UTF8"])

            temp_files_after = list(temp_dir.glob("*.tmp"))

            # Should have cleaned up temp files
            assert len(temp_files_after) <= len(temp_files_before)
