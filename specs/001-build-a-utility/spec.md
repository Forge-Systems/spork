# Feature Specification: Git Worktree Feature Request Tool

**Feature Branch**: `001-build-a-utility`
**Created**: 2025-10-02
**Status**: Draft
**Input**: User description: "build a utility that combines spec kit, claude code and git worktrees. I want to be able to go into a repo, write "frg <feature request>". Then, the current terminal shell I'm in shall create a new git worktree of the given repo, run claude code. and prompt it with "/specify <feature>" and run it."

## Execution Flow (main)
```
1. Parse user description from Input
   → If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   → Identify: actors, actions, data, constraints
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the prompt doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **Common underspecified areas**:
   - User types and permissions
   - Data retention/deletion policies
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements
   - Security/compliance needs

---

## Clarifications

### Session 2025-10-02
- Q: Worktree naming strategy when multiple developers run `frg` in same repository → A: Use incremental numbering (001-feature-name, 002-feature-name, etc.) derived from sanitized feature request text
- Q: Worktree location relative to main repository → A: Subdirectory within the main repo (e.g., `/path/to/repo/.worktrees/001-feature-name`)
- Q: Base branch for worktree creation → A: Always use the main/master branch (detect which exists)
- Q: Failure handling when worktree creation fails → A: Report error and exit immediately (no cleanup needed, no partial state)
- Q: Claude Code availability validation before worktree creation → A: Yes, validate before worktree creation; fail fast if not found
- Q: Claude Code session behavior after launch → A: Claude Code runs interactively in current shell (blocking operation, user interacts directly)

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
A developer working in a git repository wants to start a new feature specification workflow. They navigate to the repository directory in their terminal and run `spork <feature request>` where the feature request is a natural language description of what they want to build. The tool automatically creates an isolated workspace using git worktrees, launches Claude Code interactively in that workspace within the current shell, and initiates the specification process by running `/specify <feature>` with the provided feature request. The developer interacts directly with Claude Code in their current terminal session to complete the specification workflow.

### Acceptance Scenarios
1. **Given** a developer is in a git repository with Spec Kit initialized, **When** they run `spork "add user authentication"`, **Then** the system validates all prerequisites (git, Spec Kit, Claude Code), creates a new git worktree, launches Claude Code in that worktree, and runs the `/specify` command with "add user authentication" as input
2. **Given** a developer runs `frg` without providing a feature request, **When** the command executes, **Then** the system displays an error message indicating a feature request is required
3. **Given** a developer is not in a git repository, **When** they run `spork <feature>`, **Then** the system displays an error message indicating the command must be run from within a git repository
4. **Given** a developer is in a git repository without Spec Kit installed, **When** they run `spork <feature>`, **Then** the system displays an error message indicating Spec Kit must be installed and initialized
5. **Given** git or Claude Code is not installed, **When** a developer runs `spork <feature>`, **Then** the system displays an error message indicating which tool is missing
6. **Given** a developer runs `frg` with a multi-word feature request, **When** the command executes, **Then** the entire feature request is passed correctly to the `/specify` command, preserving spacing and special characters

### Edge Cases
- What happens when the worktree creation fails (e.g., due to naming conflicts or insufficient permissions)? → System reports error and exits immediately without cleanup
- How does the system handle situations where Claude Code is not installed or not accessible in the PATH? → System validates Claude Code availability before creating worktree; fails fast with error message if not found
- What happens if the user provides a feature request with special shell characters (quotes, backticks, etc.)? → System must properly escape/sanitize these for worktree naming
- How should the system behave if the current repository has uncommitted changes? → No safety checks required; worktree creation is isolated and non-destructive to working directory
- What happens when multiple developers run `frg` simultaneously in the same repository? → System fetches remote branches first, then determines next available feature number avoiding conflicts with both local and remote branches
- What happens if `git fetch` fails (network issues, authentication problems)? → System reports error and exits immediately per fail-fast policy

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST accept a feature request as a command-line argument after the `frg` command
- **FR-002**: System MUST validate that git is installed and accessible in PATH
- **FR-003**: System MUST validate that the command is executed from within a git repository directory
- **FR-004**: System MUST validate that GitHub Spec Kit is installed in the repository (check for `.specify/` directory)
- **FR-005**: System MUST validate that Spec Kit is properly initialized (verify existence of `.specify/memory/constitution.md`, `.specify/templates/`, and `.specify/scripts/`)
- **FR-005a**: System MUST validate that Spec Kit exists on the main/master branch (not just in current worktree) by checking `git show main:.specify/memory/constitution.md` succeeds
- **FR-006**: System MUST validate Claude Code availability in PATH before proceeding with worktree creation
- **FR-007**: System MUST run `git fetch` to update remote branch information before determining the next available feature number
- **FR-008**: System MUST check for existing local and remote branches matching the pattern `<number>-*` to identify the next available feature number
- **FR-009**: System MUST create worktrees in `.worktrees/` subdirectory within the main repository
- **FR-010**: System MUST use incremental numbering for worktree names (001-feature-name, 002-feature-name, etc.) derived from sanitized feature request text, selecting the next number not used by any existing local or remote branch
- **FR-011**: System MUST create new worktree based on the main/master branch (detecting which exists in the repository)
- **FR-012**: System MUST launch Claude Code interactively in the newly created worktree within the current shell (blocking operation)
- **FR-013**: System MUST launch Claude Code with an initial message containing the `/specify` command and the user-provided feature request
- **FR-014**: System MUST transfer control to the Claude Code interactive session, allowing direct user interaction until session completes
- **FR-015**: System MUST display an error message when run without a feature request argument
- **FR-016**: System MUST handle feature requests containing spaces, quotes, and special characters correctly by sanitizing for worktree naming
- **FR-017**: System MUST provide feedback to the user about each step of the process (validation, git fetch, branch conflict checking, worktree creation, Claude Code launch)
- **FR-018**: System MUST report error and exit immediately when any validation check fails or when worktree creation fails, without attempting cleanup or retry

### Key Entities
- **Feature Request**: A natural language description of the desired feature, provided as input to the tool and passed to the specification workflow
- **Worktree**: An isolated git workspace created in `.worktrees/<number>-<sanitized-name>` subdirectory, based on main/master branch
- **Worktree Name**: Incrementally numbered identifier (001, 002, etc.) combined with sanitized feature request text
- **Command Invocation**: The execution context capturing the user's request, including the feature description and current repository state
- **Spec Kit Installation**: GitHub Spec Kit presence indicated by `.specify/` directory with required subdirectories (memory, templates, scripts)
- **Validation Chain**: Sequential prerequisite checks (git installed → in git repo → Spec Kit installed → Spec Kit initialized → Claude Code available)

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---
