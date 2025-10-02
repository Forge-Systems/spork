# Quickstart Guide: frg CLI Tool

**Version**: 1.0.0
**Date**: 2025-10-02

## Installation

### Option 1: Install via pip (PyPI)

```bash
pip install frg
```

### Option 2: Install via Homebrew (macOS/Linux)

```bash
brew tap yourusername/frg
brew install frg
```

### Option 3: Install via npm

```bash
npm install -g frg-cli
# or use npx without installation
npx frg-cli "your feature request"
```

### Verify Installation

```bash
frg --version
# Expected output: frg 0.1.0
```

## Prerequisites

Before using `frg`, ensure you have:

1. **Git** installed and in PATH
   ```bash
   git --version
   # Should show: git version 2.x.x
   ```

2. **Claude Code** installed and in PATH
   ```bash
   claude --version
   # Should show Claude Code version
   ```

3. **GitHub Spec Kit** installed
   ```bash
   specify --version
   # Should show specify-cli version
   ```

## Setup Your Repository

1. **Initialize a git repository** (if not already done):
   ```bash
   cd your-project
   git init
   ```

2. **Initialize Spec Kit**:
   ```bash
   specify init .
   ```

   This creates the `.specify/` directory with templates and scripts.

3. **Verify Spec Kit initialization**:
   ```bash
   ls .specify/
   # Should show: memory/ templates/ scripts/
   ```

## Usage

### Basic Usage

```bash
frg "<your-feature-request>"
```

### Example 1: Create Your First Feature

```bash
cd ~/projects/my-app
frg "add user authentication system"
```

**What happens**:
1. ✓ Validates git, Spec Kit, and Claude Code are installed
2. ✓ Fetches latest remote branches
3. ✓ Determines next feature number (e.g., 001)
4. ✓ Creates worktree at `.worktrees/001-add-user-authentication-system`
5. ✓ Launches Claude Code interactively in the new worktree
6. Claude runs `/specify "add user authentication system"`

**You then interact with Claude Code** to complete the specification workflow.

### Example 2: Multiple Features

```bash
# First feature
frg "implement payment processing"
# Creates: .worktrees/001-implement-payment-processing

# After completing the first feature, create another
frg "add email notifications"
# Creates: .worktrees/002-add-email-notifications

# Numbers increment automatically based on existing branches
```

### Example 3: Special Characters in Feature Requests

```bash
# Quotes and symbols are handled automatically
frg "fix bug #123 (critical priority!)"
# Creates: .worktrees/003-fix-bug-123-critical-priority
```

## Workflow

### Step-by-Step Workflow

1. **Navigate to your repository**:
   ```bash
   cd ~/projects/my-app
   ```

2. **Run frg with your feature idea**:
   ```bash
   frg "add dark mode support"
   ```

3. **Wait for validation and worktree creation**:
   ```
   ✓ Validating prerequisites...
   ✓ Git found: /usr/bin/git
   ✓ In git repository: /Users/you/projects/my-app
   ✓ Spec Kit initialized
   ✓ Claude Code found: /opt/homebrew/bin/claude
   ✓ Fetching remote branches...
   ✓ Next feature number: 004
   ✓ Creating worktree at .worktrees/004-add-dark-mode-support
   ✓ Launching Claude Code...
   ```

4. **Interact with Claude Code**:
   - Claude runs `/specify "add dark mode support"` automatically
   - You collaborate with Claude to create the feature specification
   - Answer clarifying questions
   - Review and refine the spec

5. **When done with Claude**:
   - Exit Claude Code (Ctrl+D or type "exit")
   - Your original terminal session resumes

6. **Review the created artifacts**:
   ```bash
   ls .worktrees/004-add-dark-mode-support/specs/004-add-dark-mode-support/
   # Shows: spec.md, plan.md, etc.
   ```

7. **Continue with implementation**:
   ```bash
   cd .worktrees/004-add-dark-mode-support
   # Run /plan, /tasks, /implement commands in Claude Code
   ```

## Validation Tests

### Test: Prerequisites Check

**Validate git is installed**:
```bash
which git
# Should output path to git binary
```

**Validate Claude Code is installed**:
```bash
which claude
# Should output path to claude binary
```

**Validate you're in a git repository**:
```bash
git rev-parse --is-inside-work-tree
# Should output: true
```

**Validate Spec Kit is initialized**:
```bash
ls .specify/memory/constitution.md
# Should exist
ls .specify/templates/
# Should show template files
```

### Test: Successful Execution

**Run frg in a properly configured repository**:
```bash
cd ~/projects/test-repo
frg "test feature"
```

**Expected outcomes**:
- ✅ No error messages
- ✅ Worktree created at `.worktrees/001-test-feature`
- ✅ Claude Code launches
- ✅ `/specify` command executes automatically
- ✅ Exit code 0 when Claude completes

### Test: Error Handling

**Test 1: Run without git**:
```bash
PATH=/usr/bin frg "test"
# Expected: Error: Git is not installed or not in PATH
```

**Test 2: Run outside git repository**:
```bash
cd /tmp
frg "test"
# Expected: Error: Not in a git repository
```

**Test 3: Run without Spec Kit**:
```bash
cd ~/projects/repo-without-speckit
frg "test"
# Expected: Error: Spec Kit not initialized
```

**Test 4: Run without feature request**:
```bash
frg
# Expected: Error: Feature request is required
```

## Troubleshooting

### Issue: "Git is not installed"

**Solution**:
```bash
# macOS
brew install git

# Linux (Debian/Ubuntu)
sudo apt-get install git

# Verify installation
git --version
```

### Issue: "Not in a git repository"

**Solution**:
```bash
# Initialize a new repository
git init

# Or navigate to an existing repository
cd /path/to/your/repo
```

### Issue: "Spec Kit not initialized"

**Solution**:
```bash
# Install Spec Kit if not already installed
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Initialize in your repository
specify init .

# Verify initialization
ls .specify/
```

### Issue: "Claude Code not found"

**Solution**:
```bash
# Install Claude Code (check official documentation for latest instructions)
# Verify it's in your PATH
claude --version

# If installed but not in PATH, add to PATH in your shell profile
export PATH="$PATH:/path/to/claude"
```

### Issue: "Git fetch failed"

**Possible Causes**:
- Network connectivity issues
- Authentication problems with remote
- No remote configured (not critical, will show warning)

**Solution**:
```bash
# Check network connection
ping github.com

# Verify remote configuration
git remote -v

# If no remote, add one (optional for frg)
git remote add origin https://github.com/user/repo.git
```

### Issue: "Worktree already exists"

**Cause**: A worktree with that number already exists

**Solution**:
```bash
# List existing worktrees
git worktree list

# Remove old worktree if no longer needed
git worktree remove .worktrees/001-feature-name

# Or run frg again (it will use next available number)
frg "your feature request"
```

## Advanced Usage

### Working with Remote Teams

```bash
# Always fetch first to see team members' branches
git fetch

# frg automatically does this, but good to know the current state
git branch -a | grep "origin/"

# Run frg - it will pick the next available number
frg "your feature"
```

### Cleaning Up Old Worktrees

```bash
# List all worktrees
git worktree list

# Remove a specific worktree
git worktree remove .worktrees/001-old-feature

# Prune deleted worktrees
git worktree prune
```

### Checking Feature Branch Status

```bash
# See all feature branches
git branch -a | grep "^\s*\d{3}-"

# See worktrees
ls .worktrees/
```

## Integration with Spec Kit Workflow

### Complete Spec-Driven Development Workflow

```bash
# 1. Start new feature with frg
frg "implement user dashboard"
# → Creates worktree, launches Claude with /specify

# 2. In Claude Code session, complete specification
# → Answer clarification questions
# → Review generated spec.md

# 3. Run planning
# → Type /plan in Claude Code
# → Review generated plan.md, data-model.md, etc.

# 4. Generate tasks
# → Type /tasks in Claude Code
# → Review generated tasks.md

# 5. Implement
# → Type /implement in Claude Code
# → Or manually work through tasks.md

# 6. When complete, commit and push
git add .
git commit -m "feat: implement user dashboard"
git push -u origin 001-implement-user-dashboard

# 7. Create pull request (via GitHub CLI or web)
gh pr create --title "Implement user dashboard"
```

## Next Steps

After successfully running `frg`:

1. **Complete the specification** with Claude Code
2. **Review generated artifacts** in `specs/###-feature-name/`
3. **Run `/plan`** in Claude to create implementation plan
4. **Run `/tasks`** to break down into actionable tasks
5. **Run `/implement`** or manually execute tasks
6. **Commit and push** your feature branch
7. **Create pull request** for review

## Getting Help

```bash
# Show frg version
frg --version

# Show help (future feature)
frg --help
```

For issues or feature requests, visit: [GitHub Repository URL]

---

**Quickstart Complete**: You're ready to use `frg` for spec-driven development!
