"""Tests for git operations module.

This module tests all 7 git operations with mocked subprocess calls
using pytest-subprocess fixture.
"""

from pathlib import Path

import pytest


def test_is_git_installed_success(fp):
    """Given git is installed and in PATH
    When checking if git is installed
    Then should return True"""
    from spork.git_operations import is_git_installed

    # Given
    fp.register(
        ["git", "--version"],
        returncode=0,
        stdout="git version 2.39.3 (Apple Git-145)\n"
    )

    # When
    result = is_git_installed()

    # Then
    assert result is True


def test_is_git_installed_not_found(fp):
    """Given git is not installed or not in PATH
    When checking if git is installed
    Then should return False"""
    from spork.git_operations import is_git_installed

    # Given
    fp.register(
        ["git", "--version"],
        returncode=127,
        stderr="command not found: git\n"
    )

    # When
    result = is_git_installed()

    # Then
    assert result is False


def test_is_git_repository_success(fp):
    """Given current directory is inside a git repository
    When checking if in git repository
    Then should return True"""
    from spork.git_operations import is_git_repository

    # Given
    test_path = Path("/Users/dev/my-project")
    fp.register(
        ["git", "-C", str(test_path), "rev-parse", "--is-inside-work-tree"],
        returncode=0,
        stdout="true\n"
    )

    # When
    result = is_git_repository(test_path)

    # Then
    assert result is True


def test_is_git_repository_false(fp):
    """Given current directory is not in a git repository
    When checking if in git repository
    Then should return False"""
    from spork.git_operations import is_git_repository

    # Given
    test_path = Path("/Users/dev/not-a-repo")
    fp.register(
        ["git", "-C", str(test_path), "rev-parse", "--is-inside-work-tree"],
        returncode=128,
        stderr="fatal: not a git repository\n"
    )

    # When
    result = is_git_repository(test_path)

    # Then
    assert result is False


def test_get_repo_root_success(fp):
    """Given we are inside a git repository
    When getting repository root
    Then should return absolute path to repo root"""
    from spork.git_operations import get_repo_root

    # Given
    fp.register(
        ["git", "rev-parse", "--show-toplevel"],
        returncode=0,
        stdout="/Users/dev/my-project\n"
    )

    # When
    result = get_repo_root()

    # Then
    assert result == Path("/Users/dev/my-project")


def test_get_repo_root_not_repo(fp):
    """Given we are not in a git repository
    When getting repository root
    Then should raise RuntimeError"""
    from spork.git_operations import get_repo_root

    # Given
    fp.register(
        ["git", "rev-parse", "--show-toplevel"],
        returncode=128,
        stderr="fatal: not a git repository\n"
    )

    # When / Then
    with pytest.raises(RuntimeError, match="not a git repository"):
        get_repo_root()


def test_get_main_branch_uses_main(fp):
    """Given repository has 'main' branch
    When getting main branch name
    Then should return 'main'"""
    from spork.git_operations import get_main_branch

    # Given
    fp.register(
        ["git", "rev-parse", "--verify", "main"],
        returncode=0,
        stdout="a1b2c3d4e5f6\n"
    )

    # When
    result = get_main_branch()

    # Then
    assert result == "main"


def test_get_main_branch_uses_master(fp):
    """Given repository has 'master' branch but no 'main'
    When getting main branch name
    Then should return 'master'"""
    from spork.git_operations import get_main_branch

    # Given
    fp.register(
        ["git", "rev-parse", "--verify", "main"],
        returncode=128,
        stderr="fatal: Needed a single revision\n"
    )
    fp.register(
        ["git", "rev-parse", "--verify", "master"],
        returncode=0,
        stdout="a1b2c3d4e5f6\n"
    )

    # When
    result = get_main_branch()

    # Then
    assert result == "master"


def test_get_main_branch_neither_exists(fp):
    """Given repository has neither 'main' nor 'master' branch
    When getting main branch name
    Then should raise RuntimeError"""
    from spork.git_operations import get_main_branch

    # Given
    fp.register(
        ["git", "rev-parse", "--verify", "main"],
        returncode=128,
        stderr="fatal: Needed a single revision\n"
    )
    fp.register(
        ["git", "rev-parse", "--verify", "master"],
        returncode=128,
        stderr="fatal: Needed a single revision\n"
    )

    # When / Then
    with pytest.raises(RuntimeError, match="neither 'main' nor 'master' branch found"):
        get_main_branch()


def test_git_fetch_success(fp):
    """Given git fetch can connect to remote
    When running git fetch
    Then should return True"""
    from spork.git_operations import git_fetch

    # Given
    fp.register(
        ["git", "fetch"],
        returncode=0,
        stdout="From github.com:user/repo\n   a1b2c3d..e4f5g6h  main -> origin/main\n"
    )

    # When
    result = git_fetch()

    # Then
    assert result is True


def test_git_fetch_network_error(fp):
    """Given git fetch encounters network error
    When running git fetch
    Then should return False"""
    from spork.git_operations import git_fetch

    # Given
    fp.register(
        ["git", "fetch"],
        returncode=1,
        stderr="fatal: unable to access 'https://...': Could not resolve host\n"
    )

    # When
    result = git_fetch()

    # Then
    assert result is False


def test_list_all_branches_success(fp):
    """Given repository has local and remote branches
    When listing all branches
    Then should return list of branch names"""
    from spork.git_operations import list_all_branches

    # Given
    fp.register(
        ["git", "branch", "-a", "--format=%(refname:short)"],
        returncode=0,
        stdout="main\n001-add-auth\n002-fix-bug\norigin/main\norigin/001-add-auth\n"
    )

    # When
    result = list_all_branches()

    # Then
    assert result == ["main", "001-add-auth", "002-fix-bug", "origin/main", "origin/001-add-auth"]


def test_list_all_branches_includes_remote(fp):
    """Given repository has remote branches
    When listing all branches
    Then should include remote branches with origin/ prefix"""
    from spork.git_operations import list_all_branches

    # Given
    fp.register(
        ["git", "branch", "-a", "--format=%(refname:short)"],
        returncode=0,
        stdout="main\norigin/main\norigin/003-new-feature\n"
    )

    # When
    result = list_all_branches()

    # Then
    assert "origin/main" in result
    assert "origin/003-new-feature" in result


def test_create_worktree_success(fp):
    """Given valid worktree parameters
    When creating worktree
    Then should return True"""
    from spork.git_operations import create_worktree

    # Given
    path = Path(".worktrees/001-add-auth")
    branch_name = "001-add-auth"
    base_branch = "main"

    fp.register(
        ["git", "worktree", "add", str(path), "-b", branch_name, base_branch],
        returncode=0,
        stdout=f"Preparing worktree (new branch '{branch_name}')\nHEAD is now at a1b2c3d\n"
    )

    # When
    result = create_worktree(path, branch_name, base_branch)

    # Then
    assert result is True


def test_create_worktree_already_exists(fp):
    """Given branch already exists
    When creating worktree
    Then should raise RuntimeError"""
    from spork.git_operations import create_worktree

    # Given
    path = Path(".worktrees/001-add-auth")
    branch_name = "001-add-auth"
    base_branch = "main"

    fp.register(
        ["git", "worktree", "add", str(path), "-b", branch_name, base_branch],
        returncode=128,
        stderr=f"fatal: a branch named '{branch_name}' already exists\n"
    )

    # When / Then
    with pytest.raises(RuntimeError, match="already exists"):
        create_worktree(path, branch_name, base_branch)


def test_create_worktree_permission_denied(fp):
    """Given permission denied when creating worktree directory
    When creating worktree
    Then should raise RuntimeError"""
    from spork.git_operations import create_worktree

    # Given
    path = Path(".worktrees/001-add-auth")
    branch_name = "001-add-auth"
    base_branch = "main"

    fp.register(
        ["git", "worktree", "add", str(path), "-b", branch_name, base_branch],
        returncode=1,
        stderr=(
            "fatal: could not create work tree dir '.worktrees/001-add-auth': "
            "Permission denied\n"
        )
    )

    # When / Then
    with pytest.raises(RuntimeError, match="Permission denied"):
        create_worktree(path, branch_name, base_branch)
