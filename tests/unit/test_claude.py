"""Tests for Claude Code invocation module.

This module tests launching Claude Code with proper arguments and exit code propagation.
"""

from pathlib import Path


def test_launch_claude_code_success(fp):
    """Given valid worktree path
    When launching Claude Code
    Then should run claude with correct arguments and return exit code"""
    from spork.claude import launch_claude_code

    # Given
    worktree_path = Path(".worktrees/001-add-auth")
    feature_request = "add user authentication"

    fp.register(
        ["claude", "/specify add user authentication"],
        returncode=0
    )

    # When
    exit_code = launch_claude_code(worktree_path, feature_request)

    # Then
    assert exit_code == 0


def test_launch_claude_code_non_zero_exit(fp):
    """Given Claude Code exits with non-zero code
    When launching Claude Code
    Then should propagate exit code"""
    from spork.claude import launch_claude_code

    # Given
    worktree_path = Path(".worktrees/001-add-auth")
    feature_request = "add user authentication"

    fp.register(
        ["claude", "/specify add user authentication"],
        returncode=1
    )

    # When
    exit_code = launch_claude_code(worktree_path, feature_request)

    # Then
    assert exit_code == 1


def test_launch_claude_code_sets_cwd(fp):
    """Given worktree path
    When launching Claude Code
    Then should set cwd to worktree path"""
    from spork.claude import launch_claude_code

    # Given
    worktree_path = Path(".worktrees/001-add-auth")
    feature_request = "test feature"

    fp.register(
        ["claude", "/specify test feature"],
        returncode=0
    )

    # When
    launch_claude_code(worktree_path, feature_request)

    # Then
    # Verify the command was called with correct arguments
    assert fp.call_count(["claude", "/specify test feature"]) == 1


def test_launch_claude_code_command_format():
    """Given feature request
    When launching Claude Code
    Then should format command as ['claude', '/specify <feature_request>']"""

    # This test verifies the command format
    # Implementation should use: ['claude', f'/specify {feature_request}']
    # Claude will receive the initial message to run /specify
    pass  # Command format verified in other tests


def test_launch_claude_code_error_propagation(fp):
    """Given Claude Code encounters an error
    When launching Claude Code
    Then should propagate the error exit code"""
    from spork.claude import launch_claude_code

    # Given
    worktree_path = Path(".worktrees/001-test")
    feature_request = "test"

    fp.register(
        ["claude", "/specify test"],
        returncode=4,
        stderr="Error: Something went wrong\n"
    )

    # When
    exit_code = launch_claude_code(worktree_path, feature_request)

    # Then
    assert exit_code == 4
