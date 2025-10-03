# Data Model: Git Worktree Feature Request Tool

**Date**: 2025-10-02
**Feature**: 001-build-a-utility

## Overview

This document defines the core data structures and their relationships for the `frg` CLI tool. As a command-line utility, the "data model" primarily consists of Python dataclasses and types representing the tool's internal state and operations.

## Core Entities

### 1. FeatureRequest

Represents a user's feature request input.

**Fields**:
- `text` (str): Raw feature request text from command-line argument
- `sanitized_name` (str): Sanitized version safe for git branch names
- `max_length` (int): Maximum length for sanitized names (default: 50)

**Validation Rules**:
- `text` must not be empty
- `text` must not exceed 500 characters (reasonable input limit)
- `sanitized_name` derived via sanitization algorithm (see research.md)

**State Transitions**: Immutable once created

**Example**:
```python
FeatureRequest(
    text="Add user authentication system",
    sanitized_name="add-user-authentication-system",
    max_length=50
)
```

---

### 2. ValidationResult

Represents the outcome of a single validation check.

**Fields**:
- `check_name` (str): Name of the validation check (e.g., "git_installed", "in_git_repo")
- `passed` (bool): Whether the check succeeded
- `error_message` (str | None): Human-readable error if failed, None if passed
- `suggestion` (str | None): Actionable suggestion for fixing the error

**Validation Rules**:
- If `passed=False`, `error_message` must be provided
- `check_name` must match predefined validation types

**State Transitions**: Immutable once created

**Example**:
```python
ValidationResult(
    check_name="spec_kit_initialized",
    passed=False,
    error_message="Spec Kit not initialized (.specify/memory/constitution.md missing)",
    suggestion="Run 'specify init .' to initialize Spec Kit in this repository"
)
```

---

### 3. GitRepository

Represents a git repository and its metadata.

**Fields**:
- `root_path` (Path): Absolute path to repository root
- `current_branch` (str): Name of currently checked-out branch
- `has_remote` (bool): Whether repository has at least one remote
- `main_branch` (str): Name of main branch ("main" or "master")

**Validation Rules**:
- `root_path` must be an existing directory
- `root_path` must be a valid git repository
- `main_branch` must exist in the repository

**State Transitions**: Immutable snapshot of repository state at instantiation

**Example**:
```python
GitRepository(
    root_path=Path("/Users/dev/my-project"),
    current_branch="main",
    has_remote=True,
    main_branch="main"
)
```

---

### 4. FeatureNumber

Represents the numeric component of a feature branch name.

**Fields**:
- `number` (int): Feature number (1-999)
- `formatted` (str): Zero-padded 3-digit string (e.g., "001", "042", "123")

**Validation Rules**:
- `number` must be between 1 and 999 (inclusive)
- `formatted` must be exactly 3 characters, zero-padded

**Derivation**:
- Computed from existing local and remote branches
- Formula: `max(existing_feature_numbers) + 1`, or `1` if none exist

**State Transitions**: Immutable once determined

**Example**:
```python
FeatureNumber(
    number=42,
    formatted="042"
)
```

---

### 5. WorktreeConfig

Represents the configuration for creating a new worktree.

**Fields**:
- `branch_name` (str): Full branch name (e.g., "001-add-user-auth")
- `directory_path` (Path): Absolute path to worktree directory
- `base_branch` (str): Branch to base worktree on (e.g., "main")
- `feature_number` (FeatureNumber): Numeric identifier
- `feature_request` (FeatureRequest): Original user request

**Validation Rules**:
- `branch_name` must not exist in local or remote branches
- `directory_path` must not exist (no conflicts)
- `base_branch` must exist in the repository
- `branch_name` format: `{feature_number.formatted}-{feature_request.sanitized_name}`

**Relationships**:
- Composed of `FeatureNumber` and `FeatureRequest`
- Used to create worktree via git operations

**State Transitions**: Built → Validated → Used for creation

**Example**:
```python
WorktreeConfig(
    branch_name="001-add-user-auth",
    directory_path=Path("/Users/dev/my-project/.worktrees/001-add-user-auth"),
    base_branch="main",
    feature_number=FeatureNumber(1, "001"),
    feature_request=FeatureRequest("add user auth", "add-user-auth", 50)
)
```

---

### 6. CommandContext

Represents the execution context for the entire `frg` command.

**Fields**:
- `original_cwd` (Path): Working directory when command was invoked
- `repository` (GitRepository): Detected git repository
- `worktree_config` (WorktreeConfig | None): Configuration for worktree to create
- `validation_results` (list[ValidationResult]): Results from all validation checks

**Validation Rules**:
- `original_cwd` must exist
- If any `validation_results` have `passed=False`, command should fail
- `worktree_config` is None until validation passes

**Lifecycle**:
1. Created with `original_cwd`
2. Repository detected and validated
3. Validation results accumulated
4. If all validations pass, `worktree_config` is built
5. Worktree created, Claude Code launched

**Example**:
```python
CommandContext(
    original_cwd=Path("/Users/dev/my-project/src"),
    repository=GitRepository(...),
    worktree_config=WorktreeConfig(...),
    validation_results=[
        ValidationResult("git_installed", True, None, None),
        ValidationResult("in_git_repo", True, None, None),
        # ... more validations
    ]
)
```

---

## Relationships

```
CommandContext
├── original_cwd: Path
├── repository: GitRepository
│   ├── root_path: Path
│   ├── current_branch: str
│   ├── has_remote: bool
│   └── main_branch: str
├── worktree_config: WorktreeConfig
│   ├── branch_name: str
│   ├── directory_path: Path
│   ├── base_branch: str
│   ├── feature_number: FeatureNumber
│   │   ├── number: int
│   │   └── formatted: str
│   └── feature_request: FeatureRequest
│       ├── text: str
│       ├── sanitized_name: str
│       └── max_length: int
└── validation_results: list[ValidationResult]
    ├── check_name: str
    ├── passed: bool
    ├── error_message: str | None
    └── suggestion: str | None
```

## Data Flow

```
User Input (CLI args)
  ↓
FeatureRequest created
  ↓
CommandContext initialized
  ↓
Validation Chain executes → ValidationResults accumulated
  ↓
GitRepository detected
  ↓
Git fetch updates remote refs
  ↓
FeatureNumber determined from existing branches
  ↓
WorktreeConfig built
  ↓
Git worktree created
  ↓
Claude Code launched with WorktreeConfig.directory_path
```

## Invariants

1. **Atomicity**: Either entire command succeeds or fails; no partial state
2. **Immutability**: All data structures are immutable after creation
3. **Fail-Fast**: First validation failure stops execution
4. **No Persistent State**: No database, config files, or cache; all state derived from git
5. **Idempotency**: Running twice with same input produces same branch number (if no new branches created between runs)

## Type Definitions (Python)

```python
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

class FeatureRequest(BaseModel):
    model_config = {"frozen": True}

    text: str = Field(..., min_length=1, max_length=500)
    sanitized_name: str = Field(..., min_length=1, max_length=50)
    max_length: int = Field(default=50, ge=1, le=100)

    @field_validator('sanitized_name')
    @classmethod
    def validate_sanitized_name(cls, v: str) -> str:
        # Ensure only lowercase, hyphens, alphanumeric
        if not all(c.isalnum() or c == '-' for c in v):
            raise ValueError("Sanitized name must contain only alphanumeric and hyphens")
        return v

class ValidationResult(BaseModel):
    model_config = {"frozen": True}

    check_name: str
    passed: bool
    error_message: Optional[str] = None
    suggestion: Optional[str] = None

    @model_validator(mode='after')
    def validate_error_message(self):
        if not self.passed and not self.error_message:
            raise ValueError("error_message required when passed=False")
        return self

class GitRepository(BaseModel):
    model_config = {"frozen": True}

    root_path: Path
    current_branch: str
    has_remote: bool
    main_branch: str

    @field_validator('main_branch')
    @classmethod
    def validate_main_branch(cls, v: str) -> str:
        if v not in ('main', 'master'):
            raise ValueError("main_branch must be 'main' or 'master'")
        return v

class FeatureNumber(BaseModel):
    model_config = {"frozen": True}

    number: int = Field(..., ge=1, le=999)
    formatted: str = Field(..., pattern=r'^\d{3}$')

    @model_validator(mode='after')
    def validate_formatted_matches_number(self):
        if self.formatted != f"{self.number:03d}":
            raise ValueError(f"formatted '{self.formatted}' must match number {self.number:03d}")
        return self

class WorktreeConfig(BaseModel):
    model_config = {"frozen": True}

    branch_name: str
    directory_path: Path
    base_branch: str
    feature_number: FeatureNumber
    feature_request: FeatureRequest

class CommandContext(BaseModel):
    original_cwd: Path
    repository: Optional[GitRepository] = None
    worktree_config: Optional[WorktreeConfig] = None
    validation_results: list[ValidationResult] = Field(default_factory=list)
```

## Storage Considerations

**No Persistent Storage**: This tool stores no state. All information is derived from:
- Git repository metadata (branches, remotes, worktrees)
- File system (Spec Kit presence, directory existence)
- PATH environment (git, claude availability)

**Worktree Location**: `.worktrees/` subdirectory within repository, excluded via `.gitignore`

**Git Storage**: Git manages worktree metadata in `.git/worktrees/`, cleaned up via `git worktree prune`

---

**Data Model Complete**: Ready for contract definition and test generation.
