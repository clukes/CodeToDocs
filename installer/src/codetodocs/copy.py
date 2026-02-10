"""Idempotent file-copy module for installing CodeToDocs assets into a repository."""

from __future__ import annotations

import filecmp
import importlib.resources
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

from codetodocs import __version__

VERSION_FILE = ".codetodocs/.version"


class ManifestEntry(NamedTuple):
    """A single asset mapping from package source to repository target."""

    source: str
    target: str


ASSET_MANIFEST: list[ManifestEntry] = [
    ManifestEntry(
        "assets/prompts/codetodocs.init.prompt.md",
        ".github/prompts/codetodocs.init.prompt.md",
    ),
    ManifestEntry(
        "assets/prompts/codetodocs.run.prompt.md",
        ".github/prompts/codetodocs.run.prompt.md",
    ),
    ManifestEntry(
        "assets/prompts/codetodocs.status.prompt.md",
        ".github/prompts/codetodocs.status.prompt.md",
    ),
    ManifestEntry(
        "assets/templates/technical_doc.md",
        ".codetodocs/templates/technical_doc.md",
    ),
    ManifestEntry(
        "assets/templates/product_doc.md",
        ".codetodocs/templates/product_doc.md",
    ),
    ManifestEntry(
        "assets/templates/ai_context.json",
        ".codetodocs/templates/ai_context.json",
    ),
]


@dataclass
class CopyResult:
    """Result of a copy_assets operation."""

    copied: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    overwritten: list[str] = field(default_factory=list)
    backup_dir: Path | None = None
    previous_version: str | None = None
    installed_version: str = field(default_factory=lambda: __version__)


def is_git_repo(path: Path) -> bool:
    """Check if *path* is inside a Git repository.

    First checks for a ``.git`` directory, then falls back to
    ``git rev-parse --git-dir`` for worktree / bare-repo layouts.
    """
    if (path / ".git").exists():
        return True
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=path,
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_asset_path(relative: str) -> Path:
    """Resolve an asset's absolute path within the installed package.

    Uses :pep:`302` / ``importlib.resources`` so that it works with both
    regular installs and editable (``pip install -e``) installs.
    """
    package_root = importlib.resources.files("codetodocs")
    return Path(str(package_root / relative))


def _create_backup_dir(target_dir: Path) -> Path:
    """Create and return a timestamped backup directory.

    Directory is created at ``.codetodocs/backups/<YYYYMMDD_HHMMSS>/``
    inside *target_dir*.
    """
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_dir = target_dir / ".codetodocs" / "backups" / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def _backup_file(
    target_path: Path,
    target_dir: Path,
    backup_dir: Path,
    relative_target: str,
) -> None:
    """Copy *target_path* into *backup_dir* preserving the relative path."""
    backup_path = backup_dir / relative_target
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target_path, backup_path)


def copy_assets(
    target_dir: Path,
    force: bool = False,
    dry_run: bool = False,
) -> CopyResult:
    """Copy every asset in :data:`ASSET_MANIFEST` into *target_dir*.

    Default behaviour (``force=False``):
        * New files are copied.
        * Existing files with **identical** content are skipped.
        * Existing files with **different** content are backed up to
          ``.codetodocs/backups/<timestamp>/`` and then overwritten with
          the latest version.

    Force behaviour (``force=True``):
        * All files are overwritten without creating backups.

    Parameters
    ----------
    target_dir:
        Root of the repository to install into.
    force:
        When ``True``, overwrite all files without backing up.
    dry_run:
        When ``True``, classify files without writing anything.

    Returns
    -------
    CopyResult
        Lists of copied, skipped, updated, and overwritten relative paths,
        plus the backup directory (if any backups were created).
    """
    result = CopyResult()
    backup_dir: Path | None = None

    # Read previously installed version (if any)
    version_path = target_dir / VERSION_FILE
    if version_path.exists():
        result.previous_version = version_path.read_text().strip()

    for entry in ASSET_MANIFEST:
        source_path = get_asset_path(entry.source)
        target_path = target_dir / entry.target

        if target_path.exists():
            if force:
                # Force mode: overwrite without backup
                if not dry_run:
                    shutil.copy2(source_path, target_path)
                result.overwritten.append(entry.target)
            elif filecmp.cmp(source_path, target_path, shallow=False):
                # Content identical: nothing to do
                result.skipped.append(entry.target)
            else:
                # Content differs: backup then update
                if not dry_run:
                    if backup_dir is None:
                        backup_dir = _create_backup_dir(target_dir)
                    _backup_file(target_path, target_dir, backup_dir, entry.target)
                    shutil.copy2(source_path, target_path)
                result.updated.append(entry.target)
        else:
            if not dry_run:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)
            result.copied.append(entry.target)

    # Write current version marker
    if not dry_run:
        version_path.parent.mkdir(parents=True, exist_ok=True)
        version_path.write_text(__version__ + "\n")

    result.backup_dir = backup_dir
    return result
