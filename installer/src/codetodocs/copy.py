"""Idempotent file-copy module for installing CodeToDocs assets into a repository."""

from __future__ import annotations

import importlib.resources
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple


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
    overwritten: list[str] = field(default_factory=list)


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


def copy_assets(
    target_dir: Path,
    force: bool = False,
    dry_run: bool = False,
) -> CopyResult:
    """Copy every asset in :data:`ASSET_MANIFEST` into *target_dir*.

    Parameters
    ----------
    target_dir:
        Root of the repository to install into.
    force:
        When ``True``, overwrite files that already exist.
    dry_run:
        When ``True``, classify files without writing anything.

    Returns
    -------
    CopyResult
        Lists of copied, skipped, and overwritten relative paths.
    """
    result = CopyResult()

    for entry in ASSET_MANIFEST:
        source_path = get_asset_path(entry.source)
        target_path = target_dir / entry.target

        if target_path.exists():
            if force:
                if not dry_run:
                    shutil.copy2(source_path, target_path)
                result.overwritten.append(entry.target)
            else:
                result.skipped.append(entry.target)
        else:
            if not dry_run:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)
            result.copied.append(entry.target)

    return result
