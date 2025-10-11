"""Environment file (.env*) discovery and copying utilities.

.env files are never checked into git (they contain credentials), so we read them
from the main workspace filesystem and copy to new worktrees.
"""

from pathlib import Path
from typing import List

from spork.data_models import EnvFileCopyResult
from spork.git_operations import get_repo_root


def discover_env_files(workspace_path: Path) -> List[str]:
    """Discover all .env* files in the workspace filesystem.

    Args:
        workspace_path: Path to workspace directory (e.g., repository root)

    Returns:
        List of relative file paths matching .env* pattern

    Raises:
        ValueError: If workspace_path doesn't exist or isn't a directory
    """
    if not workspace_path.exists():
        raise ValueError(f"Workspace path does not exist: {workspace_path}")
    if not workspace_path.is_dir():
        raise ValueError(f"Workspace path is not a directory: {workspace_path}")

    env_files: List[str] = []

    # Recursively search for .env* files using glob pattern
    for file_path in workspace_path.rglob('.env*'):
        # Skip files in .git directory and .worktrees directory
        if '.git' in file_path.parts or '.worktrees' in file_path.parts:
            continue

        # Only include regular files (not directories)
        if file_path.is_file():
            # Get relative path from workspace root
            relative_path = file_path.relative_to(workspace_path)
            env_files.append(str(relative_path))

    return sorted(env_files)  # Sort for consistent ordering


def read_env_file_from_filesystem(workspace_path: Path, filepath: str) -> str:
    """Read .env file content from filesystem.

    Args:
        workspace_path: Path to workspace directory
        filepath: Relative path to .env file from workspace root

    Returns:
        File content as UTF-8 string

    Raises:
        ValueError: If workspace_path or filepath is invalid
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file is not valid UTF-8
    """
    if not workspace_path or not workspace_path.exists():
        raise ValueError(f"Workspace path does not exist: {workspace_path}")
    if not filepath or not filepath.strip():
        raise ValueError("Filepath cannot be empty")

    file_path = workspace_path / filepath

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {filepath}")

    # Read file content as UTF-8
    return file_path.read_text(encoding='utf-8')


def copy_env_files_to_worktree(worktree_path: Path) -> EnvFileCopyResult:
    """Copy all .env* files from main workspace to worktree.

    Discovers .env files in the main workspace filesystem and copies them
    to the worktree, preserving directory structure. Uses best-effort approach:
    attempts all files, continues on individual failures.

    Args:
        worktree_path: Destination worktree path (must exist)

    Returns:
        EnvFileCopyResult with operation statistics

    Raises:
        ValueError: If worktree_path doesn't exist or isn't a directory
        RuntimeError: If cannot determine repository root
    """
    # Validate worktree path
    if not worktree_path.exists():
        raise ValueError(f"Worktree path does not exist: {worktree_path}")
    if not worktree_path.is_dir():
        raise ValueError(f"Worktree path is not a directory: {worktree_path}")

    # Get repository root (main workspace)
    try:
        repo_root = get_repo_root()
    except RuntimeError as e:
        raise RuntimeError(f"Cannot determine repository root: {e}")

    # Discover all .env files in main workspace
    env_files = discover_env_files(repo_root)

    files_copied = 0
    files_failed = 0
    errors = []

    # Copy each file (best-effort)
    for filepath in env_files:
        try:
            # Read file content from main workspace
            content = read_env_file_from_filesystem(repo_root, filepath)

            # Determine destination path in worktree
            dest_path = worktree_path / filepath

            # Create parent directories if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content (overwrites existing)
            dest_path.write_text(content, encoding='utf-8')

            files_copied += 1

        except Exception as e:
            files_failed += 1
            error_msg = f"Failed to copy {filepath}: {str(e)}"
            errors.append(error_msg)

    return EnvFileCopyResult(
        files_discovered=len(env_files),
        files_copied=files_copied,
        files_failed=files_failed,
        errors=errors
    )
