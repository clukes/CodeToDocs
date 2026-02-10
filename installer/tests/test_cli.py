"""Tests for codetodocs.cli module."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from codetodocs.cli import main


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    """--version should print version and exit."""
    with pytest.raises(SystemExit) as exc_info:
        with patch("sys.argv", ["codetodocs", "--version"]):
            main()
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "CodeToDocs v" in captured.out


def test_help_flag(capsys: pytest.CaptureFixture[str]) -> None:
    """--help should print help text and exit."""
    with pytest.raises(SystemExit) as exc_info:
        with patch("sys.argv", ["codetodocs", "--help"]):
            main()
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "--target-dir" in captured.out
    assert "--force" in captured.out
    assert "--dry-run" in captured.out


def test_dry_run_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """--dry-run should show plan without copying files."""
    with patch("sys.argv", ["codetodocs", "--target-dir", str(tmp_path), "--dry-run"]):
        main()
    captured = capsys.readouterr()
    assert "Copied:" in captured.out or "Would copy:" in captured.out
    # Files should NOT exist
    assert not (tmp_path / ".github").exists()


def test_non_git_repo_warning(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Non-git directory should show warning."""
    with patch("sys.argv", ["codetodocs", "--target-dir", str(tmp_path)]):
        main()
    captured = capsys.readouterr()
    assert "not a Git repository" in captured.out or "Warning" in captured.out


def test_default_run(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Default run should copy files to target directory."""
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
    with patch("sys.argv", ["codetodocs", "--target-dir", str(tmp_path)]):
        main()
    captured = capsys.readouterr()
    assert "copied" in captured.out.lower()
    # Verify files exist
    assert (tmp_path / ".github" / "prompts" / "codetodocs.init.prompt.md").exists()
