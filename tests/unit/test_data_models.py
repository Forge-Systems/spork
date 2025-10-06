"""Tests for Pydantic data models.

This module tests all 6 Pydantic models with their field validators,
model validators, and validation rules.
"""

from pathlib import Path

import pytest
from pydantic import ValidationError


def test_feature_request_valid():
    """Given valid feature request data
    When creating FeatureRequest model
    Then model should be created successfully with sanitized name"""
    from spork.data_models import FeatureRequest

    # Given
    text = "Add user authentication system"
    sanitized_name = "add-user-authentication-system"

    # When
    request = FeatureRequest(text=text, sanitized_name=sanitized_name)

    # Then
    assert request.text == text
    assert request.sanitized_name == sanitized_name
    assert request.max_length == 50  # default value


def test_feature_request_text_min_length():
    """Given empty text
    When creating FeatureRequest model
    Then validation error should be raised"""
    from spork.data_models import FeatureRequest

    # Given / When / Then
    with pytest.raises(ValidationError, match="at least 1 character"):
        FeatureRequest(text="", sanitized_name="test")


def test_feature_request_text_max_length():
    """Given text exceeding 500 characters
    When creating FeatureRequest model
    Then validation error should be raised"""
    from spork.data_models import FeatureRequest

    # Given
    long_text = "x" * 501

    # When / Then
    with pytest.raises(ValidationError, match="at most 500 characters"):
        FeatureRequest(text=long_text, sanitized_name="test")


def test_feature_request_sanitized_name_validation():
    """Given sanitized name with invalid characters
    When creating FeatureRequest model
    Then validation error should be raised"""
    from spork.data_models import FeatureRequest

    # Given / When / Then
    with pytest.raises(ValidationError, match="alphanumeric and hyphens"):
        FeatureRequest(text="test", sanitized_name="test_with_underscore")


def test_feature_request_sanitized_name_valid_characters():
    """Given sanitized name with only alphanumeric and hyphens
    When creating FeatureRequest model
    Then model should be created successfully"""
    from spork.data_models import FeatureRequest

    # Given
    valid_names = ["test", "test-123", "add-user-auth", "fix-bug-42"]

    # When / Then
    for name in valid_names:
        request = FeatureRequest(text="test", sanitized_name=name)
        assert request.sanitized_name == name


def test_feature_request_immutable():
    """Given created FeatureRequest model
    When attempting to modify fields
    Then validation error should be raised (frozen model)"""
    from spork.data_models import FeatureRequest

    # Given
    request = FeatureRequest(text="test", sanitized_name="test")

    # When / Then
    with pytest.raises(ValidationError, match="frozen"):
        request.text = "new text"  # type: ignore


def test_validation_result_passed_no_error():
    """Given validation result with passed=True
    When creating ValidationResult model
    Then model should be created with error_message=None"""
    from spork.data_models import ValidationResult

    # Given / When
    result = ValidationResult(
        check_name="git_installed",
        passed=True,
        error_message=None,
        suggestion=None
    )

    # Then
    assert result.passed is True
    assert result.error_message is None


def test_validation_result_failed_requires_error_message():
    """Given validation result with passed=False and no error_message
    When creating ValidationResult model
    Then validation error should be raised"""
    from spork.data_models import ValidationResult

    # Given / When / Then
    with pytest.raises(ValidationError, match="error_message required"):
        ValidationResult(
            check_name="git_installed",
            passed=False,
            error_message=None,
            suggestion=None
        )


def test_validation_result_failed_with_error_message():
    """Given validation result with passed=False and error_message
    When creating ValidationResult model
    Then model should be created successfully"""
    from spork.data_models import ValidationResult

    # Given / When
    result = ValidationResult(
        check_name="git_installed",
        passed=False,
        error_message="Git is not installed",
        suggestion="Install git from https://git-scm.com"
    )

    # Then
    assert result.passed is False
    assert result.error_message == "Git is not installed"
    assert result.suggestion == "Install git from https://git-scm.com"


def test_validation_result_immutable():
    """Given created ValidationResult model
    When attempting to modify fields
    Then validation error should be raised (frozen model)"""
    from spork.data_models import ValidationResult

    # Given
    result = ValidationResult(
        check_name="test",
        passed=True,
        error_message=None,
        suggestion=None
    )

    # When / Then
    with pytest.raises(ValidationError, match="frozen"):
        result.passed = False  # type: ignore


def test_git_repository_valid():
    """Given valid git repository data
    When creating GitRepository model
    Then model should be created successfully"""
    from spork.data_models import GitRepository

    # Given / When
    repo = GitRepository(
        root_path=Path("/Users/dev/my-project"),
        current_branch="main",
        has_remote=True,
        main_branch="main"
    )

    # Then
    assert repo.root_path == Path("/Users/dev/my-project")
    assert repo.current_branch == "main"
    assert repo.has_remote is True
    assert repo.main_branch == "main"


def test_git_repository_main_branch_validation():
    """Given main_branch that is not 'main' or 'master'
    When creating GitRepository model
    Then validation error should be raised"""
    from spork.data_models import GitRepository

    # Given / When / Then
    with pytest.raises(ValidationError, match="must be 'main' or 'master'"):
        GitRepository(
            root_path=Path("/test"),
            current_branch="develop",
            has_remote=True,
            main_branch="develop"
        )


def test_git_repository_accepts_main():
    """Given main_branch='main'
    When creating GitRepository model
    Then model should be created successfully"""
    from spork.data_models import GitRepository

    # Given / When
    repo = GitRepository(
        root_path=Path("/test"),
        current_branch="main",
        has_remote=True,
        main_branch="main"
    )

    # Then
    assert repo.main_branch == "main"


def test_git_repository_accepts_master():
    """Given main_branch='master'
    When creating GitRepository model
    Then model should be created successfully"""
    from spork.data_models import GitRepository

    # Given / When
    repo = GitRepository(
        root_path=Path("/test"),
        current_branch="master",
        has_remote=True,
        main_branch="master"
    )

    # Then
    assert repo.main_branch == "master"


def test_git_repository_immutable():
    """Given created GitRepository model
    When attempting to modify fields
    Then validation error should be raised (frozen model)"""
    from spork.data_models import GitRepository

    # Given
    repo = GitRepository(
        root_path=Path("/test"),
        current_branch="main",
        has_remote=True,
        main_branch="main"
    )

    # When / Then
    with pytest.raises(ValidationError, match="frozen"):
        repo.main_branch = "master"  # type: ignore


def test_feature_number_valid():
    """Given valid feature number and formatted string
    When creating FeatureNumber model
    Then model should be created successfully"""
    from spork.data_models import FeatureNumber

    # Given / When
    feature_num = FeatureNumber(number=42, formatted="042")

    # Then
    assert feature_num.number == 42
    assert feature_num.formatted == "042"


def test_feature_number_range_validation_min():
    """Given number less than 1
    When creating FeatureNumber model
    Then validation error should be raised"""
    from spork.data_models import FeatureNumber

    # Given / When / Then
    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        FeatureNumber(number=0, formatted="000")


def test_feature_number_range_validation_max():
    """Given number greater than 999
    When creating FeatureNumber model
    Then validation error should be raised"""
    from spork.data_models import FeatureNumber

    # Given / When / Then
    with pytest.raises(ValidationError, match="less than or equal to 999"):
        FeatureNumber(number=1000, formatted="1000")


def test_feature_number_formatted_pattern():
    """Given formatted string not matching 3-digit pattern
    When creating FeatureNumber model
    Then validation error should be raised"""
    from spork.data_models import FeatureNumber

    # Given / When / Then
    with pytest.raises(ValidationError, match=r"String should match pattern"):
        FeatureNumber(number=1, formatted="1")


def test_feature_number_consistency_validation():
    """Given formatted string not matching number
    When creating FeatureNumber model
    Then validation error should be raised"""
    from spork.data_models import FeatureNumber

    # Given / When / Then
    with pytest.raises(ValidationError, match="formatted '042' must match number 001"):
        FeatureNumber(number=1, formatted="042")


def test_feature_number_consistency_valid():
    """Given formatted string matching number
    When creating FeatureNumber model
    Then model should be created successfully"""
    from spork.data_models import FeatureNumber

    # Given
    test_cases = [(1, "001"), (42, "042"), (123, "123"), (999, "999")]

    # When / Then
    for number, formatted in test_cases:
        feature_num = FeatureNumber(number=number, formatted=formatted)
        assert feature_num.number == number
        assert feature_num.formatted == formatted


def test_feature_number_immutable():
    """Given created FeatureNumber model
    When attempting to modify fields
    Then validation error should be raised (frozen model)"""
    from spork.data_models import FeatureNumber

    # Given
    feature_num = FeatureNumber(number=1, formatted="001")

    # When / Then
    with pytest.raises(ValidationError, match="frozen"):
        feature_num.number = 2  # type: ignore


def test_worktree_config_valid():
    """Given valid worktree configuration data
    When creating WorktreeConfig model
    Then model should be created successfully with nested models"""
    from spork.data_models import FeatureNumber, FeatureRequest, WorktreeConfig

    # Given
    feature_number = FeatureNumber(number=1, formatted="001")
    feature_request = FeatureRequest(text="add auth", sanitized_name="add-auth")

    # When
    config = WorktreeConfig(
        branch_name="001-add-auth",
        directory_path=Path(".worktrees/001-add-auth"),
        base_branch="main",
        feature_number=feature_number,
        feature_request=feature_request
    )

    # Then
    assert config.branch_name == "001-add-auth"
    assert config.directory_path == Path(".worktrees/001-add-auth")
    assert config.base_branch == "main"
    assert config.feature_number == feature_number
    assert config.feature_request == feature_request


def test_worktree_config_nested_model_composition():
    """Given WorktreeConfig with nested Pydantic models
    When accessing nested model fields
    Then nested models should be properly composed and accessible"""
    from spork.data_models import FeatureNumber, FeatureRequest, WorktreeConfig

    # Given / When
    config = WorktreeConfig(
        branch_name="042-fix-bug",
        directory_path=Path(".worktrees/042-fix-bug"),
        base_branch="main",
        feature_number=FeatureNumber(number=42, formatted="042"),
        feature_request=FeatureRequest(text="fix bug", sanitized_name="fix-bug")
    )

    # Then
    assert config.feature_number.number == 42
    assert config.feature_number.formatted == "042"
    assert config.feature_request.text == "fix bug"
    assert config.feature_request.sanitized_name == "fix-bug"


def test_worktree_config_immutable():
    """Given created WorktreeConfig model
    When attempting to modify fields
    Then validation error should be raised (frozen model)"""
    from spork.data_models import FeatureNumber, FeatureRequest, WorktreeConfig

    # Given
    config = WorktreeConfig(
        branch_name="001-test",
        directory_path=Path(".worktrees/001-test"),
        base_branch="main",
        feature_number=FeatureNumber(number=1, formatted="001"),
        feature_request=FeatureRequest(text="test", sanitized_name="test")
    )

    # When / Then
    with pytest.raises(ValidationError, match="frozen"):
        config.branch_name = "002-test"  # type: ignore


def test_command_context_valid():
    """Given valid command context data
    When creating CommandContext model
    Then model should be created successfully"""
    from spork.data_models import CommandContext

    # Given / When
    context = CommandContext(
        original_cwd=Path("/Users/dev/project"),
        repository=None,
        worktree_config=None,
        validation_results=[]
    )

    # Then
    assert context.original_cwd == Path("/Users/dev/project")
    assert context.repository is None
    assert context.worktree_config is None
    assert context.validation_results == []


def test_command_context_optional_fields():
    """Given CommandContext with optional fields
    When creating model with some fields None
    Then model should be created successfully"""
    from spork.data_models import CommandContext

    # Given / When
    context = CommandContext(original_cwd=Path("/test"))

    # Then
    assert context.repository is None
    assert context.worktree_config is None
    assert isinstance(context.validation_results, list)


def test_command_context_default_factory():
    """Given CommandContext without validation_results
    When creating model
    Then validation_results should be initialized as empty list"""
    from spork.data_models import CommandContext

    # Given / When
    context = CommandContext(original_cwd=Path("/test"))

    # Then
    assert context.validation_results == []
    assert isinstance(context.validation_results, list)


def test_command_context_with_all_fields():
    """Given CommandContext with all fields populated
    When creating model
    Then all fields should be properly set"""
    from spork.data_models import (
        CommandContext,
        FeatureNumber,
        FeatureRequest,
        GitRepository,
        ValidationResult,
        WorktreeConfig,
    )

    # Given
    repo = GitRepository(
        root_path=Path("/test"),
        current_branch="main",
        has_remote=True,
        main_branch="main"
    )
    config = WorktreeConfig(
        branch_name="001-test",
        directory_path=Path(".worktrees/001-test"),
        base_branch="main",
        feature_number=FeatureNumber(number=1, formatted="001"),
        feature_request=FeatureRequest(text="test", sanitized_name="test")
    )
    results = [
        ValidationResult(
            check_name="git_installed",
            passed=True,
            error_message=None,
            suggestion=None
        )
    ]

    # When
    context = CommandContext(
        original_cwd=Path("/test"),
        repository=repo,
        worktree_config=config,
        validation_results=results
    )

    # Then
    assert context.original_cwd == Path("/test")
    assert context.repository == repo
    assert context.worktree_config == config
    assert context.validation_results == results
