"""Tests for codetodocs.copy module."""

import subprocess
from pathlib import Path

import pytest

from codetodocs.copy import VERSION_FILE, copy_assets, is_git_repo


def test_copy_assets_fresh(tmp_path: Path) -> None:
    """Fresh copy should copy all 6 files."""
    result = copy_assets(tmp_path)

    assert len(result.copied) == 6
    assert len(result.skipped) == 0
    assert len(result.updated) == 0
    assert len(result.overwritten) == 0

    # Verify files actually exist on disk
    assert (tmp_path / ".github" / "prompts" / "codetodocs.init.prompt.md").exists()
    assert (tmp_path / ".github" / "prompts" / "codetodocs.run.prompt.md").exists()
    assert (tmp_path / ".github" / "prompts" / "codetodocs.status.prompt.md").exists()
    assert (tmp_path / ".codetodocs" / "templates" / "technical_doc.md").exists()
    assert (tmp_path / ".codetodocs" / "templates" / "product_doc.md").exists()
    assert (tmp_path / ".codetodocs" / "templates" / "ai_context.yaml").exists()

    # Version marker should be written
    assert (tmp_path / VERSION_FILE).exists()
    assert result.previous_version is None


def test_copy_assets_idempotent(tmp_path: Path) -> None:
    """Second copy with identical content should skip all files."""
    copy_assets(tmp_path)
    result = copy_assets(tmp_path)

    assert len(result.copied) == 0
    assert len(result.skipped) == 6
    assert len(result.updated) == 0
    assert len(result.overwritten) == 0
    assert result.backup_dir is None
    assert result.previous_version == result.installed_version


def test_copy_assets_update_with_backup(tmp_path: Path) -> None:
    """Re-running after user edits should back up changed files and update them."""
    copy_assets(tmp_path)

    # Simulate user modification to one file
    modified_file = tmp_path / ".github" / "prompts" / "codetodocs.init.prompt.md"
    original_content = modified_file.read_text()
    modified_file.write_text(original_content + "\n# User customisation\n")

    result = copy_assets(tmp_path)

    assert len(result.copied) == 0
    assert len(result.updated) == 1
    assert ".github/prompts/codetodocs.init.prompt.md" in result.updated
    # The other 5 files are identical, so skipped
    assert len(result.skipped) == 5
    assert len(result.overwritten) == 0

    # Backup directory should exist and contain the old file
    assert result.backup_dir is not None
    assert result.backup_dir.exists()
    backup_file = result.backup_dir / ".github" / "prompts" / "codetodocs.init.prompt.md"
    assert backup_file.exists()
    assert "# User customisation" in backup_file.read_text()

    # The installed file should now match the source (user edit overwritten)
    assert "# User customisation" not in modified_file.read_text()


def test_copy_assets_update_multiple_modified(tmp_path: Path) -> None:
    """Multiple modified files should all be backed up in the same directory."""
    copy_assets(tmp_path)

    # Modify two files
    file1 = tmp_path / ".github" / "prompts" / "codetodocs.run.prompt.md"
    file2 = tmp_path / ".codetodocs" / "templates" / "technical_doc.md"
    file1.write_text("modified run prompt")
    file2.write_text("modified technical doc")

    result = copy_assets(tmp_path)

    assert len(result.updated) == 2
    assert len(result.skipped) == 4
    assert result.backup_dir is not None

    # Both backups should be in the same timestamped directory
    assert (result.backup_dir / ".github" / "prompts" / "codetodocs.run.prompt.md").exists()
    assert (result.backup_dir / ".codetodocs" / "templates" / "technical_doc.md").exists()


def test_copy_assets_force(tmp_path: Path) -> None:
    """Force copy should overwrite existing files without backups."""
    copy_assets(tmp_path)
    result = copy_assets(tmp_path, force=True)

    assert len(result.copied) == 0
    assert len(result.skipped) == 0
    assert len(result.updated) == 0
    assert len(result.overwritten) == 6
    assert result.backup_dir is None

    # No backup directory should have been created
    backups_dir = tmp_path / ".codetodocs" / "backups"
    assert not backups_dir.exists()


def test_copy_assets_dry_run(tmp_path: Path) -> None:
    """Dry run should not create files on disk."""
    result = copy_assets(tmp_path, dry_run=True)

    assert len(result.copied) == 6
    assert len(result.skipped) == 0

    # Verify NO files were actually created
    assert not (tmp_path / ".github").exists()
    assert not (tmp_path / ".codetodocs").exists()


def test_copy_assets_dry_run_update(tmp_path: Path) -> None:
    """Dry-run update should report changes without writing backups."""
    copy_assets(tmp_path)

    # Modify a file
    modified_file = tmp_path / ".codetodocs" / "templates" / "product_doc.md"
    modified_file.write_text("user modified content")

    result = copy_assets(tmp_path, dry_run=True)

    assert len(result.updated) == 1
    assert len(result.skipped) == 5
    assert result.backup_dir is None  # No backup created in dry-run

    # File should still have user modifications
    assert modified_file.read_text() == "user modified content"


def test_is_git_repo_true(tmp_path: Path) -> None:
    """Directory with git init should be detected as git repo."""
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
    assert is_git_repo(tmp_path) is True


def test_is_git_repo_false(tmp_path: Path) -> None:
    """Plain directory should not be detected as git repo."""
    assert is_git_repo(tmp_path) is False


def test_version_file_written_on_fresh_install(tmp_path: Path) -> None:
    """Fresh install should write a .version marker file."""
    from codetodocs import __version__

    copy_assets(tmp_path)
    version_path = tmp_path / VERSION_FILE
    assert version_path.exists()
    assert version_path.read_text().strip() == __version__


def test_version_file_updated_on_reinstall(tmp_path: Path) -> None:
    """Re-install should update the .version marker and report previous version."""
    from codetodocs import __version__

    # Simulate a previous install with an older version
    version_path = tmp_path / VERSION_FILE
    version_path.parent.mkdir(parents=True, exist_ok=True)
    version_path.write_text("0.1.0\n")

    # First copy (files are new, but version file exists)
    result = copy_assets(tmp_path)

    assert result.previous_version == "0.1.0"
    assert result.installed_version == __version__
    assert version_path.read_text().strip() == __version__


def test_version_file_not_written_on_dry_run(tmp_path: Path) -> None:
    """Dry-run should not write the .version marker file."""
    copy_assets(tmp_path, dry_run=True)
    assert not (tmp_path / VERSION_FILE).exists()
