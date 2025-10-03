"""Tests for worktree utilities module.

This module tests feature name sanitization and feature number detection.
"""

import pytest


def test_sanitize_feature_name_basic():
    """Given simple feature name
    When sanitizing
    Then should convert to lowercase with hyphens"""
    from spork.worktree import sanitize_feature_name

    # Given
    name = "Add User Authentication"

    # When
    result = sanitize_feature_name(name)

    # Then
    assert result == "add-user-authentication"


def test_sanitize_feature_name_special_characters():
    """Given feature name with special characters
    When sanitizing
    Then should remove special characters and keep alphanumeric"""
    from spork.worktree import sanitize_feature_name

    # Given
    name = "Fix bug #123 (critical!)"

    # When
    result = sanitize_feature_name(name)

    # Then
    assert result == "fix-bug-123-critical"


def test_sanitize_feature_name_multiple_spaces():
    """Given feature name with multiple spaces
    When sanitizing
    Then should collapse to single hyphens"""
    from spork.worktree import sanitize_feature_name

    # Given
    name = "Add    user    profile"

    # When
    result = sanitize_feature_name(name)

    # Then
    assert result == "add-user-profile"


def test_sanitize_feature_name_leading_trailing_hyphens():
    """Given feature name that would create leading/trailing hyphens
    When sanitizing
    Then should strip leading and trailing hyphens"""
    from spork.worktree import sanitize_feature_name

    # Given
    name = "   Add feature   "

    # When
    result = sanitize_feature_name(name)

    # Then
    assert result == "add-feature"
    assert not result.startswith("-")
    assert not result.endswith("-")


def test_sanitize_feature_name_length_limit():
    """Given feature name exceeding max_length
    When sanitizing
    Then should truncate to max_length"""
    from spork.worktree import sanitize_feature_name

    # Given
    name = "This is a very long feature name that should be truncated"

    # When
    result = sanitize_feature_name(name, max_length=20)

    # Then
    assert len(result) <= 20
    assert not result.endswith("-")  # Should not end with hyphen after truncation


def test_sanitize_feature_name_underscores_to_hyphens():
    """Given feature name with underscores
    When sanitizing
    Then should convert underscores to hyphens"""
    from spork.worktree import sanitize_feature_name

    # Given
    name = "add_user_profile"

    # When
    result = sanitize_feature_name(name)

    # Then
    assert result == "add-user-profile"
    assert "_" not in result


def test_sanitize_feature_name_consecutive_hyphens():
    """Given feature name with special chars creating consecutive hyphens
    When sanitizing
    Then should collapse to single hyphens"""
    from spork.worktree import sanitize_feature_name

    # Given
    name = "fix---bug***123"

    # When
    result = sanitize_feature_name(name)

    # Then
    assert result == "fix-bug-123"
    assert "--" not in result


def test_sanitize_feature_name_default_max_length():
    """Given feature name with default max_length
    When sanitizing
    Then should use default of 50 characters"""
    from spork.worktree import sanitize_feature_name

    # Given
    name = "x" * 100

    # When
    result = sanitize_feature_name(name)

    # Then
    assert len(result) <= 50


def test_get_next_feature_number_no_existing_branches():
    """Given no existing feature branches
    When getting next feature number
    Then should return 1"""
    from spork.worktree import get_next_feature_number

    # Given
    branches = ["main", "develop", "hotfix/critical"]

    # When
    result = get_next_feature_number(branches)

    # Then
    assert result.number == 1
    assert result.formatted == "001"


def test_get_next_feature_number_with_existing_branches():
    """Given existing feature branches
    When getting next feature number
    Then should return max + 1"""
    from spork.worktree import get_next_feature_number

    # Given
    branches = ["main", "001-add-auth", "002-fix-bug", "003-new-feature"]

    # When
    result = get_next_feature_number(branches)

    # Then
    assert result.number == 4
    assert result.formatted == "004"


def test_get_next_feature_number_with_remote_branches():
    """Given remote branches with higher numbers
    When getting next feature number
    Then should consider remote branches too"""
    from spork.worktree import get_next_feature_number

    # Given
    branches = [
        "main",
        "001-add-auth",
        "002-fix-bug",
        "origin/main",
        "origin/003-new-feature",
        "origin/005-remote-feature"
    ]

    # When
    result = get_next_feature_number(branches)

    # Then
    assert result.number == 6
    assert result.formatted == "006"


def test_get_next_feature_number_non_sequential():
    """Given non-sequential feature numbers
    When getting next feature number
    Then should return max + 1 (not fill gaps)"""
    from spork.worktree import get_next_feature_number

    # Given
    branches = ["main", "001-first", "003-third", "010-tenth"]

    # When
    result = get_next_feature_number(branches)

    # Then
    assert result.number == 11
    assert result.formatted == "011"


def test_get_next_feature_number_regex_pattern():
    """Given branches with various naming patterns
    When getting next feature number
    Then should only match ^\d{3}- pattern"""
    from spork.worktree import get_next_feature_number

    # Given
    branches = [
        "main",
        "001-feature",
        "feature-002",  # Should not match (number not at start)
        "42-feature",   # Should not match (not 3 digits)
        "0042-feature", # Should not match (4 digits)
        "003-valid"     # Should match
    ]

    # When
    result = get_next_feature_number(branches)

    # Then
    assert result.number == 4  # max(1, 3) + 1
    assert result.formatted == "004"


def test_get_next_feature_number_edge_case_999():
    """Given feature number 999 exists
    When getting next feature number
    Then should handle edge case appropriately"""
    from spork.worktree import get_next_feature_number

    # Given
    branches = ["main", "999-last-feature"]

    # When
    # This might raise an error or handle specially since 1000 > 999 limit
    # Based on FeatureNumber validation, this should fail
    with pytest.raises((ValueError, Exception)):
        get_next_feature_number(branches)


def test_get_next_feature_number_return_type():
    """Given any branch list
    When getting next feature number
    Then should return FeatureNumber model"""
    from spork.data_models import FeatureNumber
    from spork.worktree import get_next_feature_number

    # Given
    branches = ["main", "001-feature"]

    # When
    result = get_next_feature_number(branches)

    # Then
    assert isinstance(result, FeatureNumber)
    assert hasattr(result, "number")
    assert hasattr(result, "formatted")
