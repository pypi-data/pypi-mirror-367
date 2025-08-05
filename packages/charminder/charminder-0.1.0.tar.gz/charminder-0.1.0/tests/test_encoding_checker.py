"""Tests for charminder.encoding_checker module."""

from charminder.encoding_checker import check_encoding_issues


class TestCheckEncodingIssues:
    """Test the core encoding validation functionality."""

    def test_valid_utf8_file(self, sample_utf8_file):
        """Test validation of a valid UTF-8 file."""
        is_valid, issues = check_encoding_issues(sample_utf8_file, "utf-8")

        assert is_valid is True
        # Should only have encoding mismatch warning
        # (charset_normalizer might detect as utf-8-sig or similar)
        error_issues = [i for i in issues if i["type"] != "encoding_mismatch"]
        assert len(error_issues) == 0

    def test_valid_ascii_file(self, sample_ascii_file):
        """Test validation of a valid ASCII file."""
        is_valid, issues = check_encoding_issues(sample_ascii_file, "ascii")

        assert is_valid is True
        error_issues = [i for i in issues if i["type"] != "encoding_mismatch"]
        assert len(error_issues) == 0

    def test_ascii_file_with_utf8_expected(self, sample_ascii_file):
        """Test ASCII file when UTF-8 is expected (should pass)."""
        is_valid, issues = check_encoding_issues(sample_ascii_file, "utf-8")

        assert is_valid is True
        error_issues = [i for i in issues if i["type"] != "encoding_mismatch"]
        assert len(error_issues) == 0

    def test_utf8_file_with_ascii_expected(self, sample_mixed_encoding_file):
        """Test UTF-8 file with non-ASCII characters when ASCII is expected."""
        is_valid, issues = check_encoding_issues(sample_mixed_encoding_file, "ascii")

        assert is_valid is False

        # Should have encode errors for non-ASCII characters
        encode_errors = [i for i in issues if i["type"] == "encode_error"]
        assert len(encode_errors) > 0

        # Check that we get details about problematic characters
        emoji_error = next((i for i in encode_errors if "🌍" in i["character"]), None)
        assert emoji_error is not None
        assert "U+1F30D" in emoji_error["unicode_codepoint"]

    def test_empty_file(self, sample_empty_file):
        """Test validation of an empty file."""
        is_valid, issues = check_encoding_issues(sample_empty_file, "utf-8")

        assert is_valid is True
        error_issues = [i for i in issues if i["type"] != "encoding_mismatch"]
        assert len(error_issues) == 0

    def test_binary_file(self, sample_binary_file):
        """Test validation of a binary file."""
        is_valid, issues = check_encoding_issues(sample_binary_file, "utf-8")

        # Binary file should fail encoding validation
        assert is_valid is False

        # Should have either decode errors or detection failed
        error_types = {i["type"] for i in issues}
        assert "decode_error" in error_types or "detection_failed" in error_types

    def test_nonexistent_file(self, temp_dir):
        """Test handling of nonexistent file."""
        nonexistent_file = temp_dir / "does_not_exist.txt"

        is_valid, issues = check_encoding_issues(nonexistent_file, "utf-8")

        assert is_valid is False
        assert len(issues) == 1
        assert issues[0]["type"] == "file_error"
        assert "File not found" in issues[0]["message"]

    def test_issue_structure_encode_error(self, sample_mixed_encoding_file):
        """Test the structure of encode error issues."""
        is_valid, issues = check_encoding_issues(sample_mixed_encoding_file, "ascii")

        encode_errors = [i for i in issues if i["type"] == "encode_error"]
        assert len(encode_errors) > 0

        error = encode_errors[0]
        required_keys = {
            "type",
            "character",
            "unicode_name",
            "unicode_codepoint",
            "line",
            "column",
            "context",
        }
        assert required_keys.issubset(error.keys())

        assert error["type"] == "encode_error"
        assert isinstance(error["line"], int)
        assert isinstance(error["column"], int)
        assert error["line"] >= 1
        assert error["column"] >= 1

    def test_encoding_mismatch_warning(self, sample_utf8_file):
        """Test encoding mismatch warning when detected encoding differs."""
        # This might not always trigger depending on charset_normalizer's detection
        is_valid, issues = check_encoding_issues(sample_utf8_file, "iso-8859-1")

        # Check if we get encoding mismatch warnings
        mismatch_warnings = [i for i in issues if i["type"] == "encoding_mismatch"]
        if mismatch_warnings:
            warning = mismatch_warnings[0]
            required_keys = {"type", "detected", "expected", "confidence", "message"}
            assert required_keys.issubset(warning.keys())
            assert warning["expected"] == "iso-8859-1"
            assert 0 <= warning["confidence"] <= 1

    def test_multiple_problematic_characters(self, temp_dir):
        """Test file with multiple problematic characters."""
        file_path = temp_dir / "multi_problem.txt"
        content = "Hello 🌍 world 🎉 with café"
        file_path.write_text(content, encoding="utf-8")

        is_valid, issues = check_encoding_issues(file_path, "ascii")

        assert is_valid is False
        encode_errors = [i for i in issues if i["type"] == "encode_error"]

        # Should find multiple problematic characters
        expected_characters = {"🌍", "🎉", "é"}
        assert len(encode_errors) >= len(expected_characters)

        # Verify we get different characters
        characters = {error["character"] for error in encode_errors}
        assert expected_characters.issubset(characters)
