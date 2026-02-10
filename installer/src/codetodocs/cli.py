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
        help="Overwrite existing files without creating backups",
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
        if result.previous_version and result.previous_version != __version__:
            print(f"CodeToDocs v{result.previous_version} \u2192 v{__version__}")
        elif result.previous_version:
            print(f"CodeToDocs v{__version__} (reinstall)")
        else:
            print(f"CodeToDocs v{__version__}")
        print()

        # --- Copied ---
        print("Copied:")
        print(_format_file_list(result.copied))
        print()

        # --- Updated (backed up + overwritten) ---
        if result.updated:
            print("Updated (previous versions backed up):")
            print(_format_file_list(result.updated))
            print()

        # --- Force-overwritten ---
        if args.force and result.overwritten:
            print("Overwritten (no backup):")
            print(_format_file_list(result.overwritten))
            print()

        # --- Skipped (identical) ---
        if result.skipped:
            print("Skipped (already up to date):")
            print(_format_file_list(result.skipped))
            print()

        # --- Backup location ---
        if result.backup_dir:
            print(f"Backups saved to: {result.backup_dir.relative_to(target_dir)}")
            print()

        # --- Summary ---
        total_changed = len(result.copied) + len(result.updated) + len(result.overwritten)
        total_skipped = len(result.skipped)
        print(f"\u2713 {total_changed} file(s) installed, {total_skipped} already up to date")
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
