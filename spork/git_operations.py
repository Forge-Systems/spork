"""Git operations module.

This module provides functions for interacting with git via subprocess.
"""

import subprocess
from pathlib import Path


def is_git_installed() -> bool:
    """Check if git is installed and accessible.

    Returns:
        True if git --version succeeds, False otherwise
    """
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def is_git_repository(path: Path) -> bool:
    """Check if path is inside a git repository.

    Args:
        path: Path to check

    Returns:
        True if inside work tree, False otherwise
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_repo_root() -> Path:
    """Get absolute path to repository root.

    Returns:
        Path object to repo root

    Raises:
        RuntimeError: If not in git repo
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        if "not a git repository" in e.stderr.lower():
            raise RuntimeError("not a git repository")
        raise RuntimeError(f"Git operation failed: {e.stderr}")
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        raise RuntimeError(f"Git operation failed: {e}")


def get_main_branch() -> str:
    """Determine main branch name (main or master).

    Returns:
        "main" or "master"

    Raises:
        RuntimeError: If neither exists
    """
    # Try 'main' first (modern convention)
    try:
        subprocess.run(
            ["git", "rev-parse", "--verify", "main"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        return "main"
    except subprocess.CalledProcessError:
        pass

    # Try 'master' (legacy convention)
    try:
        subprocess.run(
            ["git", "rev-parse", "--verify", "master"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        return "master"
    except subprocess.CalledProcessError:
        pass

    raise RuntimeError("neither 'main' nor 'master' branch found")


def git_fetch() -> bool:
    """Fetch remote branches.

    Returns:
        True if successful or no remote, False on error
    """
    try:
        subprocess.run(
            ["git", "fetch"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def list_all_branches() -> list[str]:
    """List all local and remote branches.

    Returns:
        List of branch names (short format)
    """
    try:
        result = subprocess.run(
            ["git", "branch", "-a", "--format=%(refname:short)"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        branches = result.stdout.strip().split("\n")
        return [b for b in branches if b]  # Filter out empty strings
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return []


def create_worktree(path: Path, branch_name: str, base_branch: str) -> bool:
    """Create a new worktree with a new branch.

    Args:
        path: Path for new worktree
        branch_name: Name of new branch to create
        base_branch: Branch to base new branch on

    Returns:
        True if successful

    Raises:
        RuntimeError: On error with descriptive message
    """
    try:
        subprocess.run(
            ["git", "worktree", "add", str(path), "-b", branch_name, base_branch],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        return True
    except subprocess.CalledProcessError as e:
        if "already exists" in e.stderr:
            raise RuntimeError(f"Branch or worktree already exists: {e.stderr}")
        if "Permission denied" in e.stderr:
            raise RuntimeError(f"Permission denied: {e.stderr}")
        raise RuntimeError(f"Git worktree creation failed: {e.stderr}")
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        raise RuntimeError(f"Git worktree creation failed: {e}")
