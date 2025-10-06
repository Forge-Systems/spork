"""Worktree utilities module.

This module provides functions for feature name sanitization and feature number detection.
"""

import re

from spork.data_models import FeatureNumber


def sanitize_feature_name(name: str, max_length: int = 50) -> str:
    """Sanitize feature name for use in git branch names.

    Converts to lowercase, replaces spaces and underscores with hyphens,
    removes special characters, collapses multiple hyphens, and truncates to max_length.

    Args:
        name: Raw feature name
        max_length: Maximum length for sanitized name (default: 50)

    Returns:
        Sanitized feature name safe for git branch names
    """
    # Convert to lowercase
    sanitized = name.lower()

    # Replace underscores and spaces with hyphens
    sanitized = sanitized.replace("_", "-")
    sanitized = sanitized.replace(" ", "-")

    # Remove all non-alphanumeric characters except hyphens
    sanitized = re.sub(r"[^a-z0-9-]", "-", sanitized)

    # Collapse multiple consecutive hyphens into single hyphen
    sanitized = re.sub(r"-+", "-", sanitized)

    # Strip leading and trailing hyphens
    sanitized = sanitized.strip("-")

    # Truncate to max_length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
        # Ensure we don't end with a hyphen after truncation
        sanitized = sanitized.rstrip("-")

    return sanitized


def get_next_feature_number(branches: list[str]) -> FeatureNumber:
    r"""Determine the next feature number based on existing branches.

    Parses branch names matching the pattern ^\d{3}- and returns max + 1.

    Args:
        branches: List of all local and remote branch names

    Returns:
        FeatureNumber with next available number

    Raises:
        ValueError: If next number would exceed 999
    """
    # Pattern: 3 digits at start followed by hyphen
    pattern = re.compile(r"^(\d{3})-")

    feature_numbers = []
    for branch in branches:
        # Remove remote prefix if present (e.g., "origin/001-feature" -> "001-feature")
        branch_name = branch.split("/")[-1]
        match = pattern.match(branch_name)
        if match:
            feature_numbers.append(int(match.group(1)))

    # Determine next number
    if feature_numbers:
        next_number = max(feature_numbers) + 1
    else:
        next_number = 1

    # Validate range
    if next_number > 999:
        raise ValueError(f"Feature number {next_number} exceeds maximum of 999")

    return FeatureNumber(number=next_number, formatted=f"{next_number:03d}")
