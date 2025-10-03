# spork

A CLI utility that combines git-worktrees, Claude Code, and Spec Kit from GitHub.

## Why "spork"?

The name is a playful portmanteau combining:
- **Spec** Kit - GitHub's feature specification framework
- **Work**tree - Git's isolated workspace feature
- **Fork** - Creating branches from main

Just like the utensil combines a spoon and fork, `spork` combines multiple development tools into one unified workflow for feature development.

## Installation

### Prerequisites

- Python 3.9+
- Git
- [Claude Code CLI](https://docs.claude.com/claude-code)
- Spec Kit initialized on your main/master branch

### Install from source

```bash
# Clone the repository
git clone https://github.com/Forge-Systems/frg.git
cd frg

# Install with pipx (installs globally, isolated)
pipx install .

# OR install in a virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Verify installation

```bash
spork --help
```

**Note:** If using virtual environment installation, remember to activate it before running `spork`:
```bash
source .venv/bin/activate
spork "your feature request"
```

## Usage

```bash
spork "add user authentication"
```

This will:
1. Validate prerequisites (git, Spec Kit on main branch, Claude Code)
2. Create a new git worktree in `.worktrees/001-add-user-authentication/`
3. Launch Claude Code with `/specify add user authentication` 
