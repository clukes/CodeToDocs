"""Tests for codetodocs.copy module."""

import subprocess
from pathlib import Path

import pytest

from codetodocs.copy import copy_assets, is_git_repo


def test_copy_assets_fresh(tmp_path: Path) -> None:
    """Fresh copy should copy all 6 files."""
    result = copy_assets(tmp_path)

    assert len(result.copied) == 6
    assert len(result.skipped) == 0
    assert len(result.overwritten) == 0

    # Verify files actually exist on disk
    assert (tmp_path / ".github" / "prompts" / "codetodocs.init.prompt.md").exists()
    assert (tmp_path / ".github" / "prompts" / "codetodocs.run.prompt.md").exists()
    assert (tmp_path / ".github" / "prompts" / "codetodocs.status.prompt.md").exists()
    assert (tmp_path / ".codetodocs" / "templates" / "technical_doc.md").exists()
    assert (tmp_path / ".codetodocs" / "templates" / "product_doc.md").exists()
    assert (tmp_path / ".codetodocs" / "templates" / "ai_context.json").exists()


def test_copy_assets_idempotent(tmp_path: Path) -> None:
    """Second copy should skip all files."""
    copy_assets(tmp_path)
    result = copy_assets(tmp_path)

    assert len(result.copied) == 0
    assert len(result.skipped) == 6
    assert len(result.overwritten) == 0


def test_copy_assets_force(tmp_path: Path) -> None:
    """Force copy should overwrite existing files."""
    copy_assets(tmp_path)
    result = copy_assets(tmp_path, force=True)

    assert len(result.copied) == 0
    assert len(result.skipped) == 0
    assert len(result.overwritten) == 6


def test_copy_assets_dry_run(tmp_path: Path) -> None:
    """Dry run should not create files on disk."""
    result = copy_assets(tmp_path, dry_run=True)

    assert len(result.copied) == 6
    assert len(result.skipped) == 0

    # Verify NO files were actually created
    assert not (tmp_path / ".github").exists()
    assert not (tmp_path / ".codetodocs").exists()


def test_is_git_repo_true(tmp_path: Path) -> None:
    """Directory with git init should be detected as git repo."""
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
    assert is_git_repo(tmp_path) is True


def test_is_git_repo_false(tmp_path: Path) -> None:
    """Plain directory should not be detected as git repo."""
    assert is_git_repo(tmp_path) is False
