"""Validators module.

This module provides validation functions for prerequisites.
"""

import subprocess
from pathlib import Path

from spork.data_models import ValidationResult


def is_git_installed() -> ValidationResult:
    """Validate that git is installed.

    Returns:
        ValidationResult with passed=True if git is installed
    """
    try:
        subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        return ValidationResult(
            check_name="git_installed",
            passed=True,
            error_message=None,
            suggestion=None
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return ValidationResult(
            check_name="git_installed",
            passed=False,
            error_message="Git is not installed or not in PATH",
            suggestion="Install git: https://git-scm.com/downloads"
        )


def is_spec_kit_initialized(repo_path: Path, main_branch: str) -> ValidationResult:
    """Validate that Spec Kit is properly initialized on the main branch.

    Args:
        repo_path: Path to repository root
        main_branch: Name of main branch (main or master)

    Returns:
        ValidationResult with passed=True if Spec Kit is initialized on main branch
    """
    # First check if .specify/ is in .gitignore
    gitignore_path = repo_path / ".gitignore"
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()
        for line in gitignore_content.splitlines():
            line = line.strip()
            # Check for .specify/ patterns (exact match or with wildcards)
            if line in [".specify/", ".specify", ".specify/*"] or line.startswith(".specify/"):
                return ValidationResult(
                    check_name="spec_kit_on_main",
                    passed=False,
                    error_message="Spec Kit (.specify/) is listed in .gitignore",
                    suggestion=(
                        "Remove .specify/ from .gitignore to allow committing "
                        "Spec Kit to the repository"
                    )
                )

    # Then check if Spec Kit exists on the main branch
    # This ensures worktrees created from main will have Spec Kit
    try:
        result = subprocess.run(
            ["git", "show", f"{main_branch}:.specify/memory/constitution.md"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return ValidationResult(
                check_name="spec_kit_on_main",
                passed=False,
                error_message=f"Spec Kit not found on {main_branch} branch",
                suggestion=(
                    f"Ensure Spec Kit is initialized and committed to {main_branch} branch "
                    "before creating feature worktrees"
                )
            )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return ValidationResult(
            check_name="spec_kit_on_main",
            passed=False,
            error_message=f"Could not verify Spec Kit on {main_branch} branch",
            suggestion="Ensure git is working and you have network access"
        )

    # Also verify Spec Kit structure on main branch
    required_paths = [
        f"{main_branch}:.specify/templates",
        f"{main_branch}:.specify/scripts"
    ]

    for git_path in required_paths:
        try:
            result = subprocess.run(
                ["git", "ls-tree", git_path],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0 or not result.stdout.strip():
                path_name = git_path.split(":")[-1]
                return ValidationResult(
                    check_name="spec_kit_on_main",
                    passed=False,
                    error_message=(
                        f"Spec Kit incomplete on {main_branch} branch ({path_name} missing)"
                    ),
                    suggestion=f"Run 'specify init .' and commit to {main_branch} branch"
                )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return ValidationResult(
                check_name="spec_kit_on_main",
                passed=False,
                error_message=f"Could not verify Spec Kit structure on {main_branch} branch",
                suggestion="Ensure git is working properly"
            )

    return ValidationResult(
        check_name="spec_kit_on_main",
        passed=True,
        error_message=None,
        suggestion=None
    )


def is_claude_code_installed() -> ValidationResult:
    """Validate that Claude Code is installed.

    Returns:
        ValidationResult with passed=True if Claude Code is installed
    """
    try:
        subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        return ValidationResult(
            check_name="claude_code_installed",
            passed=True,
            error_message=None,
            suggestion=None
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return ValidationResult(
            check_name="claude_code_installed",
            passed=False,
            error_message="Claude Code not found in PATH",
            suggestion="Install Claude Code or add to PATH"
        )
