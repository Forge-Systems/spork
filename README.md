# spork

A CLI utility that combines git-worktrees, Claude Code, and Spec Kit from GitHub.

## Why "spork"?

The name is a playful portmanteau combining:
- **Spec** Kit - GitHub's feature specification framework
- **Work**tree - Git's isolated workspace feature
- **Fork** - Creating branches from main

Just like the utensil combines a spoon and fork, `spork` combines multiple development tools into one unified workflow for feature development.

## Installation

**Prerequisites:** Python 3.9+, Git, [Claude Code CLI](https://docs.claude.com/claude-code)

```bash
git clone https://github.com/Forge-Systems/spork.git
cd spork
pipx install .
```

**For development:**
```bash
./setup.sh
source .venv/bin/activate
```

## Usage

```bash
spork "add user authentication"
```

This will:
1. Validate prerequisites (git, Spec Kit on main branch, Claude Code)
2. Create a new git worktree in `.worktrees/001-add-user-authentication/`
3. Launch Claude Code with `/specify add user authentication`

## Development

Requires [just](https://github.com/casey/just) command runner (`brew install just`):

```bash
just lint       # Run linter
just typecheck  # Run type checker
just test       # Run tests
just check      # Run all checks
``` 
