# Git Operations Contract

**Version**: 1.0.0
**Date**: 2025-10-02

## Overview

This contract defines the expected behavior and interface for all git operations performed by the `frg` tool. These operations are implemented as function calls to `subprocess.run()` with specific git commands.

## Operations

### 1. Check Git Installed

**Purpose**: Verify git is available in PATH

**Command**:
```bash
git --version
```

**Expected Output** (success):
```
git version 2.39.3 (Apple Git-145)
```

**Success Criteria**:
- Exit code: 0
- stdout contains "git version"

**Failure Scenarios**:
- Command not found: `git` not in PATH
- Exit code non-zero: Invalid git installation

**Python Interface**:
```python
def is_git_installed() -> bool:
    """Check if git is installed and accessible."""
    # Returns: True if git --version succeeds, False otherwise
```

**Test Contract**:
- Mock `git --version` to return 0 → expect True
- Mock command not found → expect False

---

### 2. Check In Git Repository

**Purpose**: Verify current directory is inside a git repository

**Command**:
```bash
git rev-parse --is-inside-work-tree
```

**Expected Output** (success):
```
true
```

**Success Criteria**:
- Exit code: 0
- stdout: "true\n"

**Failure Scenarios**:
- Exit code 128: Not in a git repository
- stderr: "fatal: not a git repository"

**Python Interface**:
```python
def is_git_repository(path: Path) -> bool:
    """Check if path is inside a git repository."""
    # Returns: True if inside work tree, False otherwise
```

**Test Contract**:
- Mock successful output → expect True
- Mock exit code 128 → expect False

---

### 3. Get Repository Root

**Purpose**: Find the absolute path to the git repository root

**Command**:
```bash
git rev-parse --show-toplevel
```

**Expected Output** (success):
```
/Users/dev/projects/my-app
```

**Success Criteria**:
- Exit code: 0
- stdout: absolute path to repo root

**Failure Scenarios**:
- Exit code 128: Not in a git repository

**Python Interface**:
```python
def get_repo_root() -> Path:
    """Get absolute path to repository root."""
    # Returns: Path object
    # Raises: RuntimeError if not in git repo
```

**Test Contract**:
- Mock successful path → expect Path("/mocked/repo")
- Mock failure → expect RuntimeError

---

### 4. Get Main Branch Name

**Purpose**: Determine if repository uses "main" or "master" as primary branch

**Command**:
```bash
git rev-parse --verify main
git rev-parse --verify master
```

**Expected Behavior**:
- Try "main" first (modern convention)
- If fails, try "master" (legacy convention)
- Return whichever exists

**Success Criteria**:
- Exit code 0 for either "main" or "master"

**Failure Scenarios**:
- Both commands fail: Repository has neither branch (unusual)

**Python Interface**:
```python
def get_main_branch() -> str:
    """Determine main branch name (main or master)."""
    # Returns: "main" or "master"
    # Raises: RuntimeError if neither exists
```

**Test Contract**:
- Mock "main" exists → expect "main"
- Mock "master" exists (main fails) → expect "master"
- Mock both fail → expect RuntimeError

---

### 5. Fetch Remote Branches

**Purpose**: Update remote branch information before checking for conflicts

**Command**:
```bash
git fetch
```

**Expected Output** (success):
```
From github.com:user/repo
   a1b2c3d..e4f5g6h  main       -> origin/main
```

**Success Criteria**:
- Exit code: 0
- May have no output if already up-to-date

**Failure Scenarios**:
- Exit code 1: Network error, authentication failure
- No remote configured (warning, not fatal)

**Python Interface**:
```python
def git_fetch() -> bool:
    """Fetch remote branches."""
    # Returns: True if successful or no remote, False on error
```

**Test Contract**:
- Mock exit code 0 → expect True
- Mock exit code 1 → expect False
- Mock "no remote" error → expect True (warning logged)

---

### 6. List All Branches

**Purpose**: Get list of all local and remote branch names

**Command**:
```bash
git branch -a --format='%(refname:short)'
```

**Expected Output** (success):
```
main
001-add-auth
002-fix-bug
origin/main
origin/001-add-auth
origin/003-new-feature
```

**Success Criteria**:
- Exit code: 0
- One branch name per line
- Includes both local and remote branches

**Failure Scenarios**:
- Exit code non-zero: Git repository corruption

**Python Interface**:
```python
def list_all_branches() -> list[str]:
    """List all local and remote branches."""
    # Returns: List of branch names (short format)
```

**Test Contract**:
- Mock branch list → expect parsed list
- Mock empty repository → expect empty list

---

### 7. Create Worktree

**Purpose**: Create a new git worktree with a new branch

**Command**:
```bash
git worktree add <path> -b <branch-name> <base-branch>
```

**Example**:
```bash
git worktree add .worktrees/001-add-user-auth -b 001-add-user-auth main
```

**Expected Output** (success):
```
Preparing worktree (new branch '001-add-user-auth')
HEAD is now at a1b2c3d Initial commit
```

**Success Criteria**:
- Exit code: 0
- Directory created at specified path
- New branch created and checked out in worktree

**Failure Scenarios**:
- Exit code 128: Branch already exists
- Exit code 128: Path already exists
- Permission denied: Cannot create directory

**Python Interface**:
```python
def create_worktree(path: Path, branch_name: str, base_branch: str) -> bool:
    """Create a new worktree with a new branch."""
    # Returns: True if successful, False on error
    # Raises: RuntimeError with descriptive message on failure
```

**Test Contract**:
- Mock successful creation → expect True
- Mock "already exists" error → expect RuntimeError
- Mock permission denied → expect RuntimeError

---

## Error Handling Contract

### Error Message Format

All git operations should handle errors consistently:

```python
try:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
except subprocess.CalledProcessError as e:
    # Extract meaningful error from stderr
    # Raise RuntimeError with context
    raise RuntimeError(f"Git operation failed: {e.stderr}")
```

### Exit Code Mapping

| Git Exit Code | Meaning | frg Action |
|---------------|---------|------------|
| 0 | Success | Continue execution |
| 1 | General error | Log error, exit with code 2 |
| 128 | Git-specific error (e.g., not a repo, branch exists) | Log error, exit with code 1 or 2 |
| Other | Unexpected error | Log error, exit with code 4 |

### Logging Contract

**Verbose Output** (future feature):
```
[DEBUG] Running: git fetch
[DEBUG] Git output: From github.com:user/repo...
[DEBUG] Git exited with code: 0
```

**Normal Output** (current):
```
✓ Fetching remote branches...
```

**Error Output**:
```
Error: Git fetch failed
  Check network connection and remote configuration
  Git error: fatal: unable to access 'https://...': Could not resolve host
```

---

## Contract Test Scenarios

### Test Suite: `tests/unit/test_git_operations.py`

**Setup**: Use `pytest-subprocess` to mock all git command invocations

**Test Cases**:

1. **test_is_git_installed_success**: Mock `git --version` → expect True
2. **test_is_git_installed_not_found**: Mock command not found → expect False
3. **test_is_git_repository_success**: Mock `git rev-parse --is-inside-work-tree` → expect True
4. **test_is_git_repository_false**: Mock exit code 128 → expect False
5. **test_get_repo_root_success**: Mock valid path → expect Path
6. **test_get_repo_root_not_repo**: Mock failure → expect RuntimeError
7. **test_get_main_branch_uses_main**: Mock "main" exists → expect "main"
8. **test_get_main_branch_uses_master**: Mock "master" exists → expect "master"
9. **test_get_main_branch_neither_exists**: Mock both fail → expect RuntimeError
10. **test_git_fetch_success**: Mock exit code 0 → expect True
11. **test_git_fetch_network_error**: Mock exit code 1 → expect False
12. **test_list_all_branches_success**: Mock branch list → expect parsed list
13. **test_list_all_branches_includes_remote**: Verify remote branches included
14. **test_create_worktree_success**: Mock successful creation → expect True
15. **test_create_worktree_already_exists**: Mock exit code 128 → expect RuntimeError
16. **test_create_worktree_permission_denied**: Mock permission error → expect RuntimeError

### Assertion Strategy

**Command Invocation**:
```python
def test_git_fetch(subprocess_mock):
    subprocess_mock.register(['git', 'fetch'], returncode=0)
    result = git_fetch()
    assert result is True
    # Verify command was called exactly once
    assert subprocess_mock.call_count(['git', 'fetch']) == 1
```

**Error Handling**:
```python
def test_create_worktree_failure(subprocess_mock):
    subprocess_mock.register(
        ['git', 'worktree', 'add', ANY, '-b', ANY, ANY],
        returncode=128,
        stderr="fatal: 'branch' already exists"
    )
    with pytest.raises(RuntimeError, match="already exists"):
        create_worktree(Path(".worktrees/001"), "001-feature", "main")
```

---

**Git Operations Contract Complete**: Defines all git command interactions and their expected behavior.
