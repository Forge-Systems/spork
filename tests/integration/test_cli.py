"""Integration tests for CLI.

This module tests the complete CLI workflow from argument parsing
to worktree creation and Claude Code launch.
"""

from pathlib import Path

import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    """Provide Click CLI runner for testing."""
    return CliRunner()


def register_spec_kit_on_main_mocks(fp):
    """Helper to register git commands for Spec Kit validation on main branch."""
    fp.register(
        ["git", "show", "main:.specify/memory/constitution.md"],
        stdout="# Constitution",
        returncode=0
    )
    fp.register(
        ["git", "ls-tree", "-d", "main:.specify/templates/"],
        stdout="040000 tree abc123\t.specify/templates",
        returncode=0
    )
    fp.register(
        ["git", "ls-tree", "-d", "main:.specify/scripts/"],
        stdout="040000 tree def456\t.specify/scripts",
        returncode=0
    )


def test_cli_requires_feature_request(runner):
    """Given no feature request argument
    When running CLI
    Then should exit with non-zero code and show usage"""
    from spork.cli import cli

    # Given / When
    result = runner.invoke(cli, [])

    # Then
    assert result.exit_code != 0  # Click uses exit code 2 for missing arguments
    assert "Missing argument" in result.output or "FEATURE_REQUEST" in result.output


def test_cli_validates_git_installed(runner, fp):
    """Given git is not installed
    When running CLI with feature request
    Then should exit with code 1 (validation error) and show error message"""
    from spork.cli import cli

    # Given
    fp.register(
        ["git", "--version"],
        returncode=127,
        stderr="command not found: git\n"
    )

    # When
    result = runner.invoke(cli, ["add feature"])

    # Then
    assert result.exit_code == 1
    assert "git" in result.output.lower()
    assert "not installed" in result.output.lower()


def test_cli_validates_git_repository(runner, fp, tmp_path):
    """Given not in a git repository
    When running CLI with feature request
    Then should exit with code 1 and show error message"""
    from spork.cli import cli

    # Given
    fp.register(
        ["git", "--version"],
        returncode=0,
        stdout="git version 2.39.3\n"
    )
    fp.register(
        ["git", "-C", fp.any(), "rev-parse", "--is-inside-work-tree"],
        returncode=128,
        stderr="fatal: not a git repository\n"
    )

    # When
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["add feature"])

    # Then
    assert result.exit_code == 1
    assert "not in a git repository" in result.output.lower()


def test_cli_validates_spec_kit(runner, fp, tmp_path):
    """Given Spec Kit is not initialized on main branch
    When running CLI with feature request
    Then should exit with code 1 and show error message"""
    from spork.cli import cli

    # Given
    fp.register(
        ["git", "--version"],
        returncode=0,
        stdout="git version 2.39.3\n"
    )
    fp.register(
        ["git", "-C", fp.any(), "rev-parse", "--is-inside-work-tree"],
        returncode=0,
        stdout="true\n"
    )
    fp.register(
        ["git", "rev-parse", "--show-toplevel"],
        returncode=0,
        stdout=str(tmp_path) + "\n"
    )
    fp.register(
        ["git", "rev-parse", "--verify", "main"],
        returncode=0,
        stdout="a1b2c3d\n"
    )
    register_spec_kit_on_main_mocks(fp)
    # Spec Kit missing on main branch
    fp.register(
        ["git", "show", "main:.specify/memory/constitution.md"],
        returncode=128,
        stderr="fatal: path '.specify/memory/constitution.md' does not exist"
    )

    # When
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["add feature"])

    # Then
    assert result.exit_code == 1
    assert ("spec kit" in result.output.lower() or ".specify" in result.output.lower() or "main" in result.output.lower())


def test_cli_validates_claude_code(runner, fp, tmp_path):
    """Given Claude Code is not installed
    When running CLI with feature request
    Then should exit with code 1 and show error message"""
    from spork.cli import cli

    # Given
    fp.register(
        ["git", "--version"],
        returncode=0,
        stdout="git version 2.39.3\n"
    )
    fp.register(
        ["git", "-C", fp.any(), "rev-parse", "--is-inside-work-tree"],
        returncode=0,
        stdout="true\n"
    )
    fp.register(
        ["git", "rev-parse", "--show-toplevel"],
        returncode=0,
        stdout=str(tmp_path) + "\n"
    )
    fp.register(
        ["git", "rev-parse", "--verify", "main"],
        returncode=0,
        stdout="a1b2c3d\n"
    )
    register_spec_kit_on_main_mocks(fp)
    fp.register(
        ["claude", "--version"],
        returncode=127,
        stderr="command not found: claude\n"
    )

    # When
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["add feature"])

    # Then
    assert result.exit_code == 1
    assert "claude" in result.output.lower()


def test_cli_success_path(runner, fp, tmp_path):
    """Given all validations pass
    When running CLI with feature request
    Then should create worktree and launch Claude Code"""
    from spork.cli import cli

    # Given - setup Spec Kit
    spec_kit_dir = tmp_path / ".specify"
    spec_kit_dir.mkdir()
    (spec_kit_dir / "memory").mkdir()
    (spec_kit_dir / "memory" / "constitution.md").write_text("# Constitution")
    (spec_kit_dir / "templates").mkdir()
    (spec_kit_dir / "scripts").mkdir()

    # Mock all git and validation commands
    fp.register(
        ["git", "--version"],
        returncode=0,
        stdout="git version 2.39.3\n"
    )
    fp.register(
        ["git", "-C", fp.any(), "rev-parse", "--is-inside-work-tree"],
        returncode=0,
        stdout="true\n"
    )
    fp.register(
        ["git", "rev-parse", "--show-toplevel"],
        returncode=0,
        stdout=str(tmp_path) + "\n"
    )
    fp.register(
        ["claude", "--version"],
        returncode=0,
        stdout="claude version 1.0.0\n"
    )
    fp.register(
        ["git", "fetch"],
        returncode=0
    )
    fp.register(
        ["git", "branch", "-a", "--format=%(refname:short)"],
        returncode=0,
        stdout="main\n"
    )
    fp.register(
        ["git", "rev-parse", "--verify", "main"],
        returncode=0,
        stdout="a1b2c3d\n"
    )
    register_spec_kit_on_main_mocks(fp)
    fp.register(
        ["git", "worktree", "add", fp.any(), "-b", fp.any(), "main"],
        returncode=0,
        stdout="Preparing worktree\nHEAD is now at a1b2c3d\n"
    )
    fp.register(
        ["claude", "/specify add feature"],
        returncode=0
    )

    # When
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["add feature"])

    # Then
    assert result.exit_code == 0
    assert "✓" in result.output  # Should show checkmarks for progress


def test_cli_sanitizes_feature_name(runner, fp, tmp_path):
    """Given feature request with special characters
    When running CLI
    Then should sanitize name for branch creation"""
    from spork.cli import cli

    # Given - setup Spec Kit
    spec_kit_dir = tmp_path / ".specify"
    spec_kit_dir.mkdir()
    (spec_kit_dir / "memory").mkdir()
    (spec_kit_dir / "memory" / "constitution.md").write_text("# Constitution")
    (spec_kit_dir / "templates").mkdir()
    (spec_kit_dir / "scripts").mkdir()

    # Mock commands
    fp.register(
        ["git", "--version"],
        returncode=0,
        stdout="git version 2.39.3\n"
    )
    fp.register(
        ["git", "-C", fp.any(), "rev-parse", "--is-inside-work-tree"],
        returncode=0,
        stdout="true\n"
    )
    fp.register(
        ["git", "rev-parse", "--show-toplevel"],
        returncode=0,
        stdout=str(tmp_path) + "\n"
    )
    fp.register(
        ["claude", "--version"],
        returncode=0,
        stdout="claude version 1.0.0\n"
    )
    fp.register(
        ["git", "fetch"],
        returncode=0
    )
    fp.register(
        ["git", "branch", "-a", "--format=%(refname:short)"],
        returncode=0,
        stdout="main\n"
    )
    fp.register(
        ["git", "rev-parse", "--verify", "main"],
        returncode=0,
        stdout="a1b2c3d\n"
    )
    register_spec_kit_on_main_mocks(fp)
    fp.register(
        ["git", "worktree", "add", fp.any(), "-b", "001-fix-bug-123-critical", "main"],
        returncode=0,
        stdout="Preparing worktree\n"
    )
    fp.register(
        ["claude", "/specify Fix bug #123 (critical!)"],
        returncode=0
    )

    # When
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["Fix bug #123 (critical!)"])

    # Then
    assert result.exit_code == 0
    # Verify sanitized name appears in output
    assert "001-fix-bug-123-critical" in result.output.lower() or "fix-bug-123-critical" in result.output.lower()


def test_cli_handles_special_characters(runner, fp, tmp_path):
    """Given feature request with various special characters
    When running CLI
    Then should handle them properly"""
    from spork.cli import cli

    # Given - setup Spec Kit
    spec_kit_dir = tmp_path / ".specify"
    spec_kit_dir.mkdir()
    (spec_kit_dir / "memory").mkdir()
    (spec_kit_dir / "memory" / "constitution.md").write_text("# Constitution")
    (spec_kit_dir / "templates").mkdir()
    (spec_kit_dir / "scripts").mkdir()

    # Mock commands
    fp.register(
        ["git", "--version"],
        returncode=0,
        stdout="git version 2.39.3\n"
    )
    fp.register(
        ["git", "-C", fp.any(), "rev-parse", "--is-inside-work-tree"],
        returncode=0,
        stdout="true\n"
    )
    fp.register(
        ["git", "rev-parse", "--show-toplevel"],
        returncode=0,
        stdout=str(tmp_path) + "\n"
    )
    fp.register(
        ["claude", "--version"],
        returncode=0,
        stdout="claude version 1.0.0\n"
    )
    fp.register(
        ["git", "fetch"],
        returncode=0
    )
    fp.register(
        ["git", "branch", "-a", "--format=%(refname:short)"],
        returncode=0,
        stdout="main\n"
    )
    fp.register(
        ["git", "rev-parse", "--verify", "main"],
        returncode=0,
        stdout="a1b2c3d\n"
    )
    register_spec_kit_on_main_mocks(fp)
    fp.register(
        ["git", "worktree", "add", fp.any(), "-b", fp.any(), "main"],
        returncode=0,
        stdout="Preparing worktree\n"
    )
    fp.register(
        ["claude", "/specify Add @user support & email!"],
        returncode=0
    )

    # When
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["Add @user support & email!"])

    # Then
    assert result.exit_code == 0


def test_cli_propagates_claude_exit_code(runner, fp, tmp_path):
    """Given Claude Code exits with non-zero code
    When running CLI
    Then should propagate the same exit code"""
    from spork.cli import cli

    # Given - setup Spec Kit
    spec_kit_dir = tmp_path / ".specify"
    spec_kit_dir.mkdir()
    (spec_kit_dir / "memory").mkdir()
    (spec_kit_dir / "memory" / "constitution.md").write_text("# Constitution")
    (spec_kit_dir / "templates").mkdir()
    (spec_kit_dir / "scripts").mkdir()

    # Mock commands
    fp.register(
        ["git", "--version"],
        returncode=0,
        stdout="git version 2.39.3\n"
    )
    fp.register(
        ["git", "-C", fp.any(), "rev-parse", "--is-inside-work-tree"],
        returncode=0,
        stdout="true\n"
    )
    fp.register(
        ["git", "rev-parse", "--show-toplevel"],
        returncode=0,
        stdout=str(tmp_path) + "\n"
    )
    fp.register(
        ["claude", "--version"],
        returncode=0,
        stdout="claude version 1.0.0\n"
    )
    fp.register(
        ["git", "fetch"],
        returncode=0
    )
    fp.register(
        ["git", "branch", "-a", "--format=%(refname:short)"],
        returncode=0,
        stdout="main\n"
    )
    fp.register(
        ["git", "rev-parse", "--verify", "main"],
        returncode=0,
        stdout="a1b2c3d\n"
    )
    register_spec_kit_on_main_mocks(fp)
    fp.register(
        ["git", "worktree", "add", fp.any(), "-b", fp.any(), "main"],
        returncode=0,
        stdout="Preparing worktree\n"
    )
    fp.register(
        ["claude", "/specify test"],
        returncode=2  # Claude exits with code 2
    )

    # When
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["test"])

    # Then
    assert result.exit_code == 2  # Should propagate Claude's exit code
