"""Data models and enums for charminder."""

from __future__ import annotations

from enum import StrEnum


class Encoding(StrEnum):
    """Encoding types."""

    UTF8 = "utf-8"
    UTF16 = "utf-16"
    UTF32 = "utf-32"
    ASCII = "ascii"
