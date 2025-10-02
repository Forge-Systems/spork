# Research: Git Worktree Feature Request Tool

**Date**: 2025-10-02
**Feature**: 001-build-a-utility

## Research Areas

### 1. Python CLI Framework Selection

**Decision**: Click framework

**Rationale**:
- Industry standard for Python CLI tools (used by Flask, pip, AWS CLI v2)
- Excellent argument parsing with type validation
- Built-in support for help text generation
- Easy testing with CliRunner
- Composable command structure for potential future expansion

**Alternatives Considered**:
- **argparse** (stdlib): More verbose, less elegant API, no built-in testing utilities
- **Typer**: Newer, uses type hints, but Click has broader adoption and stability
- **docopt**: DSL-based, less flexible for complex validation logic

### 2. Git Worktree Operations via Python

**Decision**: Use subprocess module with explicit git commands

**Rationale**:
- Git worktree commands are straightforward and stable
- subprocess provides full control over stdin/stdout/stderr
- No external git library dependency (GitPython, pygit2) reduces attack surface
- Direct git CLI invocation matches user's mental model
- Easy to test with pytest-subprocess mocking

**Key Commands**:
```bash
git worktree add <path> <branch>          # Create worktree
git branch -a --format='%(refname:short)' # List all branches
git fetch                                 # Update remote refs
git rev-parse --show-toplevel             # Get repo root
git rev-parse --is-inside-work-tree       # Validate git repo
```

**Alternatives Considered**:
- **GitPython**: Heavy dependency, abstracts away git semantics
- **pygit2** (libgit2 bindings): C library dependency, installation complexity

### 3. Feature Number Determination Algorithm

**Decision**: Parse branch names with regex, find max numeric prefix, increment

**Algorithm**:
```python
import re

def get_next_feature_number(branches: list[str]) -> int:
    pattern = r'^(\d{3})-'
    numbers = []
    for branch in branches:
        match = re.match(pattern, branch)
        if match:
            numbers.append(int(match.group(1)))
    return (max(numbers) + 1) if numbers else 1
```

**Rationale**:
- Simple, deterministic, no state files needed
- Works with both local and remote branches
- Handles gaps in numbering gracefully
- Three-digit zero-padding (001, 002, ..., 999) matches spec-kit convention

**Edge Cases Handled**:
- No existing feature branches → returns 001
- Non-sequential numbers → finds max and increments
- Mixed branch naming → ignores non-matching branches

### 4. String Sanitization for Branch Names

**Decision**: Lowercase, replace spaces/special chars with hyphens, limit length

**Implementation**:
```python
import re

def sanitize_feature_name(text: str, max_length: int = 50) -> str:
    # Lowercase and replace whitespace with hyphens
    sanitized = text.lower().strip()
    sanitized = re.sub(r'\s+', '-', sanitized)

    # Remove or replace special characters
    sanitized = re.sub(r'[^a-z0-9-]', '', sanitized)

    # Remove consecutive hyphens
    sanitized = re.sub(r'-+', '-', sanitized)

    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')

    # Limit length
    return sanitized[:max_length]
```

**Rationale**:
- Git branch naming rules: alphanumeric, hyphens, no spaces
- Predictable output for same input
- Length limit prevents excessively long branch names
- Preserves readability while ensuring safety

**Test Cases**:
- "Add User Authentication" → "add-user-authentication"
- "Fix bug #123 (critical!)" → "fix-bug-123-critical"
- "Support UTF-8 encoding" → "support-utf-8-encoding"

### 5. Spec Kit Detection Strategy

**Decision**: Check for `.specify/` directory structure and key files

**Validation Sequence**:
```python
from pathlib import Path

def is_spec_kit_initialized(repo_root: Path) -> tuple[bool, str]:
    specify_dir = repo_root / '.specify'
    if not specify_dir.is_dir():
        return False, "Spec Kit not installed (.specify/ directory missing)"

    required_paths = [
        specify_dir / 'memory' / 'constitution.md',
        specify_dir / 'templates',
        specify_dir / 'scripts',
    ]

    for path in required_paths:
        if not path.exists():
            return False, f"Spec Kit incomplete ({path.name} missing)"

    return True, "Spec Kit initialized"
```

**Rationale**:
- Based on Spec Kit documentation research (see web-research-specialist findings)
- Validates installation completeness, not just `.specify/` presence
- Provides specific error messages for debugging
- Minimal overhead (3-4 file system checks)

### 6. Claude Code Invocation Pattern

**Decision**: Use subprocess with cwd set to worktree, pass `/specify` via stdin

**Implementation Strategy**:
```python
import subprocess
from pathlib import Path

def launch_claude_code(worktree_path: Path, feature_request: str) -> int:
    # Change to worktree directory and invoke claude
    # Pass /specify command with feature request
    cmd = ['claude', '--', '/specify', feature_request]

    result = subprocess.run(
        cmd,
        cwd=worktree_path,
        check=False,  # Let Claude Code handle its own exit codes
    )

    return result.returncode
```

**Rationale**:
- Claude Code CLI operates in current working directory
- Passing feature request as argument ensures proper quoting
- Interactive mode is default (stdin/stdout connected to terminal)
- Exit code propagation preserves Claude's error signaling

**Alternatives Considered**:
- **Piping `/specify` via stdin**: Less reliable, quote escaping complexity
- **Using `-c` or `--command` flag**: May not exist in Claude CLI
- **Separate terminal window**: Breaks user expectation of single-shell workflow

### 7. Testing Strategy for CLI Tool

**Decision**: pytest with pytest-subprocess for external command mocking

**Test Structure**:
```python
# Unit tests: Mock subprocess calls
def test_git_fetch(subprocess_mock):
    subprocess_mock.register(['git', 'fetch'], returncode=0)
    result = git_fetch()
    assert result.success

# Integration tests: Use CliRunner with temporary git repos
def test_frg_cli_integration(cli_runner, tmp_repo):
    result = cli_runner.invoke(frg_cli, ['add user auth'])
    assert result.exit_code == 0
    assert '.worktrees/001-add-user-auth' in tmp_repo
```

**Rationale**:
- pytest-subprocess avoids actual git/Claude Code execution during tests
- CliRunner provides isolated test environment
- tmp_path fixture for temporary git repositories
- Fast, deterministic, no network dependencies

**Test Categories**:
1. **Unit**: Individual functions (validators, sanitization, parsing)
2. **Integration**: CLI commands with mocked subprocess
3. **Contract**: Verify git command syntax, exit code handling

### 8. Package Distribution Strategy

**Decision**: Multi-channel distribution (PyPI, Homebrew, npm)

**PyPI (Primary)**:
```toml
[project]
name = "frg"
version = "0.1.0"
dependencies = ["click>=8.0"]

[project.scripts]
frg = "frg.cli:main"
```

**Homebrew Formula**:
```ruby
class Frg < Formula
  include Language::Python::Virtualenv
  desc "Feature Request Git worktree automation tool"
  homepage "https://github.com/user/frg"
  url "https://files.pythonhosted.org/packages/.../frg-0.1.0.tar.gz"
  depends_on "python@3.9"

  def install
    virtualenv_install_with_resources
  end
end
```

**npm Wrapper** (optional for npx users):
```json
{
  "name": "frg-cli",
  "version": "0.1.0",
  "bin": {
    "frg": "./bin/frg-wrapper.js"
  },
  "scripts": {
    "postinstall": "pip install frg"
  }
}
```

**Rationale**:
- PyPI is primary (native Python tooling)
- Homebrew for macOS users who prefer `brew install`
- npm wrapper for JS-centric developers familiar with npx
- All methods install same Python package, ensuring consistency

**Alternatives Considered**:
- **PyInstaller binary**: Large file size (~15-20MB), slow startup
- **Nuitka compilation**: Complex build process, platform-specific
- **Standalone binary in Go/Rust**: Rewrite entire tool, loses Python ecosystem

### 9. Error Handling and Exit Codes

**Decision**: Standard Unix exit codes with descriptive stderr messages

**Exit Code Convention**:
```python
EXIT_SUCCESS = 0
EXIT_VALIDATION_ERROR = 1    # Git/Spec Kit/Claude not found
EXIT_GIT_ERROR = 2           # Git operations failed
EXIT_USER_ERROR = 3          # Invalid arguments
EXIT_RUNTIME_ERROR = 4       # Unexpected errors
```

**Error Message Format**:
```
Error: Git is not installed or not in PATH
  Install git: https://git-scm.com/downloads

Error: Not in a git repository
  Run 'git init' or navigate to an existing repository

Error: Spec Kit not initialized
  Run 'specify init .' to initialize Spec Kit
```

**Rationale**:
- Non-zero exit codes for scripting/automation
- Descriptive messages with actionable next steps
- Consistent format aids parsing/logging
- stderr for errors, stdout for normal output

### 10. Performance Optimization

**Decision**: Lazy validation (fail fast), parallel-safe design

**Optimization Strategies**:
1. **Validation Order**: Check cheapest first (PATH checks before git operations)
2. **Early Exit**: Stop on first failure, no unnecessary work
3. **Git Fetch**: Required for correctness, accept network latency
4. **Caching**: None needed (single-shot execution, no state)

**Benchmark Targets**:
- Validation chain: <500ms (typical case)
- Git fetch: Variable (network-dependent, 1-5 seconds typical)
- Worktree creation: <1 second (local file system operation)
- Total startup: <3 seconds (excluding user interaction with Claude)

**Rationale**:
- CLI tool runs once per feature, not performance-critical
- Network operations (git fetch) dominate latency
- Simplicity over micro-optimization (readable code, maintainable)

## Implementation Notes

### Module Responsibilities

**cli.py**: Click command definition, argument parsing, orchestration
**validators.py**: Prerequisite checks (git, spec-kit, claude, repository)
**git_operations.py**: Git commands (fetch, branch listing, worktree creation)
**worktree.py**: Feature numbering, name sanitization, path resolution
**claude.py**: Claude Code invocation with proper working directory

### Dependencies

**Runtime**:
- click >= 8.0 (CLI framework)
- Python 3.9+ (stdlib only otherwise)

**Development**:
- pytest >= 7.0 (testing framework)
- pytest-subprocess (subprocess mocking)
- pytest-cov (coverage reporting)
- black (code formatting)
- mypy (type checking)

### Configuration

No configuration file needed. All behavior specified via:
- Command-line arguments (feature request text)
- Environment detection (git repo, spec-kit presence)
- Convention over configuration (`.worktrees/` location, `main`/`master` branch)

## Open Questions & Future Enhancements

1. **Worktree Cleanup**: Should `frg` provide a cleanup command for old worktrees?
2. **Config File Support**: Allow customization of worktree location, branch patterns?
3. **Shell Completion**: Provide bash/zsh completion scripts?
4. **Verbose Mode**: Add `-v` flag for detailed operation logging?
5. **Dry Run**: Add `--dry-run` to preview actions without executing?

**Decision**: Defer to post-MVP. Focus on core workflow first, add features based on user feedback.

---

**Research Complete**: All technical unknowns resolved. Ready for Phase 1 design.
