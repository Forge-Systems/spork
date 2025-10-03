# CLI Contract: frg Command

**Version**: 1.0.0
**Date**: 2025-10-02

## Command Signature

```bash
frg <feature-request>
```

## Arguments

### Positional Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `feature-request` | string | Yes | Natural language description of the feature to implement |

**Validation**:
- Must be provided (not empty)
- Must be between 1-500 characters
- Can contain spaces, special characters (will be sanitized for branch name)
- Multiple words should be quoted: `spork "add user authentication"`

### Options/Flags

None in MVP. Future: `--verbose`, `--dry-run`, `--base-branch`

## Exit Codes

| Code | Name | Meaning | Example Scenario |
|------|------|---------|------------------|
| 0 | SUCCESS | Command completed successfully | Worktree created, Claude launched |
| 1 | VALIDATION_ERROR | Prerequisite validation failed | Git not installed, not in git repo, Spec Kit missing |
| 2 | GIT_ERROR | Git operation failed | `git fetch` failed, `git worktree add` failed |
| 3 | USER_ERROR | Invalid user input | No feature request provided, empty argument |
| 4 | RUNTIME_ERROR | Unexpected error | Permission denied, disk full, etc. |

## Standard Output (stdout)

**Success Path**:
```
✓ Validating prerequisites...
✓ Git found: /usr/bin/git
✓ In git repository: /Users/dev/my-project
✓ Spec Kit initialized
✓ Claude Code found: /opt/homebrew/bin/claude
✓ Fetching remote branches...
✓ Next feature number: 001
✓ Creating worktree at .worktrees/001-add-user-auth
✓ Launching Claude Code...
```

**Format Rules**:
- Progress indicators use `✓` checkmark for completed steps
- Paths shown as relative to repo root when possible
- Clear, concise messages (one line per step)
- No output after "Launching Claude Code" (control transferred to Claude)

## Standard Error (stderr)

**Error Path**:
```
Error: Git is not installed or not in PATH
  Install git: https://git-scm.com/downloads

Error: Not in a git repository
  Run 'git init' or navigate to an existing repository

Error: Spec Kit not initialized
  Run 'specify init .' to initialize Spec Kit

Error: Claude Code not found in PATH
  Install Claude Code or add to PATH
```

**Format Rules**:
- Errors prefixed with `Error: `
- Multi-line format: error message, then indented suggestion
- Actionable suggestions with specific commands
- URL links for installation help where applicable

## Input Handling

### Argument Parsing

**Single Word**:
```bash
frg authentication
# Parsed as: "authentication"
```

**Multi-Word (Quoted)**:
```bash
frg "add user authentication"
# Parsed as: "add user authentication"
```

**Multi-Word (Unquoted) - Shell Handles**:
```bash
frg add user authentication
# Shell splits into: ["add", "user", "authentication"]
# frg receives only: "add"
# User error: must quote multi-word requests
```

**Special Characters**:
```bash
frg "fix bug #123 (critical!)"
# Parsed as: "fix bug #123 (critical!)"
# Sanitized for branch: "fix-bug-123-critical"
```

### Validation Sequence

1. Parse CLI arguments
2. Validate feature request provided and not empty
3. Check git installed
4. Check in git repository
5. Check Spec Kit installed (`.specify/` exists)
6. Check Spec Kit initialized (constitution, templates, scripts exist)
7. Check Claude Code installed
8. Run `git fetch`
9. Determine next feature number
10. Create worktree
11. Launch Claude Code

**Fail-Fast**: Stop at first failed validation, print error, exit with appropriate code

## Interactive Behavior

**Blocking Operation**: Command runs synchronously, blocking terminal until Claude Code session ends

**Terminal Control**:
- Before Claude launch: `frg` controls stdout/stderr
- After Claude launch: Claude Code controls stdin/stdout/stderr
- User interacts directly with Claude (no frg intermediation)

**Session End**: When Claude exits, `frg` exits with same exit code

## Environment Requirements

**Required in PATH**:
- `git` (any version 2.x)
- `claude` (Claude Code CLI)

**Required in Repository**:
- `.git/` directory (valid git repository)
- `.specify/` directory with proper structure

**Optional**:
- Git remote (for `git fetch`; warning if missing but not fatal)

## Examples

### Example 1: Successful Execution

```bash
$ cd ~/projects/my-app
$ frg "add user profile page"
✓ Validating prerequisites...
✓ Git found: /usr/bin/git
✓ In git repository: /Users/dev/projects/my-app
✓ Spec Kit initialized
✓ Claude Code found: /opt/homebrew/bin/claude
✓ Fetching remote branches...
✓ Next feature number: 003
✓ Creating worktree at .worktrees/003-add-user-profile-page
✓ Launching Claude Code...

[Claude Code interactive session begins]
```

**Exit Code**: 0 (if Claude completes successfully)

### Example 2: Git Not Installed

```bash
$ frg "add feature"
Error: Git is not installed or not in PATH
  Install git: https://git-scm.com/downloads
```

**Exit Code**: 1

### Example 3: Not in Git Repository

```bash
$ cd ~/Desktop
$ frg "add feature"
Error: Not in a git repository
  Run 'git init' or navigate to an existing repository
```

**Exit Code**: 1

### Example 4: Spec Kit Not Initialized

```bash
$ cd ~/projects/new-repo
$ frg "add feature"
Error: Spec Kit not initialized (.specify/ directory missing)
  Run 'specify init .' to initialize Spec Kit in this repository
```

**Exit Code**: 1

### Example 5: No Feature Request Provided

```bash
$ frg
Error: Feature request is required
  Usage: frg <feature-request>
  Example: frg "add user authentication"
```

**Exit Code**: 3

## Contract Tests

**Test Cases** (to be implemented in `tests/integration/test_cli.py`):

1. **test_cli_requires_feature_request**: Verify exit code 3 when no argument
2. **test_cli_validates_git_installed**: Mock `which git` to fail, verify exit code 1
3. **test_cli_validates_git_repository**: Run in non-git dir, verify exit code 1
4. **test_cli_validates_spec_kit**: Run in repo without `.specify/`, verify exit code 1
5. **test_cli_validates_claude_code**: Mock `which claude` to fail, verify exit code 1
6. **test_cli_success_path**: Mock all prerequisites, verify exit code 0 and output format
7. **test_cli_sanitizes_feature_name**: Verify branch name sanitization in output
8. **test_cli_handles_special_characters**: Test with quotes, symbols, verify proper handling
9. **test_cli_propagates_claude_exit_code**: If Claude exits with non-zero, frg should match

**Assertion Focus**:
- Exit codes match specification
- Error messages match format (prefix, suggestion structure)
- Success output includes all checkmarks and steps
- Path formatting (relative vs absolute)

---

**CLI Contract Complete**: Defines complete command-line interface behavior.
