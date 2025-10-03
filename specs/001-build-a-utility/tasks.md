# Tasks: Git Worktree Feature Request Tool

**Input**: Design documents from `/specs/001-build-a-utility/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Extract: Python 3.9+, Click framework, Pydantic, subprocess, pathlib
   → Structure: Single project (spork/ package)
2. Load design documents:
   → data-model.md: 6 Pydantic models (FeatureRequest, ValidationResult, GitRepository, FeatureNumber, WorktreeConfig, CommandContext)
   → contracts/: cli-contract.md (9 test cases), git-operations-contract.md (16 test cases)
   → quickstart.md: Installation flows, validation tests, integration workflow
   → research.md: Technical decisions (Click, Pydantic, subprocess, pytest-subprocess)
3. Generate tasks by category:
   → Setup: Python package, dependencies, linting
   → Tests: Contract tests for CLI (9) + Git ops (16), Pydantic model tests
   → Core: Pydantic models, validators, git operations, worktree logic, Claude invocation, CLI
   → Distribution: PyPI, Homebrew, npm packages
4. Apply task rules:
   → Different modules = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Tasks numbered T001-T066
6. All contract tests before implementation
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
Single project structure at repository root:
- `spork/` - Python package source
- `tests/unit/` - Unit tests
- `tests/integration/` - Integration tests
- `pyproject.toml` - Package configuration
- `README.md` - Documentation

---

## Phase 3.1: Setup

- [X] T001 Create Python package structure (spork/__init__.py, spork/__main__.py)
- [X] T002 [P] Create pyproject.toml with Click>=8.0, Pydantic>=2.0, Python 3.9+ requirements
- [X] T003 [P] Create test directory structure (tests/unit/, tests/integration/)
- [X] T004 [P] Configure pytest with pytest-subprocess in pyproject.toml
- [X] T005 [P] Create .gitignore excluding .worktrees/, __pycache__, dist/, *.pyc

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Pydantic Model Validation Tests
- [X] T006 [P] Write tests for FeatureRequest model validation in tests/unit/test_data_models.py (test text length constraints, sanitized_name validation)
- [X] T007 [P] Write tests for ValidationResult model validation in tests/unit/test_data_models.py (test error_message conditional requirement)
- [X] T008 [P] Write tests for GitRepository model validation in tests/unit/test_data_models.py (test main_branch validation)
- [X] T009 [P] Write tests for FeatureNumber model validation in tests/unit/test_data_models.py (test range 1-999, formatted pattern, number-formatted consistency)
- [X] T010 [P] Write tests for WorktreeConfig model in tests/unit/test_data_models.py (test nested Pydantic model composition)
- [X] T011 [P] Write tests for CommandContext model in tests/unit/test_data_models.py (test optional fields, default factory)

### Git Operations Contract Tests (16 scenarios from git-operations-contract.md)
- [X] T012 [P] Write test_is_git_installed_success in tests/unit/test_git_operations.py
- [X] T013 [P] Write test_is_git_installed_not_found in tests/unit/test_git_operations.py
- [X] T014 [P] Write test_is_git_repository_success in tests/unit/test_git_operations.py
- [X] T015 [P] Write test_is_git_repository_false in tests/unit/test_git_operations.py
- [X] T016 [P] Write test_get_repo_root_success in tests/unit/test_git_operations.py
- [X] T017 [P] Write test_get_repo_root_not_repo in tests/unit/test_git_operations.py
- [X] T018 [P] Write test_get_main_branch_uses_main in tests/unit/test_git_operations.py
- [X] T019 [P] Write test_get_main_branch_uses_master in tests/unit/test_git_operations.py
- [X] T020 [P] Write test_get_main_branch_neither_exists in tests/unit/test_git_operations.py
- [X] T021 [P] Write test_git_fetch_success in tests/unit/test_git_operations.py
- [X] T022 [P] Write test_git_fetch_network_error in tests/unit/test_git_operations.py
- [X] T023 [P] Write test_list_all_branches_success in tests/unit/test_git_operations.py
- [X] T024 [P] Write test_list_all_branches_includes_remote in tests/unit/test_git_operations.py
- [X] T025 [P] Write test_create_worktree_success in tests/unit/test_git_operations.py
- [X] T026 [P] Write test_create_worktree_already_exists in tests/unit/test_git_operations.py
- [X] T027 [P] Write test_create_worktree_permission_denied in tests/unit/test_git_operations.py

### Validators Contract Tests
- [X] T028 [P] Write tests for is_git_installed validator in tests/unit/test_validators.py
- [X] T029 [P] Write tests for is_spec_kit_initialized validator in tests/unit/test_validators.py (check .specify/ structure)
- [X] T030 [P] Write tests for is_claude_code_installed validator in tests/unit/test_validators.py

### Worktree Utilities Contract Tests
- [X] T031 [P] Write tests for sanitize_feature_name in tests/unit/test_worktree.py (lowercase, hyphen replacement, special char removal, length limit)
- [X] T032 [P] Write tests for get_next_feature_number in tests/unit/test_worktree.py (regex parsing, max+1 algorithm, edge cases)

### Claude Code Invocation Tests
- [X] T033 [P] Write tests for launch_claude_code in tests/unit/test_claude.py (subprocess with cwd, exit code propagation)

### CLI Integration Tests (9 scenarios from cli-contract.md)
- [X] T034 [P] Write test_cli_requires_feature_request in tests/integration/test_cli.py
- [X] T035 [P] Write test_cli_validates_git_installed in tests/integration/test_cli.py
- [X] T036 [P] Write test_cli_validates_git_repository in tests/integration/test_cli.py
- [X] T037 [P] Write test_cli_validates_spec_kit in tests/integration/test_cli.py
- [X] T038 [P] Write test_cli_validates_claude_code in tests/integration/test_cli.py
- [X] T039 [P] Write test_cli_success_path in tests/integration/test_cli.py
- [X] T040 [P] Write test_cli_sanitizes_feature_name in tests/integration/test_cli.py
- [X] T041 [P] Write test_cli_handles_special_characters in tests/integration/test_cli.py
- [X] T042 [P] Write test_cli_propagates_claude_exit_code in tests/integration/test_cli.py

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Pydantic Models Module
- [X] T043 Implement FeatureRequest Pydantic model in spork/data_models.py (with field validators for sanitized_name)
- [X] T044 Implement ValidationResult Pydantic model in spork/data_models.py (with model validator for error_message conditional)
- [X] T045 Implement GitRepository Pydantic model in spork/data_models.py (with main_branch validator)
- [X] T046 Implement FeatureNumber Pydantic model in spork/data_models.py (with range validation and formatted consistency check)
- [X] T047 Implement WorktreeConfig Pydantic model in spork/data_models.py (nested model composition)
- [X] T048 Implement CommandContext Pydantic model in spork/data_models.py (with default factory for validation_results)

### Git Operations Module
- [X] T049 Implement is_git_installed, is_git_repository, get_repo_root in spork/git_operations.py
- [X] T050 Implement get_main_branch, git_fetch, list_all_branches in spork/git_operations.py
- [X] T051 Implement create_worktree in spork/git_operations.py

### Validators Module
- [X] T052 [P] Implement is_git_installed validator in spork/validators.py
- [X] T053 [P] Implement is_spec_kit_initialized validator in spork/validators.py (check .specify/memory/constitution.md, templates/, scripts/)
- [X] T054 [P] Implement is_claude_code_installed validator in spork/validators.py

### Worktree Utilities Module
- [X] T055 Implement sanitize_feature_name in spork/worktree.py (lowercase, regex for special chars, hyphen cleanup, length limit)
- [X] T056 Implement get_next_feature_number in spork/worktree.py (regex ^\d{3}-, max+1 algorithm)

### Claude Code Invocation Module
- [X] T057 Implement launch_claude_code in spork/claude.py (subprocess.run with cwd, command: ['claude', '--', '/specify', feature_request])

### CLI Module
- [X] T058 Implement Click command definition in spork/cli.py (single argument for feature-request)
- [X] T059 Implement validation orchestration in spork/cli.py (call all validators, accumulate ValidationResults)
- [X] T060 Implement worktree creation flow in spork/cli.py (fetch, determine number, create WorktreeConfig, call git operations)
- [X] T061 Implement Claude Code launch and exit code propagation in spork/cli.py (call launch_claude_code, return same exit code)

---

## Phase 3.4: Integration & Verification

- [X] T062 Run all tests and ensure they pass (pytest -v) - 83 tests passing
- [ ] T063 [P] Test manual execution: frg "test feature" in local repo
- [ ] T064 [P] Verify error handling: test without git, outside repo, without spec-kit

---

## Phase 3.5: Distribution

- [ ] T065 [P] Create setup.py for PyPI packaging
- [ ] T066 [P] Create README.md with installation and usage instructions (based on quickstart.md)
- [ ] T067 [P] Create Homebrew formula template in homebrew/spork.rb
- [ ] T068 [P] Create npm wrapper package.json for npx distribution

---

## Phase 3.6: Polish

- [ ] T069 [P] Add docstrings to all public functions
- [ ] T070 [P] Run type checking with mypy (if configured)
- [ ] T071 Run final integration tests from quickstart.md
- [ ] T072 Test installation via pip install -e . locally

---

## Dependencies

**Phase Order**:
- Setup (T001-T005) before Tests (T006-T042)
- Tests (T006-T042) before Implementation (T043-T061)
- Implementation (T043-T061) before Integration (T062-T064)
- Integration (T062-T064) before Distribution (T065-T068)
- Distribution (T065-T068) before Polish (T069-T072)

**Within Phases**:
- T043-T048 (Pydantic models) blocks T049-T061 (all modules use models)
- T049-T051 (git_operations) blocks T058-T061 (CLI uses git ops)
- T052-T054 (validators) blocks T058-T061 (CLI uses validators)
- T055-T056 (worktree) blocks T058-T061 (CLI uses worktree utils)
- T057 (claude) blocks T061 (CLI launch logic)

---

## Parallel Execution Examples

### Phase 3.1 Setup (run all in parallel):
```bash
# Launch T002-T005 together (different files):
Task: "Create pyproject.toml with Click>=8.0, Pydantic>=2.0, Python 3.9+ requirements"
Task: "Create test directory structure (tests/unit/, tests/integration/)"
Task: "Configure pytest with pytest-subprocess in pyproject.toml"
Task: "Create .gitignore excluding .worktrees/, __pycache__, dist/, *.pyc"
```

### Phase 3.2 Pydantic Model Tests (run all in parallel):
```bash
# Launch T006-T011 together (same file, different test functions):
Task: "Write tests for FeatureRequest model validation in tests/unit/test_data_models.py (test text length constraints, sanitized_name validation)"
Task: "Write tests for ValidationResult model validation in tests/unit/test_data_models.py (test error_message conditional requirement)"
Task: "Write tests for GitRepository model validation in tests/unit/test_data_models.py (test main_branch validation)"
Task: "Write tests for FeatureNumber model validation in tests/unit/test_data_models.py (test range 1-999, formatted pattern, number-formatted consistency)"
Task: "Write tests for WorktreeConfig model in tests/unit/test_data_models.py (test nested Pydantic model composition)"
Task: "Write tests for CommandContext model in tests/unit/test_data_models.py (test optional fields, default factory)"
```

### Phase 3.2 Git Operations Tests (run all in parallel):
```bash
# Launch T012-T027 together (same file, different test functions):
Task: "Write test_is_git_installed_success in tests/unit/test_git_operations.py"
Task: "Write test_is_git_installed_not_found in tests/unit/test_git_operations.py"
Task: "Write test_is_git_repository_success in tests/unit/test_git_operations.py"
Task: "Write test_is_git_repository_false in tests/unit/test_git_operations.py"
Task: "Write test_get_repo_root_success in tests/unit/test_git_operations.py"
Task: "Write test_get_repo_root_not_repo in tests/unit/test_git_operations.py"
Task: "Write test_get_main_branch_uses_main in tests/unit/test_git_operations.py"
Task: "Write test_get_main_branch_uses_master in tests/unit/test_git_operations.py"
Task: "Write test_get_main_branch_neither_exists in tests/unit/test_git_operations.py"
Task: "Write test_git_fetch_success in tests/unit/test_git_operations.py"
Task: "Write test_git_fetch_network_error in tests/unit/test_git_operations.py"
Task: "Write test_list_all_branches_success in tests/unit/test_git_operations.py"
Task: "Write test_list_all_branches_includes_remote in tests/unit/test_git_operations.py"
Task: "Write test_create_worktree_success in tests/unit/test_git_operations.py"
Task: "Write test_create_worktree_already_exists in tests/unit/test_git_operations.py"
Task: "Write test_create_worktree_permission_denied in tests/unit/test_git_operations.py"
```

### Phase 3.2 Validators Tests (run all in parallel):
```bash
# Launch T028-T030 together (same file, different test functions):
Task: "Write tests for is_git_installed validator in tests/unit/test_validators.py"
Task: "Write tests for is_spec_kit_initialized validator in tests/unit/test_validators.py (check .specify/ structure)"
Task: "Write tests for is_claude_code_installed validator in tests/unit/test_validators.py"
```

### Phase 3.2 Worktree Tests (run all in parallel):
```bash
# Launch T031-T032 together (same file, different test functions):
Task: "Write tests for sanitize_feature_name in tests/unit/test_worktree.py (lowercase, hyphen replacement, special char removal, length limit)"
Task: "Write tests for get_next_feature_number in tests/unit/test_worktree.py (regex parsing, max+1 algorithm, edge cases)"
```

### Phase 3.2 CLI Integration Tests (run all in parallel):
```bash
# Launch T034-T042 together (same file, different test functions):
Task: "Write test_cli_requires_feature_request in tests/integration/test_cli.py"
Task: "Write test_cli_validates_git_installed in tests/integration/test_cli.py"
Task: "Write test_cli_validates_git_repository in tests/integration/test_cli.py"
Task: "Write test_cli_validates_spec_kit in tests/integration/test_cli.py"
Task: "Write test_cli_validates_claude_code in tests/integration/test_cli.py"
Task: "Write test_cli_success_path in tests/integration/test_cli.py"
Task: "Write test_cli_sanitizes_feature_name in tests/integration/test_cli.py"
Task: "Write test_cli_handles_special_characters in tests/integration/test_cli.py"
Task: "Write test_cli_propagates_claude_exit_code in tests/integration/test_cli.py"
```

### Phase 3.3 Pydantic Models Implementation (run all in parallel):
```bash
# Launch T043-T048 together (same file, different class definitions):
Task: "Implement FeatureRequest Pydantic model in spork/data_models.py (with field validators for sanitized_name)"
Task: "Implement ValidationResult Pydantic model in spork/data_models.py (with model validator for error_message conditional)"
Task: "Implement GitRepository Pydantic model in spork/data_models.py (with main_branch validator)"
Task: "Implement FeatureNumber Pydantic model in spork/data_models.py (with range validation and formatted consistency check)"
Task: "Implement WorktreeConfig Pydantic model in spork/data_models.py (nested model composition)"
Task: "Implement CommandContext Pydantic model in spork/data_models.py (with default factory for validation_results)"
```

### Phase 3.3 Validators Implementation (run all in parallel):
```bash
# Launch T052-T054 together (same file, different functions):
Task: "Implement is_git_installed validator in spork/validators.py"
Task: "Implement is_spec_kit_initialized validator in spork/validators.py (check .specify/memory/constitution.md, templates/, scripts/)"
Task: "Implement is_claude_code_installed validator in spork/validators.py"
```

### Phase 3.5 Distribution (run all in parallel):
```bash
# Launch T065-T068 together (different files):
Task: "Create setup.py for PyPI packaging"
Task: "Create README.md with installation and usage instructions (based on quickstart.md)"
Task: "Create Homebrew formula template in homebrew/spork.rb"
Task: "Create npm wrapper package.json for npx distribution"
```

### Phase 3.6 Polish (run docstrings and type checking in parallel):
```bash
# Launch T069-T070 together (different activities):
Task: "Add docstrings to all public functions"
Task: "Run type checking with mypy (if configured)"
```

---

## Notes

- [P] tasks = different files OR different test functions/classes in same file
- Verify all tests FAIL before implementing (TDD)
- Pydantic model tests focus on validation logic (field constraints, custom validators)
- Use pytest-subprocess for all subprocess mocking in git operations and validators
- Use Click's CliRunner for CLI integration tests
- Pydantic models provide automatic validation - tests should verify edge cases and error messages
- All 6 Pydantic models can be implemented in parallel (different class definitions in same file)
- Commit after each major task completion

---

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - cli-contract.md → 9 integration test tasks (T034-T042) [P]
   - git-operations-contract.md → 16 unit test tasks (T012-T027) [P]

2. **From Data Model**:
   - 6 Pydantic models → 6 test tasks (T006-T011) [P] + 6 implementation tasks (T043-T048) [P]
   - Validation logic embedded in models via Pydantic validators

3. **From Quickstart**:
   - Installation flows → distribution tasks (T065-T068) [P]
   - Validation tests → integration verification (T062-T064)

4. **Ordering**:
   - Setup → All Tests → Pydantic Models → Git Ops → Validators → Worktree → Claude → CLI → Integration → Distribution → Polish
   - Tests come before ALL implementation
   - Dependencies block parallel execution within implementation phase

---

## Validation Checklist
*GATE: Checked before execution*

- [x] All contracts have corresponding tests (25 contract tests: 9 CLI + 16 git ops)
- [x] All entities have test tasks (6 Pydantic model test tasks)
- [x] All tests come before implementation (Phase 3.2 before 3.3)
- [x] Parallel tasks truly independent (marked [P] appropriately)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task (exception: different functions/classes in same module can be parallel)
- [x] Pydantic validation logic included in model tasks

---

**Tasks Ready for Execution**: 72 tasks, maximum parallelization applied per phase, updated for Pydantic models
