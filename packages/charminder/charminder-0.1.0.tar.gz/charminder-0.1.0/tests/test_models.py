"""Tests for charminder.models module."""

from charminder.models import Encoding

EXPECTED_ENCODINGS = {"utf-8", "utf-16", "utf-32", "ascii"}


class TestEncoding:
    """Test the Encoding enum."""

    def test_encoding_values(self):
        """Test that all encoding values are correct."""
        assert Encoding.UTF8 == "utf-8"
        assert Encoding.UTF16 == "utf-16"
        assert Encoding.UTF32 == "utf-32"
        assert Encoding.ASCII == "ascii"

    def test_encoding_enumeration(self):
        """Test that we can iterate over all encodings."""
        actual_encodings = {encoding.value for encoding in Encoding}
        assert actual_encodings == EXPECTED_ENCODINGS

    def test_encoding_count(self):
        """Test that we have the expected number of encodings."""
        assert len(list(Encoding)) == len(EXPECTED_ENCODINGS)

    def test_encoding_string_conversion(self):
        """Test string conversion of encoding values."""
        assert str(Encoding.UTF8) == "utf-8"
        assert str(Encoding.ASCII) == "ascii"

    def test_encoding_membership(self):
        """Test membership testing."""
        assert "utf-8" in [e.value for e in Encoding]
        assert "invalid" not in [e.value for e in Encoding]
