"""CLI module.

This module implements the main Click command interface.
"""

import sys
from pathlib import Path

import click

from spork.claude import launch_claude_code
from spork.data_models import FeatureRequest, GitRepository, WorktreeConfig
from spork.git_operations import (
    create_worktree,
    get_main_branch,
    get_repo_root,
    git_fetch,
    is_git_installed,
    is_git_repository,
    list_all_branches,
)
from spork.validators import (
    is_claude_code_installed,
    is_git_installed as validate_git_installed,
    is_spec_kit_initialized,
)
from spork.worktree import get_next_feature_number, sanitize_feature_name


@click.command()
@click.argument("feature_request", required=True)
def cli(feature_request: str) -> None:
    """spork - Git Worktree Feature Request Tool

    Create a new worktree and launch Claude Code for feature specification.

    FEATURE_REQUEST: Natural language description of the feature to implement
    """
    # Exit code 3 for user error (missing argument handled by Click automatically)
    if not feature_request or not feature_request.strip():
        click.echo("Error: Feature request is required", err=True)
        click.echo("  Usage: spork <feature-request>", err=True)
        click.echo('  Example: spork "add user authentication"', err=True)
        sys.exit(3)

    # Validation sequence (fail-fast)
    click.echo("✓ Validating prerequisites...")

    # 1. Check git installed
    git_validation = validate_git_installed()
    if not git_validation.passed:
        click.echo(f"Error: {git_validation.error_message}", err=True)
        if git_validation.suggestion:
            click.echo(f"  {git_validation.suggestion}", err=True)
        sys.exit(1)
    click.echo(f"✓ Git found")

    # 2. Check in git repository
    cwd = Path.cwd()
    if not is_git_repository(cwd):
        click.echo("Error: Not in a git repository", err=True)
        click.echo("  Run 'git init' or navigate to an existing repository", err=True)
        sys.exit(1)

    # Get repository root
    try:
        repo_root = get_repo_root()
        click.echo(f"✓ In git repository: {repo_root}")
    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    # Get main branch early (needed for Spec Kit validation)
    try:
        main_branch = get_main_branch()
    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)

    # 3. Check Spec Kit initialized on main branch
    spec_kit_validation = is_spec_kit_initialized(repo_root, main_branch)
    if not spec_kit_validation.passed:
        click.echo(f"Error: {spec_kit_validation.error_message}", err=True)
        if spec_kit_validation.suggestion:
            click.echo(f"  {spec_kit_validation.suggestion}", err=True)
        sys.exit(1)
    click.echo(f"✓ Spec Kit initialized on {main_branch} branch")

    # 4. Check Claude Code installed
    claude_validation = is_claude_code_installed()
    if not claude_validation.passed:
        click.echo(f"Error: {claude_validation.error_message}", err=True)
        if claude_validation.suggestion:
            click.echo(f"  {claude_validation.suggestion}", err=True)
        sys.exit(1)
    click.echo("✓ Claude Code found")

    # 5. Fetch remote branches
    click.echo("✓ Fetching remote branches...")
    if not git_fetch():
        # Warning but not fatal
        click.echo("  Warning: git fetch failed, continuing without remote updates", err=True)

    # 6. Get all branches and determine next feature number
    branches = list_all_branches()
    try:
        feature_number = get_next_feature_number(branches)
        click.echo(f"✓ Next feature number: {feature_number.formatted}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)

    # 8. Create FeatureRequest model
    sanitized_name = sanitize_feature_name(feature_request)
    try:
        feature_req = FeatureRequest(
            text=feature_request,
            sanitized_name=sanitized_name
        )
    except Exception as e:
        click.echo(f"Error: Invalid feature request: {e}", err=True)
        sys.exit(3)

    # 9. Build WorktreeConfig
    branch_name = f"{feature_number.formatted}-{feature_req.sanitized_name}"
    worktree_path = repo_root / ".worktrees" / branch_name

    try:
        worktree_config = WorktreeConfig(
            branch_name=branch_name,
            directory_path=worktree_path,
            base_branch=main_branch,
            feature_number=feature_number,
            feature_request=feature_req
        )
    except Exception as e:
        click.echo(f"Error: Failed to create worktree configuration: {e}", err=True)
        sys.exit(4)

    # 10. Create worktree
    click.echo(f"✓ Creating worktree at .worktrees/{branch_name}")
    try:
        create_worktree(
            worktree_config.directory_path,
            worktree_config.branch_name,
            worktree_config.base_branch
        )
    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)

    # 11. Launch Claude Code
    click.echo("✓ Launching Claude Code...")
    exit_code = launch_claude_code(
        worktree_config.directory_path,
        feature_req.text
    )

    # Propagate Claude's exit code
    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
