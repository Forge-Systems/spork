# Implementation Plan: Git Worktree Feature Request Tool

**Branch**: `001-build-a-utility` | **Date**: 2025-10-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-build-a-utility/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Build a CLI utility (`spork`) that automates the feature specification workflow by integrating git worktrees, GitHub Spec Kit, and Claude Code. The tool validates prerequisites, creates isolated worktree environments, and launches Claude Code interactively to execute the `/specify` command with user-provided feature requests. Packaged as a Python CLI tool distributable via Homebrew and npm.

## Technical Context
**Language/Version**: Python 3.9+ (for broad compatibility, packagable as standalone binary)
**Primary Dependencies**: Click (CLI framework), Pydantic (data validation), subprocess (git/Claude Code invocation), pathlib (file system operations)
**Storage**: File system (worktrees in `.worktrees/` subdirectory, branch tracking via git)
**Testing**: pytest with pytest-subprocess for mocking external commands
**Target Platform**: macOS/Linux (Unix-like systems with bash, git, and Claude Code installed)
**Project Type**: single (CLI utility, Python package)
**Performance Goals**: <1 second for validation checks, <3 seconds total startup time (excluding git fetch network latency)
**Constraints**: Interactive blocking operation (user must remain in shell), fail-fast on any validation error, preserve user's working directory
**Scale/Scope**: Single-user CLI tool, supports repositories with any number of existing feature branches
**Distribution**: Homebrew tap (macOS/Linux), npm package (via pyinstaller binary or npx wrapper), PyPI package

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Constitution file contains only template placeholders. Proceeding with standard CLI tool best practices:

- **Library-First Principle**: CLI tool will be structured as a Python package with reusable modules
- **CLI Interface**: Primary interface is `frg` command accepting feature request as argument, built with Click framework
- **Test-First**: Unit and integration tests will be written before implementation using pytest
- **Simplicity**: Single-purpose CLI, minimal abstractions, clear sequential validation and execution logic
- **Fail-Fast**: No error recovery, immediate exit on validation failures with clear error messages

✅ **PASS**: No constitutional violations detected. Python CLI tool aligns with standard development principles and enables broad distribution via multiple package managers.

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
spork/                         # Python package
├── __init__.py
├── __main__.py              # Entry point for `python -m spork`
├── cli.py                   # Click CLI definition
├── validators.py            # Validation functions (git, spec-kit, claude-code)
├── git_operations.py        # Git worktree and branch operations
├── worktree.py              # Worktree naming and path management
└── claude.py                # Claude Code invocation logic

tests/
├── unit/
│   ├── test_validators.py
│   ├── test_git_operations.py
│   ├── test_worktree.py
│   └── test_claude.py
└── integration/
    ├── test_cli.py          # Full CLI integration tests
    └── test_end_to_end.py   # Complete workflow validation

pyproject.toml               # Python package configuration (PEP 621)
setup.py                     # Build configuration
README.md                    # Installation and usage docs
.gitignore                   # Exclude .worktrees/, __pycache__, etc.

# Distribution files (generated)
dist/                        # Built packages (PyPI)
homebrew/                    # Homebrew formula
package.json                 # npm wrapper configuration
```

**Structure Decision**: Single project structure selected. Python CLI package with modular design: validators, git operations, worktree management, and Claude Code invocation as separate modules. Distribution via PyPI (pip install), Homebrew tap, and npm (npx wrapper or binary distribution). The `.worktrees/` directory is created dynamically and excluded from version control.

## Phase 0: Outline & Research

✅ **COMPLETED** - See [research.md](research.md)

**Research Areas Covered**:
1. Python CLI Framework Selection → Click framework
2. Git Worktree Operations → subprocess with direct git commands
3. Feature Number Determination → Regex parsing with max+1 algorithm
4. String Sanitization → Lowercase, hyphen replacement, length limiting
5. Spec Kit Detection → Directory structure validation
6. Claude Code Invocation → subprocess with cwd parameter
7. Testing Strategy → pytest with pytest-subprocess
8. Package Distribution → Multi-channel (PyPI, Homebrew, npm)
9. Error Handling → Unix exit codes with descriptive messages
10. Performance Optimization → Fail-fast, minimal latency

**Key Decisions**:
- Language: Python 3.9+ for broad compatibility and packaging
- CLI Framework: Click for elegant API and built-in testing
- Data Validation: Pydantic for robust input validation and type safety
- Git Operations: Direct subprocess calls (no GitPython dependency)
- Distribution: Primary via PyPI, secondary via Homebrew/npm
- Testing: pytest with subprocess mocking for fast, deterministic tests

**Output**: research.md with all technical unknowns resolved

## Phase 1: Design & Contracts

✅ **COMPLETED** - See artifacts below

**1. Data Model** → [data-model.md](data-model.md):
   - FeatureRequest: User input and sanitized name (Pydantic model with validation)
   - ValidationResult: Check outcomes with error messages (Pydantic model)
   - GitRepository: Repository metadata and main branch (Pydantic model)
   - FeatureNumber: Numeric identifier with formatting (Pydantic model with range validation)
   - WorktreeConfig: Complete worktree creation configuration (Pydantic model)
   - CommandContext: Overall execution state and lifecycle (Pydantic model)

**2. Contracts** → [contracts/](contracts/):
   - [cli-contract.md](contracts/cli-contract.md): Complete CLI interface specification
     * Command signature, arguments, exit codes
     * stdout/stderr format and error messages
     * Input handling and validation sequence
     * 9 contract test scenarios defined
   - [git-operations-contract.md](contracts/git-operations-contract.md): Git command specifications
     * 7 git operations with command syntax
     * Success criteria and failure scenarios
     * Error handling and exit code mapping
     * 16 contract test cases defined

**3. Test Scenarios** → Contract test specifications:
   - CLI contract tests (9 scenarios in integration suite)
   - Git operations tests (16 unit tests with subprocess mocking)
   - End-to-end integration tests (quickstart validation)

**4. Quickstart Guide** → [quickstart.md](quickstart.md):
   - Installation instructions (pip, brew, npm)
   - Prerequisites verification steps
   - Complete workflow walkthrough
   - Troubleshooting guide
   - Integration with Spec Kit workflow

**5. Agent Context** → CLAUDE.md:
   - Updated with Python 3.9+, Click framework, Pydantic
   - Added subprocess, pathlib dependencies
   - File system storage strategy documented
   - ✅ Generated via update-agent-context.sh

**Output**: All Phase 1 artifacts generated and ready for implementation

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Module structure: validators.py, git_operations.py, worktree.py, claude.py, cli.py
- Each module gets: dataclass definitions [P] → unit tests [P] → implementation
- Integration tests after all modules implemented

**Task Breakdown by Module**:

1. **Project Setup** (1-4):
   - Create Python package structure (spork/)
   - Setup pyproject.toml with Click dependency [P]
   - Create test infrastructure (pytest, pytest-subprocess) [P]
   - Setup .gitignore

2. **Data Models** (5-8):
   - Define Pydantic models in separate module (FeatureRequest, ValidationResult, etc.) [P]
   - Write unit tests for Pydantic model validation [P]
   - Implement custom validators (frozen config, field validators)
   - Write tests for edge cases and validation errors

3. **Validators Module** (9-14):
   - Write contract tests for git_installed check [P]
   - Implement is_git_installed() function
   - Write contract tests for repository check [P]
   - Implement is_git_repository() function
   - Write contract tests for spec_kit checks [P]
   - Implement spec_kit validation functions

4. **Git Operations Module** (15-20):
   - Write contract tests for git_fetch [P]
   - Implement git_fetch() function
   - Write contract tests for list_branches [P]
   - Implement list_all_branches() function
   - Write contract tests for create_worktree [P]
   - Implement create_worktree() function

5. **Worktree Module** (21-24):
   - Write tests for sanitize_feature_name [P]
   - Implement sanitization logic
   - Write tests for feature number determination [P]
   - Implement get_next_feature_number() function

6. **Claude Code Invocation** (25-26):
   - Write tests for Claude Code invocation [P]
   - Implement launch_claude_code() function

7. **CLI Module** (27-30):
   - Write Click command definition tests [P]
   - Implement main CLI command with Click
   - Write integration tests for full workflow
   - Implement orchestration logic

8. **Distribution** (31-34):
   - Create pyproject.toml for PyPI [P]
   - Create Homebrew formula [P]
   - Create npm wrapper package.json [P]
   - Write installation validation tests

9. **Documentation** (35-36):
   - Create README.md with installation/usage [P]
   - Add inline code documentation (docstrings)

**Ordering Strategy**:
- TDD order: Tests before implementation for every module
- Dependency order: Data models → Utilities (validators, git ops, worktree) → CLI → Integration
- Mark [P] for parallel execution (independent test/implementation pairs)
- Integration tests last (require all modules complete)

**Estimated Output**: 35-40 numbered, ordered tasks in tasks.md

**Key Test-First Principles**:
- Every function has tests written before implementation
- Contract tests define expected behavior explicitly
- pytest-subprocess mocks all external commands (git, claude)
- Integration tests use CliRunner for end-to-end validation

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (none)

---
*Based on Constitution (template) - See `/.specify/memory/constitution.md`*
