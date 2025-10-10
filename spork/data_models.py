"""Pydantic data models for spork CLI tool.

This module defines all core data structures with validation logic.
"""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class FeatureRequest(BaseModel):
    """Represents a user's feature request input."""

    model_config = {"frozen": True}

    text: str = Field(..., min_length=1, max_length=500)
    sanitized_name: str = Field(..., min_length=1, max_length=50)
    max_length: int = Field(default=50, ge=1, le=100)

    @field_validator("sanitized_name")
    @classmethod
    def validate_sanitized_name(cls, v: str) -> str:
        """Ensure only lowercase, hyphens, alphanumeric."""
        if not all(c.isalnum() or c == "-" for c in v):
            raise ValueError("Sanitized name must contain only alphanumeric and hyphens")
        return v


class ValidationResult(BaseModel):
    """Represents the outcome of a single validation check."""

    model_config = {"frozen": True}

    check_name: str
    passed: bool
    error_message: Optional[str] = None
    suggestion: Optional[str] = None

    @model_validator(mode="after")
    def validate_error_message(self) -> "ValidationResult":
        """Ensure error_message is provided when validation fails."""
        if not self.passed and not self.error_message:
            raise ValueError("error_message required when passed=False")
        return self


class GitRepository(BaseModel):
    """Represents a git repository and its metadata."""

    model_config = {"frozen": True}

    root_path: Path
    current_branch: str
    has_remote: bool
    main_branch: str

    @field_validator("main_branch")
    @classmethod
    def validate_main_branch(cls, v: str) -> str:
        """Ensure main_branch is either 'main' or 'master'."""
        if v not in ("main", "master"):
            raise ValueError("main_branch must be 'main' or 'master'")
        return v


class FeatureNumber(BaseModel):
    """Represents the numeric component of a feature branch name."""

    model_config = {"frozen": True}

    number: int = Field(..., ge=1, le=999)
    formatted: str = Field(..., pattern=r"^\d{3}$")

    @model_validator(mode="after")
    def validate_formatted_matches_number(self) -> "FeatureNumber":
        """Ensure formatted string matches the number."""
        if self.formatted != f"{self.number:03d}":
            raise ValueError(
                f"formatted '{self.formatted}' must match number {self.number:03d}"
            )
        return self


class WorktreeConfig(BaseModel):
    """Represents the configuration for creating a new worktree."""

    model_config = {"frozen": True}

    branch_name: str
    directory_path: Path
    base_branch: str
    feature_number: FeatureNumber
    feature_request: FeatureRequest


class CommandContext(BaseModel):
    """Represents the execution context for the entire spork command."""

    original_cwd: Path
    repository: Optional[GitRepository] = None
    worktree_config: Optional[WorktreeConfig] = None
    validation_results: list[ValidationResult] = Field(default_factory=list)


class EnvFileCopyResult(BaseModel):
    """Result of copying .env files to worktree."""

    model_config = {"frozen": True}

    files_discovered: int = Field(0, ge=0, description="Total .env files found")
    files_copied: int = Field(0, ge=0, description="Files successfully copied")
    files_failed: int = Field(0, ge=0, description="Files that failed to copy")
    errors: list[str] = Field(default_factory=list, description="Error messages")

    @model_validator(mode="after")
    def validate_counts(self) -> "EnvFileCopyResult":
        """Ensure copied + failed <= discovered."""
        total = self.files_copied + self.files_failed
        if total > self.files_discovered:
            raise ValueError(
                f"Copied ({self.files_copied}) + Failed ({self.files_failed}) "
                f"cannot exceed Discovered ({self.files_discovered})"
            )
        return self

    @property
    def success(self) -> bool:
        """Check if operation was fully successful."""
        return self.files_failed == 0 and self.files_discovered > 0

    @property
    def partial_success(self) -> bool:
        """Check if some files copied but some failed."""
        return self.files_copied > 0 and self.files_failed > 0
