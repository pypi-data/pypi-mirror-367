"""Core encoding validation logic."""

from __future__ import annotations

from typing import TYPE_CHECKING

from charset_normalizer import from_path

if TYPE_CHECKING:
    from pathlib import Path


def check_encoding_issues(  # noqa: PLR0911, C901
    file_path: Path,
    expected_encoding: str,
) -> tuple[bool, list[dict]]:
    """
    Check for encoding issues in a file using charset_normalizer.

    Returns:
        tuple: (is_valid, issues_list)
        - is_valid: True if file matches expected encoding
        - issues_list: List of dictionaries with issue details
    """
    issues = []

    if not file_path.exists():
        return False, [
            {"type": "file_error", "message": f"File not found: {file_path}"},
        ]

    try:
        detection_result = from_path(file_path).best()
    except (OSError, UnicodeError, ValueError) as e:
        return False, [{"type": "file_error", "message": f"Error reading file: {e}"}]

    if detection_result is None:
        return False, [
            {"type": "detection_failed", "message": "Could not detect file encoding"},
        ]

    detected_encoding = detection_result.encoding.lower()
    expected_lower = expected_encoding.lower().replace("-", "").replace("_", "")
    detected_lower = detected_encoding.lower().replace("-", "").replace("_", "")

    try:
        try:
            content = file_path.read_text(encoding=detected_encoding)
        except UnicodeDecodeError:
            # Fallback: try to read as bytes and decode with expected encoding
            with file_path.open("rb") as f:
                raw_content = f.read()
            try:
                content = raw_content.decode(expected_encoding)
            except UnicodeDecodeError as e:
                issues.append(
                    {
                        "type": "decode_error",
                        "encoding": expected_encoding,
                        "position": e.start,
                        "message": (
                            "Cannot decode byte "
                            f"{raw_content[e.start : e.start + 1]!r} "
                            f"at position {e.start}",
                        ),
                    },
                )
                return False, issues

        problematic_chars = []
        for line_num, line in enumerate(content.splitlines(), 1):
            for char_pos, char in enumerate(line):
                try:
                    char.encode(expected_encoding)
                except UnicodeEncodeError:
                    problematic_chars.append(
                        {
                            "type": "encode_error",
                            "character": char,
                            "unicode_name": repr(char),
                            "unicode_codepoint": f"U+{ord(char):04X}",
                            "line": line_num,
                            "column": char_pos + 1,
                            "context": line[max(0, char_pos - 10) : char_pos + 10],
                        },
                    )

        if problematic_chars:
            issues.extend(problematic_chars)
            return False, issues

        if detected_lower != expected_lower and expected_lower not in detected_lower:
            issues.append(
                {
                    "type": "encoding_mismatch",
                    "detected": detected_encoding,
                    "expected": expected_encoding,
                    "confidence": detection_result.coherence,
                    "message": (
                        f"Detected encoding '{detected_encoding}' "
                        "differs from expected '{expected_encoding}'",
                    ),
                },
            )
            # This is a warning, not necessarily an error

        return len([i for i in issues if i["type"] != "encoding_mismatch"]) == 0, issues

    except (OSError, UnicodeError, ValueError) as e:
        return False, [{"type": "file_error", "message": f"Error reading file: {e}"}]
