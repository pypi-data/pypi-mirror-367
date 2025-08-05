"""Command-line interface for charminder."""

from __future__ import annotations

from contextlib import suppress
from pathlib import Path

import click

from .encoding_checker import check_encoding_issues
from .models import Encoding
from .reporting import _get_symbols, print_encoding_report
from .url_utils import get_file_from_url, is_url


@click.command()
@click.option(
    "-f",
    "--mdf-files",
    help=(
        "MDF file(s) or URL(s) to check. Supports file paths and URLs. "
        "If you have multiple, use this for each file/URL."
    ),
    required=True,
    type=str,
    prompt=True,
    multiple=True,
)
@click.option(
    "-e",
    "--encoding",
    help="Encoding type to check for.",
    type=click.Choice([e.name for e in Encoding]),
    default=Encoding.UTF8.name,
)
def main(mdf_files: tuple[str, ...], encoding: str = Encoding.UTF8.name) -> None:
    """
    Run the check_encoding script.

    Emits nonzero exit code if characters found that are not in the specified encoding.
    """
    exit_code = 0
    temp_files = []  # Track temporary files for cleanup
    symbols = _get_symbols()

    try:
        for mdf_file in mdf_files:
            try:
                if is_url(mdf_file):
                    print(f"Downloading {mdf_file}...")
                    file_path = get_file_from_url(mdf_file)
                    temp_files.append(file_path)
                else:
                    file_path = Path(mdf_file)
                    if not file_path.exists():
                        print(f"{symbols['cross']} {mdf_file}: File not found")
                        exit_code = 1
                        continue

                encoding_value = Encoding[encoding].value
                is_valid, issues = check_encoding_issues(file_path, encoding_value)

                print_encoding_report(
                    mdf_file, issues, encoding_value, is_valid=is_valid
                )

                # Set exit code if there are actual errors (not just warnings)
                if not is_valid:
                    error_issues = [
                        i for i in issues if i["type"] != "encoding_mismatch"
                    ]
                    if error_issues:
                        exit_code = 1

            except (OSError, UnicodeError, ValueError) as e:
                print(f"{symbols['cross']} {mdf_file}: Error processing file - {e}")
                exit_code = 1

    finally:
        for temp_file in temp_files:
            with suppress(Exception):
                temp_file.unlink()

    if exit_code != 0:
        raise SystemExit(exit_code)
