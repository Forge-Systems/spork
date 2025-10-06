"""Claude Code invocation module.

This module provides functions for launching Claude Code.
"""

import subprocess
from pathlib import Path


def launch_claude_code(worktree_path: Path, feature_request: str) -> int:
    """Launch Claude Code interactively with the /specify command.

    Args:
        worktree_path: Path to worktree directory (used as cwd)
        feature_request: Feature request text to pass to /specify

    Returns:
        Exit code from Claude Code process
    """
    try:
        # Launch Claude Code interactively with an initial message
        # The message will prompt Claude to run /specify with the feature request
        initial_message = f"/specify {feature_request}"

        result = subprocess.run(
            ["claude", initial_message],
            cwd=str(worktree_path),
            timeout=None  # No timeout - Claude session can be long
        )
        return result.returncode
    except FileNotFoundError:
        # Claude not found - should have been caught by validation
        return 4
    except Exception:
        # Any other error
        return 4
