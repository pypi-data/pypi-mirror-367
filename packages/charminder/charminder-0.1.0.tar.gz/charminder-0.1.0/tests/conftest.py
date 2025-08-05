"""Shared fixtures and utilities for tests."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_utf8_file(temp_dir: Path) -> Path:
    """Create a sample UTF-8 encoded file."""
    file_path = temp_dir / "sample_utf8.txt"
    content = "Hello world! 🌍\nThis is a test file with UTF-8 encoding.\n"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_ascii_file(temp_dir: Path) -> Path:
    """Create a sample ASCII encoded file."""
    file_path = temp_dir / "sample_ascii.txt"
    content = "Hello world!\nThis is a test file with ASCII encoding.\n"
    file_path.write_text(content, encoding="ascii")
    return file_path


@pytest.fixture
def sample_mixed_encoding_file(temp_dir: Path) -> Path:
    """Create a file with characters that can't be encoded in ASCII."""
    file_path = temp_dir / "sample_mixed.txt"
    content = "Hello world! 🌍 café résumé naïve\n"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_empty_file(temp_dir: Path) -> Path:
    """Create an empty file."""
    file_path = temp_dir / "empty.txt"
    file_path.touch()
    return file_path


@pytest.fixture
def sample_binary_file(temp_dir: Path) -> Path:
    """Create a binary file."""
    file_path = temp_dir / "binary.bin"
    file_path.write_bytes(b"\x00\x01\x02\x03\xff\xfe\xfd")
    return file_path
