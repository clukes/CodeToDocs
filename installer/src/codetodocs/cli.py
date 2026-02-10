"""CLI entry point for the CodeToDocs bootstrap installer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from codetodocs import __version__
from codetodocs.copy import copy_assets, is_git_repo


def _format_file_list(files: list[str]) -> str:
    """Return an indented file list, or '(none)' when empty."""
    if not files:
        return "  (none)"
    return "\n".join(f"  {f}" for f in files)


def main() -> None:
    """Run the CodeToDocs bootstrap installer."""
    parser = argparse.ArgumentParser(
        description="CodeToDocs — Install prompt files and templates into your repository",
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=Path("."),
        help="Directory to install into",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be copied without copying",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"CodeToDocs v{__version__}",
    )

    args = parser.parse_args()

    try:
        target_dir = args.target_dir.resolve()

        result = copy_assets(
            target_dir,
            force=args.force,
            dry_run=args.dry_run,
        )

        # --- Header ---
        print(f"CodeToDocs v{__version__}")
        print()

        # --- Copied ---
        print("Copied:")
        print(_format_file_list(result.copied))
        print()

        # --- Overwritten / Skipped ---
        if args.force and result.overwritten:
            print("Overwritten:")
            print(_format_file_list(result.overwritten))
        else:
            print("Skipped (already exist):")
            print(_format_file_list(result.skipped))
        print()

        # --- Summary ---
        total_copied = len(result.copied)
        total_skipped = len(result.skipped) + len(result.overwritten)
        print(f"\u2713 {total_copied} file(s) copied, {total_skipped} skipped")
        print()

        # --- Warnings ---
        if not is_git_repo(target_dir):
            print(
                "Warning: This directory is not a Git repository. "
                "Git is required for documentation generation."
            )
            print()

        # --- Next step ---
        print(
            "Next step: Run /codetodocs.init in your AI coding assistant "
            "to complete setup."
        )

    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
