"""Tests for validators module.

This module tests all validation functions for prerequisites.
"""




def test_is_git_installed_validator_success(fp):
    """Given git is installed
    When running validator
    Then should return ValidationResult with passed=True"""
    from spork.validators import is_git_installed

    # Given
    fp.register(
        ["git", "--version"],
        returncode=0,
        stdout="git version 2.39.3\n"
    )

    # When
    result = is_git_installed()

    # Then
    assert result.passed is True
    assert result.check_name == "git_installed"
    assert result.error_message is None


def test_is_git_installed_validator_failure(fp):
    """Given git is not installed
    When running validator
    Then should return ValidationResult with passed=False and error message"""
    from spork.validators import is_git_installed

    # Given
    fp.register(
        ["git", "--version"],
        returncode=127,
        stderr="command not found: git\n"
    )

    # When
    result = is_git_installed()

    # Then
    assert result.passed is False
    assert result.check_name == "git_installed"
    assert "not installed" in result.error_message.lower()
    assert result.suggestion is not None


def test_is_spec_kit_initialized_in_gitignore(tmp_path, fp):
    """Given .specify/ is listed in .gitignore
    When running validator
    Then should return ValidationResult with passed=False"""
    from spork.validators import is_spec_kit_initialized

    # Given - Create .gitignore with .specify/ entry
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("node_modules/\n.specify/\n*.pyc\n")

    # When
    result = is_spec_kit_initialized(tmp_path, "main")

    # Then
    assert result.passed is False
    assert result.check_name == "spec_kit_on_main"
    assert ".specify/" in result.error_message
    assert "gitignore" in result.error_message.lower()
    assert "remove" in result.suggestion.lower()


def test_is_spec_kit_initialized_success(tmp_path, fp):
    """Given Spec Kit is properly initialized on main branch
    When running validator
    Then should return ValidationResult with passed=True"""
    from spork.validators import is_spec_kit_initialized

    # Given - Mock git show commands to succeed
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

    # When
    result = is_spec_kit_initialized(tmp_path, "main")

    # Then
    assert result.passed is True
    assert result.check_name == "spec_kit_on_main"
    assert result.error_message is None


def test_is_spec_kit_initialized_missing_on_main(tmp_path, fp):
    """Given Spec Kit does not exist on main branch
    When running validator
    Then should return ValidationResult with passed=False"""
    from spork.validators import is_spec_kit_initialized

    # Given - git show fails (file doesn't exist on main)
    fp.register(
        ["git", "show", "main:.specify/memory/constitution.md"],
        returncode=128,
        stderr="fatal: path '.specify/memory/constitution.md' does not exist"
    )

    # When
    result = is_spec_kit_initialized(tmp_path, "main")

    # Then
    assert result.passed is False
    assert result.check_name == "spec_kit_on_main"
    assert "not found on main" in result.error_message.lower()
    assert "main branch" in result.suggestion.lower()


def test_is_spec_kit_initialized_missing_templates_on_main(tmp_path, fp):
    """Given .specify exists but templates directory is missing on main branch
    When running validator
    Then should return ValidationResult with passed=False"""
    from spork.validators import is_spec_kit_initialized

    # Given
    fp.register(
        ["git", "show", "main:.specify/memory/constitution.md"],
        stdout="# Constitution",
        returncode=0
    )
    fp.register(
        ["git", "ls-tree", "-d", "main:.specify/templates/"],
        stdout="",  # Empty output means directory doesn't exist
        returncode=0
    )

    # When
    result = is_spec_kit_initialized(tmp_path, "main")

    # Then
    assert result.passed is False
    assert result.check_name == "spec_kit_on_main"
    assert "incomplete" in result.error_message.lower()
    assert "templates" in result.error_message.lower()


def test_is_spec_kit_initialized_missing_scripts_on_main(tmp_path, fp):
    """Given .specify exists but scripts directory is missing on main branch
    When running validator
    Then should return ValidationResult with passed=False"""
    from spork.validators import is_spec_kit_initialized

    # Given
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
        stdout="",  # Empty output means directory doesn't exist
        returncode=0
    )

    # When
    result = is_spec_kit_initialized(tmp_path, "main")

    # Then
    assert result.passed is False
    assert result.check_name == "spec_kit_on_main"
    assert "incomplete" in result.error_message.lower()
    assert "scripts" in result.error_message.lower()


def test_is_claude_code_installed_success(fp):
    """Given Claude Code is installed
    When running validator
    Then should return ValidationResult with passed=True"""
    from spork.validators import is_claude_code_installed

    # Given
    fp.register(
        ["claude", "--version"],
        returncode=0,
        stdout="claude version 1.0.0\n"
    )

    # When
    result = is_claude_code_installed()

    # Then
    assert result.passed is True
    assert result.check_name == "claude_code_installed"
    assert result.error_message is None


def test_is_claude_code_installed_failure(fp):
    """Given Claude Code is not installed
    When running validator
    Then should return ValidationResult with passed=False and error message"""
    from spork.validators import is_claude_code_installed

    # Given
    fp.register(
        ["claude", "--version"],
        returncode=127,
        stderr="command not found: claude\n"
    )

    # When
    result = is_claude_code_installed()

    # Then
    assert result.passed is False
    assert result.check_name == "claude_code_installed"
    assert "claude" in result.error_message.lower()
    assert result.suggestion is not None
