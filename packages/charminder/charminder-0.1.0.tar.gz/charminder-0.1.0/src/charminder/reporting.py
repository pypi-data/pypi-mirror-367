"""Output formatting and reporting functions."""

from __future__ import annotations

import sys


def _get_symbols() -> dict[str, str]:
    """Get appropriate symbols based on console encoding capability."""
    try:
        # Test if we can encode Unicode symbols
        test_symbols = "✓⚠✗"
        test_symbols.encode(sys.stdout.encoding or "utf-8")
    except (UnicodeEncodeError, LookupError):
        # Fallback to ASCII symbols
        return {"check": "[OK]", "warning": "[WARN]", "cross": "[ERROR]"}
    else:
        return {"check": "✓", "warning": "⚠", "cross": "✗"}


def print_encoding_report(
    file_path: str,
    issues: list[dict],
    expected_encoding: str,
    *,
    is_valid: bool,
) -> None:
    """Print a detailed encoding report."""
    symbols = _get_symbols()

    if is_valid and not issues:
        print(f"{symbols['check']} {file_path}: Valid {expected_encoding} encoding")
        return

    if is_valid and issues:
        # Only warnings
        print(
            f"{symbols['warning']} {file_path}: Valid {expected_encoding} "
            "encoding (with warnings)"
        )
    else:
        print(f"{symbols['cross']} {file_path}: Invalid {expected_encoding} encoding")

    for issue in issues:
        if issue["type"] == "decode_error":
            print(f"  • Decode error: {issue['message']}")
        elif issue["type"] == "encode_error":
            print(
                f"  • Invalid character '{issue['character']}' "
                f"({issue['unicode_codepoint']}) at line {issue['line']}, "
                f"column {issue['column']}",
            )
            print(f"    Context: ...{issue['context']}...")
        elif issue["type"] == "encoding_mismatch":
            print(
                f"  • Warning: Detected {issue['detected']} encoding "
                f"(confidence: {issue['confidence']:.2%})",
            )
        elif issue["type"] == "detection_failed" or issue["type"] == "file_error":
            print(f"  • Error: {issue['message']}")
    print()
